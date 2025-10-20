# Fire & Forget AI Accounting API Documentation

## Overview

The Fire & Forget AI Accounting API is a RESTful service that automates accounting processes from receipt upload to journal entry creation. The API provides comprehensive document processing, policy management, and accounting automation with Nordic compliance.

## Base URL

```
http://localhost:8000
```

## Authentication

The API uses JWT (JSON Web Token) authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

### Getting a Test Token

For development, you can create a test token:

```bash
curl -X POST "http://localhost:8000/api/v1/auth/test-token"
```

## API Endpoints

### Health & Status

#### GET /health
Basic health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "fireforget-accounting"
}
```

#### GET /health/detailed
Detailed system health with component status.

**Response:**
```json
{
  "status": "healthy",
  "service": "fireforget-accounting",
  "version": "0.1.0",
  "timestamp": "2024-01-01T12:00:00Z",
  "components": {
    "database": {
      "status": "healthy",
      "message": "Connected"
    },
    "storage": {
      "status": "healthy",
      "message": "Available"
    },
    "llm": {
      "status": "healthy",
      "message": "Available"
    }
  }
}
```

#### GET /status
System metrics and counts.

**Response:**
```json
{
  "status": "operational",
  "timestamp": "2024-01-01T12:00:00Z",
  "metrics": {
    "documents": 150,
    "journal_entries": 75,
    "pipeline_runs": 200,
    "policies": 3
  },
  "version": "0.1.0",
  "environment": "development"
}
```

### Authentication

#### POST /api/v1/auth/login
User authentication.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user_id": "123e4567-e89b-12d3-a456-426614174008",
  "company_id": "123e4567-e89b-12d3-a456-426614174007",
  "email": "user@example.com"
}
```

#### POST /api/v1/auth/refresh
Refresh access token.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

#### GET /api/v1/auth/me
Get current user information.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "user_id": "123e4567-e89b-12d3-a456-426614174008",
  "company_id": "123e4567-e89b-12d3-a456-426614174007",
  "email": "user@example.com",
  "roles": ["user", "admin"]
}
```

### Documents

#### POST /api/v1/documents/upload
Upload a document for processing.

**Headers:** `Authorization: Bearer <token>`

**Request Body (multipart/form-data):**
- `file`: Document file (PDF, JPEG, PNG)
- `company_id`: Company UUID
- `user_id`: User UUID (optional)
- `user_text`: Additional context (optional)

**Response:**
```json
{
  "document_id": "8fb1a796-8baf-4a10-a516-e2ade19938fe",
  "pipeline_run_id": "2dd75c08-6f40-4660-975e-939562afbed0",
  "status": "processing",
  "message": "Document uploaded and pipeline started"
}
```

#### GET /api/v1/documents
List documents for a company.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `company_id`: Company UUID (required)
- `limit`: Number of results (default: 50, max: 1000)
- `offset`: Number of results to skip (default: 0)

**Response:**
```json
[
  {
    "id": "8fb1a796-8baf-4a10-a516-e2ade19938fe",
    "filename": "receipt.jpg",
    "content_type": "image/jpeg",
    "size": 245760,
    "uploaded_at": "2024-01-01T12:00:00Z"
  }
]
```

#### GET /api/v1/documents/{document_id}
Get document details.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "id": "8fb1a796-8baf-4a10-a516-e2ade19938fe",
  "filename": "receipt.jpg",
  "content_type": "image/jpeg",
  "size": 245760,
  "uploaded_at": "2024-01-01T12:00:00Z"
}
```

#### GET /api/v1/documents/{document_id}/download
Download document content.

**Headers:** `Authorization: Bearer <token>`

**Response:** Binary file content with appropriate Content-Type and Content-Disposition headers.

### Pipelines

#### POST /api/v1/pipelines/start
Start document processing pipeline.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "document_id": "8fb1a796-8baf-4a10-a516-e2ade19938fe"
}
```

**Response:**
```json
{
  "id": "2dd75c08-6f40-4660-975e-939562afbed0",
  "document_id": "8fb1a796-8baf-4a10-a516-e2ade19938fe",
  "status": "running",
  "current_step": "load_document",
  "started_at": "2024-01-01T12:00:00Z",
  "completed_at": null,
  "error_message": null,
  "booking_id": null
}
```

#### GET /api/v1/pipelines/{run_id}
Get pipeline status.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "id": "2dd75c08-6f40-4660-975e-939562afbed0",
  "document_id": "8fb1a796-8baf-4a10-a516-e2ade19938fe",
  "status": "completed",
  "current_step": "completed",
  "started_at": "2024-01-01T12:00:00Z",
  "completed_at": "2024-01-01T12:01:30Z",
  "error_message": null,
  "booking_id": "550e8400-e29b-41d4-a716-446655440010"
}
```

#### GET /api/v1/pipelines
List pipeline runs for a company.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `company_id`: Company UUID (required)
- `limit`: Number of results (default: 50, max: 1000)
- `offset`: Number of results to skip (default: 0)

**Response:**
```json
[
  {
    "id": "2dd75c08-6f40-4660-975e-939562afbed0",
    "document_id": "8fb1a796-8baf-4a10-a516-e2ade19938fe",
    "status": "completed",
    "current_step": "completed",
    "started_at": "2024-01-01T12:00:00Z",
    "completed_at": "2024-01-01T12:01:30Z",
    "error_message": null,
    "booking_id": "550e8400-e29b-41d4-a716-446655440010"
  }
]
```

#### GET /api/v1/pipelines/{run_id}/debug
Get detailed pipeline debug information.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "id": "2dd75c08-6f40-4660-975e-939562afbed0",
  "document_id": "8fb1a796-8baf-4a10-a516-e2ade19938fe",
  "status": "completed",
  "current_step": "completed",
  "receipt_doc": {
    "vendor": "Restaurant ABC",
    "total": 450.00,
    "currency": "SEK",
    "date": "2024-01-01",
    "raw_text": "Restaurant ABC\nTotal: 450.00 SEK"
  },
  "intent": {
    "name": "representation_meal",
    "confidence": 0.95,
    "slots": {
      "attendees_count": 2,
      "purpose": "client_meeting"
    }
  },
  "proposal": {
    "lines": [
      {
        "account": "6071",
        "side": "D",
        "amount": 300.00,
        "description": "Representation meal"
      },
      {
        "account": "2641",
        "side": "D",
        "amount": 36.00,
        "description": "VAT on representation"
      },
      {
        "account": "1930",
        "side": "K",
        "amount": 336.00,
        "description": "Cash payment"
      }
    ],
    "vat_code": "12",
    "confidence": 0.95,
    "reason_codes": [],
    "stoplight": "GREEN",
    "policy_id": "SE_REPR_MEAL_V1"
  },
  "journal_entry_id": "550e8400-e29b-41d4-a716-446655440010",
  "started_at": "2024-01-01T12:00:00Z",
  "completed_at": "2024-01-01T12:01:30Z"
}
```

### Bookings (Journal Entries)

#### GET /api/v1/bookings/{booking_id}
Get journal entry details.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440010",
  "company_id": "123e4567-e89b-12d3-a456-426614174007",
  "date": "2024-01-01",
  "series": "AI",
  "number": "000001",
  "notes": "AI booking: representation_meal - Restaurant ABC",
  "created_at": "2024-01-01T12:01:30Z",
  "created_by": "123e4567-e89b-12d3-a456-426614174008",
  "lines": [
    {
      "id": "line-1",
      "account": "6071",
      "side": "D",
      "amount": 300.00,
      "dimension_project": null,
      "dimension_cost_center": null,
      "description": "Representation meal"
    },
    {
      "id": "line-2",
      "account": "2641",
      "side": "D",
      "amount": 36.00,
      "dimension_project": null,
      "dimension_cost_center": null,
      "description": "VAT on representation"
    },
    {
      "id": "line-3",
      "account": "1930",
      "side": "K",
      "amount": 336.00,
      "dimension_project": null,
      "dimension_cost_center": null,
      "description": "Cash payment"
    }
  ]
}
```

#### GET /api/v1/bookings
List journal entries for a company.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `company_id`: Company UUID (required)
- `limit`: Number of results (default: 50, max: 1000)
- `offset`: Number of results to skip (default: 0)

**Response:**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440010",
    "company_id": "123e4567-e89b-12d3-a456-426614174007",
    "date": "2024-01-01",
    "series": "AI",
    "number": "000001",
    "notes": "AI booking: representation_meal - Restaurant ABC",
    "created_at": "2024-01-01T12:01:30Z",
    "created_by": "123e4567-e89b-12d3-a456-426614174008",
    "lines": [...]
  }
]
```

### Policies

#### GET /api/v1/policies
List active policies for a country.

**Query Parameters:**
- `country`: Country code (default: "SE")

**Response:**
```json
[
  {
    "id": "SE_REPR_MEAL_V1",
    "version": "V1",
    "country": "SE",
    "effective_from": "2024-01-01",
    "effective_to": null,
    "name": "Swedish Representation Meal Policy",
    "description": "Policy for representation meals with 12% VAT and 300 SEK cap per person"
  }
]
```

#### GET /api/v1/policies/{policy_id}
Get policy details.

**Response:**
```json
{
  "id": "SE_REPR_MEAL_V1",
  "version": "V1",
  "country": "SE",
  "effective_from": "2024-01-01",
  "effective_to": null,
  "name": "Swedish Representation Meal Policy",
  "description": "Policy for representation meals with 12% VAT and 300 SEK cap per person"
}
```

#### POST /api/v1/policies
Create a new policy.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "id": "SE_NEW_POLICY_V1",
  "version": "V1",
  "country": "SE",
  "effective_from": "2024-01-01",
  "effective_to": null,
  "name": "New Swedish Policy",
  "description": "Description of the new policy",
  "rules": {
    "match": {
      "intent": "new_intent"
    },
    "posting": [
      {
        "account": "6071",
        "side": "D",
        "amount": "net_amount"
      }
    ]
  }
}
```

#### PUT /api/v1/policies/{policy_id}
Update an existing policy.

**Headers:** `Authorization: Bearer <token>`

**Request Body:** Same as POST, with fields to update.

## Error Responses

All error responses follow a consistent format:

```json
{
  "message": "Error description",
  "error_code": "ERROR_CODE",
  "details": {
    "field": "additional_error_info"
  }
}
```

### Common Error Codes

- `VALIDATION_ERROR`: Input validation failed
- `DOCUMENT_NOT_FOUND`: Document not found
- `PIPELINE_RUN_NOT_FOUND`: Pipeline run not found
- `JOURNAL_ENTRY_NOT_FOUND`: Journal entry not found
- `POLICY_NOT_FOUND`: Policy not found
- `AUTHENTICATION_ERROR`: Authentication failed
- `AUTHORIZATION_ERROR`: Insufficient permissions
- `INTERNAL_SERVER_ERROR`: Internal server error

### HTTP Status Codes

- `200`: Success
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `422`: Unprocessable Entity
- `500`: Internal Server Error

## Rate Limiting

Currently no rate limiting is implemented. This will be added in future versions.

## Pagination

List endpoints support pagination with the following parameters:

- `limit`: Number of results per page (default: 50, max: 1000)
- `offset`: Number of results to skip (default: 0)

## OpenAPI Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`
