# Quick Postman Test Guide

## 🚀 Test Natural Language Processing in 5 Minutes

### Step 1: Start the Application
```bash
# Make sure you're in the project directory
cd C:\ws\ai\fnf-accounting

# Start the application
make up
make run
```

### Step 2: Import Postman Collection
1. Open Postman
2. Click **Import**
3. Select: `postman/Fire_Forget_AI_Accounting.postman_collection.json`
4. Import the environment: `postman/Fire_Forget_AI_Accounting_Environment.postman_environment.json`

### Step 3: Get Authentication Token
1. In Postman, go to **Authentication** folder
2. Run **"Create Test Token"**
3. Copy the `access_token` from the response
4. Set it in your environment variables (click the eye icon in top right)

### Step 4: Test Natural Language Processing
1. Go to **Natural Language Processing** folder
2. Run **"Business Lunch Example"**
3. Check the response - you should see:
   ```json
   {
     "success": true,
     "message": "✅ Booking created successfully!",
     "booking_id": "some-uuid",
     "status": "GREEN",
     "booking_details": {
       "debit_accounts": [...],
       "credit_accounts": [...],
       "vat_details": {...}
     }
   }
   ```

### Step 5: Try Other Examples
Run these requests in order:
1. **"Taxi Ride Example"**
2. **"SaaS Subscription Example"**
3. **"Office Supplies Example"**
4. **"Get Examples"**

### Step 6: Verify Bookings
1. Go to **Bookings** folder
2. Run **"List Bookings"** to see all created bookings
3. Use a `booking_id` from the response to run **"Get Booking"**

## 🎯 What You Should See

### Successful Response Example:
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

## 🔧 Troubleshooting

### If you get 401 Unauthorized:
- Make sure you ran "Create Test Token" first
- Check that `access_token` is set in environment variables

### If you get 500 Server Error:
- Check that the application is running (`make run`)
- Look at the console for error messages
- Make sure your `.env` file has `OPENAI_API_KEY` set

### If you get 400 Bad Request:
- Check that `company_id` is set in environment variables
- The collection should auto-generate this

## 🎨 Try Your Own Examples

Create a new request with your own natural language input:

**Method**: POST  
**URL**: `{{base_url}}/api/v1/natural-language/process`  
**Headers**: 
```
Authorization: Bearer {{access_token}}
Content-Type: application/json
```
**Body**:
```json
{
  "text": "Your custom expense description here",
  "company_id": "{{company_id}}"
}
```

### Example Custom Inputs:
- "Coffee meeting with client, 150 SEK"
- "Train ticket to Gothenburg, 450 SEK"
- "Office printer paper, 200 SEK"
- "Client dinner at fancy restaurant, 2000 SEK"

## 🎯 Expected Results

- **GREEN**: Automatic booking created
- **YELLOW**: Needs clarification (missing info)
- **RED**: Manual review required (unclear intent)

The system will automatically:
1. Parse your natural language input
2. Extract amount, vendor, purpose, etc.
3. Detect the business intent
4. Apply appropriate accounting rules
5. Calculate VAT correctly
6. Create proper journal entries
7. Provide detailed feedback

That's it! You should now have working natural language processing for accounting bookings! 🎉
