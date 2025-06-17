#!/usr/bin/env python3
"""
Manual test script for BearTrak RFP Search API
This is a simple manual testing script that can be run independently.
Run with: uv run python tests/test_api_legacy.py
"""

import time

import requests


def test_api() -> None:
    base_url: str = "http://localhost:8000"

    # Wait a moment for server to start
    time.sleep(2)

    try:
        # Test health endpoint
        print("Testing health endpoint...")
        response: requests.Response = requests.get(f"{base_url}/health")
        print(f"Health check: {response.status_code} - {response.json()}")

        # Test search endpoint
        print("\nTesting search endpoint...")
        search_data: dict[str, str] = {"query": "software"}
        response = requests.post(f"{base_url}/api/search", data=search_data)
        print(f"Search test: {response.status_code}")
        print(f"Response preview: {response.text[:200]}...")

        print("\nAPI is working correctly!")

    except requests.exceptions.ConnectionError:
        print(
            "Could not connect to API. Make sure the server is running on localhost:8000",
        )
    except Exception as e:
        print(f"Error testing API: {e}")


if __name__ == "__main__":
    test_api()
