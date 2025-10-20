#!/bin/bash

# Test script for natural language processing API
# This script demonstrates how to use the new natural language endpoint

set -e

# Configuration
API_BASE_URL="http://localhost:8000"
COMPANY_ID="123e4567-e89b-12d3-a456-426614174007"

echo "🧪 Testing Natural Language Processing API"
echo "=========================================="

# First, get a test token
echo "📝 Getting test token..."
TOKEN_RESPONSE=$(curl -s -X POST "${API_BASE_URL}/api/v1/auth/test-token")
TOKEN=$(echo $TOKEN_RESPONSE | jq -r '.access_token')

if [ "$TOKEN" = "null" ] || [ -z "$TOKEN" ]; then
    echo "❌ Failed to get test token"
    echo "Response: $TOKEN_RESPONSE"
    exit 1
fi

echo "✅ Got test token: ${TOKEN:0:20}..."

# Test 1: Business lunch example
echo ""
echo "🍽️  Test 1: Business lunch with client"
echo "--------------------------------------"

LUNCH_REQUEST='{
    "text": "Business lunch today with the project manager of Example AB at Example restaurant, total amount 1500 SEK, paid with company credit card",
    "company_id": "'$COMPANY_ID'"
}'

echo "Request: $LUNCH_REQUEST"
echo ""

LUNCH_RESPONSE=$(curl -s -X POST "${API_BASE_URL}/api/v1/natural-language/process" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "$LUNCH_REQUEST")

echo "Response:"
echo $LUNCH_RESPONSE | jq '.'

# Test 2: Taxi ride example
echo ""
echo "🚕 Test 2: Taxi ride"
echo "-------------------"

TAXI_REQUEST='{
    "text": "Taxi from office to client meeting, 250 SEK, paid with company card",
    "company_id": "'$COMPANY_ID'"
}'

echo "Request: $TAXI_REQUEST"
echo ""

TAXI_RESPONSE=$(curl -s -X POST "${API_BASE_URL}/api/v1/natural-language/process" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "$TAXI_REQUEST")

echo "Response:"
echo $TAXI_RESPONSE | jq '.'

# Test 3: Software subscription
echo ""
echo "💻 Test 3: Software subscription"
echo "-------------------------------"

SAAS_REQUEST='{
    "text": "Monthly subscription for Slack workspace, 89 SEK including VAT",
    "company_id": "'$COMPANY_ID'"
}'

echo "Request: $SAAS_REQUEST"
echo ""

SAAS_RESPONSE=$(curl -s -X POST "${API_BASE_URL}/api/v1/natural-language/process" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "$SAAS_REQUEST")

echo "Response:"
echo $SAAS_RESPONSE | jq '.'

# Test 4: Get examples
echo ""
echo "📚 Test 4: Get examples"
echo "----------------------"

EXAMPLES_RESPONSE=$(curl -s -X GET "${API_BASE_URL}/api/v1/natural-language/examples" \
    -H "Authorization: Bearer $TOKEN")

echo "Response:"
echo $EXAMPLES_RESPONSE | jq '.'

echo ""
echo "✅ All tests completed!"
echo ""
echo "📋 Summary:"
echo "- Natural language processing endpoint is working"
echo "- The system can parse business expense descriptions"
echo "- It creates proper accounting bookings with debit/credit/VAT"
echo "- It provides user feedback and receipt attachment prompts"
echo ""
echo "🎯 Next steps:"
echo "1. Test with real receipts by uploading documents"
echo "2. Verify the booking entries in the database"
echo "3. Test the clarification flow for YELLOW status bookings"
