"""Custom exceptions for the Fire & Forget Accounting API."""

from typing import Any, Dict, Optional
from fastapi import HTTPException, status


class FireForgetException(Exception):
    """Base exception for Fire & Forget Accounting system."""
    
    def __init__(self, message: str, error_code: str = None, details: Dict[str, Any] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class DocumentNotFoundError(FireForgetException):
    """Raised when a document is not found."""
    
    def __init__(self, document_id: str):
        super().__init__(
            message=f"Document {document_id} not found",
            error_code="DOCUMENT_NOT_FOUND",
            details={"document_id": document_id}
        )


class PipelineRunNotFoundError(FireForgetException):
    """Raised when a pipeline run is not found."""
    
    def __init__(self, pipeline_run_id: str):
        super().__init__(
            message=f"Pipeline run {pipeline_run_id} not found",
            error_code="PIPELINE_RUN_NOT_FOUND",
            details={"pipeline_run_id": pipeline_run_id}
        )


class JournalEntryNotFoundError(FireForgetException):
    """Raised when a journal entry is not found."""
    
    def __init__(self, entry_id: str):
        super().__init__(
            message=f"Journal entry {entry_id} not found",
            error_code="JOURNAL_ENTRY_NOT_FOUND",
            details={"entry_id": entry_id}
        )


class PolicyNotFoundError(FireForgetException):
    """Raised when a policy is not found."""
    
    def __init__(self, policy_id: str):
        super().__init__(
            message=f"Policy {policy_id} not found",
            error_code="POLICY_NOT_FOUND",
            details={"policy_id": policy_id}
        )


class BASAccountNotFoundError(FireForgetException):
    """Raised when a BAS account is not found."""
    
    def __init__(self, account_number: str):
        super().__init__(
            message=f"BAS account {account_number} not found",
            error_code="BAS_ACCOUNT_NOT_FOUND",
            details={"account_number": account_number}
        )


class InvalidDocumentFormatError(FireForgetException):
    """Raised when document format is invalid."""
    
    def __init__(self, content_type: str, supported_formats: list = None):
        super().__init__(
            message=f"Invalid document format: {content_type}",
            error_code="INVALID_DOCUMENT_FORMAT",
            details={
                "content_type": content_type,
                "supported_formats": supported_formats or ["image/jpeg", "image/png", "application/pdf"]
            }
        )


class DocumentProcessingError(FireForgetException):
    """Raised when document processing fails."""
    
    def __init__(self, step: str, reason: str):
        super().__init__(
            message=f"Document processing failed at step '{step}': {reason}",
            error_code="DOCUMENT_PROCESSING_ERROR",
            details={"step": step, "reason": reason}
        )


class IntentDetectionError(FireForgetException):
    """Raised when intent detection fails."""
    
    def __init__(self, reason: str):
        super().__init__(
            message=f"Intent detection failed: {reason}",
            error_code="INTENT_DETECTION_ERROR",
            details={"reason": reason}
        )


class PolicyMatchingError(FireForgetException):
    """Raised when no matching policy is found."""
    
    def __init__(self, intent: str, country: str):
        super().__init__(
            message=f"No matching policy found for intent '{intent}' in country '{country}'",
            error_code="POLICY_MATCHING_ERROR",
            details={"intent": intent, "country": country}
        )


class BookingCreationError(FireForgetException):
    """Raised when journal entry creation fails."""
    
    def __init__(self, reason: str):
        super().__init__(
            message=f"Journal entry creation failed: {reason}",
            error_code="BOOKING_CREATION_ERROR",
            details={"reason": reason}
        )


class ValidationError(FireForgetException):
    """Raised when input validation fails."""
    
    def __init__(self, field: str, value: Any, reason: str):
        super().__init__(
            message=f"Validation failed for field '{field}': {reason}",
            error_code="VALIDATION_ERROR",
            details={"field": field, "value": str(value), "reason": reason}
        )


class DatabaseError(FireForgetException):
    """Raised when database operations fail."""
    
    def __init__(self, operation: str, reason: str):
        super().__init__(
            message=f"Database operation '{operation}' failed: {reason}",
            error_code="DATABASE_ERROR",
            details={"operation": operation, "reason": reason}
        )


class StorageError(FireForgetException):
    """Raised when storage operations fail."""
    
    def __init__(self, operation: str, reason: str):
        super().__init__(
            message=f"Storage operation '{operation}' failed: {reason}",
            error_code="STORAGE_ERROR",
            details={"operation": operation, "reason": reason}
        )


class ExternalServiceError(FireForgetException):
    """Raised when external service calls fail."""
    
    def __init__(self, service: str, reason: str):
        super().__init__(
            message=f"External service '{service}' failed: {reason}",
            error_code="EXTERNAL_SERVICE_ERROR",
            details={"service": service, "reason": reason}
        )


# HTTP Exception mappings
EXCEPTION_TO_HTTP_STATUS = {
    DocumentNotFoundError: status.HTTP_404_NOT_FOUND,
    PipelineRunNotFoundError: status.HTTP_404_NOT_FOUND,
    JournalEntryNotFoundError: status.HTTP_404_NOT_FOUND,
    PolicyNotFoundError: status.HTTP_404_NOT_FOUND,
    BASAccountNotFoundError: status.HTTP_404_NOT_FOUND,
    InvalidDocumentFormatError: status.HTTP_400_BAD_REQUEST,
    ValidationError: status.HTTP_422_UNPROCESSABLE_ENTITY,
    DocumentProcessingError: status.HTTP_422_UNPROCESSABLE_ENTITY,
    IntentDetectionError: status.HTTP_422_UNPROCESSABLE_ENTITY,
    PolicyMatchingError: status.HTTP_422_UNPROCESSABLE_ENTITY,
    BookingCreationError: status.HTTP_422_UNPROCESSABLE_ENTITY,
    DatabaseError: status.HTTP_500_INTERNAL_SERVER_ERROR,
    StorageError: status.HTTP_500_INTERNAL_SERVER_ERROR,
    ExternalServiceError: status.HTTP_502_BAD_GATEWAY,
}


def create_http_exception(exc: FireForgetException) -> HTTPException:
    """Convert FireForgetException to HTTPException."""
    status_code = EXCEPTION_TO_HTTP_STATUS.get(type(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return HTTPException(
        status_code=status_code,
        detail={
            "message": exc.message,
            "error_code": exc.error_code,
            "details": exc.details
        }
    )
