"""Mock booking service for testing and demonstration purposes."""

from datetime import datetime
from uuid import UUID, uuid4

from src.app.dto import BookingResponse, JournalEntryResponse
from src.domain.models import Intent, PostingProposal, ReceiptDoc


class MockBookingService:
    """Mock booking service that provides sample data for testing."""

    def __init__(self):
        # In-memory storage for mock data
        self._bookings: dict[str, BookingResponse] = {}
        self._pipeline_to_booking: dict[str, str] = {}
        self._booking_counter = 1

        # Initialize with sample data
        self._initialize_sample_data()

    def _initialize_sample_data(self):
        """Initialize with sample booking data."""
        sample_booking_id = "550e8400-e29b-41d4-a716-446655440010"
        sample_booking = BookingResponse(
            journal_entry=JournalEntryResponse(
                id=UUID(sample_booking_id),
                posting_date=datetime(2024, 1, 15).date(),
                series="AI",
                number="000001",
                notes="AI booking: representation_meal - Restaurant ABC",
                created_at=datetime(2024, 1, 15, 10, 30, 0)
            ),
            receipt={
                "total": "1008.00",
                "currency": "SEK",
                "vendor": "Restaurant ABC",
                "receipt_date": "2024-01-15",
                "confidence": 0.9
            },
            intent={
                "name": "representation_meal",
                "confidence": 0.9,
                "slots": {
                    "attendees_count": 3,
                    "purpose": "Business lunch with client"
                }
            },
            proposal={
                "lines": [
                    {
                        "account": "6071",
                        "side": "D",
                        "amount": "900.00",
                        "description": "Representation meals"
                    },
                    {
                        "account": "2641",
                        "side": "D",
                        "amount": "108.00",
                        "description": "VAT on representation"
                    },
                    {
                        "account": "1930",
                        "side": "K",
                        "amount": "1008.00",
                        "description": "Cash/Bank"
                    }
                ],
                "vat_code": "12",
                "confidence": 0.9,
                "reason_codes": ["Policy: SE_REPR_MEAL_V1", "VAT cap applied"],
                "stoplight": "GREEN",
                "policy_id": "SE_REPR_MEAL_V1"
            }
        )

        self._bookings[sample_booking_id] = sample_booking

    async def create_booking_from_pipeline(
        self,
        pipeline_run_id: str,
        company_id: UUID,
        proposal: PostingProposal,
        receipt: ReceiptDoc,
        intent: Intent,
        created_by: UUID | None = None
    ) -> BookingResponse:
        """Create a mock booking from pipeline results."""
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
        """Get mock booking by ID."""
        return self._bookings.get(str(booking_id))

    async def get_booking_by_pipeline_run(self, pipeline_run_id: str) -> BookingResponse | None:
        """Get mock booking by pipeline run ID."""
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
        """List mock bookings for a company."""
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
        """Get recent mock bookings for display."""
        bookings = list(self._bookings.values())
        bookings.sort(key=lambda x: x.journal_entry.created_at, reverse=True)
        return bookings[:limit]
