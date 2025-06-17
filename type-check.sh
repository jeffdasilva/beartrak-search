#!/bin/bash
# Type checking script

echo "🔍 Running mypy type checking..."
uv run mypy main.py test_api.py

if [ $? -eq 0 ]; then
    echo "✅ All type checks passed!"
else
    echo "❌ Type checking failed!"
    exit 1
fi
