#!/bin/bash

# Fire & Forget AI Accounting - API Test Script
# Alternative to Postman for quick API testing

BASE_URL="http://localhost:8000"
COMPANY_ID="550e8400-e29b-41d4-a716-446655440000"
USER_ID="550e8400-e29b-41d4-a716-446655440001"

echo "🧪 Fire & Forget AI Accounting - API Test Script"
echo "================================================"

# Function to make HTTP requests with error handling
make_request() {
    local method=$1
    local url=$2
    local data=$3
    local description=$4
    
    echo ""
    echo "📡 $description"
    echo "   $method $url"
    
    if [ -n "$data" ]; then
        response=$(curl -s -w "\n%{http_code}" -X "$method" -H "Content-Type: application/json" -d "$data" "$url")
    else
        response=$(curl -s -w "\n%{http_code}" "$url")
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n -1)
    
    if [ "$http_code" -eq 200 ] || [ "$http_code" -eq 201 ]; then
        echo "   ✅ Success ($http_code)"
        echo "$body" | jq . 2>/dev/null || echo "$body"
    else
        echo "   ❌ Error ($http_code)"
        echo "$body"
    fi
}

# Test 1: Health Check
make_request "GET" "$BASE_URL/health" "" "Health Check"

# Test 2: Root Endpoint
make_request "GET" "$BASE_URL/" "" "Root Endpoint"

# Test 3: List Policies
make_request "GET" "$BASE_URL/api/v1/policies?country=SE" "" "List Policies (SE)"

# Test 4: List Documents
make_request "GET" "$BASE_URL/api/v1/documents?company_id=$COMPANY_ID&limit=10&offset=0" "" "List Documents"

# Test 5: List Pipelines
make_request "GET" "$BASE_URL/api/v1/pipelines?company_id=$COMPANY_ID&limit=10&offset=0" "" "List Pipelines"

# Test 6: List Bookings
make_request "GET" "$BASE_URL/api/v1/bookings?company_id=$COMPANY_ID&limit=10&offset=0" "" "List Bookings"

echo ""
echo "🎉 API Test Complete!"
echo ""
echo "📋 To test document upload:"
echo "   curl -X POST -F 'file=@path/to/receipt.jpg' -F 'company_id=$COMPANY_ID' -F 'user_id=$USER_ID' -F 'user_text=Business lunch' $BASE_URL/api/v1/documents/upload"
echo ""
echo "📚 For more comprehensive testing, use the Postman collection:"
echo "   make setup-postman"
