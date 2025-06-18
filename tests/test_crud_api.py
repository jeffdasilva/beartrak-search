"""
Simplified tests for the CRUD API endpoints.
Tests key functionality without complex mocking.
"""

from fastapi.testclient import TestClient

from main import app


class TestCRUDBasic:
    """Basic CRUD tests that work with the actual app."""

    def test_health_endpoint(self) -> None:
        """Test the health endpoint works."""
        with TestClient(app) as client:
            response = client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert "service" in data

    def test_root_endpoint(self) -> None:
        """Test the root endpoint works."""
        with TestClient(app) as client:
            response = client.get("/")
            assert response.status_code == 200
            data = response.json()
            assert "message" in data

    def test_create_rfp_validation_error(self) -> None:
        """Test creating RFP with invalid data returns validation error."""
        with TestClient(app) as client:
            rfp_data = {
                "name": "",  # Invalid: empty name
                "url": "https://example.com",
            }
            response = client.post("/api/rfps", json=rfp_data)
            assert response.status_code == 422  # Validation error

    def test_get_nonexistent_rfp(self) -> None:
        """Test getting RFP that doesn't exist returns 404."""
        with TestClient(app) as client:
            response = client.get("/api/rfps/99999")
            assert response.status_code == 404
            assert response.json() == {"detail": "RFP not found"}

    def test_update_nonexistent_rfp(self) -> None:
        """Test updating RFP that doesn't exist returns 404."""
        with TestClient(app) as client:
            update_data = {"name": "Updated RFP"}
            response = client.put("/api/rfps/99999", json=update_data)
            assert response.status_code == 404
            assert response.json() == {"detail": "RFP not found"}

    def test_delete_nonexistent_rfp(self) -> None:
        """Test deleting RFP that doesn't exist returns 404."""
        with TestClient(app) as client:
            response = client.delete("/api/rfps/99999")
            assert response.status_code == 404
            assert response.json() == {"detail": "RFP not found"}

    def test_get_all_rfps_endpoint_exists(self) -> None:
        """Test that the get all RFPs endpoint exists and returns a list."""
        with TestClient(app) as client:
            response = client.get("/api/rfps")
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)  # Should return a list (empty or with items)


class TestCRUDIntegration:
    """Integration tests for CRUD workflow."""

    def test_create_and_update_workflow(self) -> None:
        """Test creating an RFP and then updating it."""
        with TestClient(app) as client:
            # Step 1: Create RFP
            create_data = {
                "name": "Integration Test RFP",
                "url": "https://integration-test.com",
                "description": "This is an integration test RFP",
            }
            create_response = client.post("/api/rfps", json=create_data)
            assert create_response.status_code == 201

            created_data = create_response.json()
            assert created_data["name"] == "Integration Test RFP"
            assert created_data["url"] == "https://integration-test.com"
            assert created_data["description"] == "This is an integration test RFP"
            assert "id" in created_data
            assert "updated_at" in created_data

            rfp_id = created_data["id"]

            # Step 2: Update the created RFP
            update_data = {
                "name": "Updated Integration Test RFP",
                "url": "https://updated-integration-test.com",
                "description": "This is an updated integration test RFP",
            }
            update_response = client.put(f"/api/rfps/{rfp_id}", json=update_data)
            assert update_response.status_code == 200

            updated_data = update_response.json()
            assert updated_data["id"] == rfp_id
            assert updated_data["name"] == "Updated Integration Test RFP"
            assert updated_data["url"] == "https://updated-integration-test.com"
            assert (
                updated_data["description"] == "This is an updated integration test RFP"
            )

            # Step 3: Verify the RFP was updated by getting it
            get_response = client.get(f"/api/rfps/{rfp_id}")
            assert get_response.status_code == 200

            retrieved_data = get_response.json()
            assert retrieved_data["name"] == "Updated Integration Test RFP"
            assert retrieved_data["url"] == "https://updated-integration-test.com"
            assert (
                retrieved_data["description"]
                == "This is an updated integration test RFP"
            )

            # Step 4: Clean up by deleting the RFP
            delete_response = client.delete(f"/api/rfps/{rfp_id}")
            assert delete_response.status_code == 204

            # Step 5: Verify it was deleted
            get_deleted_response = client.get(f"/api/rfps/{rfp_id}")
            assert get_deleted_response.status_code == 404

    def test_partial_update_workflow(self) -> None:
        """Test creating an RFP and then doing a partial update."""
        with TestClient(app) as client:
            # Step 1: Create RFP
            create_data = {
                "name": "Partial Update Test RFP",
                "url": "https://partial-test.com",
                "description": "Original description",
            }
            create_response = client.post("/api/rfps", json=create_data)
            assert create_response.status_code == 201

            created_data = create_response.json()
            rfp_id = created_data["id"]

            # Step 2: Partial update (only name)
            update_data = {
                "name": "Partially Updated RFP"
                # Not updating url or description
            }
            update_response = client.put(f"/api/rfps/{rfp_id}", json=update_data)
            assert update_response.status_code == 200

            updated_data = update_response.json()
            assert updated_data["name"] == "Partially Updated RFP"
            assert (
                updated_data["url"] == "https://partial-test.com"
            )  # Should remain unchanged
            assert (
                updated_data["description"] == "Original description"
            )  # Should remain unchanged

            # Clean up
            client.delete(f"/api/rfps/{rfp_id}")

    def test_create_rfp_with_minimal_data(self) -> None:
        """Test creating RFP with only required fields."""
        with TestClient(app) as client:
            # Only name is required
            create_data = {
                "name": "Minimal RFP"
                # url and description are optional
            }
            create_response = client.post("/api/rfps", json=create_data)
            assert create_response.status_code == 201

            created_data = create_response.json()
            assert created_data["name"] == "Minimal RFP"
            assert created_data["url"] is None
            assert created_data["description"] is None
            assert "id" in created_data
            assert "updated_at" in created_data

            # Clean up
            client.delete(f"/api/rfps/{created_data['id']}")
