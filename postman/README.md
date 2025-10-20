# Fire & Forget AI Accounting - Postman Collection

This directory contains a comprehensive Postman collection for testing the Fire & Forget AI Accounting API.

## 📁 Files

- `Fire_Forget_AI_Accounting.postman_collection.json` - Main API collection
- `Fire_Forget_AI_Accounting_Environment.postman_environment.json` - Environment variables
- `README.md` - This documentation

## 🚀 Quick Setup

### 1. Import Collection and Environment

1. Open Postman
2. Click **Import** button
3. Import both files:
   - `Fire_Forget_AI_Accounting.postman_collection.json`
   - `Fire_Forget_AI_Accounting_Environment.postman_environment.json`

### 2. Select Environment

1. In Postman, select the **"Fire & Forget AI Accounting - Local Development"** environment from the dropdown
2. Verify the `base_url` is set to `http://localhost:8000`

### 3. Start the Application

Make sure the Fire & Forget AI Accounting application is running:

```bash
# Start all services
make up

# Check status
docker-compose ps

# View logs if needed
make logs
```

## 📋 Collection Structure

### Health & Status
- **Health Check** - Verify API is running
- **Root Endpoint** - Get API information

### Documents
- **Upload Document** - Upload receipts/invoices and start processing
- **Get Document** - Retrieve document details
- **List Documents** - List all documents for a company

### Pipelines
- **Start Pipeline** - Manually start document processing
- **Get Pipeline Status** - Check processing progress
- **List Pipelines** - View all pipeline runs

### Bookings
- **Get Booking** - Retrieve journal entry details
- **List Bookings** - List all journal entries

### Policies
- **List Policies** - View active accounting policies
- **Get Policy** - Get specific policy details

### Test Scenarios
Complete end-to-end workflows for MVP scenarios:

#### 1. Representation Meal Flow
1. Upload restaurant receipt
2. Check pipeline status
3. Get booking result

#### 2. Taxi Transport Flow
1. Upload taxi receipt
2. Check pipeline status

#### 3. SaaS Subscription Flow
1. Upload subscription invoice
2. Check pipeline status

## 🔧 Environment Variables

The collection uses these environment variables:

| Variable | Description | Example Value |
|----------|-------------|---------------|
| `base_url` | API base URL | `http://localhost:8000` |
| `company_id` | Company UUID | `550e8400-e29b-41d4-a716-446655440000` |
| `user_id` | User UUID | `550e8400-e29b-41d4-a716-446655440001` |
| `document_id` | Auto-populated from upload response | - |
| `pipeline_run_id` | Auto-populated from pipeline response | - |
| `booking_id` | Auto-populated from booking response | - |

## 🧪 Testing Workflow

### Basic API Test
1. Run **Health Check** to verify API is running
2. Run **Root Endpoint** to get API information

### Document Processing Test
1. **Upload Document** with a sample receipt file
2. Note the `document_id` and `pipeline_run_id` from the response
3. **Get Pipeline Status** to check processing progress
4. **Get Booking** to see the final journal entry (if successful)

### Policy Testing
1. **List Policies** to see available accounting policies
2. **Get Policy** to examine specific policy details

## 📄 Sample Files for Testing

For testing document upload, you can use any image or PDF file. The system will attempt to extract text using OCR. Here are some suggestions:

### Representation Meal Receipt
- Restaurant receipt with total amount
- Should contain vendor name, date, and amount
- Example: "Restaurant ABC, Total: 1250.00 SEK, Date: 2024-01-15"

### Taxi Receipt
- Taxi receipt with fare amount
- Should contain taxi company name and amount
- Example: "Taxi Stockholm, Fare: 150.00 SEK"

### SaaS Invoice
- Software subscription invoice
- Should contain vendor name, amount, and period
- Example: "Microsoft 365, Monthly: 89.00 SEK"

## 🔍 Response Examples

### Successful Document Upload
```json
{
  "document_id": "550e8400-e29b-41d4-a716-446655440002",
  "pipeline_run_id": "550e8400-e29b-41d4-a716-446655440003",
  "status": "uploaded"
}
```

### Pipeline Status
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440003",
  "document_id": "550e8400-e29b-41d4-a716-446655440002",
  "status": "completed",
  "current_step": "completed",
  "started_at": "2024-01-15T10:30:00Z",
  "completed_at": "2024-01-15T10:30:15Z"
}
```

### Booking Result
```json
{
  "journal_entry": {
    "id": "550e8400-e29b-41d4-a716-446655440004",
    "posting_date": "2024-01-15",
    "series": "AI",
    "number": "000001",
    "notes": "AI booking: representation_meal - Restaurant ABC"
  },
  "receipt": {
    "total": "1250.00",
    "currency": "SEK",
    "vendor": "Restaurant ABC",
    "receipt_date": "2024-01-15",
    "confidence": 0.9
  },
  "intent": {
    "name": "representation_meal",
    "confidence": 0.9,
    "slots": {
      "attendees_count": 3,
      "purpose": "Business lunch with client"
    }
  },
  "proposal": {
    "lines": [
      {
        "account": "6071",
        "side": "D",
        "amount": "900.00",
        "description": "Representation meals"
      },
      {
        "account": "2641",
        "side": "D",
        "amount": "108.00",
        "description": "VAT on representation"
      },
      {
        "account": "1930",
        "side": "K",
        "amount": "1008.00",
        "description": "Cash/Bank"
      }
    ],
    "vat_code": "12",
    "confidence": 0.9,
    "reason_codes": ["Policy: SE_REPR_MEAL_V1", "VAT cap applied"],
    "stoplight": "GREEN",
    "policy_id": "SE_REPR_MEAL_V1"
  }
}
```

## 🐛 Troubleshooting

### API Not Responding
1. Check if the application is running: `docker-compose ps`
2. Check application logs: `make logs`
3. Verify the `base_url` in environment variables

### Upload Fails
1. Ensure the file is a valid image or PDF
2. Check file size (should be reasonable for testing)
3. Verify all required form fields are filled

### Pipeline Stuck
1. Check pipeline status endpoint
2. Look at application logs for errors
3. Verify all services are healthy: `docker-compose ps`

### No Policies Found
1. Check if policies are loaded in the database
2. Verify the country parameter (SE, NO, DK, FI)
3. Check policy files in `src/rules/policies/`

## 📚 Additional Resources

- [API Documentation](http://localhost:8000/docs) - Interactive Swagger UI
- [Application Logs](http://localhost:8000/health) - Health check endpoint
- [Project README](../README.md) - Main project documentation

## 🔄 Auto-Population Features

The collection includes automatic features:

1. **Auto-Generate UUIDs**: Company and user IDs are auto-generated if not set
2. **Auto-Extract IDs**: Document, pipeline, and booking IDs are automatically extracted from responses
3. **Environment Sync**: Variables are automatically updated between requests

This makes testing seamless - just run the requests in sequence and the collection handles the ID management automatically!
