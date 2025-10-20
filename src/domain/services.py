"""Domain services for business logic."""

import hashlib
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from src.domain.models import (
    Document,
    Intent,
    JournalEntry,
    JournalLine,
    PipelineRun,
    PostingProposal,
    ReceiptDoc,
    StoplightDecision,
)


class DocumentService:
    """Service for document management."""
    
    def __init__(self, storage_adapter, repository):
        self.storage = storage_adapter
        self.repository = repository
    
    async def upload_document(
        self,
        company_id: UUID,
        filename: str,
        content_type: str,
        file_content: bytes,
        uploaded_by: Optional[UUID] = None
    ) -> Document:
        """Upload and store a document."""
        # Calculate file hash for deduplication
        file_hash = hashlib.sha256(file_content).hexdigest()
        
        # Check for duplicates
        existing = await self.repository.find_document_by_hash(file_hash)
        if existing:
            return existing
        
        # Store in object storage
        storage_key = f"{company_id}/{datetime.utcnow().strftime('%Y/%m/%d')}/{filename}"
        await self.storage.store_file(storage_key, file_content, content_type)
        
        # Create document record
        document = Document(
            company_id=company_id,
            filename=filename,
            content_type=content_type,
            size=len(file_content),
            storage_key=storage_key,
            hash=file_hash,
            uploaded_by=uploaded_by
        )
        
        return await self.repository.save_document(document)
    
    async def get_document(self, document_id: UUID) -> Optional[Document]:
        """Get document by ID."""
        return await self.repository.get_document(document_id)
    
    async def download_document(self, document: Document) -> bytes:
        """Download document content."""
        return await self.storage.get_file(document.storage_key)
    
    async def list_documents(self, company_id: UUID, limit: int = 50, offset: int = 0) -> List[Document]:
        """List documents for a company."""
        return await self.repository.list_documents(company_id, limit, offset)


class ExtractionService:
    """Service for OCR and document extraction."""
    
    def __init__(self, ocr_adapter):
        self.ocr = ocr_adapter
    
    async def extract_receipt(self, file_content: bytes, content_type: str) -> ReceiptDoc:
        """Extract receipt data from document."""
        # Use OCR adapter to extract text and structured data
        extraction_result = await self.ocr.extract_receipt(file_content, content_type)
        
        return ReceiptDoc(
            total=extraction_result["total"],
            currency=extraction_result["currency"],
            vat_lines=extraction_result["vat_lines"],
            vendor=extraction_result.get("vendor"),
            date=extraction_result["date"],
            raw_text=extraction_result.get("raw_text"),
            confidence=extraction_result["confidence"]
        )


class NLUService:
    """Service for natural language understanding."""
    
    def __init__(self, llm_adapter):
        self.llm = llm_adapter
    
    async def detect_intent(
        self, 
        receipt: ReceiptDoc, 
        user_text: Optional[str] = None
    ) -> Intent:
        """Detect intent and extract slots from receipt and user text."""
        # Combine receipt data and user text for intent detection
        context = {
            "receipt": {
                "vendor": receipt.vendor,
                "total": float(receipt.total),
                "currency": receipt.currency,
                "date": receipt.date.isoformat(),
                "raw_text": receipt.raw_text
            },
            "user_text": user_text or ""
        }
        
        # Use LLM adapter for intent detection
        intent_result = await self.llm.detect_intent(context)
        
        return Intent(
            name=intent_result["intent"],
            confidence=intent_result["confidence"],
            slots=intent_result["slots"]
        )


class ProposalService:
    """Service for creating posting proposals."""
    
    def __init__(self, rule_engine):
        self.rule_engine = rule_engine
    
    async def create_proposal(
        self, 
        intent: Intent, 
        receipt: ReceiptDoc
    ) -> PostingProposal:
        """Create posting proposal using rule engine."""
        # Find matching policies
        policy_matches = self.rule_engine.find_matching_policies(intent, receipt)
        
        if not policy_matches:
            return PostingProposal(
                lines=[],
                vat_code=None,
                confidence=0.0,
                reason_codes=["No matching policy found"],
                stoplight=StoplightDecision.RED,
                policy_id=None
            )
        
        # Use the best matching policy
        best_match = policy_matches[0]
        return self.rule_engine.create_posting_proposal(best_match, intent, receipt)


class StoplightService:
    """Service for stoplight decision logic."""
    
    def __init__(self, config):
        self.config = config
    
    def decide_stoplight(
        self, 
        proposal: PostingProposal, 
        intent: Intent, 
        receipt: ReceiptDoc
    ) -> StoplightDecision:
        """Make final stoplight decision."""
        # If proposal already has a decision, use it
        if proposal.stoplight != StoplightDecision.GREEN:
            return proposal.stoplight
        
        # Apply additional business rules
        confidence_threshold = self.config.get("confidence_threshold", 0.8)
        
        if proposal.confidence < confidence_threshold:
            return StoplightDecision.YELLOW
        
        # Check for high-value transactions
        high_value_threshold = self.config.get("high_value_threshold", 10000)
        if receipt.total > high_value_threshold:
            return StoplightDecision.YELLOW
        
        return StoplightDecision.GREEN
    
    def generate_question(self, proposal: PostingProposal) -> Optional[str]:
        """Generate clarifying question for YELLOW decisions."""
        if proposal.stoplight != StoplightDecision.YELLOW:
            return None
        
        # Find the most important missing information
        if "attendees_count" in proposal.reason_codes:
            return "How many people attended this meal?"
        
        if "purpose" in proposal.reason_codes:
            return "What was the business purpose of this expense?"
        
        if "project" in proposal.reason_codes:
            return "Which project should this expense be charged to?"
        
        return "Please provide additional details for this expense."


class PolicyService:
    """Service for policy management."""
    
    def __init__(self, repository):
        self.repository = repository
    
    async def get_active_policies(self, country: str) -> List[dict]:
        """Get active policies for a country."""
        return await self.repository.get_active_policies(country)
    
    async def get_policy(self, policy_id: str) -> Optional[dict]:
        """Get policy by ID."""
        return await self.repository.get_policy(policy_id)
    
    async def create_policy(self, policy_data: dict) -> dict:
        """Create a new policy."""
        return await self.repository.create_policy(policy_data)
    
    async def update_policy(self, policy_id: str, policy_data: dict) -> dict:
        """Update an existing policy."""
        return await self.repository.update_policy(policy_id, policy_data)


class BookingService:
    """Service for creating journal entries."""
    
    def __init__(self, repository):
        self.repository = repository
    
    async def create_journal_entry(
        self,
        company_id: UUID,
        proposal: PostingProposal,
        receipt: ReceiptDoc,
        intent: Intent,
        created_by: Optional[UUID] = None
    ) -> JournalEntry:
        """Create journal entry from posting proposal."""
        # Generate journal number
        series = "AI"  # AI-generated entries
        number = await self._generate_journal_number(company_id, series)
        
        # Create journal entry
        entry = JournalEntry(
            company_id=company_id,
            date=receipt.date,
            series=series,
            number=number,
            notes=f"AI booking: {intent.name} - {receipt.vendor}",
            created_by=created_by
        )
        
        # Create journal lines
        lines = []
        for posting_line in proposal.lines:
            line = JournalLine(
                entry_id=entry.id,
                account=posting_line.account,
                side=posting_line.side,
                amount=posting_line.amount,
                dimension_project=posting_line.dimension_project,
                dimension_cost_center=posting_line.dimension_cost_center,
                description=posting_line.description
            )
            lines.append(line)
        
        # Save to database
        saved_entry = await self.repository.save_journal_entry(entry, lines)
        return saved_entry
    
    async def _generate_journal_number(self, company_id: UUID, series: str) -> str:
        """Generate next journal number for series."""
        last_number = await self.repository.get_last_journal_number(company_id, series)
        return str(int(last_number or "0") + 1).zfill(6)
    
    async def get_journal_entry(self, entry_id: UUID) -> Optional[JournalEntry]:
        """Get journal entry by ID."""
        return await self.repository.get_journal_entry(entry_id)
    
    async def list_journal_entries(self, company_id: UUID, limit: int = 50, offset: int = 0) -> List[JournalEntry]:
        """List journal entries for a company."""
        return await self.repository.list_journal_entries(company_id, limit, offset)


class ReasonService:
    """Service for generating reason codes and explanations."""
    
    def generate_reason_codes(
        self, 
        proposal: PostingProposal, 
        intent: Intent, 
        receipt: ReceiptDoc
    ) -> List[str]:
        """Generate comprehensive reason codes."""
        codes = []
        
        # Policy information
        if proposal.policy_id:
            codes.append(f"Policy: {proposal.policy_id}")
        
        # Intent information
        codes.append(f"Intent: {intent.name} (confidence: {intent.confidence:.2f})")
        
        # VAT information
        if proposal.vat_code:
            codes.append(f"VAT: {proposal.vat_code}")
        
        # Amount information
        if receipt.total > 1000:
            codes.append("High value transaction")
        
        # Vendor information
        if receipt.vendor:
            codes.append(f"Vendor: {receipt.vendor}")
        
        # Add existing reason codes
        codes.extend(proposal.reason_codes)
        
        return codes
    
    def generate_explanation(self, proposal: PostingProposal) -> str:
        """Generate human-readable explanation."""
        if proposal.stoplight == StoplightDecision.GREEN:
            return f"Automatically booked using policy {proposal.policy_id}"
        elif proposal.stoplight == StoplightDecision.YELLOW:
            return f"Requires clarification for policy {proposal.policy_id}"
        else:
            return f"Manual review required: {', '.join(proposal.reason_codes)}"


class PolicyService:
    """Service for policy management."""
    
    def __init__(self, repository):
        self.repository = repository
    
    async def get_active_policies(self, country: str) -> List[dict]:
        """Get active policies for country."""
        return await self.repository.get_active_policies(country)
    
    async def validate_policy(self, policy_data: dict) -> bool:
        """Validate policy against schema."""
        from src.rules.schemas import POLICY_SCHEMA
        import jsonschema
        
        try:
            jsonschema.validate(policy_data, POLICY_SCHEMA)
            return True
        except jsonschema.ValidationError:
            return False
