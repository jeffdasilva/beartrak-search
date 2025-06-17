# BearTrak Search Backend

A FastAPI backend for the BearTrak Search application that provides search functionality with HTMX-compatible HTML responses.

## Features

- **FastAPI Framework**: Modern, fast web framework for building APIs
- **HTMX Integration**: Returns HTML responses for seamless frontend integration
- **CORS Support**: Configured for cross-origin requests
- **Real-time Search**: Supports live search as users type
- **Sample Data**: Includes sample property data for testing
- **uv Package Management**: Modern Python package and project management

## Prerequisites

- **Python 3.10+**
- **uv** (Python package manager)

### Install uv

```bash
# On macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or with pip
pip install uv
```

## Project Structure

```
beartrak-search/
├── main.py              # Main FastAPI application
├── pyproject.toml       # Project configuration and dependencies
├── requirements.txt     # Legacy requirements (optional)
├── .env                # Environment configuration
├── start.sh            # Startup script
├── test_api.py         # API test script
├── README.md           # This file
└── .github/
    └── copilot-instructions.md
```

## Quick Start

1. **Clone and Navigate**:
   ```bash
   cd beartrak-search
   ```

2. **Install Dependencies with uv**:
   ```bash
   uv sync
   ```

3. **Run the Server**:
   ```bash
   # Using the startup script (recommended)
   ./start.sh
   
   # Or directly with uv
   uv run python main.py
   
   # Or using the project script
   uv run beartrak-search
   ```

4. **Access the API**:
   - API will be available at: `http://localhost:8000`
   - Interactive docs: `http://localhost:8000/docs`
   - Health check: `http://localhost:8000/health`

## Development Commands

### Install Dependencies
```bash
# Install all dependencies including dev dependencies
uv sync

# Install only production dependencies
uv sync --no-dev
```

### Run Tests
```bash
# Run unit tests (no server required)
make test

# Run all tests including integration (requires running server)
make test-all

# Run integration tests only (requires running server)
make test-integration

# Run quality assurance (linting + unit tests)
make qa
```

### Development Workflow
```bash
# 1. Install dependencies
uv sync

# 2. Run quality checks during development
make qa

# 3. Start server for integration testing (optional)
make start

# 4. In another terminal, run integration tests
make test-integration
```

### Add New Dependencies
```bash
# Add a production dependency
uv add package-name

# Add a development dependency
uv add --dev package-name

# Add a specific version
uv add "package-name>=1.0.0"
```

### Update Dependencies
```bash
# Update all dependencies
uv sync --upgrade

# Update specific package
uv add package-name --upgrade
```

## API Endpoints

### POST /api/search

The main search endpoint that returns HTML for HTMX integration.

**Request**:
```
POST /api/search
Content-Type: application/x-www-form-urlencoded

query=search_term
```

**Response**:
Returns HTML table with search results or a "no results" message.

### GET /

Health check endpoint.

### GET /health

Detailed health check with service information.

## Frontend Integration

This backend is designed to work with the BearTrak Search frontend. The frontend should:

1. Send POST requests to `/api/search` with form data
2. Include the search query in the `query` parameter
3. Replace the target element with the returned HTML

Example HTMX configuration:
```html
<input 
  type="text" 
  name="query" 
  hx-post="/api/search"
  hx-target="#search-results"
  hx-trigger="keyup changed delay:300ms"
>
```

## Development

### Running in Development Mode

The application includes auto-reload for development:

```bash
python main.py
```

### Adding New Features

1. **Modify Search Logic**: Update the `search_properties()` function in `main.py`
2. **Add New Endpoints**: Create new route handlers in `main.py`
3. **Update HTML Templates**: Modify the `generate_results_html()` function

### Sample Data

The application includes sample property data for testing. In production, replace the `SAMPLE_PROPERTIES` list with your actual data source (database, API, etc.).

## Configuration

Environment variables can be set in the `.env` file:

- `DEBUG`: Enable debug mode
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)
- `CORS_ORIGINS`: Allowed CORS origins

## Production Deployment

For production deployment:

1. Set `DEBUG=False` in environment
2. Configure specific CORS origins (remove "*")
3. Use a production ASGI server like Gunicorn
4. Set up proper logging and monitoring

Example production command:
```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## CI/CD

This project includes comprehensive GitHub Actions workflows for continuous integration:

### Workflows

- **Fast CI** (`fast-ci.yml`): Runs on all branch pushes
  - Quality assurance (`make qa`)
  - Code formatting checks
  - Integration testing

- **Full CI** (`ci.yml`): Comprehensive testing
  - Matrix testing across Python 3.10-3.12
  - Type checking, linting, formatting
  - Unit and integration tests
  - Security scanning

- **Main Branch CI** (`main-ci.yml`): Enhanced checks for main branch
  - Multi-version testing
  - Coverage reporting
  - Deployment readiness validation
  - OpenAPI schema validation

### Quality Checks

All workflows include:
- **Type Safety**: mypy with strict configuration
- **Code Quality**: ruff linting and formatting
- **Testing**: pytest with 46+ comprehensive tests
- **Security**: safety and bandit scanning
- **Integration**: Real HTTP API testing

## Dependencies

- **FastAPI**: Web framework
- **Uvicorn**: ASGI server
- **python-multipart**: Form data parsing
- **Jinja2**: Template engine (for future use)

## License

Copyright 2025 Bearfoot Software. All rights reserved.
