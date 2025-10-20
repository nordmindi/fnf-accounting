# Kontoplan Versioning and Policy Management

## Overview

The Fire & Forget Accounting system is designed to handle changes to the Swedish Kontoplan (Chart of Accounts) and policy versioning through a comprehensive versioning system that ensures compliance and continuity.

## Architecture

### 1. BAS Dataset Management

The system uses a structured approach to manage different versions of the Swedish BAS (Bokföringsnämnden) dataset:

```
src/rules/bas_datasets/
├── bas_2025_v1_0.json    # BAS 2025 v1.0 (Jan 2025)
├── bas_2025_v2_0.json    # BAS 2025 v2.0 (Jul 2025)
└── bas_2026_v1_0.json    # Future versions
```

### 2. Policy Versioning

Each policy references a specific BAS version:

```json
{
  "id": "SE_REPR_MEAL_V1",
  "version": "V1",
  "bas_version": "2025_v1.0",
  "effective_from": "2024-01-01",
  "effective_to": "2025-06-30"
}
```

### 3. Version Migration System

The system automatically handles:
- **Policy Migration**: Converting policies between BAS versions
- **Account Validation**: Ensuring all accounts exist in the target BAS
- **Date-based Selection**: Loading appropriate versions based on transaction dates

## Key Features

### 1. Automatic Version Selection

The system automatically selects the correct BAS version based on the transaction date:

```python
# For transactions in January 2025
bas_version = "2025_v1.0"

# For transactions in July 2025
bas_version = "2025_v2.0"
```

### 2. Policy Migration

When BAS versions change, the system can migrate existing policies:

```python
# Migrate policy from BAS 2025 v1.0 to v2.0
migrated_policy = migration.migrate_policy_to_bas_version(
    original_policy, 
    "2025_v2.0"
)
```

### 3. Account Validation

All policies are validated against the target BAS version:

```python
validation = migration.validate_policy_against_bas(policy, "2025_v2.0")
if not validation["valid"]:
    print(f"Errors: {validation['errors']}")
```

## Example: BAS 2025 v1.0 to v2.0 Migration

### New Accounts in v2.0

```json
{
  "number": "6073",
  "name": "Representation, digital",
  "account_class": "60",
  "account_type": "expense",
  "vat_hint": 25.0,
  "description": "Digital representation expenses (new in v2.0)"
},
{
  "number": "6542",
  "name": "AI och automatisering",
  "account_class": "65",
  "account_type": "expense",
  "vat_hint": 25.0,
  "description": "AI and automation services (new in v2.0)"
}
```

### Policy Updates

New policies can be created to take advantage of new accounts:

```json
{
  "id": "SE_REPR_MEAL_V2",
  "version": "V2",
  "bas_version": "2025_v2.0",
  "effective_from": "2025-07-01",
  "rules": {
    "posting": [
      {"account": "6071", "side": "D", "amount": "deductible_net", "description": "Representation, avdragsgill"},
      {"account": "6073", "side": "D", "amount": "digital_net", "description": "Representation, digital"}
    ]
  }
}
```

## Usage Examples

### 1. Loading Policies for a Specific Date

```python
from src.rules.policy_migration import PolicyVersionManager
from datetime import date

pvm = PolicyVersionManager()

# Load policies effective for January 2025
policies = pvm.load_policies_for_date(date(2025, 1, 15))

# Load policies effective for July 2025 (includes migrated policies)
policies = pvm.load_policies_for_date(date(2025, 7, 15))
```

### 2. Creating Rule Engine for Historical Dates

```python
# Create rule engine for transactions in January 2025
rule_engine = pvm.create_rule_engine_for_date(date(2025, 1, 15))

# Create rule engine for transactions in July 2025
rule_engine = pvm.create_rule_engine_for_date(date(2025, 7, 15))
```

### 3. Manual Policy Migration

```python
# Migrate a specific policy to a new BAS version
migrated_policy = migration.migrate_policy_to_bas_version(
    original_policy, 
    "2025_v2.0"
)

# Validate the migrated policy
validation = migration.validate_policy_against_bas(
    migrated_policy, 
    "2025_v2.0"
)
```

## Migration Rules

The system uses migration rules to handle changes between BAS versions:

```python
migration_rules = {
    "2025_v1.0_to_2025_v2.0": {
        "account_mappings": {
            # Map old account numbers to new ones if they change
        },
        "new_accounts": [
            "6073",  # Representation, digital
            "6542"   # AI och automatisering
        ],
        "deprecated_accounts": [
            # Accounts that are no longer valid
        ],
        "vat_rate_changes": {
            # VAT rate changes for specific accounts
        }
    }
}
```

## Benefits

### 1. **Compliance Assurance**
- Automatic validation against current BAS version
- Prevents use of deprecated accounts
- Ensures VAT rates are current

### 2. **Historical Accuracy**
- Maintains correct accounting for historical transactions
- Uses appropriate BAS version for each transaction date
- Preserves audit trail

### 3. **Seamless Updates**
- Automatic migration of existing policies
- No manual intervention required for most changes
- Backward compatibility maintained

### 4. **Future-Proof Design**
- Easy to add new BAS versions
- Flexible migration rules
- Extensible policy system

## Configuration

### Environment Variables

```bash
# Default BAS version (can be overridden by date)
DEFAULT_BAS_VERSION=2025_v1.0

# Policy cache settings
POLICY_CACHE_ENABLED=true
POLICY_CACHE_TTL=3600
```

### Policy Configuration

Each policy specifies:
- **bas_version**: Which BAS version it's designed for
- **effective_from**: When the policy becomes active
- **effective_to**: When the policy expires (optional)

## Monitoring and Alerts

The system provides monitoring for:
- **Policy Validation Failures**: When policies reference invalid accounts
- **Migration Warnings**: When policies cannot be automatically migrated
- **Version Mismatches**: When policies reference outdated BAS versions

## Best Practices

### 1. **Policy Development**
- Always specify the correct `bas_version` in policies
- Include `effective_from` and `effective_to` dates
- Test policies against the target BAS version

### 2. **Migration Testing**
- Test policy migrations before deploying new BAS versions
- Validate all migrated policies
- Monitor for validation errors

### 3. **Version Management**
- Keep migration rules up to date
- Document changes between BAS versions
- Maintain backward compatibility when possible

## Future Enhancements

### Planned Features
- **Automatic BAS Updates**: Integration with official BAS releases
- **Policy Templates**: Reusable policy components
- **Migration Analytics**: Tracking of policy usage and migration success
- **Multi-Country Support**: Extension to other Nordic countries

### API Endpoints
- `GET /api/v1/bas/versions` - List available BAS versions
- `GET /api/v1/bas/{version}/accounts` - List accounts in a BAS version
- `POST /api/v1/policies/migrate` - Migrate policies between versions
- `GET /api/v1/policies/validate` - Validate policies against BAS

This versioning system ensures that the Fire & Forget Accounting platform remains compliant with Swedish accounting standards while providing flexibility for future changes and updates.
