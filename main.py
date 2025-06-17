import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import Depends, FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from database import (
    RequestForProposalModel,
    get_async_session,
    init_database,
    populate_sample_data,
    search_rfps_db,
)
from models import HealthResponse, RFPResponse


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager for startup and shutdown events."""
    # Startup
    await init_database()
    await populate_sample_data()
    yield
    # Shutdown (if needed)


app = FastAPI(
    title="BearTrak RFP Search API",
    description="Backend API for BearTrak RFP Search frontend with SQLite database",
    lifespan=lifespan,
)

# Configure CORS to allow requests from your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your specific domain
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


def convert_to_rfp_response(rfp_model: RequestForProposalModel) -> RFPResponse:
    """Convert SQLAlchemy RequestForProposalModel to Pydantic RFPResponse."""
    return RFPResponse(
        id=rfp_model.id,
        name=rfp_model.name,
        url=rfp_model.url,
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


@app.get("/health", response_model=HealthResponse)
async def health_check_db(
    session: AsyncSession = Depends(get_async_session),
) -> HealthResponse:
    """
    Health check endpoint with database status.

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


def main() -> None:
    """Main entry point for the application"""
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("main:app", host=host, port=port, reload=True)


if __name__ == "__main__":
    main()
