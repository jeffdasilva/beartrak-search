"""
Test configuration and fixtures for BearTrak Search API tests.
"""

from collections.abc import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from database import Base, RequestForProposalModel, get_async_session
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
            sample_rfps = [
                RequestForProposalModel(
                    name="Software Development Project",
                    url="https://example.com/rfp/software",
                    description="Looking for a software development partner to build a modern web application using React and Node.js technologies.",
                ),
                RequestForProposalModel(
                    name="Marketing Campaign Services",
                    url="https://example.com/rfp/marketing",
                    description="Seeking creative agency services for a comprehensive marketing campaign targeting healthcare professionals.",
                ),
                RequestForProposalModel(
                    name="University Research Platform",
                    url=None,
                    description="University seeking proposals for a data management platform to support academic research across multiple departments.",
                ),
            ]

            for rfp in sample_rfps:
                session.add(rfp)
            await session.commit()

            yield session

    finally:
        await engine.dispose()


@pytest.fixture
def client(test_db_session: AsyncSession) -> Generator[TestClient, None, None]:
    """Create a test client for the FastAPI app with database dependency override."""

    # Override the database session dependency
    def override_get_async_session() -> AsyncSession:
        return test_db_session

    app.dependency_overrides[get_async_session] = override_get_async_session

    client = TestClient(app)

    # Clean up the override after the test
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_search_data() -> dict[str, str]:
    """Sample search data for tests."""
    return {"query": "software"}


@pytest.fixture
def empty_search_data() -> dict[str, str]:
    """Empty search data for tests."""
    return {"query": ""}


@pytest.fixture
def short_search_data() -> dict[str, str]:
    """Short search query data for tests."""
    return {"query": "a"}
