# Postman Testing Guide for Natural Language Processing

## 🚀 Quick Start

### 1. Import the Collection
1. Open Postman
2. Click **Import** button
3. Select the file: `postman/Fire_Forget_AI_Accounting.postman_collection.json`
4. Import the environment file: `postman/Fire_Forget_AI_Accounting_Environment.postman_environment.json`

### 2. Set Up Environment Variables
The collection uses these variables:
- `base_url`: `http://localhost:8000` (default)
- `company_id`: Auto-generated UUID
- `user_id`: Auto-generated UUID
- `access_token`: JWT token for authentication

### 3. Start the Application
```bash
# Make sure the application is running
make up
make run
```

## 🧪 Testing Natural Language Processing

### Step 1: Get Authentication Token

**Request**: `POST /api/v1/auth/test-token`
- **Method**: POST
- **URL**: `{{base_url}}/api/v1/auth/test-token`
- **Headers**: None required
- **Body**: None

**Expected Response**:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

**Postman Setup**:
1. Go to the **Authentication** folder
2. Run **"Create Test Token"**
3. Copy the `access_token` from the response
4. Set it in your environment variables

### Step 2: Test Natural Language Processing

#### 🍽️ Business Lunch Example

**Request**: `POST /api/v1/natural-language/process`
- **Method**: POST
- **URL**: `{{base_url}}/api/v1/natural-language/process`
- **Headers**:
  ```
  Authorization: Bearer {{access_token}}
  Content-Type: application/json
  ```
- **Body** (raw JSON):
  ```json
  {
    "text": "Business lunch today with the project manager of Example AB at Example restaurant, total amount 1500 SEK, paid with company credit card",
    "company_id": "{{company_id}}"
  }
  ```

**Expected Response**:
```json
{
  "success": true,
  "message": "✅ Booking created successfully! Representation meal expense of 1500.00 SEK has been automatically booked.",
  "booking_id": "550e8400-e29b-41d4-a716-446655440000",
  "booking_details": {
    "debit_accounts": [
      {
        "account": "6071",
        "amount": 1200.0,
        "description": "Representation meals"
      },
      {
        "account": "2641",
        "amount": 300.0,
        "description": "VAT on representation"
      }
    ],
    "credit_accounts": [
      {
        "account": "1930",
        "amount": 1500.0,
        "description": "Cash/Bank"
      }
    ],
    "vat_details": {
      "code": "12",
      "rate": "12%"
    },
    "total_amount": 1500.0,
    "currency": "SEK"
  },
  "status": "GREEN",
  "reason_codes": [
    "Policy: SE_REPR_MEAL_V1",
    "Intent: representation_meal (confidence: 0.95)",
    "VAT: 12"
  ],
  "policy_used": "SE_REPR_MEAL_V1",
  "receipt_attachment_prompt": "Would you like to attach a receipt for this booking?"
}
```

#### 🚕 Taxi Ride Example

**Request**: `POST /api/v1/natural-language/process`
- **Body**:
  ```json
  {
    "text": "Taxi from office to client meeting at Arlanda Airport, 350 SEK, paid with company card",
    "company_id": "{{company_id}}"
  }
  ```

**Expected Response**:
```json
{
  "success": true,
  "message": "✅ Booking created successfully! Taxi transport expense of 350.00 SEK has been automatically booked.",
  "booking_id": "550e8400-e29b-41d4-a716-446655440001",
  "booking_details": {
    "debit_accounts": [
      {
        "account": "6540",
        "amount": 280.0,
        "description": "Transport expenses"
      },
      {
        "account": "2640",
        "amount": 70.0,
        "description": "VAT on transport"
      }
    ],
    "credit_accounts": [
      {
        "account": "1930",
        "amount": 350.0,
        "description": "Cash/Bank"
      }
    ],
    "vat_details": {
      "code": "25",
      "rate": "25%"
    },
    "total_amount": 350.0,
    "currency": "SEK"
  },
  "status": "GREEN",
  "reason_codes": [
    "Policy: SE_TAXI_TRANSPORT_V1",
    "Intent: taxi_transport (confidence: 0.92)",
    "VAT: 25"
  ],
  "policy_used": "SE_TAXI_TRANSPORT_V1",
  "receipt_attachment_prompt": "Would you like to attach a receipt for this booking?"
}
```

#### 💻 SaaS Subscription Example

**Request**: `POST /api/v1/natural-language/process`
- **Body**:
  ```json
  {
    "text": "Monthly subscription for Slack workspace, 89 SEK including VAT, paid with company credit card",
    "company_id": "{{company_id}}"
  }
  ```

#### 📦 Office Supplies Example

**Request**: `POST /api/v1/natural-language/process`
- **Body**:
  ```json
  {
    "text": "Office supplies from IKEA, pens and notebooks for the office, 450 SEK including VAT",
    "company_id": "{{company_id}}"
  }
  ```

### Step 3: Get Examples

**Request**: `GET /api/v1/natural-language/examples`
- **Method**: GET
- **URL**: `{{base_url}}/api/v1/natural-language/examples`
- **Headers**: `Authorization: Bearer {{access_token}}`

**Expected Response**:
```json
{
  "examples": [
    {
      "description": "Business lunch with client",
      "text": "Business lunch today with the project manager of Example AB at Example restaurant, total amount 1500 SEK, paid with company credit card"
    },
    {
      "description": "Taxi ride",
      "text": "Taxi from office to client meeting, 250 SEK, paid with company card"
    },
    {
      "description": "Software subscription",
      "text": "Monthly subscription for Slack workspace, 89 SEK including VAT"
    },
    {
      "description": "Office supplies",
      "text": "Office supplies from IKEA, pens and notebooks, 450 SEK"
    }
  ]
}
```

### Step 4: Verify Bookings

After creating bookings, you can verify them:

**Request**: `GET /api/v1/bookings/{{booking_id}}`
- **Method**: GET
- **URL**: `{{base_url}}/api/v1/bookings/{{booking_id}}`
- **Headers**: `Authorization: Bearer {{access_token}}`

**Request**: `GET /api/v1/bookings?company_id={{company_id}}`
- **Method**: GET
- **URL**: `{{base_url}}/api/v1/bookings?company_id={{company_id}}&limit=10`
- **Headers**: `Authorization: Bearer {{access_token}}`

## 🎯 Using the Postman Collection

### Pre-configured Requests

The collection includes these ready-to-use requests:

1. **Process Natural Language Input** - Main endpoint with example
2. **Business Lunch Example** - Pre-configured business lunch scenario
3. **Taxi Ride Example** - Pre-configured taxi transport scenario
4. **SaaS Subscription Example** - Pre-configured software subscription
5. **Office Supplies Example** - Pre-configured office supplies
6. **Get Examples** - Retrieve example inputs
7. **Provide Clarification** - Handle YELLOW status bookings

### Environment Variables

The collection automatically manages these variables:
- `company_id` - Auto-generated UUID for your test company
- `user_id` - Auto-generated UUID for your test user
- `access_token` - JWT token for authentication
- `booking_id` - Auto-extracted from natural language responses

### Test Scripts

The collection includes automatic test scripts that:
- Extract `booking_id` from natural language responses
- Set environment variables automatically
- Validate response structure

## 🔧 Troubleshooting

### Common Issues

#### 1. Authentication Error (401)
```
{
  "detail": "Invalid or missing authentication token"
}
```
**Solution**: 
- Make sure you've run the "Create Test Token" request first
- Check that `access_token` is set in environment variables
- Verify the token hasn't expired (default: 1 hour)

#### 2. Company ID Error (400)
```
{
  "detail": "Invalid company_id format"
}
```
**Solution**:
- Make sure `company_id` is a valid UUID
- The collection auto-generates this, but you can set it manually

#### 3. Server Error (500)
```
{
  "detail": "Failed to process natural language input: [error details]"
}
```
**Solution**:
- Check that the application is running (`make run`)
- Verify database is accessible
- Check application logs for detailed error information

#### 4. LLM Service Error
If you get errors related to OpenAI API:
- Check your `.env` file has `OPENAI_API_KEY` set
- Verify the API key is valid and has credits
- The system will fall back to rule-based parsing if LLM fails

### Debug Steps

1. **Check Health**: Run `GET /health` to verify the API is running
2. **Check Status**: Run `GET /status` to see system metrics
3. **Test Authentication**: Run `POST /api/v1/auth/test-token`
4. **Check Logs**: Look at the application console for detailed error messages

## 📊 Expected Results

### Successful GREEN Status
- `success: true`
- `status: "GREEN"`
- `booking_id` is present
- Detailed booking information with debit/credit accounts
- VAT calculations are correct
- Policy information is included

### YELLOW Status (Requires Clarification)
- `success: true`
- `status: "YELLOW"`
- `booking_id` may be null
- `reason_codes` indicate what information is missing
- Use the clarification endpoint to provide additional info

### RED Status (Manual Review Required)
- `success: true`
- `status: "RED"`
- `booking_id` is null
- `reason_codes` explain why manual review is needed
- No automatic booking was created

## 🎨 Customizing Tests

### Creating Your Own Examples

1. Copy an existing request
2. Modify the `text` field in the request body
3. Update the description
4. Test with your custom input

### Testing Different Scenarios

Try these variations:
- Different amounts and currencies
- Various vendor names
- Different business purposes
- Multiple attendees for meals
- Different payment methods
- Missing information (to test YELLOW/RED status)

### Example Custom Requests

```json
// High-value transaction (should trigger YELLOW)
{
  "text": "Business dinner with 5 clients at expensive restaurant, 5000 SEK",
  "company_id": "{{company_id}}"
}

// Missing information (should trigger YELLOW)
{
  "text": "Business lunch, 800 SEK",
  "company_id": "{{company_id}}"
}

// Unclear intent (should trigger RED)
{
  "text": "Some expense, 100 SEK",
  "company_id": "{{company_id}}"
}
```

## 🚀 Advanced Testing

### Batch Testing
Create a collection runner to test multiple scenarios:
1. Go to **Collections** → **Run**
2. Select the Natural Language Processing folder
3. Configure iterations and delays
4. Run all examples automatically

### Performance Testing
- Test with multiple concurrent requests
- Monitor response times
- Check for rate limiting

### Integration Testing
- Test the complete flow: natural language → booking → verification
- Test with real receipt uploads combined with natural language
- Verify audit trails and compliance

This guide should help you thoroughly test the natural language processing functionality using Postman!
