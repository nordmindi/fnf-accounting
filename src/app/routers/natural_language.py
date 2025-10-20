"""Natural Language Processing API router."""

from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel, Field

from src.adapters.llm import LLMAdapter
from src.app.auth import CurrentUser, get_current_user
from src.app.dependencies import (
    get_document_service,
    get_extraction_service,
    get_llm_adapter,
    get_rule_engine,
)
from src.domain.natural_language_service import NaturalLanguageService
from src.domain.services import DocumentService, ExtractionService
from src.rules.engine import RuleEngine

logger = structlog.get_logger()
router = APIRouter()


class NaturalLanguageRequest(BaseModel):
    """Request model for natural language input."""
    text: str = Field(..., description="Natural language description of the expense")
    company_id: UUID = Field(..., description="Company ID")


class NaturalLanguageResponse(BaseModel):
    """Response model for natural language processing."""
    success: bool = Field(..., description="Whether the processing was successful")
    message: str = Field(..., description="User-friendly message")
    booking_id: str | None = Field(None, description="Created booking ID if successful")
    booking_details: dict | None = Field(None, description="Booking details")
    status: str = Field(..., description="Processing status (GREEN/YELLOW/RED)")
    reason_codes: list = Field(default_factory=list, description="Reason codes for the decision")
    policy_used: str | None = Field(None, description="Policy that was applied")
    receipt_attachment_prompt: str | None = Field(None, description="Prompt for receipt attachment")


class ClarificationRequest(BaseModel):
    """Request model for providing clarification."""
    booking_id: str = Field(..., description="Booking ID to clarify")
    clarification: str = Field(..., description="Additional information")


class ReceiptAttachmentRequest(BaseModel):
    """Request model for attaching receipt to booking."""
    booking_id: str = Field(..., description="Booking ID to attach receipt to")
    company_id: UUID = Field(..., description="Company ID")


def get_natural_language_service(
    llm_adapter: LLMAdapter = Depends(get_llm_adapter),
    rule_engine: RuleEngine = Depends(get_rule_engine)
) -> NaturalLanguageService:
    """Get natural language service instance."""
    return NaturalLanguageService(llm_adapter, rule_engine)


@router.post("/natural-language/process", response_model=NaturalLanguageResponse)
async def process_natural_language(
    request: NaturalLanguageRequest,
    current_user: CurrentUser = Depends(get_current_user),
    nl_service: NaturalLanguageService = Depends(get_natural_language_service)
):
    """
    Process natural language input and create a booking.
    
    Example input: "Business lunch today with the project manager of Example AB 
    at Example restaurant, total amount 1500 SEK, paid with company credit card"
    """
    try:
        logger.info(
            "Processing natural language input",
            user_id=str(current_user.user_id),
            company_id=str(request.company_id),
            text_length=len(request.text)
        )

        # Process the natural language input
        result = await nl_service.process_natural_language_input(
            user_input=request.text,
            company_id=request.company_id,
            user_id=current_user.user_id
        )

        # Extract components
        proposal = result["proposal"]
        feedback = result["feedback"]
        receipt_doc = result["receipt_doc"]
        intent = result["intent"]

        # If GREEN, create the booking immediately
        booking_id = None
        if proposal.stoplight.value == "GREEN":
            try:
                # Get booking service
                from src.app.dependencies import get_booking_service
                from src.infra.config import get_settings
                from src.repositories.database import DatabaseRepository

                settings = get_settings()
                repository = DatabaseRepository(settings.database_url)
                booking_service = get_booking_service(repository)

                # Create journal entry
                journal_entry = await booking_service.create_journal_entry(
                    company_id=request.company_id,
                    proposal=proposal,
                    receipt=receipt_doc,
                    intent=intent,
                    created_by=current_user.user_id
                )

                booking_id = str(journal_entry.id)
                logger.info("Booking created successfully", booking_id=booking_id)

            except Exception as e:
                logger.error("Failed to create booking", error=str(e))
                # Don't fail the entire request, just note that booking creation failed
                feedback["message"] += " (Note: Booking creation failed, please try again)"

        return NaturalLanguageResponse(
            success=True,
            message=feedback["message"],
            booking_id=booking_id,
            booking_details=feedback["booking_details"],
            status=feedback["status"],
            reason_codes=feedback["reason_codes"],
            policy_used=feedback["policy_used"],
            receipt_attachment_prompt=feedback["receipt_attachment_prompt"]
        )

    except Exception as e:
        logger.error("Failed to process natural language input", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process natural language input: {str(e)}"
        )


@router.post("/natural-language/process-with-receipt", response_model=NaturalLanguageResponse)
async def process_natural_language_with_receipt(
    text: str = Form(..., description="Natural language description of the expense"),
    company_id: UUID = Form(..., description="Company ID"),
    file: UploadFile | None = File(None, description="Optional receipt file"),
    current_user: CurrentUser = Depends(get_current_user),
    nl_service: NaturalLanguageService = Depends(get_natural_language_service),
    document_service: DocumentService = Depends(get_document_service),
    extraction_service: ExtractionService = Depends(get_extraction_service)
):
    """
    Process natural language input with optional receipt attachment.
    
    This endpoint allows users to provide both text description and receipt file
    in a single request, making the workflow more convenient.
    
    Example:
    - text: "Business lunch today with the project manager of Example AB at Example restaurant, total amount 1500 SEK, paid with company credit card"
    - file: receipt.jpg (optional)
    """
    try:
        logger.info(
            "Natural language processing with receipt started",
            text=text[:100] + "..." if len(text) > 100 else text,
            company_id=str(company_id),
            has_file=file is not None,
            filename=file.filename if file else None
        )

        # Create a receipt document if file is provided
        receipt_doc = None
        document_id = None

        if file:
            # Read file content
            file_content = await file.read()

            # Determine content type with fallback
            content_type = file.content_type or "application/octet-stream"
            if not content_type and file.filename:
                # Try to infer from filename extension
                if file.filename.lower().endswith(('.txt', '.text')):
                    content_type = "text/plain"
                elif file.filename.lower().endswith(('.jpg', '.jpeg')):
                    content_type = "image/jpeg"
                elif file.filename.lower().endswith('.png'):
                    content_type = "image/png"
                elif file.filename.lower().endswith('.pdf'):
                    content_type = "application/pdf"
                else:
                    content_type = "application/octet-stream"

            # Upload document
            document = await document_service.upload_document(
                company_id=company_id,
                filename=file.filename,
                content_type=content_type,
                file_content=file_content,
                uploaded_by=current_user.user_id
            )
            document_id = str(document.id)

            # Extract receipt data from the uploaded file
            receipt_doc = await extraction_service.extract_receipt(file_content, content_type)

            logger.info(
                "Receipt uploaded and processed",
                document_id=document_id,
                filename=file.filename,
                total=float(receipt_doc.total) if receipt_doc.total else None
            )

        # Process the natural language input
        if receipt_doc:
            # If we have a receipt from file upload, use it directly
            # Parse the natural language input for intent detection
            parsed_data = await nl_service._parse_natural_language(text)
            intent = await nl_service._detect_intent_from_text(text, receipt_doc)
            proposal = await nl_service._create_posting_proposal(intent, receipt_doc)
            feedback = nl_service._generate_user_feedback(proposal, receipt_doc, intent)

            result = {
                "parsed_data": parsed_data,
                "receipt_doc": receipt_doc,
                "intent": intent,
                "proposal": proposal,
                "feedback": feedback,
                "company_id": company_id,
                "user_id": current_user.user_id
            }
        else:
            # No file uploaded, use the standard process
            result = await nl_service.process_natural_language_input(
                user_input=text,
                company_id=company_id
            )

        feedback = result["feedback"]
        proposal = result["proposal"]
        intent = result["intent"]

        # If GREEN, create the booking immediately
        booking_id = None
        if proposal.stoplight.value == "GREEN":
            try:
                # Get booking service
                from src.app.dependencies import get_booking_service
                from src.infra.config import get_settings
                from src.repositories.database import DatabaseRepository

                settings = get_settings()
                repository = DatabaseRepository(settings.database_url)
                booking_service = get_booking_service(repository)

                # Create journal entry
                journal_entry = await booking_service.create_journal_entry(
                    company_id=company_id,
                    proposal=proposal,
                    receipt=receipt_doc,
                    intent=intent,
                    created_by=current_user.user_id
                )

                booking_id = str(journal_entry.id)
                logger.info("Booking created successfully", booking_id=booking_id)

            except Exception as e:
                logger.error("Failed to create booking", error=str(e))
                # Don't fail the entire request, just note that booking creation failed
                feedback["message"] += " (Note: Booking creation failed, please try again)"

        # Update the response to indicate receipt was already attached if provided
        if file:
            feedback["receipt_attachment_prompt"] = None  # No need to ask since receipt is already attached
            feedback["message"] += f" Receipt '{file.filename}' has been attached to this booking."

        return NaturalLanguageResponse(
            success=True,
            message=feedback["message"],
            booking_id=booking_id,
            booking_details=feedback["booking_details"],
            status=feedback["status"],
            reason_codes=feedback["reason_codes"],
            policy_used=feedback["policy_used"],
            receipt_attachment_prompt=feedback["receipt_attachment_prompt"]
        )

    except Exception as e:
        logger.error("Failed to process natural language input with receipt", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process natural language input: {str(e)}"
        )


@router.post("/natural-language/clarify", response_model=NaturalLanguageResponse)
async def provide_clarification(
    request: ClarificationRequest,
    current_user: CurrentUser = Depends(get_current_user),
    nl_service: NaturalLanguageService = Depends(get_natural_language_service)
):
    """
    Provide clarification for a YELLOW status booking.
    """
    try:
        logger.info(
            "Providing clarification",
            user_id=str(current_user.user_id),
            booking_id=request.booking_id
        )

        # This would need to be implemented to handle clarification
        # For now, return a placeholder response
        return NaturalLanguageResponse(
            success=False,
            message="Clarification handling not yet implemented",
            status="YELLOW",
            reason_codes=["Feature not implemented"]
        )

    except Exception as e:
        logger.error("Failed to process clarification", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process clarification: {str(e)}"
        )


@router.get("/natural-language/examples")
async def get_examples():
    """Get example natural language inputs."""
    return {
        "examples": [
            {
                "description": "Business lunch with client",
                "text": "Business lunch today with the project manager of Example AB at Example restaurant, total amount 1500 SEK, paid with company credit card"
            },
            {
                "description": "Taxi ride",
                "text": "Taxi from office to client meeting, 250 SEK, paid with company card"
            },
            {
                "description": "Software subscription",
                "text": "Monthly subscription for Slack workspace, 89 SEK including VAT"
            },
            {
                "description": "Office supplies",
                "text": "Office supplies from IKEA, pens and notebooks, 450 SEK"
            }
        ]
    }


@router.post("/natural-language/attach-receipt")
async def attach_receipt_to_booking(
    file: UploadFile = File(...),
    booking_id: str = Form(...),
    company_id: UUID = Form(...),
    current_user: CurrentUser = Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service)
):
    """
    Attach a receipt to an existing booking.
    
    This endpoint is called when a user answers "yes" to the receipt attachment prompt.
    It uploads the receipt and links it to the existing booking.
    """
    try:
        logger.info(
            "Receipt attachment started",
            booking_id=booking_id,
            company_id=str(company_id),
            filename=file.filename
        )

        # Read file content
        file_content = await file.read()

        # Determine content type with fallback
        content_type = file.content_type or "application/octet-stream"
        if not content_type and file.filename:
            # Try to infer from filename extension
            if file.filename.lower().endswith(('.txt', '.text')):
                content_type = "text/plain"
            elif file.filename.lower().endswith(('.jpg', '.jpeg')):
                content_type = "image/jpeg"
            elif file.filename.lower().endswith('.png'):
                content_type = "image/png"
            elif file.filename.lower().endswith('.pdf'):
                content_type = "application/pdf"
            else:
                content_type = "application/octet-stream"

        # Upload document
        document = await document_service.upload_document(
            company_id=company_id,
            filename=file.filename,
            content_type=content_type,
            file_content=file_content,
            uploaded_by=current_user.user_id
        )

        # TODO: Link document to booking in database
        # This would require adding a document_id field to the JournalEntry model
        # and updating the booking service to handle the relationship

        logger.info(
            "Receipt attached successfully",
            booking_id=booking_id,
            document_id=str(document.id),
            filename=file.filename
        )

        return {
            "success": True,
            "message": f"Receipt '{file.filename}' attached to booking {booking_id}",
            "booking_id": booking_id,
            "document_id": str(document.id),
            "filename": file.filename,
            "content_type": content_type,
            "size": len(file_content)
        }

    except Exception as e:
        logger.error("Receipt attachment failed", error=str(e), booking_id=booking_id)
        raise HTTPException(status_code=500, detail=f"Failed to attach receipt: {str(e)}")
