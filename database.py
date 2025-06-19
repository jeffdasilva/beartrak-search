"""
Database models and configuration for BearTrak Search API.
Uses async SQLAlchemy with aiosqlite for modern async database operations.
"""

import os
from collections.abc import AsyncGenerator
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import DateTime, String, Text, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func

# Database configuration
def get_database_url() -> str:
    """
    Get the database URL based on environment configuration.
    
    In production mode (BEARTRAK_ENVIRONMENT=production), uses beartrak.db
    In development/test mode (default), uses beartrak_test.db
    
    Can be overridden with BEARTRAK_DATABASE_URL environment variable.
    """
    # Check if BEARTRAK_DATABASE_URL is explicitly set
    if database_url := os.getenv("BEARTRAK_DATABASE_URL"):
        return database_url
    
    # Determine database file based on environment
    environment = os.getenv("BEARTRAK_ENVIRONMENT", "development").lower()
    
    if environment == "production":
        db_file = os.getenv("BEARTRAK_PRODUCTION_DB", "beartrak.db")
    else:  # development, test, or any other value
        db_file = os.getenv("BEARTRAK_DEVELOPMENT_DB", "beartrak_test.db")
    
    return f"sqlite+aiosqlite:///./{db_file}"

DATABASE_URL = get_database_url()

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=bool(os.getenv("BEARTRAK_DEBUG", False)),  # Log SQL queries in debug mode
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
class RequestForProposalModel(Base):
    """
    SQLAlchemy model for Request for Proposal data using dataclass syntax.
    This provides modern Python dataclass features with SQLAlchemy ORM.
    """

    __tablename__ = "rfps"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(), onupdate=func.now()
    )

    def __repr__(self) -> str:
        return f"RequestForProposalModel(id={self.id}, name='{self.name}', url='{self.url}', updated_at='{self.updated_at}')"


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
    Populate the database with sample RFP data if it's empty.
    This replaces the hardcoded sample data.
    """
    async with async_session_maker() as session:
        # Check if data already exists
        result = await session.execute(select(RequestForProposalModel).limit(1))
        if result.first() is not None:
            return  # Data already exists

        # Create sample RFPs
        sample_rfps = [
            RequestForProposalModel(
                name="City Infrastructure Development Project",
                url="https://seattle.gov/rfp/infrastructure-2024",
                description="The City of Seattle is seeking qualified contractors for a comprehensive infrastructure development project including road improvements, bridge maintenance, and utility upgrades across downtown Seattle. This multi-phase project spans 18 months and requires expertise in urban planning, civil engineering, and project management. Proposals should include detailed timelines, budget estimates, and sustainability considerations.",
            ),
            RequestForProposalModel(
                name="Software Development Services",
                url="https://techcompany.com/rfp/software-dev",
                description="We are looking for a software development partner to build a cloud-based customer relationship management system. The solution should support multi-tenant architecture, real-time analytics, mobile applications, and integration with existing enterprise systems. Required technologies include React, Node.js, PostgreSQL, and AWS cloud services.",
            ),
            RequestForProposalModel(
                name="Marketing Campaign for Healthcare Initiative",
                url=None,
                description="Healthcare Northwest is seeking a creative agency to develop and execute a comprehensive marketing campaign for our new community health initiative. The campaign should target diverse communities, include digital and traditional media, and demonstrate measurable impact on health awareness and program enrollment. Experience in healthcare marketing and multilingual capabilities preferred.",
            ),
            RequestForProposalModel(
                name="University Research Data Management Platform",
                url="https://university.edu/rfp/data-platform",
                description="The University is requesting proposals for a comprehensive research data management platform that will serve multiple departments and research centers. The platform must support data storage, collaboration tools, compliance with federal research regulations, and integration with existing academic systems. Proposals should address scalability, security, and long-term maintenance.",
            ),
            RequestForProposalModel(
                name="Green Energy Consulting Services",
                url="https://greenenergy.org/rfp-2024",
                description="Our organization is seeking environmental consulting services to assess renewable energy opportunities for our corporate campus. The scope includes solar panel feasibility studies, energy efficiency audits, sustainability reporting, and development of a 10-year green energy transition plan. Consultants should have experience with LEED certification and local utility partnerships.",
            ),
        ]

        # Add all RFPs to the session
        for rfp in sample_rfps:
            session.add(rfp)

        # Commit the transaction
        await session.commit()


async def search_rfps_db(
    query: str, session: AsyncSession
) -> list[RequestForProposalModel]:
    """
    Search RFPs in the database using async SQLAlchemy.

    Args:
        query: The search query string
        session: Async database session

    Returns:
        List of RequestForProposalModel instances matching the search query
    """
    if not query or len(query.strip()) < 2:
        return []

    query_lower = f"%{query.lower().strip()}%"

    # Create a comprehensive search across all relevant fields
    stmt = (
        select(RequestForProposalModel)
        .where(
            RequestForProposalModel.name.ilike(query_lower)
            | RequestForProposalModel.description.ilike(query_lower)
        )
        .order_by(RequestForProposalModel.name)
    )

    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get_all_rfps_db(session: AsyncSession) -> list[RequestForProposalModel]:
    """
    Get all RFPs from the database.

    Args:
        session: Async database session

    Returns:
        List of all RequestForProposalModel instances
    """
    stmt = select(RequestForProposalModel).order_by(RequestForProposalModel.name)
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get_rfp_by_id_db(
    session: AsyncSession, rfp_id: int
) -> RequestForProposalModel | None:
    """
    Get a single RFP by ID from the database.

    Args:
        session: Async database session
        rfp_id: The ID of the RFP to retrieve

    Returns:
        RequestForProposalModel instance or None if not found
    """
    stmt = select(RequestForProposalModel).where(RequestForProposalModel.id == rfp_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def create_rfp_db(
    session: AsyncSession,
    name: str,
    url: str | None = None,
    description: str | None = None,
) -> RequestForProposalModel:
    """
    Create a new RFP in the database.

    Args:
        session: Async database session
        name: The name of the RFP
        url: Optional URL for the RFP
        description: Optional description for the RFP

    Returns:
        The created RequestForProposalModel instance
    """
    rfp = RequestForProposalModel(
        name=name,
        url=url,
        description=description,
    )
    session.add(rfp)
    await session.commit()
    await session.refresh(rfp)
    return rfp


async def update_rfp_db(
    session: AsyncSession,
    rfp_id: int,
    name: str | None = None,
    url: str | None = None,
    description: str | None = None,
) -> RequestForProposalModel | None:
    """
    Update an existing RFP in the database.

    Args:
        session: Async database session
        rfp_id: The ID of the RFP to update
        name: Optional new name for the RFP
        url: Optional new URL for the RFP
        description: Optional new description for the RFP

    Returns:
        The updated RequestForProposalModel instance or None if not found
    """
    rfp = await get_rfp_by_id_db(session, rfp_id)
    if rfp is None:
        return None

    if name is not None:
        rfp.name = name
    if url is not None:
        rfp.url = url
    if description is not None:
        rfp.description = description

    await session.commit()
    await session.refresh(rfp)
    return rfp


async def delete_rfp_db(session: AsyncSession, rfp_id: int) -> bool:
    """
    Delete an RFP from the database.

    Args:
        session: Async database session
        rfp_id: The ID of the RFP to delete

    Returns:
        True if the RFP was deleted, False if not found
    """
    rfp = await get_rfp_by_id_db(session, rfp_id)
    if rfp is None:
        return False

    await session.delete(rfp)
    await session.commit()
    return True
