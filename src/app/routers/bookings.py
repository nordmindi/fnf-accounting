"""Booking management API router."""

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
import structlog

from src.app.dto import BookingResponse, JournalEntryResponse, ErrorResponse
from src.app.dependencies import get_booking_service
from src.domain.services import BookingService

logger = structlog.get_logger()
router = APIRouter()


@router.get("/bookings/{booking_id}", response_model=JournalEntryResponse)
async def get_booking(
    booking_id: UUID,
    booking_service: BookingService = Depends(get_booking_service)
):
    """Get booking by ID."""
    try:
        booking = await booking_service.get_journal_entry(booking_id)
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        
        return JournalEntryResponse(
            id=booking.id,
            company_id=booking.company_id,
            date=booking.date,
            series=booking.series,
            number=booking.number,
            notes=booking.notes,
            created_at=booking.created_at,
            created_by=booking.created_by,
            lines=[
                {
                    "id": line.id,
                    "account": line.account,
                    "side": line.side,
                    "amount": float(line.amount),
                    "dimension_project": line.dimension_project,
                    "dimension_cost_center": line.dimension_cost_center,
                    "description": line.description
                }
                for line in booking.lines
            ]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get booking", booking_id=str(booking_id), error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/bookings", response_model=List[JournalEntryResponse])
async def list_bookings(
    company_id: UUID,
    limit: int = 50,
    offset: int = 0,
    booking_service: BookingService = Depends(get_booking_service)
):
    """List bookings for a company."""
    try:
        bookings = await booking_service.list_journal_entries(company_id, limit, offset)
        
        return [
            JournalEntryResponse(
                id=booking.id,
                company_id=booking.company_id,
                date=booking.date,
                series=booking.series,
                number=booking.number,
                notes=booking.notes,
                created_at=booking.created_at,
                created_by=booking.created_by,
                lines=[
                    {
                        "id": line.id,
                        "account": line.account,
                        "side": line.side,
                        "amount": float(line.amount),
                        "dimension_project": line.dimension_project,
                        "dimension_cost_center": line.dimension_cost_center,
                        "description": line.description
                    }
                    for line in booking.lines
                ]
            )
            for booking in bookings
        ]
        
    except Exception as e:
        logger.error("Failed to list bookings", company_id=str(company_id), error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/bookings/by-pipeline/{pipeline_run_id}", response_model=JournalEntryResponse)
async def get_booking_by_pipeline(
    pipeline_run_id: UUID,
    booking_service: BookingService = Depends(get_booking_service)
):
    """Get booking by pipeline run ID."""
    try:
        # Get pipeline run to find the journal entry ID
        from src.app.dependencies import get_pipeline_orchestrator
        from src.orchestrator.pipeline import PipelineOrchestrator
        
        # This would need to be injected properly, but for now we'll use a simple approach
        # In a real implementation, you'd inject the pipeline orchestrator
        raise HTTPException(status_code=501, detail="Not implemented yet - requires pipeline orchestrator injection")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get booking by pipeline", pipeline_run_id=pipeline_run_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
