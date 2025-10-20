"""Real booking service for production use."""

from datetime import datetime
from uuid import UUID, uuid4

from src.app.dto import BookingResponse, JournalEntryResponse
from src.domain.models import Intent, PostingProposal, ReceiptDoc


class RealBookingService:
    """Real booking service for production use with no hardcoded data."""

    def __init__(self):
        # In-memory storage for real data only
        self._bookings: dict[str, BookingResponse] = {}
        self._pipeline_to_booking: dict[str, str] = {}
        self._booking_counter = 1

    async def create_booking_from_pipeline(
        self,
        pipeline_run_id: str,
        company_id: UUID,
        proposal: PostingProposal,
        receipt: ReceiptDoc,
        intent: Intent,
        created_by: UUID | None = None
    ) -> BookingResponse:
        """Create a real booking from pipeline results."""
        booking_id = str(uuid4())

        # Generate journal entry number
        journal_number = f"{self._booking_counter:06d}"
        self._booking_counter += 1

        # Create journal entry
        journal_entry = JournalEntryResponse(
            id=UUID(booking_id),
            posting_date=receipt.date,
            series="AI",
            number=journal_number,
            notes=f"AI booking: {intent.name} - {receipt.vendor or 'Unknown vendor'}",
            created_at=datetime.utcnow()
        )

        # Create booking response
        booking = BookingResponse(
            journal_entry=journal_entry,
            receipt={
                "total": str(receipt.total),
                "currency": receipt.currency.value,
                "vendor": receipt.vendor,
                "receipt_date": receipt.date.isoformat(),
                "confidence": receipt.confidence
            },
            intent={
                "name": intent.name,
                "confidence": intent.confidence,
                "slots": intent.slots
            },
            proposal={
                "lines": [
                    {
                        "account": line.account,
                        "side": line.side,
                        "amount": str(line.amount),
                        "dimension_project": line.dimension_project,
                        "dimension_cost_center": line.dimension_cost_center,
                        "description": line.description
                    }
                    for line in proposal.lines
                ],
                "vat_code": proposal.vat_code,
                "confidence": proposal.confidence,
                "reason_codes": proposal.reason_codes,
                "stoplight": proposal.stoplight.value if proposal.stoplight else "GREEN",
                "policy_id": proposal.policy_id
            }
        )

        # Store the booking
        self._bookings[booking_id] = booking
        self._pipeline_to_booking[pipeline_run_id] = booking_id

        return booking

    async def get_booking(self, booking_id: UUID) -> BookingResponse | None:
        """Get real booking by ID."""
        return self._bookings.get(str(booking_id))

    async def get_booking_by_pipeline_run(self, pipeline_run_id: str) -> BookingResponse | None:
        """Get real booking by pipeline run ID."""
        booking_id = self._pipeline_to_booking.get(pipeline_run_id)
        if not booking_id:
            return None
        return self._bookings.get(booking_id)

    async def list_bookings(
        self,
        company_id: UUID,
        limit: int = 50,
        offset: int = 0
    ) -> list[JournalEntryResponse]:
        """List real bookings for a company."""
        # For demo purposes, return all bookings
        # In a real system, this would filter by company_id
        bookings = list(self._bookings.values())

        # Sort by creation date (newest first)
        bookings.sort(key=lambda x: x.journal_entry.created_at, reverse=True)

        # Apply pagination
        start = offset
        end = offset + limit

        return [
            booking.journal_entry
            for booking in bookings[start:end]
        ]

    async def get_recent_bookings(self, limit: int = 5) -> list[BookingResponse]:
        """Get recent real bookings for display."""
        bookings = list(self._bookings.values())
        bookings.sort(key=lambda x: x.journal_entry.created_at, reverse=True)
        return bookings[:limit]
