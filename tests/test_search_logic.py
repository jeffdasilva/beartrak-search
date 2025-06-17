"""
Unit tests for the BearTrak Search API core search logic.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from main import search_properties


@pytest.mark.asyncio
async def test_search_properties_with_valid_query(
    test_db_session: AsyncSession,
) -> None:
    """Test that search_properties returns results for valid queries."""
    results = await search_properties("apartment", test_db_session)
    assert isinstance(results, list)
    assert len(results) > 0

    # Check that all returned items are properties with correct structure
    for prop in results:
        assert hasattr(prop, "name")
        assert hasattr(prop, "location")
        assert hasattr(prop, "type")
        assert hasattr(prop, "price")
        assert hasattr(prop, "details")


@pytest.mark.asyncio
async def test_search_properties_empty_query(test_db_session: AsyncSession) -> None:
    """Test that search_properties returns empty list for empty query."""
    results = await search_properties("", test_db_session)
    assert results == []


@pytest.mark.asyncio
async def test_search_properties_short_query(test_db_session: AsyncSession) -> None:
    """Test that search_properties returns empty list for queries shorter than 2 characters."""
    results = await search_properties("a", test_db_session)
    assert results == []


@pytest.mark.asyncio
async def test_search_properties_case_insensitive(
    test_db_session: AsyncSession,
) -> None:
    """Test that search_properties is case insensitive."""
    queries = ["apartment", "APARTMENT", "Apartment", "aPaRtMeNt"]

    results_list = []
    for query in queries:
        results = await search_properties(query, test_db_session)
        results_list.append(results)

    # All queries should return the same results
    first_result = results_list[0]
    for results in results_list[1:]:
        assert len(results) == len(first_result)
        # Check that the same properties are returned (by name)
        first_names = {prop.name for prop in first_result}
        result_names = {prop.name for prop in results}
        assert first_names == result_names


@pytest.mark.asyncio
async def test_search_properties_searches_all_fields(
    test_db_session: AsyncSession,
) -> None:
    """Test that search_properties searches across all property fields."""
    # Test searching by different fields
    test_cases = [
        ("Seattle", "location"),
        ("downtown", "name"),
        ("House", "type"),
        ("bath", "details"),
    ]

    for query, field_type in test_cases:
        results = await search_properties(query, test_db_session)
        assert len(results) > 0, (
            f"Should find results when searching for '{query}' in {field_type}"
        )

        # Verify that at least one result contains the query term
        found_match = False
        for prop in results:
            # Convert all fields to lowercase for case-insensitive comparison
            prop_text = (
                f"{prop.name} {prop.location} {prop.type} {prop.details}".lower()
            )
            if query.lower() in prop_text:
                found_match = True
                break

        assert found_match, f"Query '{query}' should match at least one property field"


@pytest.mark.asyncio
async def test_search_properties_no_matches(test_db_session: AsyncSession) -> None:
    """Test that search_properties returns empty list when no matches found."""
    results = await search_properties("zzznomatcheszzz", test_db_session)
    assert results == []


@pytest.mark.asyncio
async def test_search_properties_partial_matches(test_db_session: AsyncSession) -> None:
    """Test that search_properties works with partial matches."""
    # Test partial word matching
    results = await search_properties(
        "down", test_db_session
    )  # Should match "downtown"
    assert len(results) > 0

    # Verify that the results contain the partial match
    found_downtown = False
    for prop in results:
        if "downtown" in prop.name.lower():
            found_downtown = True
            break
    assert found_downtown, (
        "Should find properties with 'downtown' when searching for 'down'"
    )


@pytest.mark.asyncio
async def test_search_properties_whitespace_handling(
    test_db_session: AsyncSession,
) -> None:
    """Test that search_properties handles whitespace correctly."""
    # Test with leading/trailing whitespace
    results_normal = await search_properties("apartment", test_db_session)
    results_whitespace = await search_properties("  apartment  ", test_db_session)

    assert len(results_normal) == len(results_whitespace)

    # Check that the same properties are returned
    normal_names = {prop.name for prop in results_normal}
    whitespace_names = {prop.name for prop in results_whitespace}
    assert normal_names == whitespace_names


@pytest.mark.asyncio
async def test_search_properties_return_type(test_db_session: AsyncSession) -> None:
    """Test that search_properties returns the correct data types."""
    results = await search_properties("apartment", test_db_session)
    assert isinstance(results, list)

    if results:  # If we have results
        # Check the structure of returned objects
        prop = results[0]
        assert hasattr(prop, "name")
        assert hasattr(prop, "location")
        assert hasattr(prop, "type")
        assert hasattr(prop, "price")
        assert hasattr(prop, "details")

        # Check that all fields are strings
        assert isinstance(prop.name, str)
        assert isinstance(prop.location, str)
        assert isinstance(prop.type, str)
        assert isinstance(prop.price, str)
        assert isinstance(prop.details, str)


@pytest.mark.parametrize(
    ("query", "expected_count"),
    [
        ("apartment", 1),  # Should find at least 1 apartment
        ("Seattle", 1),  # Should find properties in Seattle
        ("house", 1),  # Should find at least 1 house
    ],
)
@pytest.mark.asyncio
async def test_search_properties_expected_counts(
    query: str, expected_count: int, test_db_session: AsyncSession
) -> None:
    """Test that search_properties returns expected minimum counts for known queries."""
    results = await search_properties(query, test_db_session)
    assert len(results) >= expected_count, (
        f"Expected at least {expected_count} results for query '{query}', got {len(results)}"
    )
