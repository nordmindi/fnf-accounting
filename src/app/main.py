"""FastAPI application main module."""

from contextlib import asynccontextmanager
from datetime import datetime

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.app.error_handlers import setup_error_handlers
from src.app.routers import (
    auth,
    bookings,
    documents,
    natural_language,
    pipelines,
    policies,
)
from src.infra.config import get_settings
from src.infra.database import init_db

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Fire & Forget AI Accounting API")
    settings = get_settings()

    # Initialize database
    await init_db(settings.database_url)
    logger.info("Database initialized")

    yield

    # Shutdown
    logger.info("Shutting down Fire & Forget AI Accounting API")


# Create FastAPI application
app = FastAPI(
    title="Fire & Forget AI Accounting",
    description="AI-powered autonomous accounting backend",
    version="0.1.0",
    lifespan=lifespan
)

# Set up error handlers
setup_error_handlers(app)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(documents.router, prefix="/api/v1", tags=["documents"])
app.include_router(pipelines.router, prefix="/api/v1", tags=["pipelines"])
app.include_router(bookings.router, prefix="/api/v1", tags=["bookings"])
app.include_router(policies.router, prefix="/api/v1", tags=["policies"])
app.include_router(auth.router, prefix="/api/v1", tags=["authentication"])
app.include_router(natural_language.router, prefix="/api/v1", tags=["natural-language"])


@app.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {"status": "healthy", "service": "fireforget-accounting"}


@app.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with system status."""
    from src.infra.config import get_settings
    from src.repositories.database import DatabaseRepository

    settings = get_settings()
    health_status = {
        "status": "healthy",
        "service": "fireforget-accounting",
        "version": "0.1.0",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {}
    }

    # Check database connectivity
    try:
        repository = DatabaseRepository(settings.database_url)
        # Simple query to test database connection
        from sqlalchemy import text
        async with repository.engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        health_status["components"]["database"] = {"status": "healthy", "message": "Connected"}
    except Exception as e:
        health_status["components"]["database"] = {"status": "unhealthy", "message": str(e)}
        health_status["status"] = "degraded"

    # Check storage connectivity (if configured)
    try:
        from src.adapters.storage import StorageAdapter
        storage = StorageAdapter(settings.storage_url)
        # Simple test - this would need to be implemented in StorageAdapter
        health_status["components"]["storage"] = {"status": "healthy", "message": "Available"}
    except Exception as e:
        health_status["components"]["storage"] = {"status": "unhealthy", "message": str(e)}
        health_status["status"] = "degraded"

    # Check LLM connectivity (if configured)
    try:
        from src.adapters.llm import LLMAdapter
        llm = LLMAdapter(settings.openai_api_key)
        # Simple test - this would need to be implemented in LLMAdapter
        health_status["components"]["llm"] = {"status": "healthy", "message": "Available"}
    except Exception as e:
        health_status["components"]["llm"] = {"status": "unhealthy", "message": str(e)}
        health_status["status"] = "degraded"

    return health_status


@app.get("/status")
async def system_status():
    """System status endpoint with metrics."""
    from src.infra.config import get_settings
    from src.repositories.database import DatabaseRepository

    settings = get_settings()
    repository = DatabaseRepository(settings.database_url)

    try:
        # Get basic system metrics
        from sqlalchemy import text


        async with repository.engine.begin() as conn:
            # Count documents
            doc_count_result = await conn.execute(
                text("SELECT COUNT(*) FROM documents")
            )
            doc_count = doc_count_result.scalar()

            # Count journal entries
            journal_count_result = await conn.execute(
                text("SELECT COUNT(*) FROM journal_entries")
            )
            journal_count = journal_count_result.scalar()

            # Count pipeline runs
            pipeline_count_result = await conn.execute(
                text("SELECT COUNT(*) FROM pipeline_runs")
            )
            pipeline_count = pipeline_count_result.scalar()

            # Count active policies
            policy_count_result = await conn.execute(
                text("SELECT COUNT(*) FROM policies")
            )
            policy_count = policy_count_result.scalar()

        return {
            "status": "operational",
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": {
                "documents": doc_count,
                "journal_entries": journal_count,
                "pipeline_runs": pipeline_count,
                "policies": policy_count
            },
            "version": "0.1.0",
            "environment": settings.environment
        }

    except Exception as e:
        return {
            "status": "error",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e),
            "version": "0.1.0"
        }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Fire & Forget AI Accounting API",
        "version": "0.1.0",
        "docs": "/docs"
    }
