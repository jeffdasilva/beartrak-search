"""
Unit tests for the BearTrak Search API search functionality.
"""

import pytest
from fastapi import status
from fastapi.testclient import TestClient


def test_search_endpoint_returns_200_with_valid_query(
    client: TestClient, sample_search_data: dict[str, str]
) -> None:
    """Test that search endpoint returns 200 with valid query."""
    response = client.post("/api/search", data=sample_search_data)
    assert response.status_code == status.HTTP_200_OK


def test_search_endpoint_returns_html_content_type(
    client: TestClient, sample_search_data: dict[str, str]
) -> None:
    """Test that search endpoint returns HTML content type for HTMX compatibility."""
    response = client.post("/api/search", data=sample_search_data)
    assert "text/html" in response.headers["content-type"]


def test_search_endpoint_returns_html_table(
    client: TestClient, sample_search_data: dict[str, str]
) -> None:
    """Test that search endpoint returns HTML table structure."""
    response = client.post("/api/search", data=sample_search_data)
    html_content = response.text

    # Check for table structure
    assert "<table>" in html_content
    assert "<thead>" in html_content
    assert "<tbody>" in html_content
    assert "</table>" in html_content


def test_search_endpoint_with_empty_query_returns_empty_result(
    client: TestClient, empty_search_data: dict[str, str]
) -> None:
    """Test that search endpoint returns empty results for empty query."""
    response = client.post("/api/search", data=empty_search_data)
    assert response.status_code == status.HTTP_200_OK

    html_content = response.text
    # Should contain "Start typing to search..." message for empty query
    assert "Start typing to search..." in html_content
    assert "<table>" not in html_content  # No table for empty query


def test_search_endpoint_with_short_query_returns_empty_result(
    client: TestClient, short_search_data: dict[str, str]
) -> None:
    """Test that search endpoint returns empty results for queries shorter than 2 characters."""
    response = client.post("/api/search", data=short_search_data)
    assert response.status_code == status.HTTP_200_OK

    html_content = response.text
    # Should contain "No RFPs found" message for short query
    assert "No RFPs found" in html_content
    assert "<table>" not in html_content  # No table for queries that return no results


def test_search_endpoint_case_insensitive(client: TestClient) -> None:
    """Test that search is case insensitive."""
    # Test with different cases using RFP data
    test_cases = [
        {"query": "software"},
        {"query": "SOFTWARE"},
        {"query": "Software"},
        {"query": "SoFtWaRe"},
    ]

    results: list[str] = []
    for test_data in test_cases:
        response = client.post("/api/search", data=test_data)
        assert response.status_code == status.HTTP_200_OK
        results.append(response.text)

    # All results should be identical
    assert all(result == results[0] for result in results)


def test_search_endpoint_partial_match(client: TestClient) -> None:
    """Test that search works with partial matches."""
    # Test partial matches using RFP data
    response = client.post(
        "/api/search", data={"query": "develop"}
    )  # Should match "Software Development"
    assert response.status_code == status.HTTP_200_OK

    html_content = response.text
    # Should find results containing "develop"
    assert html_content.count("<tr>") > 1  # More than just header


def test_search_endpoint_searches_multiple_fields(client: TestClient) -> None:
    """Test that search works across RFP name and description fields."""
    search_terms = [
        {"query": "Software", "field": "name"},
        {"query": "development", "field": "name"},
        {
            "query": "modern",
            "field": "description",
        },  # This should match "modern web application"
        {"query": "marketing", "field": "name"},
        {"query": "healthcare", "field": "description"},
    ]

    for search_data in search_terms:
        response = client.post("/api/search", data={"query": search_data["query"]})
        assert response.status_code == status.HTTP_200_OK

        html_content = response.text
        # Should find results
        assert html_content.count("<tr>") > 1, (
            f"No results found for {search_data['field']} search with query '{search_data['query']}'"
        )


def test_search_endpoint_returns_expected_table_headers(
    client: TestClient, sample_search_data: dict[str, str]
) -> None:
    """Test that search endpoint returns expected table headers."""
    response = client.post("/api/search", data=sample_search_data)
    html_content = response.text

    # Check for expected RFP headers
    expected_headers = ["RFP Name", "More Information"]
    for header in expected_headers:
        assert f"<th>{header}</th>" in html_content


def test_search_endpoint_with_no_results(client: TestClient) -> None:
    """Test search endpoint with query that should return no results."""
    response = client.post("/api/search", data={"query": "zzznomatcheszzz"})
    assert response.status_code == status.HTTP_200_OK

    html_content = response.text
    # Should contain "No RFPs found" message
    assert "No RFPs found" in html_content
    assert "<table>" not in html_content  # No table when no results


@pytest.mark.parametrize("method", ["GET", "PUT", "DELETE", "PATCH"])
def test_search_endpoint_only_accepts_post(client: TestClient, method: str) -> None:
    """Test that search endpoint only accepts POST requests."""
    response = client.request(method, "/api/search")
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


def test_search_endpoint_requires_query_parameter(client: TestClient) -> None:
    """Test that search endpoint handles missing query parameter gracefully."""
    response = client.post("/api/search", data={})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
