#!/bin/bash

# Upgrade Fire & Forget Accounting Mobile Client to Expo SDK 54
# This script handles the complete upgrade process

echo "🚀 Upgrading Fire & Forget Accounting Mobile Client to Expo SDK 54..."

# Navigate to mobile-client directory
cd "$(dirname "$0")/.."

# Clean previous installation
echo "🧹 Cleaning previous installation..."
rm -rf node_modules package-lock.json

# Install Expo CLI globally if not already installed
echo "📦 Ensuring Expo CLI is installed..."
npm install -g @expo/cli

# Install the new Expo SDK
echo "⬆️ Installing Expo SDK 54..."
npm install expo@~54.0.0

# Install compatible dependencies
echo "🔧 Installing compatible dependen cies..."
npx expo install --fix

# Update React and React Native to compatible versions
echo "⚛️ Updating React and React Native..."
npm install react@18.3.1 react-native@0.76.3

# Install other dependencies with legacy peer deps for compatibility
echo "📦 Installing remaining dependencies..."
npm install --legacy-peer-deps

# Check if installation was successful
if [ $? -eq 0 ]; then
    echo "✅ Upgrade completed successfully!"
    echo ""
    echo "🚀 Next steps:"
    echo "1. Start the backend: python -m uvicorn src.app.main:app --reload"
    echo "2. Start the mobile client: npm start"
    echo "3. Scan QR code with Expo Go app (SDK 54 compatible)"
    echo ""
    echo "📱 This setup now uses:"
    echo "- Expo SDK 54"
    echo "- React Native 0.76.3"
    echo "- React 18.3.1"
    echo "- Compatible Metro bundler"
    echo ""
    echo "⚠️  Important notes:"
    echo "- Your Expo Go app should now be compatible"
    echo "- If you have native code, you may need to run 'npx expo prebuild'"
    echo "- Check the Expo SDK 54 release notes for any breaking changes"
else
    echo "❌ Upgrade failed. Please check the error messages above."
    echo "You may need to manually resolve dependency conflicts."
    exit 1
fi
