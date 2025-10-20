"""Simplified services for basic API functionality."""

import hashlib
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from src.domain.models import Document


class SimpleDocumentService:
    """Simplified document service for basic functionality."""
    
    async def upload_document(
        self,
        company_id: UUID,
        filename: str,
        content_type: str,
        file_content: bytes,
        uploaded_by: Optional[UUID] = None
    ) -> Document:
        """Upload and store a document (simplified version)."""
        # Calculate file hash for deduplication
        file_hash = hashlib.sha256(file_content).hexdigest()
        
        # Create document record (in-memory for now)
        document = Document(
            company_id=company_id,
            filename=filename,
            content_type=content_type,
            size=len(file_content),
            storage_key=f"temp/{company_id}/{filename}",
            hash=file_hash,
            uploaded_by=uploaded_by
        )
        
        return document
    
    async def get_document(self, document_id: UUID) -> Optional[Document]:
        """Get document by ID (simplified version)."""
        # For now, return None - this would be implemented with real storage
        return None
    
    async def download_document(self, document: Document) -> bytes:
        """Download document content (simplified version)."""
        # For now, return empty bytes - this would be implemented with real storage
        return b""


class SimplePolicyService:
    """Simplified policy service for basic functionality."""
    
    async def get_active_policies(self, country: str) -> list:
        """Get active policies for country (simplified version)."""
        # Return sample policies for testing
        return [
            {
                "id": "SE_REPR_MEAL_V1",
                "version": "V1",
                "country": "SE",
                "effective_from": "2024-01-01",
                "effective_to": None,
                "name": "Swedish Representation Meal Policy",
                "description": "Policy for representation meals in Sweden"
            },
            {
                "id": "SE_TAXI_TRANSPORT_V1",
                "version": "V1",
                "country": "SE",
                "effective_from": "2024-01-01",
                "effective_to": None,
                "name": "Swedish Taxi Transport Policy",
                "description": "Policy for taxi and transport expenses in Sweden"
            },
            {
                "id": "SE_SAAS_SUBSCRIPTION_V1",
                "version": "V1",
                "country": "SE",
                "effective_from": "2024-01-01",
                "effective_to": None,
                "name": "Swedish SaaS Subscription Policy",
                "description": "Policy for software subscriptions in Sweden"
            }
        ]


class SimpleBookingService:
    """Simplified booking service for basic functionality."""
    
    async def get_booking(self, booking_id: UUID):
        """Get booking by ID (simplified version)."""
        # Return sample booking data for testing
        sample_bookings = {
            "550e8400-e29b-41d4-a716-446655440010": {
                "journal_entry": {
                    "id": "550e8400-e29b-41d4-a716-446655440010",
                    "posting_date": "2024-01-15",
                    "series": "AI",
                    "number": "000001",
                    "notes": "AI booking: representation_meal - Restaurant ABC",
                    "created_at": "2024-01-15T10:30:00Z"
                },
                "receipt": {
                    "total": "1008.00",
                    "currency": "SEK",
                    "vendor": "Restaurant ABC",
                    "receipt_date": "2024-01-15",
                    "confidence": 0.9
                },
                "intent": {
                    "name": "representation_meal",
                    "confidence": 0.9,
                    "slots": {
                        "attendees_count": 3,
                        "purpose": "Business lunch with client"
                    }
                },
                "proposal": {
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
            }
        }
        
        return sample_bookings.get(str(booking_id))
    
    async def list_bookings(self, company_id: UUID, limit: int = 50, offset: int = 0):
        """List bookings for a company (simplified version with sample data)."""
        # Return sample journal entries for testing
        from src.domain.models import JournalEntry, JournalLine
        from decimal import Decimal
        from datetime import date
        
        sample_entries = [
            {
                "id": "550e8400-e29b-41d4-a716-446655440010",
                "posting_date": "2024-01-15",
                "series": "AI",
                "number": "000001",
                "notes": "AI booking: representation_meal - Restaurant ABC",
                "created_at": "2024-01-15T10:30:00Z",
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
                ]
            },
            {
                "id": "550e8400-e29b-41d4-a716-446655440011",
                "posting_date": "2024-01-16",
                "series": "AI",
                "number": "000002",
                "notes": "AI booking: taxi_transport - Taxi Stockholm",
                "created_at": "2024-01-16T14:20:00Z",
                "lines": [
                    {
                        "account": "6540",
                        "side": "D",
                        "amount": "120.00",
                        "description": "Transport expenses"
                    },
                    {
                        "account": "2640",
                        "side": "D",
                        "amount": "30.00",
                        "description": "VAT on transport"
                    },
                    {
                        "account": "1930",
                        "side": "K",
                        "amount": "150.00",
                        "description": "Cash/Bank"
                    }
                ]
            },
            {
                "id": "550e8400-e29b-41d4-a716-446655440012",
                "posting_date": "2024-01-17",
                "series": "AI",
                "number": "000003",
                "notes": "AI booking: saas_subscription - Microsoft 365",
                "created_at": "2024-01-17T09:15:00Z",
                "lines": [
                    {
                        "account": "6541",
                        "side": "D",
                        "amount": "71.20",
                        "description": "Software subscriptions"
                    },
                    {
                        "account": "2640",
                        "side": "D",
                        "amount": "17.80",
                        "description": "VAT on subscriptions"
                    },
                    {
                        "account": "1930",
                        "side": "K",
                        "amount": "89.00",
                        "description": "Cash/Bank"
                    }
                ]
            }
        ]
        
        # Apply pagination
        start = offset
        end = offset + limit
        return sample_entries[start:end]
