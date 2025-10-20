#!/bin/bash

# Debug script to see what's happening in the pipeline
BASE_URL="http://localhost:8000"
COMPANY_ID="550e8400-e29b-41d4-a716-446655440000"
USER_ID="550e8400-e29b-41d4-a716-446655440001"

echo "🔍 Debug Pipeline Execution"
echo "=========================="
echo ""

# Create a simple test file
cat > debug-test.txt << 'EOF'
Restaurant Debug
Test kvitto
Total: 500.00 SEK
Moms 12%: 60.00 SEK
Datum: 2024-01-20
Test lunch med 2 personer
EOF

echo "📤 Uploading test document..."
UPLOAD_RESPONSE=$(curl -s -X POST -F 'file=@debug-test.txt' -F "company_id=$COMPANY_ID" -F "user_id=$USER_ID" -F 'user_text=Bokför det här kvittot för en företagslunch' "$BASE_URL/api/v1/documents/upload")
echo "Upload Response: $UPLOAD_RESPONSE"

# Extract pipeline_run_id
PIPELINE_RUN_ID=$(echo "$UPLOAD_RESPONSE" | grep -oP '"pipeline_run_id":"\K[^"]+')
echo "Pipeline Run ID: $PIPELINE_RUN_ID"

echo ""
echo "📊 Checking pipeline status..."
PIPELINE_STATUS=$(curl -s "$BASE_URL/api/v1/pipelines/$PIPELINE_RUN_ID")
echo "Pipeline Status: $PIPELINE_STATUS"

echo ""
echo "📋 Checking all bookings..."
ALL_BOOKINGS=$(curl -s "$BASE_URL/api/v1/bookings?company_id=$COMPANY_ID&limit=10")
echo "All Bookings: $ALL_BOOKINGS"

echo ""
echo "🔍 Checking specific booking by pipeline..."
BOOKING_BY_PIPELINE=$(curl -s "$BASE_URL/api/v1/bookings/by-pipeline/$PIPELINE_RUN_ID")
echo "Booking by Pipeline: $BOOKING_BY_PIPELINE"

echo ""
echo "🧹 Cleaning up..."
rm -f debug-test.txt

echo ""
echo "✅ Debug complete!"
