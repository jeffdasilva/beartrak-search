import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import Depends, FastAPI, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from database import (
    RequestForProposalModel,
    clear_database,
    create_rfp_db,
    delete_rfp_db,
    get_all_rfps_db,
    get_async_session,
    get_rfp_by_id_db,
    init_database,
    search_rfps_db,
    update_rfp_db,
)
from models import HealthResponse, RFPCreate, RFPResponse, RFPUpdate


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager for startup and shutdown events."""
    # Startup
    await init_database()
    # Note: populate_sample_data() removed - database starts empty
    yield
    # Shutdown (if needed)


app = FastAPI(
    title="BearTrak RFP Search API",
    description="Backend API for BearTrak RFP Search frontend with SQLite database",
    lifespan=lifespan,
    # Optimize for production - disable docs generation in production
    docs_url="/docs"
    if os.getenv("BEARTRAK_ENVIRONMENT", "development").lower() != "production"
    else None,
    redoc_url="/redoc"
    if os.getenv("BEARTRAK_ENVIRONMENT", "development").lower() != "production"
    else None,
)

# Configure CORS to allow requests from your frontend
cors_origins_env = os.getenv("BEARTRAK_CORS_ORIGINS")
if cors_origins_env:
    # Parse the JSON-like string from environment only if set
    import json

    try:
        cors_origins = json.loads(cors_origins_env)
    except json.JSONDecodeError:
        # Fallback to default if parsing fails
        cors_origins = ["*"]
else:
    # Default origins when environment variable is not set
    cors_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)


def convert_to_rfp_response(rfp_model: RequestForProposalModel) -> RFPResponse:
    """Convert SQLAlchemy RequestForProposalModel to Pydantic RFPResponse."""
    return RFPResponse(
        id=rfp_model.id,
        name=rfp_model.name,
        url=rfp_model.url,
        description=rfp_model.description,
        updated_at=rfp_model.updated_at,
    )


async def search_rfps(query: str, session: AsyncSession) -> list[RFPResponse]:
    """
    Search function using async database operations.

    Args:
        query: The search query string
        session: Async database session

    Returns:
        List of RFPResponse objects matching the search query
    """
    if not query or len(query.strip()) < 2:
        return []

    # Use the database search function
    rfp_models = await search_rfps_db(query, session)

    # Convert to Pydantic models for the API response
    return [convert_to_rfp_response(rfp) for rfp in rfp_models]


def generate_results_html(rfps: list[RFPResponse], query: str) -> str:
    """
    Generate HTML table for RFP search results

    Args:
        rfps: List of RFPs to display
        query: The search query for context

    Returns:
        HTML string containing the results table or no results message
    """
    if not rfps:
        if query.strip():
            return f'<div class="no-results">No RFPs found for "{query}"</div>'
        return '<div class="no-results">Start typing to search...</div>'

    html = """
    <table>
        <thead>
            <tr>
                <th>RFP Name</th>
                <th>More Information</th>
            </tr>
        </thead>
        <tbody>
    """

    for rfp in rfps:
        url_cell = (
            f'<a href="{rfp.url}" target="_blank">View Details</a>'
            if rfp.url
            else "N/A"
        )
        html += f"""
            <tr>
                <td>{rfp.name}</td>
                <td>{url_cell}</td>
            </tr>
        """

    html += """
        </tbody>
    </table>
    """

    return html


@app.get("/")
async def root() -> dict[str, str]:
    """
    Basic health check endpoint

    Returns:
        Dictionary with status message
    """
    return {"message": "BearTrak RFP Search API is running"}


@app.get("/health", response_model=HealthResponse)
async def health_check(
    session: AsyncSession = Depends(get_async_session),
) -> HealthResponse:
    """
    Detailed health check endpoint with database status.

    Args:
        session: Async database session (dependency injection)

    Returns:
        HealthResponse with service and database status
    """
    # Test database connection
    try:
        # Simple query to test database connectivity
        from sqlalchemy import text

        await session.execute(text("SELECT 1"))
        database_status = "healthy"
    except Exception:
        database_status = "error"

    return HealthResponse(
        status="healthy",
        service="BearTrak Search API",
        database_status=database_status,
    )


@app.post("/api/search", response_class=HTMLResponse)
async def search(
    query: str = Form(...),
    session: AsyncSession = Depends(get_async_session),
) -> HTMLResponse:
    """
    Search endpoint that returns HTML for HTMX frontend.
    Now uses async database operations for RFP search.

    Args:
        query: The search query from the form
        session: Async database session (dependency injection)

    Returns:
        HTML response containing search results
    """
    # Perform search using async database operations
    results: list[RFPResponse] = await search_rfps(query, session)

    # Generate HTML response
    html_response: str = generate_results_html(results, query)

    return HTMLResponse(content=html_response)


# REST API CRUD Endpoints


@app.get("/api/rfps", response_model=list[RFPResponse])
async def get_all_rfps(
    session: AsyncSession = Depends(get_async_session),
) -> list[RFPResponse]:
    """
    Get all RFPs from the database.

    Args:
        session: Async database session (dependency injection)

    Returns:
        List of all RFPs
    """
    rfp_models = await get_all_rfps_db(session)
    return [convert_to_rfp_response(rfp) for rfp in rfp_models]


@app.get("/api/rfps/{rfp_id}", response_model=RFPResponse)
async def get_rfp_by_id(
    rfp_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> RFPResponse:
    """
    Get a single RFP by ID.

    Args:
        rfp_id: The ID of the RFP to retrieve
        session: Async database session (dependency injection)

    Returns:
        The requested RFP

    Raises:
        HTTPException: If RFP is not found
    """
    rfp_model = await get_rfp_by_id_db(session, rfp_id)
    if rfp_model is None:
        raise HTTPException(status_code=404, detail="RFP not found")
    return convert_to_rfp_response(rfp_model)


@app.post("/api/rfps", response_model=RFPResponse, status_code=201)
async def create_rfp(
    rfp_data: RFPCreate,
    session: AsyncSession = Depends(get_async_session),
) -> RFPResponse:
    """
    Create a new RFP.

    Args:
        rfp_data: The RFP data to create
        session: Async database session (dependency injection)

    Returns:
        The created RFP
    """
    rfp_model = await create_rfp_db(
        session,
        name=rfp_data.name,
        url=rfp_data.url,
        description=rfp_data.description,
    )
    return convert_to_rfp_response(rfp_model)


@app.put("/api/rfps/{rfp_id}", response_model=RFPResponse)
async def update_rfp(
    rfp_id: int,
    rfp_data: RFPUpdate,
    session: AsyncSession = Depends(get_async_session),
) -> RFPResponse:
    """
    Update an existing RFP.

    Args:
        rfp_id: The ID of the RFP to update
        rfp_data: The RFP data to update
        session: Async database session (dependency injection)

    Returns:
        The updated RFP

    Raises:
        HTTPException: If RFP is not found
    """
    rfp_model = await update_rfp_db(
        session,
        rfp_id,
        name=rfp_data.name,
        url=rfp_data.url,
        description=rfp_data.description,
    )
    if rfp_model is None:
        raise HTTPException(status_code=404, detail="RFP not found")
    return convert_to_rfp_response(rfp_model)


@app.delete("/api/rfps/{rfp_id}", status_code=204)
async def delete_rfp(
    rfp_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> None:
    """
    Delete an RFP.

    Args:
        rfp_id: The ID of the RFP to delete
        session: Async database session (dependency injection)

    Raises:
        HTTPException: If RFP is not found
    """
    success = await delete_rfp_db(session, rfp_id)
    if not success:
        raise HTTPException(status_code=404, detail="RFP not found")


# Admin Endpoints


@app.delete("/api/admin/clear", status_code=200)
async def clear_database_endpoint() -> dict[str, str]:
    """
    Admin endpoint to clear all RFP data from the database.

    This removes all RFP records but keeps the table structure intact.
    Use with caution - this action cannot be undone.

    Returns:
        Success message confirming the database was cleared
    """
    await clear_database()
    return {"message": "Database cleared successfully"}


def main() -> None:
    """Main entry point for the application"""
    host = os.getenv("BEARTRAK_HOST", "0.0.0.0")

    # Determine port based on environment
    environment = os.getenv("BEARTRAK_ENVIRONMENT", "development").lower()
    if environment == "production":
        default_port = int(os.getenv("BEARTRAK_PRODUCTION_PORT", "8000"))
    else:
        default_port = int(os.getenv("BEARTRAK_DEVELOPMENT_PORT", "8001"))

    port = default_port
    uvicorn.run("main:app", host=host, port=port, reload=True)


if __name__ == "__main__":
    main()
