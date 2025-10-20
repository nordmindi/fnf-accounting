#!/bin/bash

# Test CI pipeline locally
# This script runs the same checks that GitHub Actions will run

set -e

echo "🚀 Testing CI pipeline locally..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

# Check Python version
echo "🐍 Checking Python version..."
python_version=$(python --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
if [[ "$python_version" == "3.12" ]]; then
    print_status "Python 3.12 detected"
else
    print_warning "Python $python_version detected (expected 3.12)"
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt
pip install -e .

# Run linting
echo "🔍 Running linting checks..."
echo "  - Running ruff..."
python -m ruff check src tests
print_status "Ruff checks passed"

echo "  - Running mypy..."
python -m mypy src
print_status "MyPy type checking passed"

echo "  - Running bandit..."
python -m bandit -r src
print_status "Bandit security checks passed"

echo "  - Running pip-audit..."
python -m pip_audit
print_status "Pip-audit security checks passed"

# Run formatting checks
echo "🎨 Checking code formatting..."
echo "  - Checking black formatting..."
python -m black --check src tests
print_status "Black formatting check passed"

echo "  - Checking isort imports..."
python -m isort --check-only src tests
print_status "Isort import sorting check passed"

# Run tests
echo "🧪 Running tests..."
pytest tests/ -v --cov=src --cov-report=term --cov-report=xml
print_status "All tests passed"

# Check if package builds
echo "📦 Checking package build..."
python -c "import src; print('Package imports successfully')"
print_status "Package build check passed"

# Run pre-commit hooks if available
if command -v pre-commit &> /dev/null; then
    echo "🪝 Running pre-commit hooks..."
    pre-commit run --all-files
    print_status "Pre-commit hooks passed"
else
    print_warning "Pre-commit not installed, skipping hooks"
fi

echo ""
print_status "🎉 All CI checks passed locally!"
echo ""
echo "Your code is ready for GitHub Actions! 🚀"
echo ""
echo "Next steps:"
echo "1. Commit your changes"
echo "2. Push to GitHub"
echo "3. Check the Actions tab for automated CI results"
