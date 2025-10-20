#!/bin/bash

# Script to toggle mock data on/off
ENV_FILE=".env"

echo "🔧 Mock Data Toggle Script"
echo "========================="
echo ""

# Check if .env file exists
if [ ! -f "$ENV_FILE" ]; then
    echo "❌ .env file not found. Creating from env.example..."
    cp env.example .env
    echo "✅ Created .env file from env.example"
fi

# Get current setting
CURRENT_SETTING=$(grep "^USE_MOCK_DATA=" "$ENV_FILE" 2>/dev/null | cut -d'=' -f2)

if [ -z "$CURRENT_SETTING" ]; then
    echo "❌ USE_MOCK_DATA not found in .env file"
    echo "Adding USE_MOCK_DATA=true to .env file..."
    echo "USE_MOCK_DATA=true" >> "$ENV_FILE"
    CURRENT_SETTING="true"
fi

echo "Current USE_MOCK_DATA setting: $CURRENT_SETTING"

# Toggle the setting
if [ "$CURRENT_SETTING" = "true" ]; then
    NEW_SETTING="false"
    echo "🔄 Switching to: $NEW_SETTING (no mock data)"
else
    NEW_SETTING="true"
    echo "🔄 Switching to: $NEW_SETTING (with mock data)"
fi

# Update the .env file
sed -i "s/^USE_MOCK_DATA=.*/USE_MOCK_DATA=$NEW_SETTING/" "$ENV_FILE"

echo "✅ Updated .env file"
echo ""
echo "📋 Current .env mock data settings:"
grep "USE_MOCK_DATA" "$ENV_FILE"

echo ""
echo "⚠️  Note: You need to restart the Docker services for changes to take effect:"
echo "   make down && make up"
echo ""
echo "🧪 To test with the new setting:"
if [ "$NEW_SETTING" = "false" ]; then
    echo "   make test-no-mock"
else
    echo "   make test-api"
fi
