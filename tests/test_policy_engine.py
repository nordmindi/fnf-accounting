"""Comprehensive tests for Policy Engine and Migration System."""

import json
from datetime import date
from decimal import Decimal
from unittest.mock import Mock, patch

import pytest

from src.domain.models import Currency, Intent, ReceiptDoc, VATLine
from src.rules.bas_dataset import BASManager
from src.rules.engine import RuleEngine
from src.rules.policy_migration import PolicyMigration, PolicyVersionManager


class TestRuleEngine:
    """Test suite for Rule Engine."""

    @pytest.fixture
    def sample_policies(self):
        """Sample policies for testing."""
        return [
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
            }
        ]

    @pytest.fixture
    def rule_engine(self, sample_policies):
        """Rule engine instance."""
        return RuleEngine(sample_policies)

    @pytest.fixture
    def sample_intent(self):
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
    def sample_receipt(self):
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

    def test_policy_matching(self, rule_engine, sample_intent, sample_receipt):
        """Test policy matching logic."""
        matches = rule_engine.find_matching_policies(sample_intent, sample_receipt)

        assert len(matches) == 1
        assert matches[0].policy_id == "SE_REPR_MEAL_V1"
        assert matches[0].matched is True
        assert matches[0].confidence == 0.9

    def test_policy_requirements_validation(self, rule_engine, sample_receipt):
        """Test policy requirements validation."""
        # Test with missing required field
        incomplete_intent = Intent(
            name="representation_meal",
            confidence=0.9,
            slots={"attendees_count": 2}  # Missing purpose
        )

        matches = rule_engine.find_matching_policies(incomplete_intent, sample_receipt)

        assert len(matches) == 1
        assert matches[0].matched is False
        assert "purpose" in matches[0].missing_requirements

    def test_vat_calculation_standard(self, rule_engine, sample_intent, sample_receipt):
        """Test standard VAT calculation."""
        policy = rule_engine.policies[0]
        amounts = rule_engine._calculate_amounts(
            Decimal('1500.00'),
            policy["rules"]["vat"],
            sample_intent.slots
        )

        assert amounts["gross"] == Decimal('1500.00')
        assert amounts["net_before_cap"] == Decimal('1339.29')
        assert amounts["vat_before_cap"] == Decimal('160.71')
        assert amounts["vat_mode"] == "standard"

    def test_vat_calculation_reverse_charge(self, rule_engine):
        """Test reverse charge VAT calculation."""
        policy = rule_engine.policies[1]  # SaaS reverse charge policy
        amounts = rule_engine._calculate_amounts(
            Decimal('4500.00'),  # This is treated as net amount
            policy["rules"]["vat"],
            {"service_period": "October 2025"}
        )

        assert amounts["net_before_cap"] == Decimal('4500.00')
        assert amounts["vat_before_cap"] == Decimal('1125.00')
        assert amounts["gross"] == Decimal('5625.00')
        assert amounts["vat_mode"] == "reverse_charge"

    def test_vat_calculation_deductible_split(self, rule_engine, sample_intent):
        """Test deductible split calculation for representation meals."""
        policy = rule_engine.policies[0]  # Representation meal policy
        amounts = rule_engine._calculate_amounts(
            Decimal('1500.00'),
            policy["rules"]["vat"],
            sample_intent.slots
        )

        # With 2 attendees, max deductible is 600 SEK (2 * 300)
        assert amounts["deductible_net"] == Decimal('480.00')
        assert amounts["non_deductible_net"] == Decimal('900.00')
        assert amounts["vat_deductible"] == Decimal('120.00')
        assert amounts["vat_mode"] == "standard"

    def test_posting_line_creation(self, rule_engine, sample_intent):
        """Test posting line creation."""
        amounts = {
            "deductible_net": Decimal('480.00'),
            "non_deductible_net": Decimal('900.00'),
            "vat_deductible": Decimal('120.00'),
            "gross": Decimal('1500.00')
        }

        posting_rule = {
            "account": "6071",
            "side": "D",
            "amount": "deductible_net",
            "description": "Representation, avdragsgill"
        }

        line = rule_engine._create_posting_line(posting_rule, amounts, sample_intent.slots)

        assert line.account == "6071"
        assert line.side == "D"
        assert line.amount == Decimal('480.00')
        assert line.description == "Representation, avdragsgill"

    def test_stoplight_determination(self, rule_engine, sample_intent, sample_receipt):
        """Test stoplight decision logic."""
        # Test GREEN - all requirements met
        matches = rule_engine.find_matching_policies(sample_intent, sample_receipt)
        proposal = rule_engine.apply_policy(matches[0], sample_intent, sample_receipt)

        assert proposal.stoplight.value == "GREEN"

        # Test YELLOW - missing requirements
        incomplete_intent = Intent(
            name="representation_meal",
            confidence=0.9,
            slots={"attendees_count": 2}  # Missing purpose
        )

        matches = rule_engine.find_matching_policies(incomplete_intent, sample_receipt)
        proposal = rule_engine.apply_policy(matches[0], incomplete_intent, sample_receipt)

        assert proposal.stoplight.value == "YELLOW"

    def test_policy_application(self, rule_engine, sample_intent, sample_receipt):
        """Test complete policy application."""
        matches = rule_engine.find_matching_policies(sample_intent, sample_receipt)
        proposal = rule_engine.apply_policy(matches[0], sample_intent, sample_receipt)

        assert proposal.stoplight.value == "GREEN"
        assert len(proposal.lines) == 4
        assert proposal.vat_mode == "standard"

        # Verify posting lines
        accounts = [line.account for line in proposal.lines]
        assert "6071" in accounts  # Deductible representation
        assert "6072" in accounts  # Non-deductible representation
        assert "2641" in accounts  # VAT deductible
        assert "1930" in accounts  # Bank


class TestPolicyMigration:
    """Test suite for Policy Migration System."""

    @pytest.fixture
    def bas_manager(self):
        """BAS manager instance."""
        return BASManager()

    @pytest.fixture
    def migration(self, bas_manager):
        """Policy migration instance."""
        return PolicyMigration(bas_manager)

    @pytest.fixture
    def sample_policy_v1(self):
        """Sample policy for BAS v1.0."""
        return {
            "id": "SE_REPR_MEAL_V1",
            "version": "V1",
            "bas_version": "2025_v1.0",
            "effective_from": "2024-01-01",
            "rules": {
                "posting": [
                    {"account": "6071", "side": "D", "amount": "deductible_net"},
                    {"account": "2641", "side": "D", "amount": "vat_deductible"},
                    {"account": "1930", "side": "K", "amount": "gross"}
                ]
            }
        }

    def test_policy_migration_same_version(self, migration, sample_policy_v1):
        """Test migration when versions are the same."""
        result = migration.migrate_policy_to_bas_version(
            sample_policy_v1,
            "2025_v1.0"
        )

        assert result == sample_policy_v1  # No changes needed

    def test_policy_migration_different_version(self, migration, sample_policy_v1):
        """Test migration between different BAS versions."""
        result = migration.migrate_policy_to_bas_version(
            sample_policy_v1,
            "2025_v2.0"
        )

        assert result["bas_version"] == "2025_v2.0"
        assert result["id"] == sample_policy_v1["id"]  # ID unchanged

    def test_policy_validation_valid_accounts(self, migration, sample_policy_v1):
        """Test policy validation with valid accounts."""
        validation = migration.validate_policy_against_bas(sample_policy_v1, "2025_v1.0")

        assert validation["valid"] is True
        assert len(validation["errors"]) == 0

    def test_policy_validation_invalid_accounts(self, migration):
        """Test policy validation with invalid accounts."""
        invalid_policy = {
            "id": "TEST_POLICY",
            "bas_version": "2025_v1.0",
            "rules": {
                "posting": [
                    {"account": "9999", "side": "D", "amount": "gross"}  # Invalid account
                ]
            }
        }

        validation = migration.validate_policy_against_bas(invalid_policy, "2025_v1.0")

        assert validation["valid"] is False
        assert len(validation["errors"]) > 0
        assert "Account 9999 not found" in validation["errors"][0]

    def test_compatible_policies_filtering(self, migration):
        """Test filtering of compatible policies."""
        policies = [
            {
                "id": "POLICY_V1",
                "bas_version": "2025_v1.0",
                "rules": {"posting": [{"account": "6071", "side": "D", "amount": "gross"}]}
            },
            {
                "id": "POLICY_V2",
                "bas_version": "2025_v2.0",
                "rules": {"posting": [{"account": "6071", "side": "D", "amount": "gross"}]}
            }
        ]

        compatible = migration.get_compatible_policies(policies, "2025_v1.0")

        assert len(compatible) == 1
        assert compatible[0]["id"] == "POLICY_V1"


class TestPolicyVersionManager:
    """Test suite for Policy Version Manager."""

    @pytest.fixture
    def pvm(self):
        """Policy version manager instance."""
        return PolicyVersionManager()

    def test_bas_version_selection(self, pvm):
        """Test BAS version selection based on date."""
        # Test January 2025
        bas_v1 = pvm._get_bas_version_for_date(date(2025, 1, 15))
        assert bas_v1 == "2025_v1.0"

        # Test July 2025
        bas_v2 = pvm._get_bas_version_for_date(date(2025, 7, 15))
        assert bas_v2 == "2025_v2.0"

    def test_policy_effectiveness_check(self, pvm):
        """Test policy effectiveness date checking."""
        policy = {
            "effective_from": "2024-01-01",
            "effective_to": "2025-06-30"
        }

        # Test within effective period
        assert pvm._is_policy_effective(policy, date(2025, 3, 15)) is True

        # Test before effective period
        assert pvm._is_policy_effective(policy, date(2023, 12, 31)) is False

        # Test after effective period
        assert pvm._is_policy_effective(policy, date(2025, 7, 1)) is False

    def test_policy_effectiveness_no_end_date(self, pvm):
        """Test policy effectiveness without end date."""
        policy = {
            "effective_from": "2024-01-01"
        }

        # Test after effective date
        assert pvm._is_policy_effective(policy, date(2025, 12, 31)) is True

        # Test before effective date
        assert pvm._is_policy_effective(policy, date(2023, 12, 31)) is False

    @patch('src.rules.policy_migration.Path')
    def test_policy_loading(self, mock_path, pvm):
        """Test policy loading from files."""
        # Mock file system
        mock_file = Mock()
        mock_file.glob.return_value = [Mock()]
        mock_path.return_value = mock_file

        # Mock file content
        with patch('builtins.open', mock_open()) as mock_file_open:
            mock_file_open.return_value.__enter__.return_value.read.return_value = json.dumps({
                "id": "TEST_POLICY",
                "bas_version": "2025_v1.0",
                "effective_from": "2024-01-01"
            })

            policies = pvm._load_all_policies()

            assert len(policies) == 1
            assert policies[0]["id"] == "TEST_POLICY"


def mock_open():
    """Mock open function for testing."""
    from unittest.mock import mock_open as _mock_open
    return _mock_open()
