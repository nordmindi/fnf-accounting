# Test Data for Fire & Forget AI Accounting

This directory contains sample files for testing the document upload functionality.

## 📄 Sample Files

### Receipt Images
- `sample-receipt.jpg` - Restaurant receipt (representation meal)
- `sample-taxi.jpg` - Taxi receipt (transport expense)
- `sample-invoice.pdf` - Software subscription invoice

### Test Scenarios

#### 1. Representation Meal
- **File**: `sample-receipt.jpg`
- **Expected Intent**: `representation_meal`
- **Expected Policy**: `SE_REPR_MEAL_V1`
- **Expected Accounts**: 6071 (expense), 2641 (VAT), 1930 (cash)

#### 2. Taxi Transport
- **File**: `sample-taxi.jpg`
- **Expected Intent**: `taxi_transport`
- **Expected Policy**: `SE_TAXI_TRANSPORT_V1`
- **Expected Accounts**: 6540 (expense), 2640 (VAT), 1930 (cash)

#### 3. SaaS Subscription
- **File**: `sample-invoice.pdf`
- **Expected Intent**: `saas_subscription`
- **Expected Policy**: `SE_SAAS_SUBSCRIPTION_V1`
- **Expected Accounts**: 6541 (expense), 2640 (VAT), 1930 (cash)

## 🧪 How to Use

1. Import the Postman collection
2. Select the appropriate test scenario
3. Upload the corresponding sample file
4. Follow the complete workflow to test the pipeline

## 📝 Creating Your Own Test Files

When creating your own test files, ensure they contain:

### Receipt Requirements
- Clear vendor name
- Total amount
- Date
- VAT information (if applicable)
- Good image quality for OCR

### Invoice Requirements
- Vendor name
- Amount
- Service period
- Clear text for OCR processing

## 🔍 OCR Tips

For best OCR results:
- Use high-resolution images (300 DPI or higher)
- Ensure good contrast between text and background
- Avoid blurry or rotated images
- Use standard fonts when possible
- Include clear numerical amounts
