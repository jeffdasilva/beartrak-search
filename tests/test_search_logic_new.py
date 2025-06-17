"""
Unit tests for the BearTrak RFP Search API core search logic.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from main import search_rfps


@pytest.mark.asyncio
async def test_search_rfps_with_valid_query(
    test_db_session: AsyncSession,
) -> None:
    """Test that search_rfps returns results for valid queries."""
    results = await search_rfps("software", test_db_session)
    assert isinstance(results, list)
    assert len(results) > 0

    # Check that all returned items are RFPs with correct structure
    for rfp in results:
        assert hasattr(rfp, "name")
        assert hasattr(rfp, "url")
        # Note: description is not returned in RFPResponse, only used for search


@pytest.mark.asyncio
async def test_search_rfps_empty_query(test_db_session: AsyncSession) -> None:
    """Test that search_rfps returns empty list for empty query."""
    results = await search_rfps("", test_db_session)
    assert results == []


@pytest.mark.asyncio
async def test_search_rfps_short_query(test_db_session: AsyncSession) -> None:
    """Test that search_rfps returns empty list for queries shorter than 2 characters."""
    results = await search_rfps("a", test_db_session)
    assert results == []


@pytest.mark.asyncio
async def test_search_rfps_case_insensitive(test_db_session: AsyncSession) -> None:
    """Test that search_rfps is case insensitive."""
    queries = ["software", "SOFTWARE", "Software", "SoFtWaRe"]

    results_list = []
    for query in queries:
        results = await search_rfps(query, test_db_session)
        results_list.append(results)

    # All queries should return the same results
    first_result = results_list[0]
    for results in results_list[1:]:
        assert len(results) == len(first_result)
        # Check that the same RFPs are returned (by name)
        first_names = {rfp.name for rfp in first_result}
        result_names = {rfp.name for rfp in results}
        assert first_names == result_names


@pytest.mark.asyncio
async def test_search_rfps_searches_all_fields(test_db_session: AsyncSession) -> None:
    """Test that search_rfps searches across name and description fields."""
    # Test searching by different fields
    test_cases = [
        ("software", "name and description"),
        ("marketing", "name and description"),
        ("university", "description"),
        ("platform", "description"),
    ]

    for query, field_type in test_cases:
        results = await search_rfps(query, test_db_session)
        assert len(results) > 0, (
            f"Should find results when searching for '{query}' in {field_type}"
        )

        # Verify that at least one result name contains a relevant term
        found_match = False
        for rfp in results:
            if query.lower() in rfp.name.lower():
                found_match = True
                break

        assert found_match, f"Query '{query}' should match at least one RFP"


@pytest.mark.asyncio
async def test_search_rfps_no_matches(test_db_session: AsyncSession) -> None:
    """Test that search_rfps returns empty list when no matches found."""
    results = await search_rfps("zzznomatcheszzz", test_db_session)
    assert results == []


@pytest.mark.asyncio
async def test_search_rfps_partial_matches(test_db_session: AsyncSession) -> None:
    """Test that search_rfps works with partial matches."""
    # Test partial word matching
    results = await search_rfps("soft", test_db_session)  # Should match "software"
    assert len(results) > 0

    # Verify that the results contain the partial match
    found_software = False
    for rfp in results:
        if "software" in rfp.name.lower():
            found_software = True
            break
    assert found_software, "Should find RFPs with 'software' when searching for 'soft'"


@pytest.mark.asyncio
async def test_search_rfps_whitespace_handling(test_db_session: AsyncSession) -> None:
    """Test that search_rfps handles whitespace correctly."""
    # Test with leading/trailing whitespace
    results_normal = await search_rfps("software", test_db_session)
    results_whitespace = await search_rfps("  software  ", test_db_session)

    assert len(results_normal) == len(results_whitespace)

    # Check that the same RFPs are returned
    normal_names = {rfp.name for rfp in results_normal}
    whitespace_names = {rfp.name for rfp in results_whitespace}
    assert normal_names == whitespace_names


@pytest.mark.asyncio
async def test_search_rfps_return_type(test_db_session: AsyncSession) -> None:
    """Test that search_rfps returns the correct data types."""
    results = await search_rfps("software", test_db_session)
    assert isinstance(results, list)

    if results:  # If we have results
        # Check the structure of returned objects
        rfp = results[0]
        assert hasattr(rfp, "name")
        assert hasattr(rfp, "url")

        # Check that all fields are of correct types
        assert isinstance(rfp.name, str)
        assert rfp.url is None or isinstance(rfp.url, str)


@pytest.mark.parametrize(
    ("query", "expected_count"),
    [
        ("software", 1),  # Should find at least 1 software RFP
        ("marketing", 1),  # Should find marketing RFPs
        ("university", 1),  # Should find university RFPs
    ],
)
@pytest.mark.asyncio
async def test_search_rfps_expected_counts(
    query: str, expected_count: int, test_db_session: AsyncSession
) -> None:
    """Test that search_rfps returns expected minimum counts for known queries."""
    results = await search_rfps(query, test_db_session)
    assert len(results) >= expected_count, (
        f"Expected at least {expected_count} results for query '{query}', got {len(results)}"
    )
