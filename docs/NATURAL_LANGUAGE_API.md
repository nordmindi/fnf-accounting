# Natural Language Processing API

## Overview

The Natural Language Processing API allows users to create accounting bookings by simply describing expenses in natural language. Instead of filling out forms or uploading receipts, users can say things like:

> "Business lunch today with the project manager of Example AB at Example restaurant, total amount 1500 SEK, paid with company credit card"

The system will automatically:
1. Parse the natural language input
2. Extract relevant information (amount, vendor, purpose, etc.)
3. Detect the business intent (representation meal, taxi, SaaS subscription, etc.)
4. Apply appropriate accounting rules and VAT calculations
5. Create a proper journal entry with debit/credit accounts
6. Provide user feedback and ask for receipt attachment

## API Endpoints

### Process Natural Language Input

**POST** `/api/v1/natural-language/process`

Creates a booking from natural language input.

#### Request Body

```json
{
  "text": "Business lunch today with the project manager of Example AB at Example restaurant, total amount 1500 SEK, paid with company credit card",
  "company_id": "123e4567-e89b-12d3-a456-426614174007"
}
```

#### Response

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

### Provide Clarification

**POST** `/api/v1/natural-language/clarify`

Provides additional information for bookings that require clarification (YELLOW status).

#### Request Body

```json
{
  "booking_id": "550e8400-e29b-41d4-a716-446655440000",
  "clarification": "There were 3 people at the lunch meeting"
}
```

### Get Examples

**GET** `/api/v1/natural-language/examples`

Returns example natural language inputs for different types of expenses.

#### Response

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

## Supported Expense Types

The system recognizes and handles the following types of business expenses:

### 1. Representation Meals
- **Intent**: `representation_meal`
- **Policy**: `SE_REPR_MEAL_V1`
- **VAT**: 12% with 300 SEK cap per person
- **Accounts**: 6071 (expense), 2641 (VAT), 1930 (cash)

**Example**: "Business lunch with client at restaurant, 800 SEK"

### 2. Taxi Transport
- **Intent**: `taxi_transport`
- **Policy**: `SE_TAXI_TRANSPORT_V1`
- **VAT**: 25% standard rate
- **Accounts**: 6540 (expense), 2640 (VAT), 1930 (cash)

**Example**: "Taxi from office to airport, 350 SEK"

### 3. SaaS Subscriptions
- **Intent**: `saas_subscription`
- **Policy**: `SE_SAAS_SUBSCRIPTION_V1`
- **VAT**: 25% standard rate
- **Accounts**: 6541 (expense), 2640 (VAT), 1930 (cash)

**Example**: "Monthly Slack subscription, 89 SEK"

### 4. Office Supplies
- **Intent**: `office_supplies`
- **Policy**: `SE_OTHER_BUSINESS_V1`
- **VAT**: 25% standard rate
- **Accounts**: 6542 (expense), 2640 (VAT), 1930 (cash)

**Example**: "Office supplies from IKEA, 450 SEK"

## Stoplight System

The system uses a stoplight model to determine how to handle each booking:

### 🟢 GREEN - Auto-Book
- High confidence (>0.9)
- All required information present
- Policy rules satisfied
- **Action**: Automatically creates journal entry

### 🟡 YELLOW - Ask Clarification
- Medium confidence (0.5-0.9)
- Missing some required information
- **Action**: Asks one clarifying question

### 🔴 RED - Manual Review
- Low confidence (<0.5)
- No matching policy found
- **Action**: Requires human review

## Natural Language Parsing

The system can extract the following information from natural language:

### Required Information
- **Amount**: The total expense amount
- **Currency**: SEK, NOK, DKK, EUR, USD
- **Vendor**: Restaurant, company, or service name
- **Date**: Transaction date (defaults to today)

### Optional Information
- **Purpose**: Business purpose or description
- **Attendees Count**: Number of people (for meals)
- **Client**: Client name (for representation)
- **Project**: Project code or name
- **Payment Method**: How it was paid
- **Location**: Where the expense occurred

### Parsing Examples

**Input**: "Business lunch today with the project manager of Example AB at Example restaurant, total amount 1500 SEK, paid with company credit card"

**Parsed**:
```json
{
  "amount": 1500,
  "currency": "SEK",
  "vendor": "Example restaurant",
  "date": "2024-01-15",
  "purpose": "Business lunch with project manager",
  "attendees_count": 2,
  "client": "Example AB",
  "payment_method": "company credit card"
}
```

## Error Handling

### Common Errors

#### 400 Bad Request
```json
{
  "detail": "Invalid request format"
}
```

#### 401 Unauthorized
```json
{
  "detail": "Invalid or missing authentication token"
}
```

#### 500 Internal Server Error
```json
{
  "detail": "Failed to process natural language input: [error details]"
}
```

### Fallback Behavior

If the LLM-based parsing fails, the system falls back to rule-based parsing using regex patterns to extract:
- Amount and currency
- Vendor name
- Basic purpose
- Client information

## Usage Examples

### cURL Examples

#### Basic Business Lunch
```bash
curl -X POST "http://localhost:8000/api/v1/natural-language/process" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Business lunch with client at restaurant, 800 SEK",
    "company_id": "123e4567-e89b-12d3-a456-426614174007"
  }'
```

#### Taxi Ride
```bash
curl -X POST "http://localhost:8000/api/v1/natural-language/process" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Taxi from office to client meeting, 250 SEK",
    "company_id": "123e4567-e89b-12d3-a456-426614174007"
  }'
```

### Python Example

```python
import requests

# Get authentication token
token_response = requests.post("http://localhost:8000/api/v1/auth/test-token")
token = token_response.json()["access_token"]

# Process natural language input
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
data = {
    "text": "Business lunch today with the project manager of Example AB at Example restaurant, total amount 1500 SEK, paid with company credit card",
    "company_id": "123e4567-e89b-12d3-a456-426614174007"
}

response = requests.post(
    "http://localhost:8000/api/v1/natural-language/process",
    headers=headers,
    json=data
)

result = response.json()
print(f"Status: {result['status']}")
print(f"Message: {result['message']}")
if result['booking_id']:
    print(f"Booking ID: {result['booking_id']}")
```

## Testing

Use the provided test script to verify the functionality:

```bash
./scripts/test-natural-language.sh
```

This script will:
1. Get an authentication token
2. Test various natural language inputs
3. Display the responses
4. Show booking details and accounting entries

## Integration with Existing System

The natural language processing integrates seamlessly with the existing system:

1. **Uses existing policies**: Leverages the same rule engine and policies
2. **Creates standard journal entries**: Uses the same booking service
3. **Follows audit trail**: All bookings are logged and auditable
4. **Supports receipt attachment**: Can be combined with document upload
5. **Respects company isolation**: All bookings are company-specific

## Future Enhancements

Planned improvements include:

1. **Voice input support**: Integration with speech-to-text
2. **Multi-language support**: Swedish, Norwegian, Danish, Finnish
3. **Smart suggestions**: Learn from user corrections
4. **Batch processing**: Handle multiple expenses at once
5. **Mobile app integration**: Native mobile interface
6. **Advanced clarification**: Multi-step clarification flows
