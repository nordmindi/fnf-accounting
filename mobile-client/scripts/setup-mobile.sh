#!/bin/bash

# Setup script for Fire & Forget Accounting Mobile Client
# This script ensures all dependencies are properly installed

echo "🔥 Setting up Fire & Forget Accounting Mobile Client..."

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: Please run this script from the mobile-client directory"
    exit 1
fi

# Clean install
echo "🧹 Cleaning previous installations..."
rm -rf node_modules package-lock.json

# Install dependencies with legacy peer deps
echo "📦 Installing dependencies..."
npm install --legacy-peer-deps

# Check if installation was successful
if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully!"
    echo ""
    echo "🚀 Next steps:"
    echo "1. Start the backend: python -m uvicorn src.app.main:app --reload"
    echo "2. Start the mobile client: npm start"
    echo "3. Scan QR code with Expo Go app"
    echo ""
    echo "📱 Test the NLP interface:"
    echo "- Enter: 'Business lunch with client at restaurant, 800 SEK'"
    echo "- Tap 'Submit Expense'"
    echo "- Watch the AI process and create the booking!"
else
    echo "❌ Installation failed. Please check the error messages above."
    exit 1
fi
