# BearTrak RFP Search Backend

A FastAPI backend for the BearTrak RFP Search application that provides search functionality for Request for Proposal (RFP) data with HTMX-compatible HTML responses.

## Features

- **FastAPI Framework**: Modern, fast web framework for building APIs
- **HTMX Integration**: Returns HTML responses for seamless frontend integration
- **CORS Support**: Configured for cross-origin requests
- **Real-time Search**: Supports live search as users type
- **Multi-Environment Database**: Separate databases for development, testing, and production
- **Sample Data**: Includes sample RFP data for testing
- **uv Package Management**: Modern Python package and project management

## Database Configuration

The application uses SQLite databases with different files for each environment:

- **Production**: `beartrak.db` - Clean database for production use  
- **Development/Testing**: `beartrak_test.db` - Shared database for development and testing

The database selection is controlled by the `ENVIRONMENT` variable in `.env`:

```env
ENVIRONMENT=development  # Options: development, production 
PRODUCTION_DB=beartrak.db
DEVELOPMENT_DB=beartrak_test.db
```

**Note**: Both development and testing use the same database file (`beartrak_test.db`). Tests automatically recreate tables with fresh sample data, so there's no interference between development work and test runs.

## Port Configuration

The application uses different default ports for each environment to avoid conflicts:

- **Production**: Port `8000` (default)
- **Development**: Port `8001` (default)

### Port Override Options:

1. **Environment Variables** (recommended):
   ```bash
   PRODUCTION_PORT=9000 make start      # Production on port 9000
   DEVELOPMENT_PORT=9001 make start-dev # Development on port 9001
   ```

2. **In `.env` file**:
   ```env
   PRODUCTION_PORT=9000
   DEVELOPMENT_PORT=9001
   ```

3. **Legacy PORT variable** (affects current environment):
   ```env
   PORT=9000  # Overrides the default for current ENVIRONMENT
   ```

You can also override the database URL directly:
```env
DATABASE_URL=sqlite+aiosqlite:///./custom.db
```

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
├── main.py                    # Main FastAPI application
├── Makefile                   # Development workflow commands
├── pyproject.toml            # Project configuration and dependencies
├── uv.lock                   # Dependency lock file
├── .env                      # Environment configuration (PORT=8000)
├── .gitignore               # Git ignore patterns
├── mypy.ini                 # Type checking configuration
├── README.md                # This file
├── tests/                   # Test suite
│   ├── __init__.py
│   ├── conftest.py              # Test fixtures and configuration
│   ├── test_app.py              # FastAPI application tests
│   ├── test_health.py           # Health endpoint tests
│   ├── test_search.py           # Search endpoint tests
│   ├── test_search_logic_new.py # RFP search logic unit tests
│   ├── test_integration.py      # Integration tests
│   └── test_api_legacy.py       # Manual API testing script
└── .github/
    ├── copilot-instructions.md # Development guidelines
    └── workflows/             # CI/CD workflows
        ├── ci.yml            # Comprehensive CI pipeline
        ├── fast-ci.yml       # Fast quality checks
        └── main-ci.yml       # Main branch validations
```

## Quick Start

1. **Clone and Navigate**:
   ```bash
   cd beartrak-search
   ```

2. **Install Dependencies**:
   ```bash
   # Install all dependencies (including development tools)
   make dev
   
   # Or install only production dependencies
   make install
   ```

3. **Run the Server**:
   ```bash
   # Start the production server (port 8000)
   make start
   
   # Start the development server (port 8001) - recommended for development
   make start-dev
   
   # Production server: http://localhost:8000
   # Development server: http://localhost:8001
   ```

4. **Access the API**:
   - **Production**: `http://localhost:8000` (clean database)
   - **Development**: `http://localhost:8001` (with sample data)
   - Interactive docs: `http://localhost:XXXX/docs` (replace XXXX with port)
   - Health check: `http://localhost:XXXX/health`

> **Port Configuration**: Default ports are 8000 (production) and 8001 (development). You can override these by setting `PRODUCTION_PORT` and `DEVELOPMENT_PORT` environment variables, or use the `PORT` variable in `.env` for the current environment.

## Development Workflow

### Quick Setup
```bash
# 1. Install dependencies and development tools
make dev

# 2. Run quality checks to ensure everything is working
make qa

# 3. Start the development server
make start-dev
```

### Available Make Targets

**Setup and Installation:**
- `make install` - Install production dependencies only
- `make dev` - Install all dependencies including development tools

**Development:**
- `make start` - Start the production server with auto-reload
- `make start-dev` - Start the development server with auto-reload (recommended for development)
- `make server` - Alias for start-dev (backward compatibility)

**Code Quality:**
- `make qa` - Run all quality checks (linting + unit tests)
- `make lint` - Run all linting and formatting checks  
- `make format` - Format code with ruff
- `make format-check` - Check if code is properly formatted
- `make type-check` - Run type checking with mypy

**Testing:**
- `make test` - Run unit tests (no server required)
- `make test-all` - Run all tests including integration (requires development server)
- `make test-integration` - Run integration tests (requires development server)
- `make test-health` - Quick health check test (development server)
- `make test-health-prod` - Quick health check test (production server)

**Utilities:**
- `make clean` - Clean up cache files and temporary directories
- `make info` - Show project information
- `make help` - Display all available targets
- `make deps-check` - Verify uv is installed
- `make upgrade` - Upgrade all dependencies

### Development Commands

#### Daily Development
```bash
# Check code quality before committing
make qa

# Format your code
make format

# Run only unit tests (fast)
make test
```

#### Integration Testing
```bash
# Terminal 1: Start the development server (recommended)
make start-dev

# Terminal 2: Run integration tests
make test-integration

# Or run all tests (unit + integration) 
make test-all

# To test against production server instead:
# Terminal 1: make start
# Terminal 2: TEST_SERVER_PORT=8000 make test-integration
```

**Note**: GitHub CI automatically runs integration tests against the development server (port 8001) to match the local development workflow.

#### Project Maintenance
```bash
# Get project information
make info

# Clean up cache files
make clean

# Upgrade dependencies
make upgrade
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

### Daily Development Workflow

1. **Start your development session**:
   ```bash
   make dev    # Ensure all dependencies are installed
   make qa     # Verify code quality
   ```

2. **During development**:
   ```bash
   make format     # Format your code
   make test      # Run unit tests quickly
   make qa        # Full quality check before commits
   ```

3. **Testing with integration**:
   ```bash
   # Terminal 1
   make start
   
   # Terminal 2  
   make test-integration
   ```

### Adding New Dependencies

Use `uv` commands to manage dependencies:

```bash
# Add a production dependency
uv add package-name

# Add a development dependency  
uv add --dev package-name

# Add a specific version
uv add "package-name>=1.0.0"

# Update dependencies
make upgrade
```

### Running in Development Mode

The development server includes auto-reload:

```bash
make start
# Server automatically restarts when you modify files
```

### Adding New Features

1. **Modify Search Logic**: Update the `search_rfps()` function in `main.py`
2. **Add New Endpoints**: Create new route handlers in `main.py`  
3. **Update HTML Templates**: Modify the `generate_results_html()` function
4. **Test Your Changes**: Run `make qa` to ensure quality
5. **Integration Test**: Use `make test-integration` with a running server

### Sample Data

The application includes sample RFP data for testing. The database is automatically populated with sample Request for Proposal records including software development, marketing, and research platform RFPs.

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

This project includes comprehensive GitHub Actions workflows for continuous integration that validate both direct commands and Makefile targets.

### Workflows

- **Fast CI** (`fast-ci.yml`): Runs on all branch pushes
  - Uses `make qa` for quality assurance
  - Uses `make format-check` for code formatting validation
  - Integration testing with server setup

- **Full CI** (`ci.yml`): Comprehensive testing pipeline
  - Matrix testing across Python 3.10-3.12
  - Validates all Makefile targets (`make help`, `make qa`, `make test`, etc.)
  - Integration tests using `make test-integration`
  - Security scanning

- **Main Branch CI** (`main-ci.yml`): Enhanced checks for main branch
  - Multi-version testing with `make all`
  - Coverage reporting
  - Deployment readiness validation

### Quality Checks

All workflows use Makefile targets for consistency:
- **Type Safety**: `make type-check` (mypy with strict configuration)
- **Code Quality**: `make lint` (ruff linting and formatting)
- **Testing**: `make test` (pytest with 45+ comprehensive tests)
- **Integration**: `make test-integration` (Real HTTP API testing)
- **Complete QA**: `make qa` (combines linting + testing)

### Local Development vs CI

The CI workflows validate that the developer experience (Makefile targets) works correctly:

```bash
# What developers run locally:
make qa

# What CI validates:
make qa
make test-integration  # (with server running)
make format-check
# ... and many other Makefile targets
```

This ensures that local development commands match exactly what CI expects, preventing "works on my machine" issues.

## Dependencies

- **FastAPI**: Web framework
- **Uvicorn**: ASGI server
- **python-multipart**: Form data parsing
- **Jinja2**: Template engine (for future use)

## License

Copyright 2025 Bearfoot Software. All rights reserved.
