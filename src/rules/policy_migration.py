"""Policy migration system for handling Kontoplan and policy version changes."""

import json
from datetime import date, datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

from src.rules.bas_dataset import BASManager, BASDataset
from src.rules.engine import RuleEngine


class PolicyMigration:
    """Handles migration between policy and BAS versions."""
    
    def __init__(self, bas_manager: BASManager):
        self.bas_manager = bas_manager
        self.migration_rules = self._load_migration_rules()
    
    def _load_migration_rules(self) -> Dict[str, Any]:
        """Load policy migration rules."""
        return {
            "2025_v1.0_to_2025_v2.0": {
                "account_mappings": {
                    # If account numbers change, map old to new
                    # "6071": "6071"  # No change
                },
                "new_accounts": [
                    "6073",  # Representation, digital
                    "6542"   # AI och automatisering
                ],
                "deprecated_accounts": [
                    # Accounts that are no longer valid
                ],
                "vat_rate_changes": {
                    # "6071": {"old_rate": 12, "new_rate": 12}  # No change
                }
            }
        }
    
    def migrate_policy_to_bas_version(
        self, 
        policy: Dict[str, Any], 
        target_bas_version: str
    ) -> Dict[str, Any]:
        """Migrate a policy to work with a different BAS version."""
        
        current_bas_version = policy.get("bas_version", "2025_v1.0")
        
        if current_bas_version == target_bas_version:
            return policy  # No migration needed
        
        migration_key = f"{current_bas_version}_to_{target_bas_version}"
        
        if migration_key not in self.migration_rules:
            raise ValueError(f"No migration rules found for {migration_key}")
        
        migration_rule = self.migration_rules[migration_key]
        migrated_policy = policy.copy()
        
        # Update BAS version reference
        migrated_policy["bas_version"] = target_bas_version
        
        # Migrate account numbers in posting rules
        if "posting" in migrated_policy.get("rules", {}):
            for posting_rule in migrated_policy["rules"]["posting"]:
                old_account = posting_rule.get("account")
                if old_account in migration_rule.get("account_mappings", {}):
                    posting_rule["account"] = migration_rule["account_mappings"][old_account]
        
        # Update VAT rates if changed
        if "vat" in migrated_policy.get("rules", {}):
            vat_rules = migrated_policy["rules"]["vat"]
            for account, rate_change in migration_rule.get("vat_rate_changes", {}).items():
                # This would need more complex logic based on the specific policy
                pass
        
        return migrated_policy
    
    def validate_policy_against_bas(
        self, 
        policy: Dict[str, Any], 
        bas_version: Optional[str] = None
    ) -> Dict[str, Any]:
        """Validate that all accounts in a policy exist in the specified BAS version."""
        
        if bas_version:
            # Load specific BAS version
            bas_dataset = self._load_bas_version(bas_version)
        else:
            bas_dataset = self.bas_manager.get_current_dataset()
        
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "bas_version": bas_dataset.version
        }
        
        # Extract all account numbers from posting rules
        posting_rules = policy.get("rules", {}).get("posting", [])
        used_accounts = [rule.get("account") for rule in posting_rules if rule.get("account")]
        
        for account_number in used_accounts:
            if not bas_dataset.validate_account(account_number, "SE"):
                validation_result["valid"] = False
                validation_result["errors"].append(
                    f"Account {account_number} not found in BAS {bas_dataset.version}"
                )
        
        return validation_result
    
    def _load_bas_version(self, version: str) -> BASDataset:
        """Load a specific BAS version."""
        bas_file = f"src/rules/bas_datasets/bas_{version.replace('.', '_')}.json"
        
        if not Path(bas_file).exists():
            raise FileNotFoundError(f"BAS dataset {version} not found at {bas_file}")
        
        return self.bas_manager.load_dataset_from_file(bas_file)
    
    def get_compatible_policies(
        self, 
        policies: List[Dict[str, Any]], 
        bas_version: str
    ) -> List[Dict[str, Any]]:
        """Get policies that are compatible with a specific BAS version."""
        
        compatible_policies = []
        
        for policy in policies:
            policy_bas_version = policy.get("bas_version", "2025_v1.0")
            
            if policy_bas_version == bas_version:
                # Direct compatibility
                compatible_policies.append(policy)
            else:
                # Try to migrate
                try:
                    migrated_policy = self.migrate_policy_to_bas_version(policy, bas_version)
                    validation = self.validate_policy_against_bas(migrated_policy, bas_version)
                    
                    if validation["valid"]:
                        compatible_policies.append(migrated_policy)
                    else:
                        print(f"Policy {policy['id']} cannot be migrated: {validation['errors']}")
                        
                except Exception as e:
                    print(f"Failed to migrate policy {policy['id']}: {str(e)}")
        
        return compatible_policies


class PolicyVersionManager:
    """Manages policy versions and BAS compatibility."""
    
    def __init__(self):
        self.bas_manager = BASManager()
        self.migration = PolicyMigration(self.bas_manager)
        self._policy_cache: Dict[str, List[Dict[str, Any]]] = {}
    
    def load_policies_for_date(
        self, 
        target_date: date, 
        bas_version: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Load policies that are effective for a specific date and BAS version."""
        
        if bas_version is None:
            bas_version = self._get_bas_version_for_date(target_date)
        
        cache_key = f"{target_date.isoformat()}_{bas_version}"
        
        if cache_key in self._policy_cache:
            return self._policy_cache[cache_key]
        
        # Load all policies
        all_policies = self._load_all_policies()
        
        # Filter by effective date
        effective_policies = [
            policy for policy in all_policies
            if self._is_policy_effective(policy, target_date)
        ]
        
        # Get compatible policies
        compatible_policies = self.migration.get_compatible_policies(
            effective_policies, bas_version
        )
        
        self._policy_cache[cache_key] = compatible_policies
        return compatible_policies
    
    def _get_bas_version_for_date(self, target_date: date) -> str:
        """Determine which BAS version to use for a given date."""
        
        # This would typically be configured or determined by business rules
        if target_date >= date(2025, 7, 1):
            return "2025_v2.0"
        else:
            return "2025_v1.0"
    
    def _is_policy_effective(self, policy: Dict[str, Any], target_date: date) -> bool:
        """Check if a policy is effective on a given date."""
        
        effective_from = datetime.fromisoformat(policy.get("effective_from", "2024-01-01")).date()
        effective_to = policy.get("effective_to")
        
        if effective_to:
            effective_to = datetime.fromisoformat(effective_to).date()
            return effective_from <= target_date <= effective_to
        else:
            return target_date >= effective_from
    
    def _load_all_policies(self) -> List[Dict[str, Any]]:
        """Load all policy files."""
        
        policies = []
        policy_dir = Path("src/rules/policies")
        
        for policy_file in policy_dir.glob("*.json"):
            try:
                with open(policy_file, 'r', encoding='utf-8') as f:
                    policy = json.load(f)
                    policies.append(policy)
            except Exception as e:
                print(f"Failed to load policy {policy_file}: {str(e)}")
        
        return policies
    
    def create_rule_engine_for_date(
        self, 
        target_date: date, 
        bas_version: Optional[str] = None
    ) -> RuleEngine:
        """Create a RuleEngine with policies effective for a specific date."""
        
        policies = self.load_policies_for_date(target_date, bas_version)
        return RuleEngine(policies)


# Global policy version manager
policy_version_manager = PolicyVersionManager()
