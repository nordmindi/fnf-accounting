"""Integration tests for end-to-end scenarios."""

import pytest
import asyncio
from decimal import Decimal
from datetime import date
from unittest.mock import Mock, patch, AsyncMock

from src.domain.natural_language_service import NaturalLanguageService
from src.adapters.llm import LLMAdapter
from src.rules.engine import RuleEngine
from src.domain.models import Intent, ReceiptDoc, Currency, VATLine


class TestEndToEndScenarios:
    """Integration tests for complete user scenarios."""
    
    @pytest.fixture
    def mock_llm(self):
        """Mock LLM adapter."""
        llm = Mock(spec=LLMAdapter)
        llm.detect_intent = AsyncMock()
        return llm
    
    @pytest.fixture
    def real_rule_engine(self):
        """Real rule engine with actual policies."""
        # Load actual policies for integration testing
        policies = [
            {
                "id": "SE_REPR_MEAL_V1",
                "version": "V1",
                "country": "SE",
                "effective_from": "2024-01-01",
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
            },
            {
                "id": "SE_SAAS_REVERSE_CHARGE_V1",
                "version": "V1",
                "country": "SE",
                "effective_from": "2024-01-01",
                "bas_version": "2025_v1.0",
                "rules": {
                    "match": {
                        "intent": "saas_subscription",
                        "supplier_country": {"$ne": "SE"}
                    },
                    "requires": [{"field": "service_period", "op": "exists"}],
                    "vat": {
                        "rate": 25,
                        "code": "RC25",
                        "reverse_charge": True,
                        "report_boxes": {"21": "net_before_cap", "30": "vat_before_cap", "48": "vat_before_cap"}
                    },
                    "posting": [
                        {"account": "6540", "side": "D", "amount": "net_before_cap", "description": "IT-tjänster (omvänd moms)"},
                        {"account": "2614", "side": "K", "amount": "vat_before_cap", "description": "Utgående moms omvänd 25%"},
                        {"account": "2645", "side": "D", "amount": "vat_before_cap", "description": "Ingående moms omvänd 25%"},
                        {"account": "1930", "side": "K", "amount": "gross", "description": "Bank"}
                    ],
                    "stoplight": {
                        "on_missing_required": "YELLOW",
                        "on_fail": "RED",
                        "confidence_threshold": 0.8
                    }
                }
            },
            {
                "id": "SE_MOBILE_PHONE_INSTALLMENT_V1",
                "version": "V1",
                "country": "SE",
                "effective_from": "2024-01-01",
                "bas_version": "2025_v1.0",
                "rules": {
                    "match": {
                        "intent": "mobile_phone_purchase",
                        "total_amount_min": 10000
                    },
                    "requires": [
                        {"field": "installment_months", "op": ">=", "value": 1},
                        {"field": "device_type", "op": "exists"}
                    ],
                    "vat": {
                        "rate": 25,
                        "code": "25"
                    },
                    "posting": [
                        {"account": "1630", "side": "D", "amount": "net_before_cap", "description": "Mobiltelefoner och kommunikationsutrustning"},
                        {"account": "2640", "side": "D", "amount": "vat_before_cap", "description": "Ingående moms 25%"},
                        {"account": "2440", "side": "K", "amount": "gross", "description": "Leverantörsskuld (delbetalning)"}
                    ],
                    "stoplight": {
                        "on_missing_required": "YELLOW",
                        "on_fail": "RED",
                        "confidence_threshold": 0.8
                    }
                }
            }
        ]
        return RuleEngine(policies)
    
    @pytest.fixture
    def nl_service(self, mock_llm, real_rule_engine):
        """Natural Language Service with real rule engine."""
        return NaturalLanguageService(mock_llm, real_rule_engine)
    
    @pytest.mark.asyncio
    async def test_representation_meal_complete_flow(self, nl_service, mock_llm):
        """Test complete flow for representation meal scenario."""
        # Mock LLM response
        mock_llm.detect_intent.return_value = {
            "intent": "representation_meal",
            "confidence": 0.9,
            "slots": {
                "attendees_count": 2,
                "purpose": "Business meeting with client from Example AB",
                "client": "Example AB"
            }
        }
        
        # Process the request
        result = await nl_service.process_natural_language_input(
            "Business lunch today with the project manager of Example AB at Example restaurant, total amount 1500 SEK, paid with company credit card",
            "123e4567-e89b-12d3-a456-426614174007"
        )
        
        # Verify intent detection
        assert result['intent'].name == "representation_meal"
        assert result['intent'].slots['attendees_count'] == 2
        assert result['intent'].slots['purpose'] == "Business meeting with client from Example AB"
        
        # Verify proposal
        assert result['proposal'].stoplight.value == "GREEN"
        assert len(result['proposal'].lines) == 4
        
        # Verify posting lines
        lines = result['proposal'].lines
        accounts = [line.account for line in lines]
        assert "6071" in accounts  # Deductible representation
        assert "6072" in accounts  # Non-deductible representation
        assert "2641" in accounts  # VAT deductible
        assert "1930" in accounts  # Bank
        
        # Verify amounts (with 2 attendees, max deductible is 600 SEK)
        deductible_line = next(line for line in lines if line.account == "6071")
        non_deductible_line = next(line for line in lines if line.account == "6072")
        vat_line = next(line for line in lines if line.account == "2641")
        bank_line = next(line for line in lines if line.account == "1930")
        
        assert deductible_line.amount == Decimal('480.00')  # 600 / 1.12
        assert non_deductible_line.amount == Decimal('900.00')  # 1500 - 600
        assert vat_line.amount == Decimal('120.00')  # 600 - 480
        assert bank_line.amount == Decimal('1500.00')
        
        # Verify VAT mode
        assert result['proposal'].vat_mode == "standard"
    
    @pytest.mark.asyncio
    async def test_saas_reverse_charge_complete_flow(self, nl_service, mock_llm):
        """Test complete flow for SaaS reverse charge scenario."""
        # Mock LLM response
        mock_llm.detect_intent.return_value = {
            "intent": "saas_subscription",
            "confidence": 0.9,
            "slots": {
                "service_period": "October 2025",
                "vendor": "Amazon Web Services",
                "supplier_country": "US"
            }
        }
        
        # Process the request
        result = await nl_service.process_natural_language_input(
            "Paid Amazon Web Services cloud service for 4500 SEK for October 2025",
            "123e4567-e89b-12d3-a456-426614174007"
        )
        
        # Verify intent detection
        assert result['intent'].name == "saas_subscription"
        assert result['intent'].slots['service_period'] == "October 2025"
        
        # Verify proposal
        assert result['proposal'].stoplight.value == "GREEN"
        assert len(result['proposal'].lines) == 4
        
        # Verify posting lines
        lines = result['proposal'].lines
        accounts = [line.account for line in lines]
        assert "6540" in accounts  # IT services
        assert "2614" in accounts  # Outgoing reverse charge VAT
        assert "2645" in accounts  # Incoming reverse charge VAT
        assert "1930" in accounts  # Bank
        
        # Verify amounts (reverse charge: 4500 is net, VAT is 1125)
        it_line = next(line for line in lines if line.account == "6540")
        outgoing_vat_line = next(line for line in lines if line.account == "2614")
        incoming_vat_line = next(line for line in lines if line.account == "2645")
        bank_line = next(line for line in lines if line.account == "1930")
        
        assert it_line.amount == Decimal('4500.00')  # Net amount
        assert outgoing_vat_line.amount == Decimal('1125.00')  # 25% of 4500
        assert incoming_vat_line.amount == Decimal('1125.00')  # Same VAT amount
        assert bank_line.amount == Decimal('5625.00')  # Net + VAT
        
        # Verify VAT mode and report boxes
        assert result['proposal'].vat_mode == "reverse_charge"
        assert result['proposal'].report_boxes["21"] == "net_before_cap"
        assert result['proposal'].report_boxes["30"] == "vat_before_cap"
        assert result['proposal'].report_boxes["48"] == "vat_before_cap"
    
    @pytest.mark.asyncio
    async def test_mobile_phone_installment_complete_flow(self, nl_service, mock_llm):
        """Test complete flow for mobile phone installment scenario."""
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
        
        # Process the request
        result = await nl_service.process_natural_language_input(
            "Jag har köpt en mobil telefon från NetOnNet på företagskortet. Mobilen kostar 15000 och ska avbetal under 12 månader",
            "123e4567-e89b-12d3-a456-426614174007"
        )
        
        # Verify intent detection
        assert result['intent'].name == "mobile_phone_purchase"
        assert result['intent'].slots['installment_months'] == 12
        assert result['intent'].slots['device_type'] == "mobile phone"
        
        # Verify proposal
        assert result['proposal'].stoplight.value == "GREEN"
        assert len(result['proposal'].lines) == 3
        
        # Verify posting lines
        lines = result['proposal'].lines
        accounts = [line.account for line in lines]
        assert "1630" in accounts  # Mobile phones and communication equipment
        assert "2640" in accounts  # Input VAT 25%
        assert "2440" in accounts  # Supplier liability (installment)
        
        # Verify amounts
        asset_line = next(line for line in lines if line.account == "1630")
        vat_line = next(line for line in lines if line.account == "2640")
        liability_line = next(line for line in lines if line.account == "2440")
        
        assert asset_line.amount == Decimal('12000.00')  # 15000 / 1.25
        assert vat_line.amount == Decimal('3000.00')  # 25% of 12000
        assert liability_line.amount == Decimal('15000.00')  # Total amount
        
        # Verify VAT mode
        assert result['proposal'].vat_mode == "standard"
    
    @pytest.mark.asyncio
    async def test_fallback_detection_flow(self, nl_service, mock_llm):
        """Test fallback detection when LLM fails."""
        # Mock LLM failure
        mock_llm.detect_intent.side_effect = Exception("LLM API error")
        
        # Process the request
        result = await nl_service.process_natural_language_input(
            "office supplies 2500 SEK",
            "123e4567-e89b-12d3-a456-426614174007"
        )
        
        # Verify fallback detection worked
        assert result['intent'].name == "office_supplies"
        assert result['intent'].slots['purpose'] == "Office supplies"
        
        # Should get YELLOW stoplight due to no matching policy
        assert result['proposal'].stoplight.value == "YELLOW"
    
    @pytest.mark.asyncio
    async def test_low_confidence_fallback_flow(self, nl_service, mock_llm):
        """Test fallback when LLM returns low confidence."""
        # Mock LLM low confidence response
        mock_llm.detect_intent.return_value = {
            "intent": "other_business",
            "confidence": 0.3,
            "slots": {}
        }
        
        # Process the request
        result = await nl_service.process_natural_language_input(
            "mobile phone purchase 10000 SEK",
            "123e4567-e89b-12d3-a456-426614174007"
        )
        
        # Verify fallback detection worked
        assert result['intent'].name == "mobile_phone_purchase"
        assert result['intent'].slots['device_type'] == "mobile phone"
    
    @pytest.mark.asyncio
    async def test_swedish_language_processing(self, nl_service, mock_llm):
        """Test processing of Swedish language input."""
        # Mock LLM response
        mock_llm.detect_intent.return_value = {
            "intent": "representation_meal",
            "confidence": 0.9,
            "slots": {
                "attendees_count": 3,
                "purpose": "Affärsmöte med kund",
                "client": "Exempel AB"
            }
        }
        
        # Process Swedish request
        result = await nl_service.process_natural_language_input(
            "Affärslunch idag med projektledaren från Exempel AB på Exempel restaurang, totalt belopp 1800 SEK, betalt med företagskort",
            "123e4567-e89b-12d3-a456-426614174007"
        )
        
        # Verify processing
        assert result['intent'].name == "representation_meal"
        assert result['intent'].slots['attendees_count'] == 3
        assert result['intent'].slots['purpose'] == "Affärsmöte med kund"
        
        # With 3 attendees, max deductible is 900 SEK (3 * 300)
        lines = result['proposal'].lines
        deductible_line = next(line for line in lines if line.account == "6071")
        non_deductible_line = next(line for line in lines if line.account == "6072")
        
        assert deductible_line.amount == Decimal('720.00')  # 900 / 1.12
        assert non_deductible_line.amount == Decimal('900.00')  # 1800 - 900
    
    @pytest.mark.asyncio
    async def test_error_handling_and_recovery(self, nl_service, mock_llm):
        """Test error handling and recovery mechanisms."""
        # Test with malformed input
        result = await nl_service.process_natural_language_input(
            "invalid input with no clear intent",
            "123e4567-e89b-12d3-a456-426614174007"
        )
        
        # Should not crash and return some result
        assert result is not None
        assert result['intent'] is not None
        assert result['proposal'] is not None
        
        # Test with empty input
        result = await nl_service.process_natural_language_input(
            "",
            "123e4567-e89b-12d3-a456-426614174007"
        )
        
        # Should handle gracefully
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_multiple_scenarios_consistency(self, nl_service, mock_llm):
        """Test consistency across multiple scenarios."""
        scenarios = [
            {
                "input": "Business lunch with 2 people, 1200 SEK",
                "expected_intent": "representation_meal",
                "expected_attendees": 2
            },
            {
                "input": "AWS cloud service 3000 SEK for November 2025",
                "expected_intent": "saas_subscription",
                "expected_period": "November 2025"
            },
            {
                "input": "Mobile phone from Elgiganten 12000 SEK, 24 months",
                "expected_intent": "mobile_phone_purchase",
                "expected_months": 24
            }
        ]
        
        for scenario in scenarios:
            # Mock appropriate LLM response
            if scenario["expected_intent"] == "representation_meal":
                mock_llm.detect_intent.return_value = {
                    "intent": "representation_meal",
                    "confidence": 0.9,
                    "slots": {
                        "attendees_count": scenario["expected_attendees"],
                        "purpose": "Business meeting"
                    }
                }
            elif scenario["expected_intent"] == "saas_subscription":
                mock_llm.detect_intent.return_value = {
                    "intent": "saas_subscription",
                    "confidence": 0.9,
                    "slots": {
                        "service_period": scenario["expected_period"],
                        "supplier_country": "US"
                    }
                }
            elif scenario["expected_intent"] == "mobile_phone_purchase":
                mock_llm.detect_intent.return_value = {
                    "intent": "mobile_phone_purchase",
                    "confidence": 0.9,
                    "slots": {
                        "installment_months": scenario["expected_months"],
                        "device_type": "mobile phone"
                    }
                }
            
            # Process scenario
            result = await nl_service.process_natural_language_input(
                scenario["input"],
                "123e4567-e89b-12d3-a456-426614174007"
            )
            
            # Verify intent
            assert result['intent'].name == scenario["expected_intent"]
            
            # Verify proposal exists
            assert result['proposal'] is not None
            assert result['proposal'].stoplight is not None
