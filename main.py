from typing import TypedDict

import uvicorn
from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse


# Define the structure for property data
class Property(TypedDict):
    name: str
    location: str
    type: str
    price: str
    details: str


app = FastAPI(
    title="BearTrak Search API",
    description="Backend API for BearTrak Search frontend",
)

# Configure CORS to allow requests from your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your specific domain
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Sample data - replace with your actual data source
SAMPLE_PROPERTIES: list[Property] = [
    {
        "name": "Modern Downtown Apartment",
        "location": "Downtown Seattle",
        "type": "Apartment",
        "price": "$2,500/month",
        "details": "2 bed, 2 bath, City views",
    },
    {
        "name": "Cozy Suburban House",
        "location": "Bellevue",
        "type": "House",
        "price": "$3,200/month",
        "details": "3 bed, 2 bath, Garden",
    },
    {
        "name": "Luxury Waterfront Condo",
        "location": "Capitol Hill",
        "type": "Condo",
        "price": "$4,000/month",
        "details": "2 bed, 2 bath, Water view",
    },
    {
        "name": "Student-Friendly Studio",
        "location": "University District",
        "type": "Studio",
        "price": "$1,200/month",
        "details": "Studio, Near campus",
    },
    {
        "name": "Family Townhouse",
        "location": "Redmond",
        "type": "Townhouse",
        "price": "$2,800/month",
        "details": "4 bed, 3 bath, Garage",
    },
]


def search_properties(query: str) -> list[Property]:
    """
    Simple search function - replace with your actual search logic

    Args:
        query: The search query string

    Returns:
        List of properties matching the search query
    """
    if not query or len(query.strip()) < 2:
        return []

    query_lower: str = query.lower().strip()
    results: list[Property] = []

    for prop in SAMPLE_PROPERTIES:
        # Search in name, location, type, and details
        searchable_text: str = f"{prop['name']} {prop['location']} {prop['type']} {prop['details']}".lower()

        if query_lower in searchable_text:
            results.append(prop)

    return results


def generate_results_html(properties: list[Property], query: str) -> str:
    """
    Generate HTML table for search results

    Args:
        properties: List of properties to display
        query: The search query for context

    Returns:
        HTML string containing the results table or no results message
    """
    if not properties:
        if query.strip():
            return f'<div class="no-results">No results found for "{query}"</div>'
        return '<div class="no-results">Start typing to search...</div>'

    html = """
    <table>
        <thead>
            <tr>
                <th>Property</th>
                <th>Location</th>
                <th>Type</th>
                <th>Price</th>
                <th>Details</th>
            </tr>
        </thead>
        <tbody>
    """

    for prop in properties:
        html += f"""
            <tr>
                <td>{prop["name"]}</td>
                <td>{prop["location"]}</td>
                <td>{prop["type"]}</td>
                <td>{prop["price"]}</td>
                <td>{prop["details"]}</td>
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
    Health check endpoint

    Returns:
        Dictionary with status message
    """
    return {"message": "BearTrak Search API is running"}


@app.post("/api/search", response_class=HTMLResponse)
async def search(query: str = Form(...)) -> HTMLResponse:
    """
    Search endpoint that returns HTML for HTMX frontend

    Args:
        query: The search query from the form

    Returns:
        HTML response containing search results
    """
    # Perform search
    results: list[Property] = search_properties(query)

    # Generate HTML response
    html_response: str = generate_results_html(results, query)

    return HTMLResponse(content=html_response)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """
    Health check endpoint

    Returns:
        Dictionary with health status information
    """
    return {"status": "healthy", "service": "BearTrak Search API"}


def main() -> None:
    """Main entry point for the application"""
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
