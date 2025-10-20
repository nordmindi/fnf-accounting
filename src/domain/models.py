"""Domain models for Fire & Forget AI Accounting."""

from datetime import date as Date, datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Literal, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class StoplightDecision(str, Enum):
    """Stoplight decision states."""
    GREEN = "GREEN"  # Auto-book
    YELLOW = "YELLOW"  # Ask one question
    RED = "RED"  # Park for manual review


class Currency(str, Enum):
    """Supported currencies."""
    SEK = "SEK"
    NOK = "NOK"
    DKK = "DKK"
    EUR = "EUR"
    USD = "USD"


class VATLine(BaseModel):
    """VAT line from a receipt."""
    rate: Decimal = Field(..., decimal_places=2)
    amount: Decimal = Field(..., decimal_places=2)
    base_amount: Decimal = Field(..., decimal_places=2)
    
    class Config:
        json_encoders = {
            Decimal: str,
        }


class ReceiptDoc(BaseModel):
    """Normalized receipt document from OCR extraction."""
    total: Decimal = Field(..., decimal_places=2, description="Total amount including VAT")
    currency: Currency = Field(..., description="Currency code")
    vat_lines: List[VATLine] = Field(default_factory=list, description="VAT breakdown")
    vendor: Optional[str] = Field(None, description="Vendor name")
    date: Date = Field(..., description="Receipt date")
    raw_text: Optional[str] = Field(None, description="Raw OCR text")
    confidence: float = Field(..., ge=0.0, le=1.0, description="OCR confidence score")
    
    class Config:
        json_encoders = {
            Decimal: str,
            Date: lambda v: v.isoformat(),
        }


class Intent(BaseModel):
    """Intent detection result from NLU service."""
    name: str = Field(..., description="Intent name (e.g., 'representation_meal')")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Intent confidence score")
    slots: Dict[str, Any] = Field(default_factory=dict, description="Extracted slots")
    
    class Config:
        json_encoders = {
            Decimal: str,
        }


class PostingLine(BaseModel):
    """Single posting line for journal entry."""
    account: str = Field(..., description="Account code")
    side: Literal["D", "K"] = Field(..., description="Debit (D) or Credit (K)")
    amount: Decimal = Field(..., decimal_places=2, description="Amount")
    dimension_project: Optional[str] = Field(None, description="Project dimension")
    dimension_cost_center: Optional[str] = Field(None, description="Cost center dimension")
    description: Optional[str] = Field(None, description="Line description")
    
    class Config:
        json_encoders = {
            Decimal: str,
        }


class PostingProposal(BaseModel):
    """Posting proposal from rule engine."""
    lines: List[PostingLine] = Field(..., description="Journal entry lines")
    vat_code: Optional[str] = Field(None, description="VAT code")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Proposal confidence")
    reason_codes: List[str] = Field(default_factory=list, description="Reason codes for decision")
    stoplight: StoplightDecision = Field(..., description="Stoplight decision")
    policy_id: Optional[str] = Field(None, description="Applied policy ID")
    vat_mode: Optional[str] = Field(None, description="VAT mode: 'reverse_charge' or 'standard'")
    report_boxes: Optional[Dict[str, str]] = Field(None, description="VAT report boxes mapping")
    
    class Config:
        json_encoders = {
            Decimal: str,
        }


class JournalEntry(BaseModel):
    """Journal entry model."""
    id: UUID = Field(default_factory=uuid4, description="Unique identifier")
    company_id: UUID = Field(..., description="Company identifier")
    date: Date = Field(..., description="Posting date")
    series: str = Field(..., description="Journal series")
    number: str = Field(..., description="Journal number")
    notes: Optional[str] = Field(None, description="Entry notes")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    created_by: Optional[UUID] = Field(None, description="User who created the entry")
    
    class Config:
        json_encoders = {
            UUID: str,
            Date: lambda v: v.isoformat(),
            datetime: lambda v: v.isoformat(),
        }


class JournalLine(BaseModel):
    """Journal line model."""
    id: UUID = Field(default_factory=uuid4, description="Unique identifier")
    entry_id: UUID = Field(..., description="Parent journal entry ID")
    account: str = Field(..., description="Account code")
    side: Literal["D", "K"] = Field(..., description="Debit (D) or Credit (K)")
    amount: Decimal = Field(..., decimal_places=2, description="Amount")
    dimension_project: Optional[str] = Field(None, description="Project dimension")
    dimension_cost_center: Optional[str] = Field(None, description="Cost center dimension")
    description: Optional[str] = Field(None, description="Line description")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    
    class Config:
        json_encoders = {
            UUID: str,
            Decimal: str,
            datetime: lambda v: v.isoformat(),
        }


class Document(BaseModel):
    """Document model for uploaded files."""
    id: UUID = Field(default_factory=uuid4, description="Unique identifier")
    company_id: UUID = Field(..., description="Company identifier")
    filename: str = Field(..., description="Original filename")
    content_type: str = Field(..., description="MIME type")
    size: int = Field(..., description="File size in bytes")
    storage_key: str = Field(..., description="Storage key in S3/MinIO")
    hash: str = Field(..., description="File hash for deduplication")
    uploaded_at: datetime = Field(default_factory=datetime.utcnow, description="Upload timestamp")
    uploaded_by: Optional[UUID] = Field(None, description="User who uploaded the file")
    
    class Config:
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat(),
        }


class PipelineRun(BaseModel):
    """Pipeline execution model."""
    id: UUID = Field(default_factory=uuid4, description="Unique identifier")
    document_id: UUID = Field(..., description="Source document ID")
    company_id: UUID = Field(..., description="Company identifier")
    status: Literal["pending", "running", "completed", "failed"] = Field(
        default="pending", description="Pipeline status"
    )
    current_step: Optional[str] = Field(None, description="Current pipeline step")
    receipt_doc: Optional[ReceiptDoc] = Field(None, description="Extracted receipt data")
    intent: Optional[Intent] = Field(None, description="Detected intent")
    proposal: Optional[PostingProposal] = Field(None, description="Posting proposal")
    journal_entry_id: Optional[UUID] = Field(None, description="Created journal entry ID")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    started_at: Optional[datetime] = Field(None, description="Pipeline start time")
    completed_at: Optional[datetime] = Field(None, description="Pipeline completion time")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    
    class Config:
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat(),
            Decimal: str,
            Date: lambda v: v.isoformat(),
        }


class Policy(BaseModel):
    """Policy model for rule engine."""
    id: str = Field(..., description="Policy identifier")
    version: str = Field(..., description="Policy version")
    country: str = Field(..., description="Country code (SE, NO, DK, FI)")
    effective_from: Date = Field(..., description="Policy effective date")
    effective_to: Optional[Date] = Field(None, description="Policy end date")
    name: str = Field(..., description="Policy name")
    description: Optional[str] = Field(None, description="Policy description")
    rules: Dict[str, Any] = Field(..., description="Policy rules in DSL format")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    created_by: Optional[UUID] = Field(None, description="User who created the policy")
    
    class Config:
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat(),
            Date: lambda v: v.isoformat(),
        }
