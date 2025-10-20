"""Factory for creating booking services based on configuration."""


from src.app.mock_booking_service import MockBookingService
from src.app.real_booking_service import RealBookingService
from src.infra.config import get_settings


class BookingServiceFactory:
    """Factory for creating booking services."""

    @staticmethod
    def create_booking_service() -> MockBookingService | RealBookingService:
        """Create a booking service based on configuration."""
        settings = get_settings()

        if settings.use_mock_data:
            return MockBookingService()
        else:
            return RealBookingService()
