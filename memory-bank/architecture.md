# System Architecture – Fire & Forget AI Accounting

## Overview
Fire & Forget AI Accounting is an autonomous accounting backend that processes financial documents (receipts, invoices) and natural-language instructions, applies localized accounting rules, and produces legally valid journal entries with audit trails. The system is Nordic-ready (SE first, extendable to NO/DK/FI).

## Core Flow

### Document Processing Flow
```
Upload → OCR → Intent Detection (LLM) → Rule Engine → Stoplight Decision → Booking → Journal Entry → Audit
```

### Natural Language Processing Flow
```
Text Input → Intent Detection (LLM) → Entity Extraction → Rule Engine → Stoplight Decision → Booking → Journal Entry → User Feedback
```

## High-Level Component Diagram
```
Frontend (Next.js later)
       ↓
API Layer (FastAPI + JWT Auth)
       ↓
Error Handling & Validation
       ↓
Orchestrator (Pipeline + Natural Language Service)
       ↓
Domain Services (Document, Booking, Policy, NLU, Natural Language)
       ↓
Repository Layer (Database)
       ↓
Policy Engine (Country-specific DSL + BAS Versioning)
       ↓
Accounting Core (double-entry, VAT, Deductible Optimization)
       ↓
PostgreSQL + Object Storage (S3-compatible)
       ↓
Health Monitoring & Observability
```

## Backend Tech Stack
| Layer | Technology |
|------|------------|
| API | Python + FastAPI + OpenAPI docs |
| Authentication | JWT + bcrypt + role-based access control |
| Business Logic | Modular Domain Services (Pydantic models) |
| Error Handling | Custom exception hierarchy + global handlers |
| Validation | Pydantic + custom validators |
| Rule Engine | Custom JSON/YAML Policy DSL + JSON Schema validation |
| OCR | Tesseract (local) + optional Cloud Vision/Textract |
| LLM | OpenAI or Local LLaMA via vLLM/llama.cpp (function calling) |
| Database | PostgreSQL (JSONB) + Alembic migrations |
| Object Storage | MinIO / S3 |
| Jobs/Queues | Celery + Redis |
| Health Monitoring | Real-time component status + metrics |
| Observability | OpenTelemetry + structured logging |

## Directory Structure (backend)
```
src/
├─ app/                 # FastAPI (Routers, DTOs, Auth, Error Handlers)
│  ├─ routers/          # API endpoints (documents, pipelines, bookings, policies, auth)
│  ├─ auth.py           # JWT authentication & authorization
│  ├─ exceptions.py     # Custom exception hierarchy
│  ├─ error_handlers.py # Global error handling
│  ├─ validators.py     # Input validation utilities
│  ├─ dependencies.py   # Dependency injection
│  └─ main.py           # FastAPI app configuration
├─ domain/              # Core logic (Services, Models)
│  ├─ services.py       # Business logic services
│  └─ models.py         # Pydantic domain models
├─ adapters/            # OCR, LLM, Storage, Exporters
├─ rules/               # Policy DSL + engine + schemas
├─ orchestrator/        # Pipeline orchestration
├─ repositories/        # DB access layer (DatabaseRepository)
├─ infra/               # DB, migrations (alembic), config
└─ tests/               # unit, integration, e2e
```

## API Architecture

### Authentication Flow
```
Client → JWT Token → FastAPI → Auth Middleware → Route Handler
```

### Request Processing Flow
```
1. Request → FastAPI Router
2. Authentication & Authorization
3. Input Validation (Pydantic + Custom Validators)
4. Business Logic (Domain Services)
5. Database Operations (Repository Pattern)
6. Response Serialization
7. Error Handling (Global Exception Handlers)
```

### Data Persistence
- **Documents**: Stored in object storage (MinIO/S3) with metadata in PostgreSQL
- **Pipeline Runs**: Complete audit trail in PostgreSQL with JSONB for complex data
- **Journal Entries**: Double-entry bookkeeping with line items
- **Policies**: JSON-based rules stored in PostgreSQL JSONB
- **BAS Accounts**: Standardized chart of accounts for Nordic countries

### Error Handling Strategy
- **Custom Exceptions**: Domain-specific exceptions with error codes
- **Global Handlers**: Centralized error processing with structured responses
- **Validation**: Input validation with detailed error messages
- **Logging**: Structured logging with request tracing

## Health Monitoring

### Health Check Endpoints
- `/health` - Basic liveness check
- `/health/detailed` - Component status (database, storage, LLM)
- `/status` - System metrics and counts

### Monitoring Components
- Database connectivity and performance
- Object storage availability
- LLM service status
- System resource usage
- Request/response metrics

## Natural Language Processing Architecture

### Intent Detection & Entity Extraction
```
User Input → LLM Adapter → Intent Classification → Entity Extraction → Fallback Detection → Structured Data
```

### Key Components
- **LLM Adapter**: OpenAI GPT-4 integration with structured prompts
- **Intent Detection**: Classification of business transaction types
- **Entity Extraction**: Amount, vendor, purpose, attendees, dates
- **Fallback System**: Keyword-based detection when LLM confidence is low
- **Multi-language Support**: Swedish and English processing

### Supported Intents
- `representation_meal`: Business meals and entertainment
- `saas_subscription`: Software and cloud services
- `mobile_phone_purchase`: Mobile devices and electronics
- `office_supplies`: Office materials and supplies
- `computer_purchase`: Computers and IT equipment
- `consulting_services`: Consulting and professional services
- `employee_expense`: Employee expenses and reimbursements
- `leasing`: Equipment leasing and rentals

## BAS Versioning & Policy Migration

### Version Management
```
Transaction Date → BAS Version Selection → Policy Loading → Account Validation → Booking Creation
```

### Key Features
- **Date-based Version Selection**: Automatic BAS version based on transaction date
- **Policy Migration**: Automatic migration between BAS versions
- **Account Validation**: Ensures all accounts exist in target BAS
- **Backward Compatibility**: Historical transactions remain accurate

### BAS Versions
- **BAS 2025 v1.0**: January 2025 - June 2025
- **BAS 2025 v2.0**: July 2025+ (with new accounts for digital services)

### Migration Rules
- Account number mapping between versions
- VAT rate changes handling
- New account introduction
- Deprecated account removal

## VAT Optimization System

### Deductible Split Logic
```
Representation Meal → Per-person Cap (300 SEK) → Deductible/Non-deductible Split → Tax Benefit Calculation
```

### VAT Modes
- **Standard VAT**: 25% or 12% with standard deduction
- **Reverse Charge**: For foreign suppliers (AWS, etc.)
- **Deductible Split**: For representation meals with caps
- **Capped VAT**: Maximum deductible amounts per person

### Tax Benefit Optimization
- Automatic calculation of maximum deductible amounts
- Split between deductible and non-deductible portions
- VAT deduction optimization
- Compliance with Swedish tax regulations

## Deployment & Ops
- Docker/Docker Compose; separate workers for Celery
- CI/CD: lint, type-check, tests, policy validation, build, deploy
- Configurable single-tenant / multi-tenant mode
- EU/EES data residency by default; DPIA documented
- Health monitoring and alerting
- Structured logging and observability

