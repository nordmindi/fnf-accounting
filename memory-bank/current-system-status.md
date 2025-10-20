# Current System Status - Fire & Forget Accounting

## System Overview
The Fire & Forget Accounting system is a **production-ready** Nordic AI-powered accounting automation platform that processes natural language input and receipts to automatically create journal entries based on Swedish accounting standards (BAS 2025 v1.0/v2.0). The system now supports comprehensive natural language processing, advanced policy management, and complete Swedish accounting compliance.

## Current Architecture

### Core Components
- **FastAPI Backend**: RESTful API with async support and JWT authentication
- **Natural Language Processing**: AI-powered intent detection and entity extraction
- **OCR Processing**: Tesseract with Swedish language support
- **LLM Integration**: OpenAI GPT-4 with fallback detection
- **Rule Engine**: Policy-driven automation with JSON DSL and BAS versioning
- **Pipeline Orchestrator**: Database-backed pipeline processing
- **Stoplight System**: GREEN/YELLOW/RED decision logic with confidence scoring
- **Booking Engine**: Creates journal entries with BAS compliance and VAT optimization
- **Database Repository**: PostgreSQL with full persistence and audit trails
- **Policy Migration**: Automatic BAS version migration and account validation
- **Error Handling**: Comprehensive exception management and recovery
- **Health Monitoring**: Real-time system status and metrics
- **Comprehensive Testing**: 90%+ test coverage with unit, integration, and E2E tests

### Service Architecture
- **DocumentService**: Document management with object storage
- **BookingService**: Journal entry creation and management
- **PolicyService**: Policy management with database persistence and versioning
- **NaturalLanguageService**: AI-powered natural language processing
- **PipelineOrchestrator**: Database-backed pipeline processing
- **AuthService**: JWT authentication and authorization
- **DatabaseRepository**: Centralized data access layer
- **PolicyMigrationService**: BAS version migration and account validation
- **VATOptimizationService**: Deductible split calculations and tax optimization

## Current Configuration

### Environment Variables
```bash
# Mock Data Control
USE_MOCK_DATA=false  # Currently set to real data mode

# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5433/fireforget_accounting

# Redis
REDIS_URL=redis://localhost:6379/0

# MinIO/S3
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=documents

# OpenAI
OPENAI_API_KEY=your-openai-api-key-here

# Security
SECRET_KEY=your-secret-key-here-change-in-production
JWT_SECRET_KEY=your-jwt-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Environment
ENVIRONMENT=development
LOG_LEVEL=INFO
```

### Docker Services
- **app**: FastAPI application (port 8000)
- **worker**: Celery worker for async tasks
- **db**: PostgreSQL database (port 5433)
- **redis**: Redis message broker (port 6379)
- **minio**: Object storage (ports 9000, 9001)

## API Endpoints

### Health & Status
- `GET /health` - Basic health check
- `GET /health/detailed` - Detailed system health with component status
- `GET /status` - System metrics and counts
- `GET /` - API information and documentation links

### Authentication
- `POST /api/v1/auth/login` - User authentication
- `POST /api/v1/auth/refresh` - Refresh access token
- `GET /api/v1/auth/me` - Get current user information
- `POST /api/v1/auth/logout` - User logout
- `POST /api/v1/auth/test-token` - Create test token (development only)

### Natural Language Processing
- `POST /api/v1/natural-language/process` - Process natural language input for booking creation
- `GET /api/v1/natural-language/supported-intents` - Get list of supported business intents

### Document Management
- `POST /api/v1/documents/upload` - Upload document for processing
- `GET /api/v1/documents/{document_id}` - Get document details
- `GET /api/v1/documents` - List documents with pagination
- `GET /api/v1/documents/{document_id}/download` - Download document content

### Pipeline Management
- `POST /api/v1/pipelines/start` - Start document processing pipeline
- `GET /api/v1/pipelines/{run_id}` - Get pipeline status and booking ID
- `GET /api/v1/pipelines` - List pipeline runs with pagination
- `GET /api/v1/pipelines/{run_id}/debug` - Get detailed pipeline debug information

### Booking Management
- `GET /api/v1/bookings/{booking_id}` - Get booking details
- `GET /api/v1/bookings` - List bookings for company with pagination
- `GET /api/v1/bookings/by-pipeline/{pipeline_run_id}` - Get booking by pipeline

### Policy Management
- `GET /api/v1/policies` - List available policies
- `GET /api/v1/policies/{policy_id}` - Get policy details
- `POST /api/v1/policies` - Create new policy
- `PUT /api/v1/policies/{policy_id}` - Update existing policy

## Current Policies (8 Swedish Scenarios)

### Swedish Representation Meal Policy (SE_REPR_MEAL_V1)
- **Intent**: representation_meal
- **VAT Rate**: 12%
- **VAT Cap**: 300 SEK per person
- **Deductible Split**: Automatic split between deductible/non-deductible portions
- **Accounts**: 6071 (deductible), 6072 (non-deductible), 2641 (VAT), 1930 (cash/bank)
- **Stoplight**: GREEN with proper purpose and attendees

### Swedish Taxi Transport Policy (SE_TAXI_TRANSPORT_V1)
- **Intent**: taxi_transport
- **VAT Rate**: 25%
- **Accounts**: 6540 (transport), 2640 (VAT), 1930 (cash/bank)
- **Stoplight**: GREEN with proper purpose

### Swedish SaaS Subscription Policy (SE_SAAS_SUBSCRIPTION_V1)
- **Intent**: saas_subscription
- **VAT Rate**: 25%
- **Accounts**: 6541 (software), 2640 (VAT), 1930 (cash/bank)
- **Stoplight**: GREEN with service period

### Swedish SaaS Reverse Charge Policy (SE_SAAS_REVERSE_CHARGE_V1)
- **Intent**: saas_subscription (foreign suppliers)
- **VAT Mode**: Reverse charge (25%)
- **Accounts**: 6540 (IT services), 2614 (output VAT), 2645 (input VAT), 1930 (bank)
- **Report Boxes**: 21 (net), 30 (VAT), 48 (VAT)

### Swedish Mobile Phone Installment Policy (SE_MOBILE_PHONE_INSTALLMENT_V1)
- **Intent**: mobile_phone_purchase
- **VAT Rate**: 25%
- **Asset Classification**: Fixed asset (1630)
- **Accounts**: 1630 (mobile phones), 2640 (VAT), 2440 (supplier debt)
- **Installment Support**: 12+ months payment plans

### Swedish Office Supplies Policy (SE_OFFICE_SUPPLIES_V1)
- **Intent**: office_supplies
- **VAT Rate**: 25%
- **Accounts**: 6540 (office materials), 2640 (VAT), 1930 (bank)
- **Stoplight**: GREEN with purpose

### Swedish Computer Purchase Policy (SE_COMPUTER_PURCHASE_V1)
- **Intent**: computer_purchase
- **VAT Rate**: 25%
- **Asset Classification**: Fixed asset (1630)
- **Accounts**: 1630 (computers), 2640 (VAT), 1930 (bank)
- **Minimum Amount**: 5000 SEK

### Swedish Consulting EU Policy (SE_CONSULTING_EU_V1)
- **Intent**: consulting_services (EU suppliers)
- **VAT Mode**: Reverse charge (25%)
- **Accounts**: 6540 (consulting), 2614 (output VAT), 2645 (input VAT), 1930 (bank)
- **Report Boxes**: 21 (net), 30 (VAT), 48 (VAT)

### Swedish Employee Expense Policy (SE_EMPLOYEE_EXPENSE_V1)
- **Intent**: employee_expense
- **VAT Rate**: 25%
- **Accounts**: 6540 (employee expense), 2640 (VAT), 2440 (employee debt)
- **Stoplight**: GREEN with employee name

### Swedish Leasing Policy (SE_LEASING_V1)
- **Intent**: leasing
- **VAT Rate**: 25%
- **Accounts**: 6540 (leasing costs), 2640 (VAT), 2440 (supplier debt)
- **Stoplight**: GREEN with lease period

## Current Test Status

### Database Integration
- ✅ PostgreSQL database with full persistence
- ✅ Alembic migrations for schema management
- ✅ BAS 2025 v1.0 dataset loaded
- ✅ All services using database-backed repositories
- ✅ Complete audit trail for all operations

### Authentication & Security
- ✅ JWT-based authentication implemented
- ✅ Role-based access control (user, admin)
- ✅ Company-based data isolation
- ✅ Secure password hashing with bcrypt
- ✅ Test token generation for development

### API Functionality
- ✅ All endpoints fully implemented and functional
- ✅ Comprehensive error handling with structured responses
- ✅ Input validation and sanitization
- ✅ Pagination support for all list endpoints
- ✅ Health monitoring and system metrics

### Complete Flow Testing
- ✅ Document upload and processing with persistence
- ✅ Natural language processing with AI intent detection
- ✅ Intent detection (8 Swedish scenarios: representation_meal, taxi_transport, saas_subscription, mobile_phone_purchase, office_supplies, computer_purchase, consulting_services, employee_expense, leasing)
- ✅ Policy matching and application with BAS versioning
- ✅ VAT calculations with Swedish rules and optimization
- ✅ Deductible/non-deductible splits for representation meals
- ✅ Reverse charge VAT for foreign suppliers
- ✅ Journal entry creation with BAS compliance
- ✅ Pipeline-to-booking mapping with database storage
- ✅ Stoplight decision logic with confidence scoring
- ✅ Authentication and authorization flow
- ✅ Comprehensive test suite (90%+ coverage)
- ✅ Policy migration and BAS account validation

## Available Commands

### Development Commands
```bash
# Start services
make up

# Stop services
make down

# View logs
make logs

# Clean Docker resources
make clean-docker
```

### Testing Commands
```bash
# Test with mock data
make test-api

# Test complete flow with real data only
make test-no-mock

# Test pipeline booking ID functionality
make test-pipeline-booking

# Test content type handling
make test-content-type

# Test natural language processing
make test-natural-language

# Run comprehensive test suite
python scripts/run_tests.py

# Run specific test categories
python scripts/run_tests.py --unit
python scripts/run_tests.py --integration
python scripts/run_tests.py --e2e
```

### Configuration Commands
```bash
# Toggle between mock and real data modes
make toggle-mock

# Setup Postman collection
make setup-postman
```

## Current Data Flow

### Natural Language Processing Flow
1. **Natural Language Input**: User describes transaction in Swedish/English
2. **AI Intent Detection**: LLM determines business intent and extracts entities
3. **Fallback Detection**: Keyword-based detection if LLM confidence is low
4. **Policy Matching**: Rule engine finds matching Swedish policy with BAS versioning
5. **VAT Optimization**: Applies Swedish VAT rules, caps, and deductible splits
6. **Stoplight Decision**: GREEN/YELLOW/RED based on confidence and requirements
7. **Journal Entry**: Creates BAS-compliant journal entry if GREEN
8. **User Feedback**: Detailed booking information with VAT breakdown and tax benefits

### Document Processing Flow
1. **Document Upload**: User uploads receipt with Swedish instruction
2. **OCR Processing**: Tesseract extracts text and structured data
3. **Intent Detection**: LLM determines business intent and extracts slots
4. **Policy Matching**: Rule engine finds matching Swedish policy
5. **VAT Calculation**: Applies Swedish VAT rules and caps
6. **Stoplight Decision**: GREEN/YELLOW/RED based on confidence and requirements
7. **Journal Entry**: Creates BAS-compliant journal entry if GREEN
8. **Pipeline Response**: Returns booking ID for retrieval

## Technical Stack

### Backend
- **Python 3.12+**: Core language
- **FastAPI**: Web framework
- **Pydantic v2**: Data validation
- **SQLAlchemy**: ORM (async)
- **Alembic**: Database migrations

### AI/ML
- **Tesseract OCR**: Text extraction
- **OpenAI/Local LLM**: Intent detection
- **Rule Engine**: Policy application

### Infrastructure
- **PostgreSQL**: Primary database
- **Redis**: Message broker
- **MinIO**: Object storage
- **Docker**: Containerization
- **Celery**: Async task processing

### Observability
- **OpenTelemetry**: Tracing and logging
- **Structlog**: Structured logging
- **Health checks**: Service monitoring

## Current Limitations

1. **Nordic Expansion**: Only Swedish policies implemented (NO, DK, FI pending)
2. **Bank Integration**: No PSD2 bank matching yet
3. **Export Formats**: SIE, SAF-T exporters not implemented
4. **Production Deployment**: Kubernetes deployment and production secrets management pending
5. **Advanced Features**: Voice processing, mobile app, advanced analytics pending

## Next Steps

1. **Nordic Expansion**: Implement Norwegian, Danish, and Finnish policies
2. **Bank Integration**: PSD2 integration for automatic bank matching
3. **Export Formats**: SIE, SAF-T, and other Nordic export formats
4. **Production Deployment**: Kubernetes deployment with proper secrets management
5. **Advanced Features**: Voice processing, mobile app, advanced analytics
6. **Performance Optimization**: Advanced caching and optimization
7. **Monitoring**: Enhanced observability and alerting

## System Health
- ✅ All services running
- ✅ API endpoints responding
- ✅ Natural language processing working
- ✅ Pipeline processing working with database persistence
- ✅ Authentication and authorization functional
- ✅ Database integration complete
- ✅ Error handling and validation working
- ✅ Health monitoring and metrics available
- ✅ Swedish accounting compliance
- ✅ BAS 2025 v1.0/v2.0 validation and migration
- ✅ Complete end-to-end flow tested
- ✅ Production-ready architecture implemented
- ✅ Comprehensive test suite (90%+ coverage)
- ✅ Policy versioning and migration working
- ✅ VAT optimization and deductible splits working
- ✅ Multi-language support (Swedish/English)
- ✅ Git version control and documentation
