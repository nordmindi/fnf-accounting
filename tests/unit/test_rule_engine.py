"""Unit tests for rule engine."""

import pytest
from decimal import Decimal

from src.rules.engine import RuleEngine
from tests.conftest import sample_receipt, sample_intent, sample_policy


class TestRuleEngine:
    """Test rule engine functionality."""
    
    def test_policy_validation(self, sample_policy):
        """Test policy validation against schema."""
        engine = RuleEngine([sample_policy])
        # Should not raise an exception
        assert engine.policies == [sample_policy]
    
    def test_invalid_policy_validation(self):
        """Test invalid policy raises validation error."""
        invalid_policy = {
            "id": "INVALID",
            "version": "V1",
            "country": "SE",
            "effective_from": "2024-01-01",
            "name": "Invalid Policy",
            "rules": {
                "match": {"intent": "test"},
                "posting": []
            }
        }
        
        with pytest.raises(ValueError, match="Invalid policy"):
            RuleEngine([invalid_policy])
    
    def test_find_matching_policies(self, sample_policy, sample_receipt, sample_intent):
        """Test finding matching policies."""
        engine = RuleEngine([sample_policy])
        matches = engine.find_matching_policies(sample_intent, sample_receipt)
        
        assert len(matches) == 1
        assert matches[0].policy_id == "SE_REPR_MEAL_V1"
        assert matches[0].matched is True
        assert matches[0].confidence > 0
    
    def test_create_posting_proposal(self, sample_policy, sample_receipt, sample_intent):
        """Test creating posting proposal."""
        engine = RuleEngine([sample_policy])
        matches = engine.find_matching_policies(sample_intent, sample_receipt)
        
        proposal = engine.create_posting_proposal(matches[0], sample_intent, sample_receipt)
        
        assert proposal.policy_id == "SE_REPR_MEAL_V1"
        assert proposal.stoplight.value == "GREEN"
        assert len(proposal.lines) == 3
        assert proposal.vat_code == "12"
    
    def test_vat_cap_calculation(self, sample_policy, sample_receipt, sample_intent):
        """Test VAT cap calculation."""
        engine = RuleEngine([sample_policy])
        matches = engine.find_matching_policies(sample_intent, sample_receipt)
        
        proposal = engine.create_posting_proposal(matches[0], sample_intent, sample_receipt)
        
        # With 3 attendees and 300 SEK cap per person, max VAT should be 900 SEK
        # Total receipt is 1250 SEK, so VAT should be capped
        vat_line = next(line for line in proposal.lines if line.account == "2641")
        assert vat_line.amount == Decimal("108.00")  # 900 * 0.12
    
    def test_missing_requirements(self, sample_policy, sample_receipt):
        """Test handling of missing requirements."""
        # Create intent without required fields
        incomplete_intent = Intent(
            name="representation_meal",
            confidence=0.9,
            slots={}  # Missing attendees_count and purpose
        )
        
        engine = RuleEngine([sample_policy])
        matches = engine.find_matching_policies(incomplete_intent, sample_receipt)
        
        assert len(matches) == 1
        assert matches[0].matched is False
        assert len(matches[0].missing_requirements) > 0
        
        proposal = engine.create_posting_proposal(matches[0], incomplete_intent, sample_receipt)
        assert proposal.stoplight.value == "YELLOW"
