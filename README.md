# Fire & Forget AI Accounting

[![CI Pipeline](https://github.com/nordmindi/fnf-accounting/actions/workflows/ci.yml/badge.svg)](https://github.com/nordmindi/fnf-accounting/actions/workflows/ci.yml)
[![Code Quality](https://github.com/nordmindi/fnf-accounting/actions/workflows/quality.yml/badge.svg)](https://github.com/nordmindi/fnf-accounting/actions/workflows/quality.yml)
[![Test Matrix](https://github.com/nordmindi/fnf-accounting/actions/workflows/test-matrix.yml/badge.svg)](https://github.com/nordmindi/fnf-accounting/actions/workflows/test-matrix.yml)
[![Dependencies](https://github.com/nordmindi/fnf-accounting/actions/workflows/dependencies.yml/badge.svg)](https://github.com/nordmindi/fnf-accounting/actions/workflows/dependencies.yml)

## What it does
AI-powered backend that automates accounting from receipt to journal entry with Nordic compliance and full auditability. The system processes financial documents, applies localized accounting rules, and produces legally valid journal entries with complete audit trails.

## Architecture
- **Modular Domain Services** with adapters/ports pattern
- **Policy-driven Rule Engine** using JSON/YAML DSL
- **Pipeline Orchestrator** for document processing
- **Vertical Slices** architecture for maintainability
- **Database-backed Services** with PostgreSQL persistence
- **JWT Authentication** with role-based authorization
- **Comprehensive Error Handling** with structured responses
- **Health Monitoring** with detailed system status

## Tech Stack
- **Backend:** Python 3.12 + FastAPI + Pydantic v2
- **Database:** PostgreSQL with JSONB for flexible data
- **OCR:** Tesseract (local) + optional Cloud Vision
- **LLM:** OpenAI API or local LLaMA via vLLM
- **Storage:** MinIO/S3-compatible object storage
- **Jobs:** Celery + Redis for async processing
- **Observability:** OpenTelemetry + structured logging

## Key Features

### 🗣️ **Natural Language Processing**
- **Voice & Text Input**: Process natural language descriptions of expenses
- **Multi-language Support**: Swedish and English input processing
- **Intent Detection**: AI-powered classification of business transactions
- **Entity Extraction**: Automatic extraction of amounts, vendors, purposes, attendees
- **Fallback Detection**: Robust keyword-based fallback when AI confidence is low

### 🧠 **AI-Powered Accounting**
- **LLM Integration**: OpenAI GPT-4 for intelligent transaction understanding
- **Rule Engine**: Policy-driven accounting decisions with Swedish BAS compliance
- **Stoplight System**: Confidence-based automation (Green/Yellow/Red)
- **VAT Optimization**: Automatic deductible/non-deductible splits for maximum tax benefits
- **Compliance Assurance**: Full Swedish accounting standards compliance

### 🔐 **Authentication & Security**
- JWT-based authentication with role-based access control
- Company-based data isolation
- Secure API key management
- Password hashing with bcrypt

### 📊 **Data Management**
- PostgreSQL database with full persistence
- JSONB support for flexible policy storage
- Alembic database migrations
- BAS 2025 v1.0/v2.0 dataset integration with versioning

### 🚀 **API Features**
- RESTful API design with OpenAPI documentation
- Comprehensive error handling with structured responses
- Input validation and sanitization
- Pagination support for all list endpoints
- **Natural Language API**: Direct text-to-booking processing

### 🔍 **Monitoring & Health**
- Real-time health checks for all system components
- System metrics and performance monitoring
- Structured logging with request tracing
- Component status monitoring (database, storage, LLM)

### 📋 **Document Processing**
- Multi-format document support (PDF, JPEG, PNG)
- OCR text extraction with confidence scoring
- Intent detection using LLM integration
- Policy-based rule engine for accounting decisions

### 📚 **Policy Management**
- JSON-based policy DSL for accounting rules
- Country-specific compliance (Sweden, Norway, Denmark, Finland)
- Version-controlled policy management with BAS versioning
- Dynamic policy updates without system restart
- **Policy Migration**: Automatic migration between BAS versions

## Quickstart (Development)

### Prerequisites
- Python 3.12+
- Docker & Docker Compose
- Git

### Setup
```bash
# Clone repository
git clone <repo-url>
cd fnf-accounting

# Setup environment
cp env.example .env
# Edit .env with your configuration

# Install dependencies
make setup

# Start services
make up

# Run database migrations
make upgrade

# Start the application
make run
```

### Development Commands
```bash
make help          # Show all available commands
make test          # Run tests
make lint          # Run linting
make format        # Format code
make clean         # Clean temporary files
make dev           # Start full development environment
```

## API Endpoints

### Health & Status
- `GET /health` – Basic health check
- `GET /health/detailed` – Detailed system health with component status
- `GET /status` – System metrics and counts
- `GET /` – API information and documentation links

### Authentication
- `POST /api/v1/auth/login` – User authentication
- `POST /api/v1/auth/refresh` – Refresh access token
- `GET /api/v1/auth/me` – Get current user information
- `POST /api/v1/auth/logout` – User logout
- `POST /api/v1/auth/test-token` – Create test token (development only)

### Documents
- `POST /api/v1/documents/upload` – Upload document and start processing
- `GET /api/v1/documents/{id}` – Get document details
- `GET /api/v1/documents` – List documents with pagination
- `GET /api/v1/documents/{id}/download` – Download document content

### Pipelines
- `POST /api/v1/pipelines/start` – Start document processing pipeline
- `GET /api/v1/pipelines/{id}` – Get pipeline status
- `GET /api/v1/pipelines` – List pipeline runs with pagination
- `GET /api/v1/pipelines/{id}/debug` – Get detailed pipeline debug information

### Bookings (Journal Entries)
- `GET /api/v1/bookings/{id}` – Get journal entry details
- `GET /api/v1/bookings` – List journal entries with pagination
- `GET /api/v1/bookings/by-pipeline/{pipeline_run_id}` – Get booking by pipeline run

### Policies
- `GET /api/v1/policies` – List active policies
- `GET /api/v1/policies/{id}` – Get policy details
- `POST /api/v1/policies` – Create new policy
- `PUT /api/v1/policies/{id}` – Update existing policy

### Natural Language Processing
- `POST /api/v1/natural-language/process` – Process natural language input and create booking
- `POST /api/v1/natural-language/validate` – Validate natural language input without creating booking

## Supported Scenarios (Sweden)

### 🍽️ **Representation Meals**
- **Policy:** SE_REPR_MEAL_V1
- **VAT:** 12% with 300 SEK cap per person
- **Accounts:** 6071 (deductible), 6072 (non-deductible), 2641 (VAT), 1930 (cash)
- **Example:** "Business lunch with client from Example AB, 1500 SEK"

### 🚗 **Transport & Travel**
- **Policy:** SE_TAXI_TRANSPORT_V1
- **VAT:** 25% standard rate
- **Accounts:** 6540 (expense), 2640 (VAT), 1930 (cash)
- **Example:** "Taxi to client meeting, 450 SEK"

### ☁️ **SaaS & Cloud Services**
- **Policy:** SE_SAAS_SUBSCRIPTION_V1 (standard) / SE_SAAS_REVERSE_CHARGE_V1 (foreign)
- **VAT:** 25% standard or reverse charge for foreign suppliers
- **Accounts:** 6541 (expense), 2640 (VAT), 1930 (cash) or 6540, 2614, 2645, 1930 (reverse charge)
- **Example:** "AWS cloud service 4500 SEK for October 2025"

### 📱 **Mobile Phone Purchases**
- **Policy:** SE_MOBILE_PHONE_INSTALLMENT_V1
- **VAT:** 25% standard rate
- **Accounts:** 1630 (asset), 2640 (VAT), 2440 (liability)
- **Example:** "Mobile phone from NetOnNet 15000 SEK, 12 months installment"

### 🏢 **Office Supplies**
- **Policy:** SE_OFFICE_SUPPLIES_V1
- **VAT:** 25% standard rate
- **Accounts:** 6540 (expense), 2640 (VAT), 1930 (cash)
- **Example:** "Office supplies 2500 SEK"

### 💻 **Computer Purchases**
- **Policy:** SE_COMPUTER_PURCHASE_V1
- **VAT:** 25% standard rate
- **Accounts:** 1630 (asset), 2640 (VAT), 1930 (cash)
- **Example:** "Computer purchase 10000 SEK"

### 📋 **Leasing**
- **Policy:** SE_LEASING_V1
- **VAT:** 25% standard rate
- **Accounts:** 6540 (expense), 2640 (VAT), 2440 (liability)
- **Example:** "Leasing kopiator 3000 SEK per month"

### 👥 **Employee Expenses**
- **Policy:** SE_EMPLOYEE_EXPENSE_V1
- **VAT:** 25% standard rate
- **Accounts:** 6540 (expense), 2640 (VAT), 2440 (liability)
- **Example:** "Employee expense 1500 SEK"

## Policy DSL

Policies are defined in JSON format with the following structure:

```json
{
  "id": "SE_REPR_MEAL_V1",
  "version": "V1",
  "country": "SE",
  "effective_from": "2024-01-01",
  "name": "Swedish Representation Meal Policy",
  "rules": {
    "match": {
      "intent": "representation_meal"
    },
    "requires": [
      {"field": "slots.attendees_count", "op": ">=", "value": 1},
      {"field": "slots.purpose", "op": "exists"}
    ],
    "vat": {
      "rate": 12,
      "cap_sek_per_person": 300,
      "code": "12"
    },
    "posting": [
      {"account": "6071", "side": "D", "amount": "net_after_cap"},
      {"account": "2641", "side": "D", "amount": "vat_allowed"},
      {"account": "1930", "side": "K", "amount": "gross"}
    ],
    "stoplight": {
      "on_missing_required": "YELLOW",
      "on_fail": "RED",
      "confidence_threshold": 0.8
    }
  }
}
```

## Stoplight System

- **GREEN:** Automatically book the entry
- **YELLOW:** Ask one clarifying question, then book
- **RED:** Park for manual review

## Authentication

The API uses JWT-based authentication. For development, you can create a test token:

```bash
# Create test token
curl -X POST "http://localhost:8000/api/v1/auth/test-token"

# Use token in requests
curl -X GET "http://localhost:8000/api/v1/documents" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### User Roles
- **user**: Standard user with company access
- **admin**: Administrative access across companies

## Usage Examples

### Upload and Process Document
```bash
# Upload a receipt
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@receipt.jpg" \
  -F "company_id=123e4567-e89b-12d3-a456-426614174007" \
  -F "user_text=Business lunch with client"

# Check pipeline status
curl -X GET "http://localhost:8000/api/v1/pipelines/PIPELINE_ID" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### List Documents and Bookings
```bash
# List documents
curl -X GET "http://localhost:8000/api/v1/documents?company_id=123e4567-e89b-12d3-a456-426614174007&limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"

# List journal entries
curl -X GET "http://localhost:8000/api/v1/bookings?company_id=123e4567-e89b-12d3-a456-426614174007&limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Health Monitoring
```bash
# Basic health check
curl -X GET "http://localhost:8000/health"

# Detailed system status
curl -X GET "http://localhost:8000/health/detailed"

# System metrics
curl -X GET "http://localhost:8000/status"
```

## Testing

### Comprehensive Test Suite

The system includes a comprehensive test suite covering:

- **Unit Tests**: Individual component testing
- **Integration Tests**: End-to-end scenario testing
- **Policy Tests**: Rule engine and migration testing
- **Natural Language Tests**: NLP functionality testing

### Running Tests

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run specific test types
python scripts/run_tests.py --type unit          # Unit tests
python scripts/run_tests.py --type integration   # Integration tests
python scripts/run_tests.py --type all          # All tests

# Run specific scenarios
python scripts/run_tests.py --scenario representation_meal
python scripts/run_tests.py --scenario saas_reverse_charge
python scripts/run_tests.py --scenario mobile_phone

# Run with coverage report
python scripts/run_tests.py --coverage

# Run performance tests
python scripts/run_tests.py --performance
```

### Test Coverage

The test suite covers:
- ✅ Natural Language Processing (intent detection, entity extraction, fallback)
- ✅ Policy Engine (rule matching, VAT calculation, posting generation)
- ✅ Policy Migration (BAS versioning, account validation)
- ✅ End-to-End Scenarios (complete user workflows)
- ✅ Error Handling (graceful failure, recovery mechanisms)
- ✅ Multi-language Support (Swedish and English)
- ✅ VAT Optimization (deductible splits, reverse charge)

## CI/CD Pipeline

The project includes comprehensive GitHub Actions workflows for continuous integration and deployment:

### 🔄 **CI Pipeline** (`ci.yml`)
- **Linting**: ruff, black, isort, mypy, bandit, pip-audit
- **Testing**: pytest with coverage reporting
- **Database**: PostgreSQL and Redis services
- **Security**: Automated security scanning
- **Code Quality**: Format checking and type validation

### 🧪 **Test Matrix** (`test-matrix.yml`)
- **Multi-version Testing**: Python 3.11 and 3.12
- **Test Types**: Unit and integration tests
- **Coverage**: Codecov integration for coverage tracking
- **Services**: Full database and Redis setup

### 🔍 **Code Quality** (`quality.yml`)
- **Pre-commit Hooks**: Automated code quality checks
- **Security Scanning**: Bandit and pip-audit security analysis
- **Dependency Checks**: Conflict detection and outdated package scanning

### 📦 **Dependencies** (`dependencies.yml`)
- **Weekly Security Scans**: Automated dependency vulnerability checks
- **Update Monitoring**: Outdated package detection
- **Conflict Detection**: Dependency conflict resolution

### 🚀 **Pre-commit Configuration**
- **Automated Formatting**: Black, isort, ruff
- **Type Checking**: mypy with strict mode
- **Security**: Bandit security linting
- **Quality**: Flake8 code quality checks

## Quality Standards

- **Type Safety:** mypy strict mode enabled
- **Code Style:** Black + isort + ruff
- **Security:** bandit + pip-audit
- **Testing:** pytest with 80%+ coverage target
- **Documentation:** Docstrings for all public functions
- **CI/CD:** Automated testing, linting, and security scanning

## Development Workflow

1. **Feature Branch:** Create feature branch from main
2. **TDD:** Write tests first, then implementation
3. **Code Quality:** Ensure all linting passes
4. **Testing:** All tests must pass
5. **PR:** Create pull request with description
6. **Review:** At least one reviewer required
7. **Merge:** CI must be green before merge

## Roadmap

See `memory-bank/roadmap.md` for detailed milestones.

## Documentation

- **API Documentation**: Complete API reference in `docs/API.md`
- **Natural Language API**: NLP API documentation in `docs/NATURAL_LANGUAGE_API.md`
- **Postman Testing**: Testing guide in `docs/POSTMAN_TESTING_GUIDE.md`
- **Kontoplan Versioning**: Versioning system in `docs/KONTOPLAN_VERSIONING.md`
- **Architecture**: System architecture in `memory-bank/architecture.md`
- **Current Status**: System status and capabilities in `memory-bank/current-system-status.md`
- **Interactive Docs**: Swagger UI available at `http://localhost:8000/docs`

## Contributing

1. Read the development rules in `.cursor/rules.mdc`
2. Follow the quality standards in `memory-bank/quality-standards.md`
3. Check the architecture in `memory-bank/architecture.md`
4. Review the API documentation in `docs/API.md`
5. Open a PR with clear description

## License

[Add your license here]
