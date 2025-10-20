# Fire & Forget Accounting – Nordic AI Architecture  
**Version:** 1.0  
**Date:** 2025-10-19  
**Author:** Nordmind Interactive  
**Filename:** `fire-and-forget-accounting_nordic-ai-architecture.md`

---

## Table of Contents
1. [Part A – Executive Summary](#part-a--executive-summary)
   - [1. Vision](#1-vision)
   - [2. Market Context & Opportunity](#2-market-context--opportunity)
   - [3. Value Proposition](#3-value-proposition)
   - [4. Key Risks and Mitigation](#4-key-risks-and-mitigation)
   - [5. Legal & Regulatory Landscape (Nordic Focus)](#5-legal--regulatory-landscape-nordic-focus)
   - [6. Strategic Pilot Plan (8 Weeks)](#6-strategic-pilot-plan-8-weeks)
   - [7. Success Metrics & Go/No-Go Criteria](#7-success-metrics--gono-go-criteria)
   - [8. Nordic Expansion Strategy](#8-nordic-expansion-strategy)
2. [Part B – Technical RFC / Design Specification](#part-b--technical-rfc--design-specification)
   - [1. Objective & Scope](#1-objective--scope)
   - [2. Core Architecture Overview](#2-core-architecture-overview)
   - [3. Policy Layer & Rule Engine Design](#3-policy-layer--rule-engine-design)
   - [4. AI & NLP Components](#4-ai--nlp-components)
   - [5. Compliance and Legal Engine](#5-compliance-and-legal-engine)
   - [6. Trust, Security & Explainability Layer](#6-trust-security--explainability-layer)
   - [7. Data Model](#7-data-model)
   - [8. Key Technical Risks & Controls](#8-key-technical-risks--controls)
   - [9. Metrics & Monitoring](#9-metrics--monitoring)
   - [10. Pilot Implementation Plan](#10-pilot-implementation-plan)
   - [11. Roles & Responsibilities](#11-roles--responsibilities)
   - [12. Nordic Readiness Checklist](#12-nordic-readiness-checklist)
   - [13. “Done for Pilot” Definition](#13-done-for-pilot-definition)

---

## Part A – Executive Summary

### 1. Vision
**Fire & Forget Accounting** is an AI-driven platform that transforms bookkeeping into a fully automated, language-based experience.  
Users simply say or type:  
> “Book this receipt for a business lunch,”  
and upload the receipt. The system extracts data, interprets intent, applies accounting and tax rules, and posts the correct journal entry—fully compliant, explainable, and auditable.

The concept: **hands-free, regulation-safe, one-minute bookkeeping**.

---

### 2. Market Context & Opportunity
Nordic small businesses and accounting firms face a paradox:
- They are **digitally mature** (high SaaS adoption, bank API integrations).
- Yet **manual bookkeeping persists** (receipt handling, VAT, representation, expense categorization).

The addressable market:
- ~2 million SMEs in the Nordics.
- >40% report bookkeeping as their top administrative burden.
- Existing solutions (Fortnox, Visma, Tripletex, Bokio, Pleo) offer **semi-automation**, but rely on human confirmation.

**Gap:** True “fire-and-forget” automation—where AI + rule engine + compliance logic make confident, explainable, and lawful decisions.

---

### 3. Value Proposition
- **Human-free bookkeeping:** Upload, confirm, done.  
- **Built-in Nordic compliance:** Follows BAS (SE), SAF-T (NO), SKAT (DK), and Finnish accounting standards.  
- **Explainable AI:** Every automated decision includes reasoning and traceable policy reference.  
- **Adaptive learning:** Learns from user corrections and vendor history.  
- **Audit-ready:** Immutable WORM logs, reversible transactions, and VAT-compliance validation.  

---

### 4. Key Risks and Mitigation

| Risk Area | Description | Mitigation |
|------------|--------------|-------------|
| **Legal/Compliance** | Incorrect handling of VAT or representation could breach tax law. | Versioned policy engine, legal review per country, “stoplight” control (green/yellow/red). |
| **AI Misclassification** | LLM hallucinates or misclassifies. | JSON-schema enforcement, confidence scoring, rule-based overrides. |
| **Trust & Liability** | Businesses fear errors or unclear responsibility. | Transparent reasoning layer, rollback system, limited liability terms. |
| **Data Privacy (GDPR)** | Receipts contain personal data. | EU-hosted, data minimization, on-device OCR, encryption, DPIA. |
| **Regulatory Drift** | Tax laws evolve annually. | Modular rule versioning (“effective-from” metadata), CI-based policy testing. |

---

### 5. Legal & Regulatory Landscape (Nordic Focus)

**Sweden (SE)**  
- Bookkeeping Act: 7-year retention; original image required.  
- VAT: 25/12/6% rates; representation deduction limited.  
- BFN: “God redovisningssed”; BAS plan required.  

**Norway (NO)**  
- Regnskapsloven: 5-year retention; SAF-T reporting mandatory.  
- MVA: 25/15/12%; “mva-koder” must match accounting system.  
- Focus: automation accepted but audit trail required.  

**Denmark (DK)**  
- Bogføringsloven: digital bookkeeping mandatory (from 2024).  
- VAT: 25%; representation rarely deductible.  
- SKAT requires transaction-level traceability.  

**Finland (FI)**  
- Bookkeeping Act: 6-year retention.  
- VAT: 24/14/10%; strong regulation around mixed rates.  
- FAS-compliant structure, strict document auditability.  

**Pan-Nordic Legal Themes:**  
1. Strict retention (5–7 years).  
2. Original receipt format preservation.  
3. Representation and VAT complexity.  
4. Reconciliation between bank feeds and ledgers.  
5. Auditability and explainability expectations.

---

### 6. Strategic Pilot Plan (8 Weeks)

| Sprint | Focus | Deliverables | Validation |
|--------|--------|--------------|-------------|
| 1 | Core OCR & Intent Engine | Upload → JSON → basic classification | Internal test data |
| 2 | Rule Engine + Stoplight Model | Auto-booking + confidence gating | Accounting review |
| 3 | WORM & Compliance Layer | Immutable logs + reversible bookings | Auditor validation |
| 4 | Pilot with Swedish SME & partner accountant | Measure automation precision | Pilot report |
| 4.5 | Nordic Readiness Check | Add DK/NO/FI VAT schemas | Compliance matrix |

---

### 7. Success Metrics & Go/No-Go Criteria

| Metric | Target | Meaning |
|--------|--------|---------|
| **Automation Rate (Green)** | ≥60% | % of transactions fully automated |
| **Precision (Top Scenarios)** | ≥95% | Correct account/moms/dimension mapping |
| **Time-to-Book** | <15s median | End-to-end latency |
| **Exception Rate** | <10% | % flagged for manual review |
| **User Adjustment Rate** | <5% | % of auto-posts later changed |
| **VAT Compliance Errors** | <1% | Detected inconsistencies |

**Go/No-Go Decision:**  
Proceed to Beta rollout only if ≥4 of 6 KPIs are met and auditor approval granted for compliance layer.

---

### 8. Nordic Expansion Strategy
- **Phase 1 (SE)**: Focus on representation, travel, SaaS subscriptions.  
- **Phase 2 (NO)**: Integrate SAF-T schema, MVA code mapping.  
- **Phase 3 (DK)**: Add SKAT compliance export, extend rule set for non-deductible meals.  
- **Phase 4 (FI)**: Extend VAT module and FAS integration.  

---

## Part B – Technical RFC / Design Specification

### 1. Objective & Scope
Build a **Nordic-ready AI-driven accounting engine** that automates bookkeeping via natural language and receipts, maintaining full compliance and auditability.

**Goals**
- Multi-country rule engine (SE, NO, DK, FI)
- Stoplight auto-booking system
- Hybrid AI (LLM + deterministic policy)
- Zero-touch processing pipeline
- Compliance-first data architecture

---

### 2. Core Architecture Overview

User Input (voice/text)
↓
Document Ingestion (OCR + Parsing)
↓
NLU Layer (Intent + Entity Extraction)
↓
Rule Engine (Policy Match + Country Layer)
↓
Confidence Evaluation (Stoplight: Green/Yellow/Red)
↓
Accounting Core (Journal Entry + Ledger Update)
↓
Compliance Engine (Logs + VAT + Audit)
↓
Dashboard/UI Feedback + Reason Codes

bash
Copy code

**Stack (reference choice):**
- Backend: Node.js (NestJS) or Python (FastAPI)
- Database: PostgreSQL (JSONB)
- Storage: S3-compatible, WORM compliance mode
- Frontend: React/Vue + Web Speech API
- OCR: Tesseract (local) + Vision API fallback
- LLM: Local (vLLM) or API (OpenAI, Anthropic) with strict schema enforcement
- Policy Engine: JSON-rule DSL (`$gt`, `$in`, `$and`) + version control

---

### 3. Policy Layer & Rule Engine Design
Each country has:
- **Core Policy Layer:** shared business logic (debit=credit, date rules, etc.)
- **National Policy Module:** VAT rules, representation limits, retention periods
- **Company Overrides:** custom mappings, internal dimensions

Rules are stored as:
```json
{
  "country": "SE",
  "version": "2025-10-A",
  "effective_from": "2025-10-01",
  "conditions": {
    "intent": "representation_meal",
    "amount": {"$lt": 10000},
    "currency": "SEK"
  },
  "actions": {
    "accounts": [
      {"account": "6071", "side": "D"},
      {"account": "2641", "side": "D"},
      {"account": "1930", "side": "K"}
    ],
    "vat_code": "REP12",
    "requires_fields": ["purpose", "participants"]
  }
}
4. AI & NLP Components
Intent Model: Identifies transaction type (representation, taxi, SaaS, etc.)

Entity Extractor: Pulls context from receipts and text (vendor, VAT, amount, participants).

Confidence Scoring: Combines LLM probability + rule validation output.

Language Coverage: sv, no, da, fi, en.

Retraining Loop: Uses user corrections and yellow-zone feedback.

5. Compliance and Legal Engine
Immutable WORM logging (Write Once Read Many)

Digital signature per booking

Versioned policy trace per entry

Document retention per jurisdiction

Country-specific VAT export (SIE, SAF-T, SKAT XML, FAS CSV)

6. Trust, Security & Explainability Layer
Stoplight Model:

🟢 Green = auto-book (confidence > 0.9, rule validated)

🟡 Yellow = ask one clarifying question

🔴 Red = human review

Explainability:

“Reason codes” (e.g., policy_SE_6071_repr, mva_kode_1)

Change audit trail

Transparent JSON output for every step

Security:

TLS 1.3, AES-256 encryption

Role-based access

GDPR-compliant storage (EU-only)

7. Data Model
Core Tables:

documents – source files, hash, metadata

extractions – OCR results

intents – parsed commands

postings – journal entries

rules – accounting policy versions

audits – WORM change logs

suppliers – vendor history & profiles

8. Key Technical Risks & Controls
Risk	Impact	Control
LLM hallucination	Incorrect account/moms	Schema enforcement + rule validation
Policy mismatch	Wrong rule version	Version pinning + regression tests
OCR error	Incorrect amount	Field-level confidence + fallback parsing
Multi-country drift	Wrong VAT logic	Country-specific policy modules
Data leakage	GDPR breach	Local PII masking + EU-only storage

9. Metrics & Monitoring
Metric	Goal	Monitored By
Automation Rate	≥60%	Pipeline logs
Precision	≥95%	Sampled audit tests
Exception Rate	<10%	Dashboard alerts
Policy Drift	0 per release	Regression test suite
VAT Compliance Errors	<1%	Cross-check reports

10. Pilot Implementation Plan
Sprint	Focus	Deliverables
1	OCR + NLU + JSON output	Working ingestion → classification pipeline
2	Policy Engine + Stoplight	Dynamic rule application + confidence thresholds
3	Compliance Layer	WORM, audit trail, reversible postings
4	Swedish live pilot	Measure KPIs, collect corrections
4.5	Nordic Layer	Add DK/NO/FI policy modules

11. Roles & Responsibilities
Role	Responsibility
CTO / System Architect	Oversees architecture, compliance validation
ML Developer	Builds NLU models, confidence scoring
Backend Developer	Rule engine, API, audit pipeline
Accountant/Legal Advisor	Validates rules, tests policy accuracy
QA / Compliance Tester	Regression & VAT test suites
Pilot Partner (SME/Byrå)	Provides data, feedback, validation

12. Nordic Readiness Checklist
 Multi-language OCR support

 Policy DSL versioning

 Separate VAT schemas for SE/NO/DK/FI

 WORM logging with EU storage

 Legal validation per country

 Localization (currency, VAT codes)

13. “Done for Pilot” Definition
✅ 3 top scenarios automated (representation, taxi, SaaS)
✅ ≥95% accuracy verified by accountant
✅ Immutable audit logs stored
✅ Stoplight model functional
✅ Nordic policy modules loaded
✅ One SME and one accounting firm successfully processed 100+ transactions with <5% manual corrections.

End of Document
© 2025 Nordmind Interactive. All rights reserved.

For internal use and pilot evaluation only.