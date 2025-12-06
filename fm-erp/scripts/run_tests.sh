#!/bin/bash

set -e

echo "🧪 Running FM-ERP Test Suite"
echo "============================"

# Run unit tests (fast)
echo "1️⃣  Running unit tests..."
pytest tests/unit -v -m "unit" --cov=fm_erp --cov-report=html:htmlcov/unit

# Run integration tests (requires Docker)
echo "2️⃣  Running integration tests..."
pytest tests/integration -v -m "integration" --cov=fm_erp --cov-append --cov-report=html:htmlcov/integration

# Run system tests (slow)
echo "3️⃣  Running system tests..."
pytest tests/system -v -m "system and not slow" --cov=fm_erp --cov-append --cov-report=html:htmlcov/system

# Run property-based tests
echo "4️⃣  Running property-based tests..."
pytest tests/property -v --cov=fm_erp --cov-append --cov-report=html:htmlcov/property

# Generate combined coverage report
echo "📊 Generating coverage report..."
pytest --cov=fm_erp --cov-report=html:htmlcov/combined --cov-report=term-missing --cov-fail-under=85

# Performance benchmarks (optional)
if [ "$RUN_BENCHMARKS" = "true" ]; then
    echo "⚡ Running performance benchmarks..."
    locust -f tests/performance/test_scalability.py --headless -u 100 -r 10 -t 60s
fi

echo "✅ All tests passed!"
echo "📈 Coverage report: htmlcov/combined/index.html"
