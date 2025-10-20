#!/bin/bash

# Test script to verify content type fix
BASE_URL="http://localhost:8000"
COMPANY_ID="550e8400-e29b-41d4-a716-446655440000"
USER_ID="550e8400-e29b-41d4-a716-446655440001"

echo "🔧 Testing Content Type Fix"
echo "=========================="
echo ""

# Test 1: Upload a file without explicit content type
echo "📤 Test 1: Upload file without content type"
cat > test-no-content-type.txt << 'EOF'
Test Receipt
Total: 100.00 SEK
VAT: 25.00 SEK
Date: 2024-01-22
EOF

echo "Uploading file without content type..."
UPLOAD_RESPONSE=$(curl -s -X POST -F 'file=@test-no-content-type.txt' -F "company_id=$COMPANY_ID" -F "user_id=$USER_ID" -F 'user_text=Test upload' "$BASE_URL/api/v1/documents/upload")
echo "Upload Response: $UPLOAD_RESPONSE"

# Check if upload was successful
if echo "$UPLOAD_RESPONSE" | grep -q "document_id"; then
    echo "✅ Upload successful - content type fix working!"
else
    echo "❌ Upload failed - content type issue still exists"
    echo "Response: $UPLOAD_RESPONSE"
fi

echo ""
echo "🧹 Cleaning up..."
rm -f test-no-content-type.txt

echo ""
echo "✅ Content Type Fix Test Complete!"
