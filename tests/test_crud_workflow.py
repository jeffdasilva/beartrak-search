"""
Integration test demonstrating CRUD workflow using database functions directly.
This ensures the CRUD functionality works as requested.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from database import (
    create_rfp_db,
    delete_rfp_db,
    get_all_rfps_db,
    get_rfp_by_id_db,
    update_rfp_db,
)


class TestCRUDWorkflowIntegration:
    """Integration test demonstrating full CRUD workflow."""

    @pytest.mark.asyncio
    async def test_complete_crud_workflow_demonstration(
        self, test_db_session: AsyncSession
    ) -> None:
        """
        Complete demonstration of CRUD workflow:
        1. Create a new RFP
        2. Retrieve it by ID
        3. Update it
        4. Verify the update worked
        5. Delete it
        6. Verify deletion
        """

        # Step 1: Create a new RFP
        print("\n=== STEP 1: Creating new RFP ===")
        created_rfp = await create_rfp_db(
            test_db_session,
            name="Demo RFP for CRUD Workflow",
            url="https://demo-crud.example.com",
            description="This RFP demonstrates the complete CRUD workflow functionality",
        )

        assert created_rfp.id is not None
        assert created_rfp.name == "Demo RFP for CRUD Workflow"
        assert created_rfp.url == "https://demo-crud.example.com"
        assert (
            created_rfp.description
            == "This RFP demonstrates the complete CRUD workflow functionality"
        )
        assert created_rfp.updated_at is not None

        rfp_id = created_rfp.id
        print(f"✅ Created RFP with ID: {rfp_id}")
        print(f"   Name: {created_rfp.name}")
        print(f"   URL: {created_rfp.url}")
        print(f"   Created/Updated at: {created_rfp.updated_at}")

        # Step 2: Retrieve the RFP by ID
        print("\n=== STEP 2: Retrieving RFP by ID ===")
        retrieved_rfp = await get_rfp_by_id_db(test_db_session, rfp_id)

        assert retrieved_rfp is not None
        assert retrieved_rfp.id == rfp_id
        assert retrieved_rfp.name == "Demo RFP for CRUD Workflow"
        assert retrieved_rfp.url == "https://demo-crud.example.com"
        assert (
            retrieved_rfp.description
            == "This RFP demonstrates the complete CRUD workflow functionality"
        )

        print(f"✅ Retrieved RFP with ID: {retrieved_rfp.id}")
        print(f"   Name: {retrieved_rfp.name}")
        print(f"   URL: {retrieved_rfp.url}")

        # Step 3: Update the RFP
        print("\n=== STEP 3: Updating RFP ===")

        # Small delay to ensure updated_at changes (if implementation supports it)
        import asyncio

        await asyncio.sleep(0.1)

        updated_rfp = await update_rfp_db(
            test_db_session,
            rfp_id,
            name="Updated Demo RFP for CRUD Workflow",
            url="https://updated-demo-crud.example.com",
            description="This RFP has been updated to demonstrate the complete CRUD workflow functionality",
        )

        assert updated_rfp is not None
        assert updated_rfp.id == rfp_id
        assert updated_rfp.name == "Updated Demo RFP for CRUD Workflow"
        assert updated_rfp.url == "https://updated-demo-crud.example.com"
        assert (
            updated_rfp.description
            == "This RFP has been updated to demonstrate the complete CRUD workflow functionality"
        )

        print(f"✅ Updated RFP with ID: {updated_rfp.id}")
        print(f"   New Name: {updated_rfp.name}")
        print(f"   New URL: {updated_rfp.url}")
        print(f"   New Description: {updated_rfp.description}")
        print(f"   Updated at: {updated_rfp.updated_at}")

        # Step 4: Verify the update by retrieving again
        print("\n=== STEP 4: Verifying update ===")
        verified_rfp = await get_rfp_by_id_db(test_db_session, rfp_id)

        assert verified_rfp is not None
        assert verified_rfp.name == "Updated Demo RFP for CRUD Workflow"
        assert verified_rfp.url == "https://updated-demo-crud.example.com"
        assert (
            verified_rfp.description
            == "This RFP has been updated to demonstrate the complete CRUD workflow functionality"
        )

        print("✅ Verified RFP was updated correctly")
        print(f"   Name: {verified_rfp.name}")
        print(f"   URL: {verified_rfp.url}")

        # Step 5: Check that it appears in the list of all RFPs
        print("\n=== STEP 5: Verifying RFP appears in list ===")
        all_rfps = await get_all_rfps_db(test_db_session)

        found_rfps = [rfp for rfp in all_rfps if rfp.id == rfp_id]
        assert len(found_rfps) == 1
        assert found_rfps[0].name == "Updated Demo RFP for CRUD Workflow"

        print("✅ Found RFP in list of all RFPs")
        print(f"   Total RFPs in database: {len(all_rfps)}")
        print(f"   Our RFP name in list: {found_rfps[0].name}")

        # Step 6: Delete the RFP
        print("\n=== STEP 6: Deleting RFP ===")
        delete_success = await delete_rfp_db(test_db_session, rfp_id)

        assert delete_success is True
        print(f"✅ Deleted RFP with ID: {rfp_id}")

        # Step 7: Verify deletion
        print("\n=== STEP 7: Verifying deletion ===")
        deleted_rfp = await get_rfp_by_id_db(test_db_session, rfp_id)

        assert deleted_rfp is None
        print("✅ Verified RFP was deleted (no longer exists)")

        # Step 8: Verify it's no longer in the list
        print("\n=== STEP 8: Verifying RFP removed from list ===")
        all_rfps_after_delete = await get_all_rfps_db(test_db_session)

        found_rfps_after_delete = [
            rfp for rfp in all_rfps_after_delete if rfp.id == rfp_id
        ]
        assert len(found_rfps_after_delete) == 0

        print("✅ Verified RFP is no longer in list")
        print(f"   Total RFPs in database after deletion: {len(all_rfps_after_delete)}")

        print("\n🎉 CRUD WORKFLOW DEMONSTRATION COMPLETE! 🎉")
        print("All CRUD operations (Create, Read, Update, Delete) work correctly!")

    @pytest.mark.asyncio
    async def test_partial_update_demonstration(
        self, test_db_session: AsyncSession
    ) -> None:
        """Demonstrate partial update functionality."""

        print("\n=== PARTIAL UPDATE DEMONSTRATION ===")

        # Create RFP
        rfp = await create_rfp_db(
            test_db_session,
            name="Original Name",
            url="https://original.com",
            description="Original description",
        )

        print(f"Created RFP: {rfp.name}, {rfp.url}, {rfp.description}")

        # Partial update - only name
        updated_rfp = await update_rfp_db(
            test_db_session,
            rfp.id,
            name="Updated Name Only",
            # url and description not provided
        )

        assert updated_rfp is not None
        assert updated_rfp.name == "Updated Name Only"
        assert updated_rfp.url == "https://original.com"  # Should remain unchanged
        assert (
            updated_rfp.description == "Original description"
        )  # Should remain unchanged

        print("✅ Partial update successful!")
        print(f"   Updated name: {updated_rfp.name}")
        print(f"   URL unchanged: {updated_rfp.url}")
        print(f"   Description unchanged: {updated_rfp.description}")

        # Clean up
        await delete_rfp_db(test_db_session, rfp.id)
        print("✅ Cleanup complete")
