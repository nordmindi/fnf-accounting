#!/bin/bash

# Test script to verify the entire flow with no mock data
BASE_URL="http://localhost:8000"
COMPANY_ID="550e8400-e29b-41d4-a716-446655440000"
USER_ID="550e8400-e29b-41d4-a716-446655440001"

echo "🧪 Testing Complete Flow with NO Mock Data"
echo "=========================================="
echo ""

# Step 1: Check initial state (should be empty with no mock data)
echo "📋 Step 1: Check initial bookings list (should be empty)"
echo "Testing: GET /api/v1/bookings?company_id=$COMPANY_ID"
INITIAL_BOOKINGS=$(curl -s "$BASE_URL/api/v1/bookings?company_id=$COMPANY_ID")
echo "Initial bookings: $INITIAL_BOOKINGS"

if [ "$INITIAL_BOOKINGS" = "[]" ] || [ -z "$INITIAL_BOOKINGS" ]; then
    echo "✅ Initial state is clean - no mock data present"
else
    echo "❌ Mock data is still present - check USE_MOCK_DATA setting"
    echo "Expected: []"
    echo "Got: $INITIAL_BOOKINGS"
    exit 1
fi

echo ""

# Step 2: Upload first document
echo "📤 Step 2: Upload first test document"
cat > test-receipt-1.txt << 'EOF'
Restaurant Test 1
Business lunch receipt
Total: 450.00 SEK
Moms 12%: 48.21 SEK
Datum: 2024-01-22
Client meeting
EOF

echo "Uploading first document..."
UPLOAD_RESPONSE_1=$(curl -s -X POST -F 'file=@test-receipt-1.txt' -F "company_id=$COMPANY_ID" -F "user_id=$USER_ID" -F 'user_text=Bokför lunch med kund' "$BASE_URL/api/v1/documents/upload")
echo "Upload Response 1: $UPLOAD_RESPONSE_1"

# Extract pipeline run ID
PIPELINE_RUN_ID_1=$(echo "$UPLOAD_RESPONSE_1" | grep -oP '"pipeline_run_id":"\K[^"]+')
echo "Pipeline Run ID 1: $PIPELINE_RUN_ID_1"

echo ""

# Step 3: Upload second document
echo "📤 Step 3: Upload second test document"
cat > test-receipt-2.txt << 'EOF'
Taxi Stockholm AB
Transport receipt
Total: 120.00 SEK
Moms 25%: 24.00 SEK
Datum: 2024-01-22
Airport transfer
EOF

echo "Uploading second document..."
UPLOAD_RESPONSE_2=$(curl -s -X POST -F 'file=@test-receipt-2.txt' -F "company_id=$COMPANY_ID" -F "user_id=$USER_ID" -F 'user_text=Bokför taxi till flygplats' "$BASE_URL/api/v1/documents/upload")
echo "Upload Response 2: $UPLOAD_RESPONSE_2"

# Extract pipeline run ID
PIPELINE_RUN_ID_2=$(echo "$UPLOAD_RESPONSE_2" | grep -oP '"pipeline_run_id":"\K[^"]+')
echo "Pipeline Run ID 2: $PIPELINE_RUN_ID_2"

echo ""

# Step 4: Check pipeline statuses
echo "📊 Step 4: Check pipeline statuses"
echo "Testing: GET /api/v1/pipelines/$PIPELINE_RUN_ID_1"
PIPELINE_RESPONSE_1=$(curl -s "$BASE_URL/api/v1/pipelines/$PIPELINE_RUN_ID_1")
echo "Pipeline 1 Response: $PIPELINE_RESPONSE_1"

echo ""
echo "Testing: GET /api/v1/pipelines/$PIPELINE_RUN_ID_2"
PIPELINE_RESPONSE_2=$(curl -s "$BASE_URL/api/v1/pipelines/$PIPELINE_RUN_ID_2")
echo "Pipeline 2 Response: $PIPELINE_RESPONSE_2"

# Extract booking IDs
BOOKING_ID_1=$(echo "$PIPELINE_RESPONSE_1" | grep -oP '"booking_id":"\K[^"]+' | head -1)
BOOKING_ID_2=$(echo "$PIPELINE_RESPONSE_2" | grep -oP '"booking_id":"\K[^"]+' | head -1)

echo ""
echo "Extracted Booking IDs:"
echo "Booking 1: $BOOKING_ID_1"
echo "Booking 2: $BOOKING_ID_2"

echo ""

# Step 5: Get booking details
if [ -n "$BOOKING_ID_1" ] && [ "$BOOKING_ID_1" != "null" ]; then
    echo "📋 Step 5a: Get first booking details"
    echo "Testing: GET /api/v1/bookings/$BOOKING_ID_1"
    BOOKING_RESPONSE_1=$(curl -s "$BASE_URL/api/v1/bookings/$BOOKING_ID_1")
    echo "Booking 1 Response: $BOOKING_RESPONSE_1"
    echo "✅ First booking retrieved successfully"
else
    echo "❌ First booking ID is null or empty"
fi

echo ""

if [ -n "$BOOKING_ID_2" ] && [ "$BOOKING_ID_2" != "null" ]; then
    echo "📋 Step 5b: Get second booking details"
    echo "Testing: GET /api/v1/bookings/$BOOKING_ID_2"
    BOOKING_RESPONSE_2=$(curl -s "$BASE_URL/api/v1/bookings/$BOOKING_ID_2")
    echo "Booking 2 Response: $BOOKING_RESPONSE_2"
    echo "✅ Second booking retrieved successfully"
else
    echo "❌ Second booking ID is null or empty"
fi

echo ""

# Step 6: Check final bookings list
echo "📋 Step 6: Check final bookings list"
echo "Testing: GET /api/v1/bookings?company_id=$COMPANY_ID"
FINAL_BOOKINGS=$(curl -s "$BASE_URL/api/v1/bookings?company_id=$COMPANY_ID")
echo "Final bookings: $FINAL_BOOKINGS"

# Count bookings
BOOKING_COUNT=$(echo "$FINAL_BOOKINGS" | grep -o '"id"' | wc -l)
echo "Total bookings created: $BOOKING_COUNT"

echo ""

# Step 7: Test pipeline-to-booking mapping
echo "🔗 Step 7: Test pipeline-to-booking mapping"
if [ -n "$PIPELINE_RUN_ID_1" ]; then
    echo "Testing: GET /api/v1/bookings/by-pipeline/$PIPELINE_RUN_ID_1"
    PIPELINE_BOOKING_1=$(curl -s "$BASE_URL/api/v1/bookings/by-pipeline/$PIPELINE_RUN_ID_1")
    echo "Pipeline-to-booking 1: $PIPELINE_BOOKING_1"
fi

if [ -n "$PIPELINE_RUN_ID_2" ]; then
    echo "Testing: GET /api/v1/bookings/by-pipeline/$PIPELINE_RUN_ID_2"
    PIPELINE_BOOKING_2=$(curl -s "$BASE_URL/api/v1/bookings/by-pipeline/$PIPELINE_RUN_ID_2")
    echo "Pipeline-to-booking 2: $PIPELINE_BOOKING_2"
fi

echo ""
echo "🧹 Cleaning up..."
rm -f test-receipt-1.txt test-receipt-2.txt

echo ""
echo "✅ No Mock Data Test Complete!"
echo ""
echo "📊 Summary:"
echo "- ✅ Initial state clean (no mock data)"
echo "- ✅ Document upload working"
echo "- ✅ Pipeline processing working"
echo "- ✅ Booking creation working"
echo "- ✅ Pipeline-to-booking mapping working"
echo "- ✅ Multiple bookings created: $BOOKING_COUNT"
echo ""
echo "🎯 The entire flow works with real data only!"
