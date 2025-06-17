"""
Test configuration and fixtures for BearTrak Search API tests.
"""

import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def sample_search_data() -> dict[str, str]:
    """Sample search data for tests."""
    return {"query": "apartment"}


@pytest.fixture
def empty_search_data() -> dict[str, str]:
    """Empty search data for tests."""
    return {"query": ""}


@pytest.fixture
def short_search_data() -> dict[str, str]:
    """Short search query data for tests."""
    return {"query": "a"}


@pytest.fixture
def sample_properties() -> list[dict[str, str]]:
    """Sample property data for testing."""
    return [
        {
            "name": "Cozy Downtown Apartment",
            "location": "Berkeley, CA",
            "type": "Apartment",
            "price": "$2,800/month",
            "details": "2 bed, 1 bath, near BART station",
        },
        {
            "name": "Spacious Family Home",
            "location": "Oakland, CA",
            "type": "House",
            "price": "$4,200/month",
            "details": "3 bed, 2 bath, large yard, garage",
        },
    ]
