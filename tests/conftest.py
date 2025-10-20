"""Test configuration and fixtures."""

import asyncio
from datetime import date
from decimal import Decimal

import pytest

from src.domain.models import Currency, Intent, ReceiptDoc, VATLine


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_intent():
    """Sample intent for testing."""
    return Intent(
        name="representation_meal",
        confidence=0.9,
        slots={
            "attendees_count": 2,
            "purpose": "Business meeting with client",
            "client": "Example AB"
        }
    )


@pytest.fixture
def sample_receipt():
    """Sample receipt for testing."""
    return ReceiptDoc(
        total=Decimal('1500.00'),
        currency=Currency.SEK,
        vat_lines=[
            VATLine(
                rate=Decimal('0.12'),
                amount=Decimal('160.71'),
                base_amount=Decimal('1339.29')
            )
        ],
        vendor="Test Restaurant",
        date=date(2024, 1, 15),
        raw_text="Business lunch with client",
        confidence=0.9
    )


@pytest.fixture
def sample_company_id():
    """Sample company ID for testing."""
    return "123e4567-e89b-12d3-a456-426614174007"


@pytest.fixture
def mock_llm_response():
    """Mock LLM response for testing."""
    return {
        "intent": "representation_meal",
        "confidence": 0.9,
        "slots": {
            "attendees_count": 2,
            "purpose": "Business meeting with client",
            "client": "Example AB"
        }
    }


@pytest.fixture
def mock_policy():
    """Mock policy for testing."""
    return {
        "id": "SE_REPR_MEAL_V1",
        "version": "V1",
        "country": "SE",
        "effective_from": "2024-01-01",
        "name": "Swedish Representation Meal Policy",
        "bas_version": "2025_v1.0",
        "rules": {
            "match": {"intent": "representation_meal"},
            "requires": [
                {"field": "attendees_count", "op": ">=", "value": 1},
                {"field": "purpose", "op": "exists"}
            ],
            "vat": {
                "rate": 12,
                "cap_sek_per_person": 300,
                "code": "12",
                "deductible_split": True
            },
            "posting": [
                {"account": "6071", "side": "D", "amount": "deductible_net", "description": "Representation, avdragsgill"},
                {"account": "6072", "side": "D", "amount": "non_deductible_net", "description": "Representation, ej avdragsgill"},
                {"account": "2641", "side": "D", "amount": "vat_deductible", "description": "Ingående moms, avdragsgill"},
                {"account": "1930", "side": "K", "amount": "gross", "description": "Cash/Bank"}
            ],
            "stoplight": {
                "on_missing_required": "YELLOW",
                "on_fail": "RED",
                "confidence_threshold": 0.8
            }
        }
    }


@pytest.fixture
def mock_bas_account():
    """Mock BAS account for testing."""
    return {
        "number": "6071",
        "name": "Representation",
        "account_class": "60",
        "account_type": "expense",
        "vat_hint": 12.0,
        "allowed_regions": ["SE"],
        "description": "Representation meals and entertainment"
    }


# Test data for various scenarios
@pytest.fixture
def test_scenarios():
    """Test scenarios for comprehensive testing."""
    return {
        "representation_meal": {
            "input": "Business lunch with client from Example AB, 1500 SEK",
            "expected_intent": "representation_meal",
            "expected_attendees": 2,
            "expected_amount": 1500.0
        },
        "saas_reverse_charge": {
            "input": "Paid Amazon Web Services cloud service for 4500 SEK for October 2025",
            "expected_intent": "saas_subscription",
            "expected_period": "October 2025",
            "expected_amount": 4500.0
        },
        "mobile_phone_installment": {
            "input": "Jag har köpt en mobil telefon från NetOnNet på företagskortet. Mobilen kostar 15000 och ska avbetal under 12 månader",
            "expected_intent": "mobile_phone_purchase",
            "expected_months": 12,
            "expected_amount": 15000.0
        },
        "office_supplies": {
            "input": "office supplies 2500 SEK",
            "expected_intent": "office_supplies",
            "expected_amount": 2500.0
        },
        "computer_purchase": {
            "input": "computer purchase 10000 SEK",
            "expected_intent": "computer_purchase",
            "expected_amount": 10000.0
        },
        "leasing": {
            "input": "leasing kopiator 3000 SEK per månad",
            "expected_intent": "leasing",
            "expected_amount": 3000.0
        },
        "employee_expense": {
            "input": "utlägg från anställd 1500 SEK",
            "expected_intent": "employee_expense",
            "expected_amount": 1500.0
        }
    }


# Performance testing fixtures
@pytest.fixture
def performance_test_data():
    """Data for performance testing."""
    return {
        "large_receipt": ReceiptDoc(
            total=Decimal('50000.00'),
            currency=Currency.SEK,
            vat_lines=[
                VATLine(
                    rate=Decimal('0.25'),
                    amount=Decimal('10000.00'),
                    base_amount=Decimal('40000.00')
                )
            ],
            vendor="Large Vendor",
            date=date(2024, 1, 15),
            raw_text="Large transaction with multiple line items and complex VAT calculations",
            confidence=0.9
        ),
        "complex_intent": Intent(
            name="representation_meal",
            confidence=0.9,
            slots={
                "attendees_count": 10,
                "purpose": "Complex business meeting with multiple clients and stakeholders",
                "client": "Multiple Clients AB",
                "project": "PROJ-2024-001",
                "cost_center": "CC-001"
            }
        )
    }


# Error testing fixtures
@pytest.fixture
def error_test_cases():
    """Test cases for error handling."""
    return {
        "empty_input": "",
        "invalid_input": "!@#$%^&*()",
        "no_amount": "business lunch with client",
        "negative_amount": "business lunch -1500 SEK",
        "zero_amount": "business lunch 0 SEK",
        "very_large_amount": "business lunch 999999999 SEK",
        "invalid_currency": "business lunch 1500 XYZ",
        "malformed_date": "business lunch 1500 SEK on 32/13/2024"
    }
