"""Data Transfer Objects for API."""

from datetime import date as Date, datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class DocumentUploadRequest(BaseModel):
    """Request for document upload."""
    filename: str = Field(..., description="Original filename")
    content_type: str = Field(..., description="MIME type")
    user_text: Optional[str] = Field(None, description="User instruction or context")


class DocumentUploadResponse(BaseModel):
    """Response for document upload."""
    document_id: UUID = Field(..., description="Document ID")
    pipeline_run_id: UUID = Field(..., description="Pipeline run ID")
    status: str = Field(..., description="Upload status")


class DocumentResponse(BaseModel):
    """Document response."""
    id: UUID = Field(..., description="Document ID")
    filename: str = Field(..., description="Filename")
    content_type: str = Field(..., description="MIME type")
    size: int = Field(..., description="File size in bytes")
    uploaded_at: datetime = Field(..., description="Upload timestamp")
    
    class Config:
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat(),
        }


class PipelineStartRequest(BaseModel):
    """Request to start pipeline."""
    document_id: UUID = Field(..., description="Document ID")
    user_text: Optional[str] = Field(None, description="User instruction")


class PipelineResponse(BaseModel):
    """Pipeline run response."""
    id: UUID = Field(..., description="Pipeline run ID")
    document_id: UUID = Field(..., description="Document ID")
    status: str = Field(..., description="Pipeline status")
    current_step: Optional[str] = Field(None, description="Current step")
    started_at: Optional[datetime] = Field(None, description="Start time")
    completed_at: Optional[datetime] = Field(None, description="Completion time")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    booking_id: Optional[UUID] = Field(None, description="Booking ID if booking was created")
    
    class Config:
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat(),
        }


class ReceiptDocResponse(BaseModel):
    """Receipt document response."""
    total: Decimal = Field(..., description="Total amount")
    currency: str = Field(..., description="Currency code")
    vendor: Optional[str] = Field(None, description="Vendor name")
    receipt_date: Date = Field(..., description="Receipt date")
    confidence: float = Field(..., description="OCR confidence")
    
    class Config:
        json_encoders = {
            Decimal: str,
            Date: lambda v: v.isoformat(),
        }


class IntentResponse(BaseModel):
    """Intent detection response."""
    name: str = Field(..., description="Intent name")
    confidence: float = Field(..., description="Intent confidence")
    slots: Dict[str, Any] = Field(..., description="Extracted slots")
    
    class Config:
        json_encoders = {
            Decimal: str,
        }


class PostingLineResponse(BaseModel):
    """Posting line response."""
    account: str = Field(..., description="Account code")
    side: str = Field(..., description="Debit (D) or Credit (K)")
    amount: Decimal = Field(..., description="Amount")
    dimension_project: Optional[str] = Field(None, description="Project dimension")
    dimension_cost_center: Optional[str] = Field(None, description="Cost center dimension")
    description: Optional[str] = Field(None, description="Line description")
    
    class Config:
        json_encoders = {
            Decimal: str,
        }


class PostingProposalResponse(BaseModel):
    """Posting proposal response."""
    lines: List[PostingLineResponse] = Field(..., description="Journal entry lines")
    vat_code: Optional[str] = Field(None, description="VAT code")
    confidence: float = Field(..., description="Proposal confidence")
    reason_codes: List[str] = Field(..., description="Reason codes")
    stoplight: str = Field(..., description="Stoplight decision")
    policy_id: Optional[str] = Field(None, description="Applied policy ID")


class JournalEntryResponse(BaseModel):
    """Journal entry response."""
    id: UUID = Field(..., description="Journal entry ID")
    posting_date: Date = Field(..., description="Posting date")
    series: str = Field(..., description="Journal series")
    number: str = Field(..., description="Journal number")
    notes: Optional[str] = Field(None, description="Entry notes")
    created_at: datetime = Field(..., description="Creation timestamp")
    
    class Config:
        json_encoders = {
            UUID: str,
            Date: lambda v: v.isoformat(),
            datetime: lambda v: v.isoformat(),
        }


class BookingResponse(BaseModel):
    """Booking response."""
    journal_entry: JournalEntryResponse = Field(..., description="Journal entry")
    receipt: ReceiptDocResponse = Field(..., description="Receipt data")
    intent: IntentResponse = Field(..., description="Detected intent")
    proposal: PostingProposalResponse = Field(..., description="Posting proposal")


class PolicyResponse(BaseModel):
    """Policy response."""
    id: str = Field(..., description="Policy ID")
    version: str = Field(..., description="Policy version")
    country: str = Field(..., description="Country code")
    effective_from: Date = Field(..., description="Effective date")
    effective_to: Optional[Date] = Field(None, description="End date")
    name: str = Field(..., description="Policy name")
    description: Optional[str] = Field(None, description="Policy description")
    
    class Config:
        json_encoders = {
            Date: lambda v: v.isoformat(),
        }


class ErrorResponse(BaseModel):
    """Error response."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Error details")
    code: Optional[str] = Field(None, description="Error code")
