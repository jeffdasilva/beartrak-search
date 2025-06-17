<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# BearTrak Search Backend

This is a FastAPI backend project for the BearTrak Search frontend application. The API provides search functionality that returns HTML responses for HTMX integration.

## Key Guidelines:

- Use FastAPI for all API endpoints
- Return HTML responses for HTMX compatibility 
- Implement CORS middleware for frontend integration
- Follow RESTful API design principles
- Use proper error handling and status codes
- Maintain consistent response formats
- Focus on search functionality and data retrieval

## Development Guidelines:

### Package Management & Dependencies:
- Use `uv` for package management (not pip)
- Add new dependencies to `pyproject.toml`
- Run `uv sync` to install dependencies
- Use `uv run` prefix for running Python commands

### Code Quality & Type Safety:
- Follow strict type hints for all functions (mypy enforced)
- Include docstrings for API endpoints and public functions
- Use pydantic models for request/response validation
- Prefer async/await for I/O operations
- All code must pass `make qa` (linting + tests)

### Testing Standards:
- All tests are in the `tests/` directory using pytest
- Write comprehensive unit tests for new functionality
- Use the existing test fixtures in `tests/conftest.py`
- Add type annotations (`-> None`) to all test functions
- Integration tests should work with a running server
- Maintain high test coverage for critical functionality

### Code Formatting & Linting:
- Use `ruff` for formatting and linting (preferred over black/isort)
- Run `make format` before committing code
- All code must pass `make lint` (mypy + ruff)
- Assert statements are allowed in test files only

### Available Make Targets:
- `make start` - Start the development server
- `make test` - Run all unit tests with pytest
- `make test-integration` - Run integration tests (requires running server)
- `make lint` - Run type checking and linting
- `make format` - Format code with ruff
- `make qa` - Run complete quality checks (lint + test)
- `make clean` - Clean up cache files