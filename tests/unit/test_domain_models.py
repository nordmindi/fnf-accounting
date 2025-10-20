"""Unit tests for domain models."""

import pytest
from decimal import Decimal
from datetime import date, datetime
from uuid import uuid4

from src.domain.models import (
    ReceiptDoc, Intent, PostingProposal, JournalEntry, 
    JournalLine, StoplightDecision, Currency
)


class TestReceiptDoc:
    """Test ReceiptDoc model."""
    
    def test_receipt_creation(self):
        """Test creating a receipt document."""
        receipt = ReceiptDoc(
            total=Decimal("100.00"),
            currency=Currency.SEK,
            vendor="Test Vendor",
            date=date(2024, 1, 15),
            confidence=0.9
        )
        
        assert receipt.total == Decimal("100.00")
        assert receipt.currency == Currency.SEK
        assert receipt.vendor == "Test Vendor"
        assert receipt.date == date(2024, 1, 15)
        assert receipt.confidence == 0.9
    
    def test_receipt_validation(self):
        """Test receipt validation."""
        with pytest.raises(ValueError):
            ReceiptDoc(
                total=Decimal("100.00"),
                currency=Currency.SEK,
                vendor="Test Vendor",
                date=date(2024, 1, 15),
                confidence=1.5  # Invalid confidence > 1.0
            )


class TestIntent:
    """Test Intent model."""
    
    def test_intent_creation(self):
        """Test creating an intent."""
        intent = Intent(
            name="representation_meal",
            confidence=0.9,
            slots={"attendees_count": 3, "purpose": "Client meeting"}
        )
        
        assert intent.name == "representation_meal"
        assert intent.confidence == 0.9
        assert intent.slots["attendees_count"] == 3
        assert intent.slots["purpose"] == "Client meeting"


class TestPostingProposal:
    """Test PostingProposal model."""
    
    def test_posting_proposal_creation(self):
        """Test creating a posting proposal."""
        proposal = PostingProposal(
            lines=[],
            vat_code="12",
            confidence=0.9,
            reason_codes=["Policy applied"],
            stoplight=StoplightDecision.GREEN,
            policy_id="SE_REPR_MEAL_V1"
        )
        
        assert proposal.vat_code == "12"
        assert proposal.confidence == 0.9
        assert proposal.stoplight == StoplightDecision.GREEN
        assert proposal.policy_id == "SE_REPR_MEAL_V1"


class TestJournalEntry:
    """Test JournalEntry model."""
    
    def test_journal_entry_creation(self):
        """Test creating a journal entry."""
        company_id = uuid4()
        entry = JournalEntry(
            company_id=company_id,
            date=date(2024, 1, 15),
            series="AI",
            number="000001",
            notes="Test entry"
        )
        
        assert entry.company_id == company_id
        assert entry.date == date(2024, 1, 15)
        assert entry.series == "AI"
        assert entry.number == "000001"
        assert entry.notes == "Test entry"
        assert entry.created_at is not None


class TestJournalLine:
    """Test JournalLine model."""
    
    def test_journal_line_creation(self):
        """Test creating a journal line."""
        entry_id = uuid4()
        line = JournalLine(
            entry_id=entry_id,
            account="6071",
            side="D",
            amount=Decimal("100.00"),
            description="Test line"
        )
        
        assert line.entry_id == entry_id
        assert line.account == "6071"
        assert line.side == "D"
        assert line.amount == Decimal("100.00")
        assert line.description == "Test line"
