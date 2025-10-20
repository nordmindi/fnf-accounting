"""Natural Language Processing API router."""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
import structlog

from src.app.auth import get_current_user, CurrentUser
from src.app.dependencies import get_llm_adapter, get_rule_engine
from src.domain.natural_language_service import NaturalLanguageService
from src.domain.services import BookingService
from src.adapters.llm import LLMAdapter
from src.rules.engine import RuleEngine
from src.infra.config import get_settings

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
    booking_id: Optional[str] = Field(None, description="Created booking ID if successful")
    booking_details: Optional[dict] = Field(None, description="Booking details")
    status: str = Field(..., description="Processing status (GREEN/YELLOW/RED)")
    reason_codes: list = Field(default_factory=list, description="Reason codes for the decision")
    policy_used: Optional[str] = Field(None, description="Policy that was applied")
    receipt_attachment_prompt: Optional[str] = Field(None, description="Prompt for receipt attachment")


class ClarificationRequest(BaseModel):
    """Request model for providing clarification."""
    booking_id: str = Field(..., description="Booking ID to clarify")
    clarification: str = Field(..., description="Additional information")


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
                from src.repositories.database import DatabaseRepository
                from src.infra.config import get_settings
                
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
