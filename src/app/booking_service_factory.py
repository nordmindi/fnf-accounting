"""Factory for creating booking services based on configuration."""

from typing import Union

from src.infra.config import get_settings
from src.app.mock_booking_service import MockBookingService
from src.app.real_booking_service import RealBookingService


class BookingServiceFactory:
    """Factory for creating booking services."""
    
    @staticmethod
    def create_booking_service() -> Union[MockBookingService, RealBookingService]:
        """Create a booking service based on configuration."""
        settings = get_settings()
        
        if settings.use_mock_data:
            return MockBookingService()
        else:
            return RealBookingService()
