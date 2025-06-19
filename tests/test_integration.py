"""
Integration tests for the BearTrak Search API.
Tests the full application flow and real HTTP requests.
"""

import os
import time

import requests


def wait_for_server(base_url: str, timeout: int = 30) -> bool:
    """Wait for the server to be ready."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{base_url}/health", timeout=1)
            if response.status_code == 200:
                return True
        except requests.exceptions.RequestException:
            pass
        time.sleep(0.5)
    return False


def test_api_integration() -> None:
    """Integration test for the BearTrak Search API."""
    # Use environment variable for port, default to development port
    port = os.getenv("BEARTRAK_TEST_SERVER_PORT", "8001")  # Default to dev server port
    base_url = f"http://localhost:{port}"

    # Note: This test requires the server to be running
    # Run with: make start-dev (in background) && make test-integration
    # Or: BEARTRAK_TEST_SERVER_PORT=8000 make test-integration (for production server)

    try:
        # Test health endpoint
        response = requests.get(f"{base_url}/health", timeout=5)
        assert response.status_code == 200

        health_data = response.json()
        assert health_data["status"] == "healthy"
        assert health_data["service"] == "BearTrak Search API"

        # Test search endpoint with valid query
        search_data = {"query": "software"}
        response = requests.post(f"{base_url}/api/search", data=search_data, timeout=5)
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

        html_content = response.text
        assert "<table>" in html_content
        assert "<thead>" in html_content
        assert "<tbody>" in html_content

        # Test search endpoint with empty query
        empty_search_data = {"query": ""}
        response = requests.post(
            f"{base_url}/api/search", data=empty_search_data, timeout=5
        )
        assert response.status_code == 200

        html_content = response.text
        # Empty query should return no-results div
        assert '<div class="no-results">' in html_content
        assert "Start typing to search..." in html_content

        print("✅ Integration tests passed!")

    except requests.exceptions.ConnectionError:
        print(
            f"❌ Could not connect to API. Make sure the server is running on localhost:{port}"
        )
        print("   Run: make start-dev (in another terminal)")
        print(
            "   Or: BEARTRAK_TEST_SERVER_PORT=8000 make test-integration (for production server)"
        )
        raise
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        raise


if __name__ == "__main__":
    test_api_integration()
