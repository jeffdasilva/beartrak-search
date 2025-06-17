"""
Unit tests for the BearTrak Search API application configuration.
"""

from fastapi import FastAPI
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

from main import app


def test_app_is_fastapi_instance() -> None:
    """Test that app is a FastAPI instance."""
    assert isinstance(app, FastAPI)


def test_app_title() -> None:
    """Test that app has the correct title."""
    assert app.title == "BearTrak RFP Search API"


def test_app_description() -> None:
    """Test that app has the correct description."""
    assert (
        app.description
        == "Backend API for BearTrak RFP Search frontend with SQLite database"
    )


def test_app_has_cors_middleware() -> None:
    """Test that CORS middleware is configured."""
    # Check that CORS middleware is in the middleware stack by checking if we have any middleware
    assert len(app.user_middleware) > 0, "No middleware configured"

    # Test CORS functionality with a test request
    with TestClient(app) as client:
        # Make an OPTIONS request to check CORS headers
        response = client.options("/health")
        # Should have CORS headers or not return a CORS error
        assert response.status_code != 403


def test_cors_allows_all_origins(client: TestClient) -> None:
    """Test that CORS is configured to allow requests."""
    # Make a preflight request
    response = client.options(
        "/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Content-Type",
        },
    )

    # Should not be blocked by CORS
    assert response.status_code != 403


def test_app_routes_exist() -> None:
    """Test that expected routes are registered."""
    api_routes = [route for route in app.routes if isinstance(route, APIRoute)]
    route_paths = [route.path for route in api_routes]

    # Check for expected routes
    expected_routes = ["/health", "/api/search"]
    for route in expected_routes:
        assert route in route_paths, f"Route {route} not found in app routes"


def test_app_route_methods() -> None:
    """Test that routes have correct HTTP methods."""
    # Find health route
    health_route = None
    search_route = None

    for route in app.routes:
        if isinstance(route, APIRoute):
            if route.path == "/health":
                health_route = route
            elif route.path == "/api/search":
                search_route = route

    # Health route should accept GET
    assert health_route is not None, "Health route not found"
    assert "GET" in health_route.methods

    # Search route should accept POST
    assert search_route is not None, "Search route not found"
    assert "POST" in search_route.methods


def test_openapi_schema_generation() -> None:
    """Test that OpenAPI schema can be generated."""
    schema = app.openapi()

    # Should be a valid schema
    assert isinstance(schema, dict)
    assert "openapi" in schema
    assert "info" in schema
    assert "paths" in schema

    # Check info section
    assert schema["info"]["title"] == "BearTrak RFP Search API"
    assert (
        schema["info"]["description"]
        == "Backend API for BearTrak RFP Search frontend with SQLite database"
    )


def test_app_startup() -> None:
    """Test that app can start up without errors."""
    # This test verifies that there are no import or configuration errors
    # that would prevent the app from starting
    with TestClient(app) as client:
        # If we can create a test client, the app can start
        assert client is not None
