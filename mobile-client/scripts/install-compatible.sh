#!/bin/bash

# Install compatible versions for Fire & Forget Accounting Mobile Client
# This script uses Expo SDK 54 with React Native 0.76.3 for better compatibility

echo "🔥 Installing compatible versions for Fire & Forget Accounting Mobile Client..."

# Clean previous installation
echo "🧹 Cleaning previous installation..."
rm -rf node_modules package-lock.json

# Install with specific versions
echo "📦 Installing dependencies with compatible versions..."
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
    echo "📱 This setup uses:"
    echo "- Expo SDK 54"
    echo "- React Native 0.76.3"
    echo "- React 18.3.1"
    echo "- Compatible Metro bundler"
else
    echo "❌ Installation failed. Please check the error messages above."
    exit 1
fi
