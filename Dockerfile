# Use Python 3.12 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Create data directory for database persistence
RUN mkdir -p /app/data /data

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Copy pyproject.toml and uv.lock first for better caching
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev

# Copy application code
COPY . .

# Set environment variables for production
ENV BEARTRAK_ENVIRONMENT=production
ENV BEARTRAK_HOST=0.0.0.0
ENV BEARTRAK_PRODUCTION_PORT=8080
ENV BEARTRAK_DEBUG=False
ENV BEARTRAK_PRODUCTION_DB=/data/beartrak.db

# Create volume for database persistence
VOLUME ["/app/data"]

# Expose port
EXPOSE 8080

# Run the application
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
