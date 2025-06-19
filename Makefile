.DEFAULT_GOAL := help

# Variables
PYTHON_FILES := main.py tests/
UV := uv
# Port configuration - can be overridden via BEARTRAK_ environment variables
PRODUCTION_PORT := $(shell echo $${BEARTRAK_PRODUCTION_PORT:-8000})
DEVELOPMENT_PORT := $(shell echo $${BEARTRAK_DEVELOPMENT_PORT:-8001})

.PHONY: help
help: ## Show this help message
	@echo "🐻 BearTrak Search API - Available Make Targets"
	@echo "================================================="
	@echo ""
	@echo "Setup and Installation:"
	@echo "  install          Install production dependencies"
	@echo "  dev              Install all dependencies (including dev)"
	@echo ""
	@echo "Development:"
	@echo "  start            Start the production server (requires: install)"
	@echo "  start-dev        Start the development server (requires: install)"
	@echo "  server           Alias for start-dev (backward compatibility)"
	@echo ""
	@echo "Code Quality:"
	@echo "  type-check       Run type checking with mypy"
	@echo "  lint-ruff        Run linting with ruff"
	@echo "  lint             Run all linting and formatting checks"
	@echo ""
	@echo "Code Formatting (Preferred - Ruff):"
	@echo "  format           Format code with ruff (preferred)"
	@echo "  format-check     Check if code is properly formatted with ruff"
	@echo "  format-ruff      Format code with ruff (preferred formatter)"
	@echo "  format-ruff-check Check code formatting with ruff"
	@echo ""
	@echo "Code Formatting (Legacy):"
	@echo "  format-isort     Sort imports with isort (legacy - prefer ruff)"
	@echo "  format-black     Format code with black (legacy - prefer ruff)"
	@echo "  format-legacy    Format code with legacy tools (isort + black)"
	@echo ""
	@echo "Quality Assurance:"
	@echo "  qa               Run all quality checks (linting + tests)"
	@echo "  ci               Run CI checks (for automation)"
	@echo ""
	@echo "Testing:"
	@echo "  test             Run unit tests with pytest (no server required)"
	@echo "  test-all         Run all tests including integration (requires server)"
	@echo "  test-legacy      Run the legacy API test script"
	@echo "  test-integration Run integration tests (requires running server)"
	@echo "  test-health      Quick health check test (development server)"
	@echo "  test-health-prod Quick health check test (production server)"
	@echo ""
	@echo "Utilities:"
	@echo "  clean            Clean up cache files and temporary directories"
	@echo "  deps-check       Check if uv is installed"
	@echo "  upgrade          Upgrade all dependencies"
	@echo "  info             Show project information"
	@echo ""
	@echo "All-in-one:"
	@echo "  all              Run complete setup and validation"

.PHONY: install
install: ## Install production dependencies
	@echo "📦 Installing dependencies with uv..."
	@$(UV) sync --no-dev

.PHONY: dev
dev: ## Install all dependencies (including dev)
	@echo "📦 Installing all dependencies with uv..."
	@$(UV) sync

.PHONY: start
start: install ## Start the production server
	@echo "🚀 Starting BearTrak Search API (Production Mode)..."
	@echo "📍 Server will be available at: http://localhost:$(PRODUCTION_PORT)"
	@echo "📚 API documentation: http://localhost:$(PRODUCTION_PORT)/docs"
	@echo "❤️  Health check: http://localhost:$(PRODUCTION_PORT)/health"
	@echo "🗄️  Using production database: beartrak.db"
	@echo ""
	@echo "🔄 Starting server..."
	@BEARTRAK_ENVIRONMENT=production $(UV) run uvicorn main:app --host 0.0.0.0 --port $(PRODUCTION_PORT) --reload

.PHONY: start-dev
start-dev: install ## Start the development server
	@echo "🚀 Starting BearTrak Search API (Development Mode)..."
	@echo "📍 Server will be available at: http://localhost:$(DEVELOPMENT_PORT)"
	@echo "📚 API documentation: http://localhost:$(DEVELOPMENT_PORT)/docs"
	@echo "❤️  Health check: http://localhost:$(DEVELOPMENT_PORT)/health"
	@echo "🗄️  Using development database: beartrak_test.db"
	@echo ""
	@echo "🔄 Starting server..."
	@BEARTRAK_ENVIRONMENT=development $(UV) run uvicorn main:app --host 0.0.0.0 --port $(DEVELOPMENT_PORT) --reload

.PHONY: server
server: start-dev ## Alias for start-dev (backward compatibility)

.PHONY: check
check: lint ## Run all checks (linting + type checking)
	@echo "✅ All checks passed!"

.PHONY: type-check
type-check: ## Run type checking with mypy
	@echo "🔍 Running mypy type checking..."
	@$(UV) run mypy $(PYTHON_FILES)
	@echo "✅ All type checks passed!"

.PHONY: lint-ruff
lint-ruff: ## Run linting with ruff
	@echo "🔍 Running ruff linting..."
	@$(UV) run ruff check $(PYTHON_FILES)
	@echo "✅ Ruff linting passed!"

.PHONY: lint
lint: type-check lint-ruff format-check ## Run all linting and formatting checks
	@echo "✅ All linting and formatting checks passed!"

.PHONY: format
format: format-ruff ## Format code with ruff (preferred)
	@echo "✅ Code formatting complete!"

.PHONY: format-check
format-check: format-ruff-check ## Check if code is properly formatted with ruff (preferred)
	@echo "✅ Code formatting check complete!"

.PHONY: format-ruff
format-ruff: ## Format code with ruff (preferred formatter)
	@echo "🎨 Formatting code with ruff..."
	@$(UV) run ruff format $(PYTHON_FILES)
	@$(UV) run ruff check --fix $(PYTHON_FILES)

.PHONY: format-ruff-check
format-ruff-check: ## Check code formatting with ruff
	@echo "🔍 Checking code formatting with ruff..."
	@$(UV) run ruff format --check $(PYTHON_FILES)
	@$(UV) run ruff check $(PYTHON_FILES)

.PHONY: format-isort
format-isort: ## Sort imports with isort (legacy - prefer ruff)
	@echo "📝 Sorting imports with isort..."
	@$(UV) run isort $(PYTHON_FILES)

.PHONY: format-isort-check
format-isort-check: ## Check import sorting with isort (legacy - prefer ruff)
	@echo "📋 Checking import sorting with isort..."
	@$(UV) run isort --check-only --diff $(PYTHON_FILES)

.PHONY: format-black
format-black: ## Format code with black (legacy - prefer ruff)
	@echo "🎨 Formatting code with black..."
	@$(UV) run black $(PYTHON_FILES)

.PHONY: format-black-check
format-black-check: ## Check code formatting with black (legacy - prefer ruff)
	@echo "🔍 Checking code formatting with black..."
	@$(UV) run black --check --diff $(PYTHON_FILES)

.PHONY: format-legacy
format-legacy: format-isort format-black ## Format code with legacy tools (isort + black)
	@echo "✅ Legacy code formatting complete!"

.PHONY: format-legacy-check
format-legacy-check: format-isort-check format-black-check ## Check if code is properly formatted with legacy tools
	@echo "✅ Legacy code formatting check complete!"

.PHONY: qa
qa: lint test ## Run all quality checks (linting + tests)
	@echo "✅ All quality checks passed!"

.PHONY: ci
ci: format-check type-check ## Run CI checks (for automation)
	@echo "✅ CI checks complete!"

.PHONY: test
test: ## Run unit tests with pytest
	@echo "🧪 Running unit tests with pytest..."
	@$(UV) run pytest tests/ -v --ignore=tests/test_integration.py

.PHONY: test-legacy
test-legacy: ## Run the manual API test script
	@echo "🧪 Running manual API test..."
	@$(UV) run python tests/test_api_legacy.py

.PHONY: test-integration
test-integration: ## Run integration tests (requires running server)
	@echo "🧪 Running integration tests..."
	@echo "💡 Assuming development server on port $(DEVELOPMENT_PORT)"
	@echo "   To test production server: BEARTRAK_TEST_SERVER_PORT=8000 make test-integration"
	@BEARTRAK_TEST_SERVER_PORT=$(DEVELOPMENT_PORT) $(UV) run python tests/test_integration.py

.PHONY: test-all
test-all: ## Run all tests including integration (requires running server)
	@echo "🧪 Running all tests (unit + integration)..."
	@echo "💡 Integration tests will use development server on port $(DEVELOPMENT_PORT)"
	@echo "   To test production server: BEARTRAK_TEST_SERVER_PORT=8000 make test-all"
	@BEARTRAK_TEST_SERVER_PORT=$(DEVELOPMENT_PORT) $(UV) run pytest tests/ -v

.PHONY: test-health
test-health: ## Quick health check test
	@echo "🩺 Testing health endpoint on development server..."
	@curl -s http://localhost:$(DEVELOPMENT_PORT)/health | $(UV) run python -m json.tool || echo "❌ Development server not running on port $(DEVELOPMENT_PORT)"

.PHONY: test-health-prod
test-health-prod: ## Quick health check test for production server
	@echo "🩺 Testing health endpoint on production server..."
	@curl -s http://localhost:$(PRODUCTION_PORT)/health | $(UV) run python -m json.tool || echo "❌ Production server not running on port $(PRODUCTION_PORT)"

.PHONY: clean
clean: ## Clean up cache files and temporary directories
	@echo "🧹 Cleaning up..."
	@rm -rf __pycache__/ .mypy_cache/ .pytest_cache/ .ruff_cache/
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -delete
	@echo "✅ Cleanup complete!"

.PHONY: deps-check
deps-check: ## Check if uv is installed
	@command -v $(UV) >/dev/null 2>&1 || { echo "❌ uv is not installed. Install it with: curl -LsSf https://astral.sh/uv/install.sh | sh"; exit 1; }
	@echo "✅ uv is installed"

.PHONY: upgrade
upgrade: ## Upgrade all dependencies
	@echo "⬆️  Upgrading dependencies..."
	@$(UV) sync --upgrade

.PHONY: all
all: clean deps-check dev type-check test ## Run complete setup and validation
	@echo "🎉 All tasks completed successfully!"

.PHONY: info
info: ## Show project information
	@echo "📋 Project Information"
	@echo "======================"
	@echo "Name: BearTrak Search API"
	@echo "Description: FastAPI backend with HTMX integration"
	@echo "Python: $(shell $(UV) run python --version 2>/dev/null || echo 'Not found')"
	@echo "UV: $(shell $(UV) --version 2>/dev/null || echo 'Not found')"
	@echo "Port: $(PORT)"
	@echo ""
	@echo "📁 Key Files:"
	@echo "  - main.py (FastAPI application)"
	@echo "  - tests/ (Unit and integration tests)"
	@echo "  - pyproject.toml (Dependencies & config)"
	@echo "  - Makefile (This file)"
	@echo ""
	@echo "🎯 Preferred Tools:"
	@echo "  - Formatter: ruff (use 'make format')"
	@echo "  - Linter: ruff (included in 'make lint')"
	@echo "  - Type Checker: mypy"
	@echo ""
	@echo "🔧 Legacy Tools (still available):"
	@echo "  - black (use 'make format-black')"
	@echo "  - isort (use 'make format-isort')"

