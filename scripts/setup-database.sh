#!/bin/bash
# Setup database for Fire & Forget Accounting

set -e

echo "🚀 Setting up Fire & Forget Accounting Database..."

# Check if we're in the right directory
if [ ! -f "alembic.ini" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found. Please copy env.example to .env and configure it"
    exit 1
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

echo "📊 Running database migrations..."

# Run Alembic migrations
alembic upgrade head

echo "✅ Database migrations completed!"

echo "📋 Loading BAS 2025 v1.0 data..."

# Load BAS data
python scripts/load_bas_data.py

echo "✅ BAS data loaded successfully!"

echo "🎉 Database setup completed!"
echo ""
echo "Next steps:"
echo "1. Start the application: make run"
echo "2. Test the API: make test-api"
echo "3. Check the database: psql $DATABASE_URL"
