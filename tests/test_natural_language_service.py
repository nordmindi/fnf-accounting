"""Comprehensive tests for Natural Language Service."""

import pytest
from decimal import Decimal
from datetime import date
from unittest.mock import Mock, AsyncMock, patch

from src.domain.natural_language_service import NaturalLanguageService
from src.domain.models import (
    Intent, ReceiptDoc, Currency, VATLine, PostingProposal, 
    StoplightDecision, PostingLine
)
from src.adapters.llm import LLMAdapter
from src.rules.engine import RuleEngine


class TestNaturalLanguageService:
    """Test suite for Natural Language Service."""
    
    @pytest.fixture
    def mock_llm(self):
        """Mock LLM adapter."""
        llm = Mock(spec=LLMAdapter)
        llm.detect_intent = AsyncMock()
        return llm
    
    @pytest.fixture
    def mock_rule_engine(self):
        """Mock rule engine."""
        engine = Mock(spec=RuleEngine)
        engine.find_matching_policies = Mock()
        engine.apply_policy = Mock()
        return engine
    
    @pytest.fixture
    def nl_service(self, mock_llm, mock_rule_engine):
        """Natural Language Service instance."""
        return NaturalLanguageService(mock_llm, mock_rule_engine)
    
    @pytest.fixture
    def sample_receipt(self):
        """Sample receipt document."""
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
    
    @pytest.mark.asyncio
    async def test_representation_meal_processing(self, nl_service, mock_llm, mock_rule_engine, sample_receipt):
        """Test processing of representation meal scenario."""
        # Mock LLM response
        mock_llm.detect_intent.return_value = {
            "intent": "representation_meal",
            "confidence": 0.9,
            "slots": {
                "attendees_count": 2,
                "purpose": "Business meeting with client",
                "client": "Example AB"
            }
        }
        
        # Mock rule engine response
        mock_proposal = PostingProposal(
            stoplight=StoplightDecision.GREEN,
            lines=[
                PostingLine(account="6071", side="D", amount=Decimal('480.00'), description="Representation, avdragsgill"),
                PostingLine(account="6072", side="D", amount=Decimal('900.00'), description="Representation, ej avdragsgill"),
                PostingLine(account="2641", side="D", amount=Decimal('120.00'), description="Ingående moms, avdragsgill"),
                PostingLine(account="1930", side="K", amount=Decimal('1500.00'), description="Cash/Bank")
            ],
            vat_mode="standard",
            report_boxes={}
        )
        
        mock_rule_engine.find_matching_policies.return_value = [Mock()]
        mock_rule_engine.apply_policy.return_value = mock_proposal
        
        # Test processing
        result = await nl_service.process_natural_language_input(
            "Business lunch with client from Example AB, 1500 SEK",
            "123e4567-e89b-12d3-a456-426614174007"
        )
        
        # Assertions
        assert result['intent'].name == "representation_meal"
        assert result['intent'].slots['attendees_count'] == 2
        assert result['proposal'].stoplight == StoplightDecision.GREEN
        assert len(result['proposal'].lines) == 4
        
        # Verify LLM was called
        mock_llm.detect_intent.assert_called_once()
        
        # Verify rule engine was called
        mock_rule_engine.find_matching_policies.assert_called_once()
        mock_rule_engine.apply_policy.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_saas_reverse_charge_processing(self, nl_service, mock_llm, mock_rule_engine):
        """Test processing of SaaS subscription with reverse charge."""
        # Mock LLM response
        mock_llm.detect_intent.return_value = {
            "intent": "saas_subscription",
            "confidence": 0.9,
            "slots": {
                "service_period": "October 2025",
                "vendor": "Amazon Web Services"
            }
        }
        
        # Mock rule engine response
        mock_proposal = PostingProposal(
            stoplight=StoplightDecision.GREEN,
            lines=[
                PostingLine(account="6540", side="D", amount=Decimal('4500.00'), description="IT-tjänster (omvänd moms)"),
                PostingLine(account="2614", side="K", amount=Decimal('1125.00'), description="Utgående moms omvänd 25%"),
                PostingLine(account="2645", side="D", amount=Decimal('1125.00'), description="Ingående moms omvänd 25%"),
                PostingLine(account="1930", side="K", amount=Decimal('4500.00'), description="Bank")
            ],
            vat_mode="reverse_charge",
            report_boxes={"21": "net_before_cap", "30": "vat_before_cap", "48": "vat_before_cap"}
        )
        
        mock_rule_engine.find_matching_policies.return_value = [Mock()]
        mock_rule_engine.apply_policy.return_value = mock_proposal
        
        # Test processing
        result = await nl_service.process_natural_language_input(
            "Paid Amazon Web Services cloud service for 4500 SEK for October 2025",
            "123e4567-e89b-12d3-a456-426614174007"
        )
        
        # Assertions
        assert result['intent'].name == "saas_subscription"
        assert result['proposal'].vat_mode == "reverse_charge"
        assert result['proposal'].report_boxes["21"] == "net_before_cap"
        assert result['proposal'].report_boxes["30"] == "vat_before_cap"
        assert result['proposal'].report_boxes["48"] == "vat_before_cap"
    
    @pytest.mark.asyncio
    async def test_mobile_phone_installment_processing(self, nl_service, mock_llm, mock_rule_engine):
        """Test processing of mobile phone purchase with installment."""
        # Mock LLM response
        mock_llm.detect_intent.return_value = {
            "intent": "mobile_phone_purchase",
            "confidence": 0.9,
            "slots": {
                "total_amount": 15000,
                "installment_months": 12,
                "device_type": "mobile phone",
                "vendor": "NetOnNet"
            }
        }
        
        # Mock rule engine response
        mock_proposal = PostingProposal(
            stoplight=StoplightDecision.GREEN,
            lines=[
                PostingLine(account="1630", side="D", amount=Decimal('12000.00'), description="Mobiltelefoner och kommunikationsutrustning"),
                PostingLine(account="2640", side="D", amount=Decimal('3000.00'), description="Ingående moms 25%"),
                PostingLine(account="2440", side="K", amount=Decimal('15000.00'), description="Leverantörsskuld (delbetalning)")
            ],
            vat_mode="standard",
            report_boxes={}
        )
        
        mock_rule_engine.find_matching_policies.return_value = [Mock()]
        mock_rule_engine.apply_policy.return_value = mock_proposal
        
        # Test processing
        result = await nl_service.process_natural_language_input(
            "Jag har köpt en mobil telefon från NetOnNet på företagskortet. Mobilen kostar 15000 och ska avbetal under 12 månader",
            "123e4567-e89b-12d3-a456-426614174007"
        )
        
        # Assertions
        assert result['intent'].name == "mobile_phone_purchase"
        assert result['intent'].slots['installment_months'] == 12
        assert result['intent'].slots['device_type'] == "mobile phone"
        assert result['proposal'].stoplight == StoplightDecision.GREEN
    
    @pytest.mark.asyncio
    async def test_fallback_intent_detection(self, nl_service, mock_llm, mock_rule_engine):
        """Test fallback intent detection when LLM fails."""
        # Mock LLM failure
        mock_llm.detect_intent.side_effect = Exception("LLM API error")
        
        # Mock rule engine response
        mock_proposal = PostingProposal(
            stoplight=StoplightDecision.YELLOW,
            lines=[],
            vat_mode="standard",
            report_boxes={}
        )
        
        mock_rule_engine.find_matching_policies.return_value = []
        mock_rule_engine.apply_policy.return_value = mock_proposal
        
        # Test processing
        result = await nl_service.process_natural_language_input(
            "office supplies 2500 SEK",
            "123e4567-e89b-12d3-a456-426614174007"
        )
        
        # Assertions
        assert result['intent'].name == "office_supplies"
        assert result['proposal'].stoplight == StoplightDecision.YELLOW
    
    @pytest.mark.asyncio
    async def test_low_confidence_fallback(self, nl_service, mock_llm, mock_rule_engine):
        """Test fallback when LLM returns low confidence."""
        # Mock LLM low confidence response
        mock_llm.detect_intent.return_value = {
            "intent": "other_business",
            "confidence": 0.3,
            "slots": {}
        }
        
        # Mock rule engine response
        mock_proposal = PostingProposal(
            stoplight=StoplightDecision.YELLOW,
            lines=[],
            vat_mode="standard",
            report_boxes={}
        )
        
        mock_rule_engine.find_matching_policies.return_value = []
        mock_rule_engine.apply_policy.return_value = mock_proposal
        
        # Test processing
        result = await nl_service.process_natural_language_input(
            "mobile phone purchase 10000 SEK",
            "123e4567-e89b-12d3-a456-426614174007"
        )
        
        # Assertions - should use fallback detection
        assert result['intent'].name == "mobile_phone_purchase"
    
    def test_fallback_parse_amount_extraction(self, nl_service):
        """Test amount extraction in fallback parsing."""
        # Test various amount formats
        test_cases = [
            ("1500 SEK", 1500.0),
            ("2500 kr", 2500.0),
            ("1000", 1000.0),
            ("€500", 500.0),
            ("$200", 200.0)
        ]
        
        for text, expected_amount in test_cases:
            result = nl_service._fallback_parse(text, Mock())
            assert result["amount"] == expected_amount
    
    def test_fallback_parse_vendor_extraction(self, nl_service):
        """Test vendor extraction in fallback parsing."""
        # Test various vendor patterns
        test_cases = [
            ("Business lunch at Restaurant ABC", "Restaurant ABC"),
            ("from NetOnNet", "NetOnNet"),
            ("från Elgiganten", "Elgiganten"),
            ("köpt från Media Markt", "Media Markt")
        ]
        
        for text, expected_vendor in test_cases:
            result = nl_service._fallback_parse(text, Mock())
            assert result["vendor"] == expected_vendor
    
    def test_fallback_intent_detection_keywords(self, nl_service):
        """Test keyword-based intent detection."""
        # Test various intent keywords
        test_cases = [
            ("business lunch with client", "representation_meal"),
            ("office supplies and materials", "office_supplies"),
            ("computer purchase from Elgiganten", "computer_purchase"),
            ("leasing kopiator", "leasing"),
            ("utlägg från anställd", "employee_expense"),
            ("AWS cloud service", "saas_subscription")
        ]
        
        for text, expected_intent in test_cases:
            result = nl_service._fallback_intent_detection(text, Mock())
            assert result["intent"] == expected_intent
    
    def test_deductible_breakdown_calculation(self, nl_service):
        """Test deductible breakdown calculation for representation meals."""
        # Mock proposal with deductible split
        mock_proposal = Mock()
        mock_proposal.vat_mode = "standard"
        mock_proposal.lines = [
            Mock(account="6071", amount=Decimal('480.00')),
            Mock(account="6072", amount=Decimal('900.00')),
            Mock(account="2641", amount=Decimal('120.00'))
        ]
        
        # Mock receipt
        mock_receipt = Mock()
        mock_receipt.total = Decimal('1500.00')
        
        # Mock intent
        mock_intent = Mock()
        mock_intent.name = "representation_meal"
        mock_intent.slots = {"attendees_count": 2}
        
        # Test feedback generation
        feedback = {
            "booking_details": {
                "deductible_breakdown": {}
            }
        }
        
        nl_service._add_deductible_breakdown(feedback, mock_proposal, mock_receipt, mock_intent)
        
        # Assertions
        breakdown = feedback["booking_details"]["deductible_breakdown"]
        assert breakdown["max_deductible_per_person_sek"] == 300
        assert breakdown["attendees_count"] == 2
        assert breakdown["max_deductible_total_sek"] == 600
        assert breakdown["deductible_net"] == 480.0
        assert breakdown["non_deductible_net"] == 900.0
        assert breakdown["vat_deductible"] == 120.0
        assert breakdown["total_deductible"] == 600.0
        assert breakdown["total_non_deductible"] == 900.0
        assert breakdown["tax_benefit_sek"] == 150.0  # 25% of 600
    
    @pytest.mark.asyncio
    async def test_error_handling(self, nl_service, mock_llm, mock_rule_engine):
        """Test error handling in various scenarios."""
        # Test LLM error
        mock_llm.detect_intent.side_effect = Exception("API Error")
        
        result = await nl_service.process_natural_language_input(
            "test input",
            "123e4567-e89b-12d3-a456-426614174007"
        )
        
        # Should not crash and return fallback result
        assert result is not None
        assert result['intent'] is not None
        
        # Test rule engine error
        mock_llm.detect_intent.side_effect = None
        mock_llm.detect_intent.return_value = {
            "intent": "representation_meal",
            "confidence": 0.9,
            "slots": {"attendees_count": 2, "purpose": "test"}
        }
        
        mock_rule_engine.find_matching_policies.side_effect = Exception("Rule Engine Error")
        
        result = await nl_service.process_natural_language_input(
            "business lunch",
            "123e4567-e89b-12d3-a456-426614174007"
        )
        
        # Should handle error gracefully
        assert result is not None
