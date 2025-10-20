"""Dependency injection for FastAPI application."""

from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from src.adapters.llm import LLMAdapter
from src.adapters.ocr import OCRAdapter
from src.adapters.storage import StorageAdapter
from src.domain.services import (
    BookingService,
    DocumentService,
    ExtractionService,
    NLUService,
    PolicyService,
    ProposalService,
    ReasonService,
    StoplightService,
)
from src.infra.config import get_settings
from src.repositories.database import DatabaseRepository
from src.rules.engine import RuleEngine


@lru_cache
def get_database_repository():
    """Get database repository instance."""
    settings = get_settings()
    return DatabaseRepository(settings.database_url)


@lru_cache
def get_storage_adapter():
    """Get storage adapter instance."""
    settings = get_settings()
    config = {
        "endpoint": settings.minio_endpoint,
        "access_key": settings.minio_access_key,
        "secret_key": settings.minio_secret_key,
        "secure": settings.minio_secure,
        "bucket": settings.minio_bucket,
    }
    return StorageAdapter(config)


@lru_cache
def get_ocr_adapter():
    """Get OCR adapter instance."""
    config = {
        "tesseract": {
            "language": "swe+eng",
            "psm": 6,
        }
    }
    return OCRAdapter(config)


@lru_cache
def get_llm_adapter():
    """Get LLM adapter instance."""
    settings = get_settings()
    config = {
        "api_key": settings.openai_api_key,
        "model": "gpt-4",
        "temperature": 0.1,
    }
    return LLMAdapter(config)


@lru_cache
def get_rule_engine():
    """Get rule engine instance."""
    # Load policies from files
    policies = []
    try:
        import json
        import os

        policies_dir = "src/rules/policies"
        if os.path.exists(policies_dir):
            for filename in os.listdir(policies_dir):
                if filename.endswith(".json"):
                    with open(os.path.join(policies_dir, filename)) as f:
                        policy = json.load(f)
                        policies.append(policy)
    except Exception as e:
        print(f"Warning: Could not load policies: {e}")

    return RuleEngine(policies)


# Service dependencies
def get_document_service(
    storage: Annotated[StorageAdapter, Depends(get_storage_adapter)],
    repository: Annotated[DatabaseRepository, Depends(get_database_repository)],
) -> DocumentService:
    """Get document service instance."""
    return DocumentService(storage, repository)


def get_extraction_service(
    ocr: Annotated[OCRAdapter, Depends(get_ocr_adapter)],
) -> ExtractionService:
    """Get extraction service instance."""
    return ExtractionService(ocr)


def get_nlu_service(
    llm: Annotated[LLMAdapter, Depends(get_llm_adapter)],
) -> NLUService:
    """Get NLU service instance."""
    return NLUService(llm)


def get_proposal_service(
    rule_engine: Annotated[RuleEngine, Depends(get_rule_engine)],
) -> ProposalService:
    """Get proposal service instance."""
    return ProposalService(rule_engine)


def get_stoplight_service() -> StoplightService:
    """Get stoplight service instance."""
    config = {
        "confidence_threshold": 0.8,
        "high_value_threshold": 10000,
    }
    return StoplightService(config)


def get_booking_service(
    repository: Annotated[DatabaseRepository, Depends(get_database_repository)],
) -> BookingService:
    """Get booking service instance."""
    return BookingService(repository)


def get_reason_service() -> ReasonService:
    """Get reason service instance."""
    return ReasonService()


def get_policy_service(
    repository: Annotated[DatabaseRepository, Depends(get_database_repository)],
) -> PolicyService:
    """Get policy service instance."""
    return PolicyService(repository)


def get_pipeline_orchestrator(
    document_service: Annotated[DocumentService, Depends(get_document_service)],
    extraction_service: Annotated[ExtractionService, Depends(get_extraction_service)],
    nlu_service: Annotated[NLUService, Depends(get_nlu_service)],
    proposal_service: Annotated[ProposalService, Depends(get_proposal_service)],
    stoplight_service: Annotated[StoplightService, Depends(get_stoplight_service)],
    booking_service: Annotated[BookingService, Depends(get_booking_service)],
    reason_service: Annotated[ReasonService, Depends(get_reason_service)],
    repository: Annotated[DatabaseRepository, Depends(get_database_repository)],
):
    """Get pipeline orchestrator instance."""
    from src.orchestrator.pipeline import PipelineOrchestrator
    return PipelineOrchestrator(
        document_service=document_service,
        extraction_service=extraction_service,
        nlu_service=nlu_service,
        proposal_service=proposal_service,
        stoplight_service=stoplight_service,
        booking_service=booking_service,
        reason_service=reason_service,
        repository=repository
    )
