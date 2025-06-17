"""
Unit tests for the BearTrak Search API health endpoint.
"""

import pytest
from fastapi import status
from fastapi.testclient import TestClient


def test_health_endpoint_returns_200(client: TestClient) -> None:
    """Test that health endpoint returns 200 status code."""
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK


def test_health_endpoint_returns_correct_content_type(client: TestClient) -> None:
    """Test that health endpoint returns JSON content type."""
    response = client.get("/health")
    assert response.headers["content-type"] == "application/json"


def test_health_endpoint_returns_expected_structure(client: TestClient) -> None:
    """Test that health endpoint returns expected JSON structure."""
    response = client.get("/health")
    data = response.json()

    # Check that response has required keys
    assert "status" in data
    assert "service" in data

    # Check values
    assert data["status"] == "healthy"
    assert data["service"] == "BearTrak Search API"


def test_health_endpoint_response_is_valid_json(client: TestClient) -> None:
    """Test that health endpoint returns valid JSON."""
    response = client.get("/health")

    # This will raise an exception if not valid JSON
    data = response.json()
    assert isinstance(data, dict)


@pytest.mark.parametrize("method", ["POST", "PUT", "DELETE", "PATCH"])
def test_health_endpoint_only_accepts_get(client: TestClient, method: str) -> None:
    """Test that health endpoint only accepts GET requests."""
    response = client.request(method, "/health")
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
