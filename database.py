"""
Database models and configuration for BearTrak Search API.
Uses async SQLAlchemy with aiosqlite for modern async database operations.
"""

import os
from collections.abc import AsyncGenerator
from dataclasses import dataclass

from sqlalchemy import String, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./beartrak_search.db")

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=bool(os.getenv("DEBUG", False)),  # Log SQL queries in debug mode
)

# Create async session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Base class for all database models."""



@dataclass
class PropertyModel(Base):
    """
    SQLAlchemy model for property data using dataclass syntax.
    This provides modern Python dataclass features with SQLAlchemy ORM.
    """

    __tablename__ = "properties"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(String(100), nullable=False)
    price: Mapped[str] = mapped_column(String(100), nullable=False)
    details: Mapped[str] = mapped_column(String(500), nullable=False)

    def __repr__(self) -> str:
        return f"PropertyModel(id={self.id}, name='{self.name}', location='{self.location}')"


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get an async database session.
    This will be used with FastAPI's dependency injection system.
    """
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_database() -> None:
    """
    Initialize the database by creating all tables.
    This should be called on application startup.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def populate_sample_data() -> None:
    """
    Populate the database with sample data if it's empty.
    This replaces the hardcoded SAMPLE_PROPERTIES.
    """
    async with async_session_maker() as session:
        # Check if data already exists
        result = await session.execute(select(PropertyModel).limit(1))
        if result.first() is not None:
            return  # Data already exists

        # Create sample properties
        sample_properties = [
            PropertyModel(
                name="Modern Downtown Apartment",
                location="Downtown Seattle",
                type="Apartment",
                price="$2,500/month",
                details="2 bed, 2 bath, City views",
            ),
            PropertyModel(
                name="Cozy Suburban House",
                location="Bellevue",
                type="House",
                price="$3,200/month",
                details="3 bed, 2 bath, Garden",
            ),
            PropertyModel(
                name="Luxury Waterfront Condo",
                location="Capitol Hill",
                type="Condo",
                price="$4,000/month",
                details="2 bed, 2 bath, Water view",
            ),
            PropertyModel(
                name="Student-Friendly Studio",
                location="University District",
                type="Studio",
                price="$1,200/month",
                details="Studio, Near campus",
            ),
            PropertyModel(
                name="Family Townhouse",
                location="Redmond",
                type="Townhouse",
                price="$2,800/month",
                details="4 bed, 3 bath, Garage",
            ),
        ]

        # Add all properties to the session
        for prop in sample_properties:
            session.add(prop)

        # Commit the transaction
        await session.commit()


async def search_properties_db(
    query: str, session: AsyncSession
) -> list[PropertyModel]:
    """
    Search properties in the database using async SQLAlchemy.

    Args:
        query: The search query string
        session: Async database session

    Returns:
        List of PropertyModel instances matching the search query
    """
    if not query or len(query.strip()) < 2:
        return []

    query_lower = f"%{query.lower().strip()}%"

    # Create a comprehensive search across all relevant fields
    stmt = (
        select(PropertyModel)
        .where(
            PropertyModel.name.ilike(query_lower)
            | PropertyModel.location.ilike(query_lower)
            | PropertyModel.type.ilike(query_lower)
            | PropertyModel.details.ilike(query_lower)
        )
        .order_by(PropertyModel.name)
    )

    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get_all_properties_db(session: AsyncSession) -> list[PropertyModel]:
    """
    Get all properties from the database.

    Args:
        session: Async database session

    Returns:
        List of all PropertyModel instances
    """
    stmt = select(PropertyModel).order_by(PropertyModel.name)
    result = await session.execute(stmt)
    return list(result.scalars().all())
