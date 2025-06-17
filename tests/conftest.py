"""
Test configuration and fixtures for BearTrak Search API tests.
"""

from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from database import Base, PropertyModel
from main import app

# Test database engine - use in-memory SQLite for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def test_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session with sample data."""
    # Create test engine and session maker
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    session_maker = async_sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
    )

    try:
        # Create tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        # Get a session for the test and populate with sample data
        async with session_maker() as session:
            sample_properties = [
                PropertyModel(
                    name="Cozy Downtown Apartment",
                    location="Berkeley, CA",
                    type="Apartment",
                    price="$2,800/month",
                    details="2 bed, 1 bath, near BART station",
                ),
                PropertyModel(
                    name="Spacious Family Home",
                    location="Oakland, CA",
                    type="House",
                    price="$4,200/month",
                    details="3 bed, 2 bath, large yard, garage",
                ),
                PropertyModel(
                    name="Modern Seattle Apartment",
                    location="Seattle, WA",
                    type="Apartment",
                    price="$3,200/month",
                    details="1 bed, 1 bath, downtown location",
                ),
            ]

            for prop in sample_properties:
                session.add(prop)
            await session.commit()

            yield session

    finally:
        await engine.dispose()


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
