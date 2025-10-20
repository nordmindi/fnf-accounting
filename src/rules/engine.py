"""Policy rule engine for applying accounting rules."""

import json
from datetime import date
from decimal import Decimal
from typing import Any, Dict, List, Optional

import jsonschema
from pydantic import BaseModel

from src.domain.models import Intent, PostingLine, PostingProposal, ReceiptDoc, StoplightDecision
from src.rules.bas_dataset import validate_bas_account, get_bas_account_info


class PolicyMatch(BaseModel):
    """Result of policy matching."""
    policy_id: str
    confidence: float
    matched: bool
    missing_requirements: List[str]
    applied_rules: Dict[str, Any]


class RuleEngine:
    """Rule engine for applying accounting policies."""
    
    def __init__(self, policies: List[Dict[str, Any]]):
        """Initialize rule engine with policies."""
        self.policies = policies
        self._validate_policies()
    
    def _validate_policies(self) -> None:
        """Validate all policies against JSON schema."""
        from src.rules.schemas import POLICY_SCHEMA
        
        for policy in self.policies:
            try:
                jsonschema.validate(policy, POLICY_SCHEMA)
            except jsonschema.ValidationError as e:
                raise ValueError(f"Invalid policy {policy.get('id', 'unknown')}: {e.message}")
    
    def find_matching_policies(
        self, 
        intent: Intent, 
        receipt: ReceiptDoc
    ) -> List[PolicyMatch]:
        """Find policies that match the given intent and receipt."""
        matches = []
        
        for policy in self.policies:
            match = self._match_policy(policy, intent, receipt)
            matches.append(match)
        
        # Sort by confidence descending
        matches.sort(key=lambda x: x.confidence, reverse=True)
        return matches
    
    def _match_policy(
        self, 
        policy: Dict[str, Any], 
        intent: Intent, 
        receipt: ReceiptDoc
    ) -> PolicyMatch:
        """Match a single policy against intent and receipt."""
        rules = policy["rules"]
        match_rules = rules.get("match", {})
        
        confidence = 0.0
        matched = True
        missing_requirements = []
        
        
        # Check intent match
        if "intent" in match_rules:
            if intent.name == match_rules["intent"]:
                confidence += 0.5
            else:
                matched = False
        
        # Check vendor patterns
        if "vendor_patterns" in match_rules and receipt.vendor:
            vendor_matched = any(
                pattern.lower() in receipt.vendor.lower() 
                for pattern in match_rules["vendor_patterns"]
            )
            if vendor_matched:
                confidence += 0.2
        
        # Check amount ranges
        if "amount_min" in match_rules:
            if receipt.total < Decimal(str(match_rules["amount_min"])):
                matched = False
        
        if "amount_max" in match_rules:
            if receipt.total > Decimal(str(match_rules["amount_max"])):
                matched = False
        
        # Check required fields
        requirements = rules.get("requires", [])
        for req in requirements:
            field_path = req["field"]
            op = req["op"]
            expected_value = req.get("value")  # Use get() to handle missing value for 'exists' operator
            
            actual_value = self._get_field_value(intent.slots, field_path)
            
            if not self._evaluate_requirement(actual_value, op, expected_value):
                missing_requirements.append(field_path)
                matched = False
        
        # Add confidence for meeting all requirements
        if matched and not missing_requirements:
            confidence += 0.3
        
        return PolicyMatch(
            policy_id=policy["id"],
            confidence=confidence,
            matched=matched,
            missing_requirements=missing_requirements,
            applied_rules=rules
        )
    
    def _get_field_value(self, slots: Dict[str, Any], field_path: str) -> Any:
        """Get value from nested field path."""
        parts = field_path.split(".")
        value = slots
        
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return None
        
        return value
    
    def _evaluate_requirement(self, actual_value: Any, op: str, expected_value: Any) -> bool:
        """Evaluate a requirement condition."""
        if op == "exists":
            return actual_value is not None
        elif op == ">=":
            return actual_value is not None and actual_value >= expected_value
        elif op == "<=":
            return actual_value is not None and actual_value <= expected_value
        elif op == "==":
            return actual_value == expected_value
        elif op == "!=":
            return actual_value != expected_value
        elif op == "in":
            return actual_value in expected_value
        elif op == "not_in":
            return actual_value not in expected_value
        else:
            return False
    
    def create_posting_proposal(
        self, 
        policy_match: PolicyMatch, 
        intent: Intent, 
        receipt: ReceiptDoc
    ) -> PostingProposal:
        """Create posting proposal from policy match."""
        if not policy_match.matched:
            return self._create_failed_proposal(policy_match)
        
        rules = policy_match.applied_rules
        posting_rules = rules.get("posting", [])
        vat_rules = rules.get("vat", {})
        stoplight_rules = rules.get("stoplight", {})
        
        # Calculate amounts
        amounts = self._calculate_amounts(receipt, vat_rules, intent.slots)
        
        # Create posting lines
        lines = []
        for posting_rule in posting_rules:
            line = self._create_posting_line(posting_rule, amounts, intent.slots)
            if line:
                lines.append(line)
        
        # Determine stoplight decision
        stoplight = self._determine_stoplight(
            policy_match, 
            stoplight_rules, 
            amounts.get("confidence", 0.0)
        )
        
        # Generate reason codes
        reason_codes = self._generate_reason_codes(policy_match, amounts)
        
        return PostingProposal(
            lines=lines,
            vat_code=vat_rules.get("code"),
            confidence=policy_match.confidence,
            reason_codes=reason_codes,
            stoplight=stoplight,
            policy_id=policy_match.policy_id,
            vat_mode=("reverse_charge" if vat_rules.get("reverse_charge") else "standard"),
            report_boxes=vat_rules.get("report_boxes")
        )
    
    def _calculate_amounts(
        self, 
        receipt: ReceiptDoc, 
        vat_rules: Dict[str, Any], 
        slots: Dict[str, Any]
    ) -> Dict[str, Decimal]:
        """Calculate posting amounts based on VAT rules.

        Notes:
        - For standard VAT scenarios, the incoming amount (gross) includes VAT; we split into net and VAT.
        - For reverse charge scenarios (vat.reverse_charge == true), the incoming amount is treated as net,
          and VAT is computed on top (no change to cash/bank amount).
        - For deductible_split scenarios (e.g., representation meals), we split into deductible and non-deductible portions."""
        gross = receipt.total
        vat_rate = Decimal(str(vat_rules.get("rate", 0))) / 100
        cap_per_person = Decimal(str(vat_rules.get("cap_sek_per_person", 0)))
        is_reverse_charge = bool(vat_rules.get("reverse_charge", False))
        is_deductible_split = bool(vat_rules.get("deductible_split", False))

        if is_reverse_charge:
            # For reverse charge, treat the provided amount as net and compute VAT on top.
            net_before_cap = gross.quantize(Decimal('0.01'))
            vat_before_cap = (net_before_cap * vat_rate).quantize(Decimal('0.01'))
            # No VAT cap logic applies typically to reverse charge; keep net_after_cap equal to net_before_cap
            net_after_cap = net_before_cap
            vat_allowed = vat_before_cap
            vat_excess = Decimal("0")
            deductible_net = Decimal("0")
            non_deductible_net = Decimal("0")
            vat_deductible = Decimal("0")
        elif is_deductible_split:
            # For deductible split (representation meals), calculate deductible vs non-deductible portions
            attendees_count = slots.get("attendees_count", 1)
            max_deductible_gross = cap_per_person * attendees_count
            
            # Calculate total VAT
            net_before_cap = (gross / (1 + vat_rate)).quantize(Decimal('0.01'))
            vat_before_cap = (gross - net_before_cap).quantize(Decimal('0.01'))
            
            if gross <= max_deductible_gross:
                # Entire amount is deductible
                deductible_net = net_before_cap
                non_deductible_net = Decimal("0")
                vat_deductible = vat_before_cap
                vat_allowed = vat_before_cap
                vat_excess = Decimal("0")
            else:
                # Split into deductible and non-deductible portions
                deductible_gross = max_deductible_gross
                deductible_net = (deductible_gross / (1 + vat_rate)).quantize(Decimal('0.01'))
                vat_deductible = (deductible_gross - deductible_net).quantize(Decimal('0.01'))
                
                non_deductible_gross = gross - deductible_gross
                non_deductible_net = (non_deductible_gross / (1 + vat_rate)).quantize(Decimal('0.01'))
                
                vat_allowed = vat_deductible
                vat_excess = vat_before_cap - vat_deductible
            
            net_after_cap = net_before_cap  # Keep for compatibility
        else:
            # Standard VAT: the provided amount includes VAT; split into net and VAT parts.
            net_before_cap = (gross / (1 + vat_rate)).quantize(Decimal('0.01'))
            vat_before_cap = (gross - net_before_cap).quantize(Decimal('0.01'))
            
            # Apply per-person cap if applicable (e.g., representation meals)
            attendees_count = slots.get("attendees_count", 1)
            max_vat_allowed = cap_per_person * attendees_count
            
            if vat_before_cap <= max_vat_allowed or max_vat_allowed == 0:
                vat_allowed = vat_before_cap
                net_after_cap = net_before_cap
                vat_excess = Decimal("0")
            else:
                vat_allowed = max_vat_allowed
                net_after_cap = (gross - vat_allowed).quantize(Decimal('0.01'))
                vat_excess = (vat_before_cap - vat_allowed).quantize(Decimal('0.01'))
            
            deductible_net = Decimal("0")
            non_deductible_net = Decimal("0")
            vat_deductible = Decimal("0")
        
        return {
            "gross": gross,
            "net_before_cap": net_before_cap,
            "net_after_cap": net_after_cap,
            "vat_before_cap": vat_before_cap,
            "vat_allowed": vat_allowed,
            "vat_excess": vat_excess,
            "deductible_net": deductible_net,
            "non_deductible_net": non_deductible_net,
            "vat_deductible": vat_deductible,
            "confidence": 0.9  # TODO: Calculate based on data quality
        }
    
    def _create_posting_line(
        self, 
        posting_rule: Dict[str, Any], 
        amounts: Dict[str, Decimal], 
        slots: Dict[str, Any]
    ) -> Optional[PostingLine]:
        """Create a single posting line from rule."""
        amount_key = posting_rule["amount"]
        
        if amount_key not in amounts:
            return None
        
        account_number = posting_rule["account"]
        
        # Validate account against BAS dataset
        if not validate_bas_account(account_number, "SE"):
            # Log warning but continue - in production this should be stricter
            print(f"Warning: Account {account_number} not found in BAS dataset")
        
        return PostingLine(
            account=account_number,
            side=posting_rule["side"],
            amount=amounts[amount_key],
            dimension_project=posting_rule.get("dimension_project") or slots.get("project"),
            dimension_cost_center=posting_rule.get("dimension_cost_center") or slots.get("cost_center"),
            description=posting_rule.get("description")
        )
    
    def _determine_stoplight(
        self, 
        policy_match: PolicyMatch, 
        stoplight_rules: Dict[str, Any], 
        confidence: float
    ) -> StoplightDecision:
        """Determine stoplight decision."""
        if policy_match.missing_requirements:
            return StoplightDecision(stoplight_rules.get("on_missing_required", "YELLOW"))
        
        confidence_threshold = stoplight_rules.get("confidence_threshold", 0.8)
        
        if confidence >= confidence_threshold:
            return StoplightDecision.GREEN
        else:
            return StoplightDecision(stoplight_rules.get("on_fail", "RED"))
    
    def _create_failed_proposal(self, policy_match: PolicyMatch) -> PostingProposal:
        """Create proposal for failed policy match."""
        return PostingProposal(
            lines=[],
            vat_code=None,
            confidence=0.0,
            reason_codes=[f"Policy {policy_match.policy_id} failed to match"],
            stoplight=StoplightDecision.RED,
            policy_id=policy_match.policy_id
        )
    
    def _generate_reason_codes(
        self, 
        policy_match: PolicyMatch, 
        amounts: Dict[str, Decimal]
    ) -> List[str]:
        """Generate reason codes for the proposal."""
        codes = [f"Policy: {policy_match.policy_id}"]
        
        if amounts.get("vat_excess", 0) > 0:
            codes.append("VAT cap applied")
        
        if policy_match.missing_requirements:
            codes.append(f"Missing: {', '.join(policy_match.missing_requirements)}")
        
        return codes
