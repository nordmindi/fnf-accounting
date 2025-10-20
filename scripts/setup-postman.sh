#!/bin/bash

echo "🚀 Setting up Postman Collection for Fire & Forget AI Accounting"
echo "=============================================================="

# Check if Postman is installed
if ! command -v postman &> /dev/null; then
    echo "⚠️  Postman CLI not found. Please install Postman CLI or import manually."
    echo "   Download from: https://www.postman.com/downloads/"
fi

# Check if collection files exist
if [ ! -f "postman/Fire_Forget_AI_Accounting.postman_collection.json" ]; then
    echo "❌ Collection file not found!"
    exit 1
fi

if [ ! -f "postman/Fire_Forget_AI_Accounting_Environment.postman_environment.json" ]; then
    echo "❌ Environment file not found!"
    exit 1
fi

echo "✅ Collection files found"

# Check if API is running
echo "🔍 Checking if API is running..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ API is running at http://localhost:8000"
else
    echo "⚠️  API is not running. Please start it with: make up"
    echo "   Then run this script again."
    exit 1
fi

echo ""
echo "📋 Next Steps:"
echo "1. Open Postman"
echo "2. Click 'Import' button"
echo "3. Import these files:"
echo "   - postman/Fire_Forget_AI_Accounting.postman_collection.json"
echo "   - postman/Fire_Forget_AI_Accounting_Environment.postman_environment.json"
echo "4. Select 'Fire & Forget AI Accounting - Local Development' environment"
echo "5. Start testing with the 'Health Check' request"
echo ""
echo "📚 Documentation: postman/README.md"
echo "🧪 Test data: postman/test-data/"
echo ""
echo "🎉 Setup complete! Happy testing!"
