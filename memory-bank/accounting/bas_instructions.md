# BAS 2025 v1.0 Integration Guidelines

## Purpose
This document describes how the Fire & Forget AI Accounting system integrates and uses **Kontoplan – BAS 2025 v. 1.0** as a structured, versioned reference model for bookkeeping logic, policy enforcement, validation, and journal entry generation.

---

## Why BAS Is Required
✅ Official Swedish standardized chart of accounts  
✅ Guarantees legal compliance for booking and exports (SIE, SAF-T)  
✅ Ensures postings are validated against approved accounts  
✅ Enables rules-based mappings per accounting class  
✅ Forms the foundation for VAT logic, income/cost classification, and reporting categories  

---

## Where BAS Is Used in the System

| System Component | How BAS is used |
|------------------|-----------------|
| Policy DSL Engine | Rules map logical posting types to BAS account numbers |
| Posting Proposal | Account numbers validated against BAS dataset |
| Confidence Scoring | Invalid/dubious account mappings reduce score |
| Booking Service | Only BAS-approved accounts are allowed |
| WORM Audit | Accounts attached to audit history |
| Exporters (SIE, SAF-T) | BAS structure ensures compliant output |
| Reporting & Analysis | Classification by BAS account group |

---

## Storage Format

BAS must be stored as a **versioned dataset**, not hard-coded into logic.

Example JSON (stored as `bas_2025_v1.json` or in DB):

```json
{
  "version": "2025_v1.0",
  "effective_from": "2025-01-01",
  "accounts": [
    {
      "number": "6071",
      "name": "Representation",
      "class": "60",
      "type": "expense",
      "vat_hint": "12",
      "allowed_regions": ["SE"]
    }
  ]
}
```

---

## Database Table Suggestion

```sql
CREATE TABLE bas_accounts (
  number VARCHAR PRIMARY KEY,
  name TEXT NOT NULL,
  account_class VARCHAR NOT NULL,
  account_type VARCHAR NOT NULL,
  vat_hint NUMERIC(4,2),
  allowed_regions TEXT[],
  bas_version TEXT NOT NULL,
  effective_from DATE NOT NULL
);
```

---

## Referencing BAS in Rules

Instead of hardcoding account numbers in policies, policies should reference logical types or categories:

✅ Example in policy DSL:
```json
"posting": [
  { "resolve_account": "EXPENSE::REPRESENTATION", "side": "D", "amount": "net_after_cap" }
]
```

The system will:
1. Look up BAS accounts linked to `EXPENSE::REPRESENTATION`
2. Validate against correct BAS version
3. Apply regional filtering (e.g., SE-specific accounts)

Fallback: Direct assignment is allowed only if validated against current BAS version.

---

## Version Control & Validation

| Action | Rule |
|--------|------|
| Import new BAS version | Must be stored independently with version + effective_from |
| Policy referencing BAS | Must include a `bas_version` field |
| CI checks | Validate all referenced BAS accounts exist for specified version |
| BAS updates | Must revalidate affected policies before promotion |

---

## BAS Upgrade Process

| Step | Action |
|------|--------|
| 1 | Upload new BAS dataset (e.g., `bas_2026_v1.0.json`) |
| 2 | Run policy validation job |
| 3 | Identify affected accounts/rules |
| 4 | Approve or update affected mappings |
| 5 | Set `effective_from` for new version |
| 6 | Deploy with changelog |

---

## Future Enhancements
✅ Automatic vendor → BAS classification (ML-assisted)  
✅ Group-based approval per account class  
✅ VAT consistency warnings (rate mismatch vs BAS)  
✅ Dimensional hints (project/cost center) based on BAS grouping  

---

## Ownership & Responsibility
| Role | Responsibility |
|------|----------------|
| Accounting/Policy Owner | Approve BAS version updates |
| Rule Engine Developer | Ensure BAS compliance in rules |
| QA | Run regression tests on BAS-sensitive workflows |
| DevOps | Handle BAS dataset deployment & versioning |

---

## Summary
BAS is not just a list — it is a foundational compliance and logic model. It must be versioned, validated, referenced dynamically, and used across rules, booking, audit, and exports for full automation and legal safety.
