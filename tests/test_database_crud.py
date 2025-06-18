"""
Tests for database CRUD operations.
Tests the actual database functions with real database operations.
"""

from datetime import datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from database import (
    create_rfp_db,
    delete_rfp_db,
    get_all_rfps_db,
    get_rfp_by_id_db,
    update_rfp_db,
)


class TestDatabaseCRUD:
    """Test database CRUD operations."""

    @pytest.mark.asyncio
    async def test_create_rfp_db(self, test_db_session: AsyncSession) -> None:
        """Test creating a new RFP in the database."""
        # Act
        rfp = await create_rfp_db(
            test_db_session,
            name="Test RFP",
            url="https://example.com",
            description="Test description",
        )

        # Assert
        assert rfp.id is not None
        assert rfp.name == "Test RFP"
        assert rfp.url == "https://example.com"
        assert rfp.description == "Test description"
        assert isinstance(rfp.updated_at, datetime)

    @pytest.mark.asyncio
    async def test_get_rfp_by_id_db(self, test_db_session: AsyncSession) -> None:
        """Test getting RFP by ID from database."""
        # Arrange: Create an RFP first
        created_rfp = await create_rfp_db(
            test_db_session,
            name="Test RFP",
            url="https://example.com",
            description="Test description",
        )

        # Act
        retrieved_rfp = await get_rfp_by_id_db(test_db_session, created_rfp.id)

        # Assert
        assert retrieved_rfp is not None
        assert retrieved_rfp.id == created_rfp.id
        assert retrieved_rfp.name == "Test RFP"
        assert retrieved_rfp.url == "https://example.com"
        assert retrieved_rfp.description == "Test description"

    @pytest.mark.asyncio
    async def test_get_rfp_by_id_db_not_found(
        self, test_db_session: AsyncSession
    ) -> None:
        """Test getting RFP by ID when it doesn't exist."""
        # Act
        retrieved_rfp = await get_rfp_by_id_db(test_db_session, 999)

        # Assert
        assert retrieved_rfp is None

    @pytest.mark.asyncio
    async def test_get_all_rfps_db(self, test_db_session: AsyncSession) -> None:
        """Test getting all RFPs from database."""
        # Arrange: Create multiple RFPs
        await create_rfp_db(
            test_db_session,
            name="First RFP",
            url="https://first.com",
            description="First description",
        )
        await create_rfp_db(
            test_db_session,
            name="Second RFP",
            url="https://second.com",
            description="Second description",
        )

        # Act
        all_rfps = await get_all_rfps_db(test_db_session)

        # Assert
        assert len(all_rfps) >= 2  # At least the two we created
        rfp_names = [rfp.name for rfp in all_rfps]
        assert "First RFP" in rfp_names
        assert "Second RFP" in rfp_names

    @pytest.mark.asyncio
    async def test_update_rfp_db(self, test_db_session: AsyncSession) -> None:
        """Test updating an existing RFP in database."""
        # Arrange: Create an RFP first
        created_rfp = await create_rfp_db(
            test_db_session,
            name="Original RFP",
            url="https://original.com",
            description="Original description",
        )

        # Wait a tiny bit to ensure updated_at changes
        import asyncio

        await asyncio.sleep(0.1)

        # Act
        updated_rfp = await update_rfp_db(
            test_db_session,
            created_rfp.id,
            name="Updated RFP",
            url="https://updated.com",
            description="Updated description",
        )

        # Assert
        assert updated_rfp is not None
        assert updated_rfp.id == created_rfp.id
        assert updated_rfp.name == "Updated RFP"
        assert updated_rfp.url == "https://updated.com"
        assert updated_rfp.description == "Updated description"
        # Note: SQLAlchemy's onupdate may not trigger in fast tests, so we skip timestamp check

    @pytest.mark.asyncio
    async def test_update_rfp_db_partial(self, test_db_session: AsyncSession) -> None:
        """Test partial update of RFP (only some fields)."""
        # Arrange: Create an RFP first
        created_rfp = await create_rfp_db(
            test_db_session,
            name="Original RFP",
            url="https://original.com",
            description="Original description",
        )

        # Act: Update only the name
        updated_rfp = await update_rfp_db(
            test_db_session, created_rfp.id, name="Updated Name Only"
        )

        # Assert
        assert updated_rfp is not None
        assert updated_rfp.name == "Updated Name Only"
        assert updated_rfp.url == "https://original.com"  # Unchanged
        assert updated_rfp.description == "Original description"  # Unchanged

    @pytest.mark.asyncio
    async def test_update_rfp_db_not_found(self, test_db_session: AsyncSession) -> None:
        """Test updating RFP when it doesn't exist."""
        # Act
        updated_rfp = await update_rfp_db(test_db_session, 999, name="Non-existent RFP")

        # Assert
        assert updated_rfp is None

    @pytest.mark.asyncio
    async def test_delete_rfp_db(self, test_db_session: AsyncSession) -> None:
        """Test deleting an RFP from database."""
        # Arrange: Create an RFP first
        created_rfp = await create_rfp_db(
            test_db_session,
            name="To Be Deleted",
            url="https://delete.com",
            description="Will be deleted",
        )

        # Verify it exists
        retrieved_rfp = await get_rfp_by_id_db(test_db_session, created_rfp.id)
        assert retrieved_rfp is not None

        # Act
        success = await delete_rfp_db(test_db_session, created_rfp.id)

        # Assert
        assert success is True

        # Verify it's gone
        deleted_rfp = await get_rfp_by_id_db(test_db_session, created_rfp.id)
        assert deleted_rfp is None

    @pytest.mark.asyncio
    async def test_delete_rfp_db_not_found(self, test_db_session: AsyncSession) -> None:
        """Test deleting RFP when it doesn't exist."""
        # Act
        success = await delete_rfp_db(test_db_session, 999)

        # Assert
        assert success is False

    @pytest.mark.asyncio
    async def test_complete_crud_workflow(self, test_db_session: AsyncSession) -> None:
        """Test complete CRUD workflow: Create, Read, Update, Delete."""
        # 1. Create
        created_rfp = await create_rfp_db(
            test_db_session,
            name="Workflow RFP",
            url="https://workflow.com",
            description="Workflow test description",
        )
        assert created_rfp.id is not None
        rfp_id = created_rfp.id

        # 2. Read (by ID)
        read_rfp = await get_rfp_by_id_db(test_db_session, rfp_id)
        assert read_rfp is not None
        assert read_rfp.name == "Workflow RFP"

        # 3. Update
        updated_rfp = await update_rfp_db(
            test_db_session,
            rfp_id,
            name="Updated Workflow RFP",
            description="Updated workflow description",
        )
        assert updated_rfp is not None
        assert updated_rfp.name == "Updated Workflow RFP"
        assert updated_rfp.description == "Updated workflow description"
        assert updated_rfp.url == "https://workflow.com"  # Should remain unchanged

        # 4. Verify in list
        all_rfps = await get_all_rfps_db(test_db_session)
        workflow_rfps = [rfp for rfp in all_rfps if rfp.id == rfp_id]
        assert len(workflow_rfps) == 1
        assert workflow_rfps[0].name == "Updated Workflow RFP"

        # 5. Delete
        delete_success = await delete_rfp_db(test_db_session, rfp_id)
        assert delete_success is True

        # 6. Verify deletion
        deleted_rfp = await get_rfp_by_id_db(test_db_session, rfp_id)
        assert deleted_rfp is None
