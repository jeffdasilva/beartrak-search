"""
Unit tests for the BearTrak Search API core search logic.
"""

import pytest

from main import search_properties


def test_search_properties_with_valid_query() -> None:
    """Test that search_properties returns results for valid queries."""
    results = search_properties("apartment")
    assert isinstance(results, list)
    assert len(results) > 0

    # Check that all returned items are properties with correct structure
    for prop in results:
        assert "name" in prop
        assert "location" in prop
        assert "type" in prop
        assert "price" in prop
        assert "details" in prop


def test_search_properties_empty_query() -> None:
    """Test that search_properties returns empty list for empty query."""
    results = search_properties("")
    assert results == []


def test_search_properties_short_query() -> None:
    """Test that search_properties returns empty list for queries shorter than 2 characters."""
    results = search_properties("a")
    assert results == []


def test_search_properties_case_insensitive() -> None:
    """Test that search_properties is case insensitive."""
    queries = ["apartment", "APARTMENT", "Apartment", "aPaRtMeNt"]

    results_list = [search_properties(query) for query in queries]

    # All should return same results
    first_result = results_list[0]
    for result in results_list[1:]:
        assert result == first_result


def test_search_properties_searches_all_fields() -> None:
    """Test that search_properties searches across all property fields."""
    # Test searching by different fields
    test_cases = [
        ("Seattle", "location"),
        ("downtown", "name"),
        ("House", "type"),
        ("bath", "details"),
    ]

    for query, field_type in test_cases:
        results = search_properties(query)
        assert len(results) > 0, (
            f"No results found for {field_type} search with '{query}'"
        )

        # Verify the query appears in at least one field of returned properties
        found_match = False
        for prop in results:
            searchable_text = f"{prop['name']} {prop['location']} {prop['type']} {prop['details']}".lower()
            if query.lower() in searchable_text:
                found_match = True
                break
        assert found_match, f"Query '{query}' not found in search results"


def test_search_properties_no_matches() -> None:
    """Test that search_properties returns empty list when no matches found."""
    results = search_properties("zzznomatcheszzz")
    assert results == []


def test_search_properties_partial_matches() -> None:
    """Test that search_properties works with partial matches."""
    # Test partial word matching
    results = search_properties("down")  # Should match "downtown"
    assert len(results) > 0

    # Verify that at least one result contains the partial match
    found_match = False
    for prop in results:
        searchable_text = f"{prop['name']} {prop['location']} {prop['type']} {prop['details']}".lower()
        if "down" in searchable_text:
            found_match = True
            break
    assert found_match


def test_search_properties_whitespace_handling() -> None:
    """Test that search_properties handles whitespace correctly."""
    # Test with leading/trailing whitespace
    results_normal = search_properties("apartment")
    results_whitespace = search_properties("  apartment  ")

    assert results_normal == results_whitespace


def test_search_properties_return_type() -> None:
    """Test that search_properties returns the correct data types."""
    results = search_properties("apartment")

    # Should return a list
    assert isinstance(results, list)

    # Each item should be a dict with string values
    for prop in results:
        assert isinstance(prop, dict)
        for key, value in prop.items():
            assert isinstance(key, str)
            assert isinstance(value, str)


@pytest.mark.parametrize(
    ("query", "expected_count"),
    [
        ("apartment", 1),  # Should find at least 1 apartment
        ("Seattle", 1),  # Should find properties in Seattle
        ("house", 1),  # Should find at least 1 house
    ],
)
def test_search_properties_expected_counts(query: str, expected_count: int) -> None:
    """Test that search_properties returns expected minimum counts for known queries."""
    results = search_properties(query)
    assert len(results) >= expected_count, (
        f"Expected at least {expected_count} results for '{query}'"
    )
