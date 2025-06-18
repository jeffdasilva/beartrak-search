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


@pytest.mark.parametrize(
    ("query", "expected_matches"),
    [
        # Test queries from debug_test.py to ensure comprehensive coverage
        ("software", ["Software Development Project"]),
        ("modern", ["Software Development Project"]),  # Should match description
        ("healthcare", ["Marketing Campaign Services"]),  # Should match description
        ("web application", ["Software Development Project"]),  # Multi-word phrase
        ("development", ["Software Development Project"]),  # Should match name
        ("react", ["Software Development Project"]),  # Should match description
        (
            "node.js",
            ["Software Development Project"],
        ),  # Should match description with special chars
        ("creative", ["Marketing Campaign Services"]),  # Should match description
        ("agency", ["Marketing Campaign Services"]),  # Should match description
        (
            "campaign",
            ["Marketing Campaign Services"],
        ),  # Should match name and description
        (
            "research",
            ["University Research Platform"],
        ),  # Should match name and description
        (
            "platform",
            ["University Research Platform"],
        ),  # Should match name and description
        ("data management", ["University Research Platform"]),  # Multi-word phrase
        ("academic", ["University Research Platform"]),  # Should match description
        ("departments", ["University Research Platform"]),  # Should match description
    ],
)
@pytest.mark.asyncio
async def test_search_rfps_debug_test_coverage(
    query: str, expected_matches: list[str], test_db_session: AsyncSession
) -> None:
    """
    Test search functionality with all queries from debug_test.py and more.
    This ensures we have complete coverage of the debug_test.py functionality.
    """
    results = await search_rfps(query, test_db_session)

    # Should find at least one result for all these queries
    assert len(results) > 0, f"Query '{query}' should return at least one result"

    # Check that expected matches are found
    result_names = {rfp.name for rfp in results}
    for expected_name in expected_matches:
        assert expected_name in result_names, (
            f"Query '{query}' should find RFP '{expected_name}'. Found: {result_names}"
        )


@pytest.mark.asyncio
async def test_search_rfps_comprehensive_field_search(
    test_db_session: AsyncSession,
) -> None:
    """
    Test that search works comprehensively across all fields.
    This covers the debug_test.py scenario of testing multiple different search terms.
    """
    test_cases = [
        # Name field searches
        {"query": "Software", "should_find": "Software Development Project"},
        {"query": "Marketing", "should_find": "Marketing Campaign Services"},
        {"query": "University", "should_find": "University Research Platform"},
        # Description field searches
        {"query": "React", "should_find": "Software Development Project"},
        {
            "query": "healthcare professionals",
            "should_find": "Marketing Campaign Services",
        },
        {
            "query": "multiple departments",
            "should_find": "University Research Platform",
        },
        # Cross-field partial matches
        {"query": "web", "should_find": "Software Development Project"},
        {"query": "seeking", "should_find": "Marketing Campaign Services"},
        {"query": "proposals", "should_find": "University Research Platform"},
    ]

    for case in test_cases:
        results = await search_rfps(case["query"], test_db_session)

        # Should find at least one result
        assert len(results) > 0, f"Query '{case['query']}' should return results"

        # Should find the expected RFP
        found_expected = any(case["should_find"] in rfp.name for rfp in results)
        assert found_expected, (
            f"Query '{case['query']}' should find RFP containing '{case['should_find']}'. "
            f"Found: {[rfp.name for rfp in results]}"
        )


@pytest.mark.asyncio
async def test_search_rfps_description_content_verification(
    test_db_session: AsyncSession,
) -> None:
    """
    Test search results to verify they match the expected database content.
    This replicates the debug_test.py output verification functionality.
    """
    # Test that we can find all three sample RFPs with appropriate queries
    all_queries_and_expected: list[tuple[str, str]] = [
        ("software development", "Software Development Project"),
        ("marketing campaign", "Marketing Campaign Services"),
        ("university research", "University Research Platform"),
    ]

    for query, expected_name in all_queries_and_expected:
        results = await search_rfps(query, test_db_session)

        # Should find the expected RFP
        found_rfp = None
        for rfp in results:
            if expected_name in rfp.name:
                found_rfp = rfp
                break

        assert found_rfp is not None, (
            f"Should find RFP '{expected_name}' with query '{query}'"
        )

        # Note: RFPResponse doesn't include description, but we can verify the search worked
        # by ensuring the correct RFP was found by name
        assert found_rfp.name == expected_name


@pytest.mark.asyncio
async def test_search_rfps_edge_cases_comprehensive(
    test_db_session: AsyncSession,
) -> None:
    """
    Test comprehensive edge cases that debug_test.py might encounter.
    """
    # Test various edge cases
    edge_cases: list[tuple[str, list[str]]] = [
        # Empty and minimal queries (should return empty)
        ("", []),
        ("a", []),  # Too short
        ("ab", []),  # Minimum length but no matches
        # Special characters and punctuation
        ("node.js", ["Software Development Project"]),  # Period in search
        ("web application", ["Software Development Project"]),  # Space in search
        # Case variations
        ("SOFTWARE", ["Software Development Project"]),  # All caps
        ("Marketing", ["Marketing Campaign Services"]),  # Mixed case
        ("university", ["University Research Platform"]),  # All lowercase
        # Partial word matches
        ("soft", ["Software Development Project"]),  # Partial beginning
        ("ware", ["Software Development Project"]),  # Partial middle/end
        ("develop", ["Software Development Project"]),  # Partial word
        # Non-existent terms
        ("nonexistent", []),
        ("zzz", []),
        ("12345", []),
    ]

    for query, expected_names in edge_cases:
        results = await search_rfps(query, test_db_session)

        if not expected_names:  # Should be empty
            assert len(results) == 0, f"Query '{query}' should return no results"
        else:  # Should find expected RFPs
            result_names = {rfp.name for rfp in results}
            for expected_name in expected_names:
                assert expected_name in result_names, (
                    f"Query '{query}' should find '{expected_name}'. Found: {result_names}"
                )
