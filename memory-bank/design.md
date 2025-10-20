# Design Specification – Fire & Forget AI Accounting

## Design Principles ✅ IMPLEMENTED
- **Separation of concerns**: API vs. Services vs. Adapters vs. Rules. ✅
- **Policy-driven automation**: All tax/VAT/representation logic lives in versioned policies. ✅
- **Explainability**: Every booking carries reason codes and a verifiable audit chain. ✅
- **Stoplight decisions**: GREEN (auto-book), YELLOW (one clarifying question), RED (park). ✅
- **Nordic-ready**: Country policy layers (SE → NO/DK/FI) atop a shared core. ✅ (SE implemented)
- **Natural Language Processing**: AI-powered intent detection and entity extraction. ✅
- **BAS Versioning**: Support for multiple BAS versions with automatic migration. ✅
- **VAT Optimization**: Deductible splits and reverse charge VAT handling. ✅

## Domain Services (Responsibilities) ✅ IMPLEMENTED
| Service | Responsibility | Status |
|---------|----------------|--------|
| DocumentService | Intake, dedupe (hash+amount+date), storage metadata | ✅ |
| ExtractionService | OCR + parsing → normalized `ReceiptDoc` JSON | ✅ |
| NLUService | Intent & slot detection from user text + doc context | ✅ |
| NaturalLanguageService | AI-powered NLP processing with fallback detection | ✅ |
| ProposalService | LLM suggestion + Rules application → posting proposal | ✅ |
| StoplightService | Decide GREEN/YELLOW/RED based on confidence & policy requirements | ✅ |
| BookingService | Create `JournalEntry` + `JournalLines`, handle dimensions | ✅ |
| PolicyService | Load/validate policy DSL (JSON Schema) + BAS versioning | ✅ |
| PolicyMigrationService | BAS version migration and account validation | ✅ |
| VATOptimizationService | Deductible splits and tax optimization | ✅ |
| ReasonService | Produce concise explanation tags (policy hits, VAT decisions) | ✅ |

## Pipeline (run_pipeline) ✅ IMPLEMENTED
1. Load document ✅
2. OCR & parse (totals, VAT lines, vendor, date, currency) ✅
3. Infer intent & slots (purpose, attendees, project/cost-center) ✅
4. Apply policy DSL (country-specific rules) ✅
5. Build posting proposal (accounts, VAT, amounts, dimensions) ✅
6. Stoplight decision (conf thresholds, required fields) ✅
7. If GREEN → post booking; If YELLOW → one question; If RED → park ✅
8. Persist audit (WORM), link to original document ✅

## Natural Language Processing Pipeline ✅ IMPLEMENTED
1. Natural language input (Swedish/English) ✅
2. AI intent detection with OpenAI GPT-4 ✅
3. Entity extraction (amount, vendor, purpose, attendees, etc.) ✅
4. Fallback detection when LLM confidence is low ✅
5. Policy matching with BAS versioning ✅
6. VAT optimization (deductible splits, reverse charge) ✅
7. Stoplight decision based on confidence and requirements ✅
8. Journal entry creation with detailed user feedback ✅

## Policy DSL (JSON Example – SE representation meal) ✅ IMPLEMENTED
```json
{
  "id": "SE_REPR_MEAL_V1",
  "version": "V1",
  "country": "SE",
  "effective_from": "2024-01-01",
  "name": "Swedish Representation Meal Policy",
  "description": "Policy for representation meals in Sweden with VAT cap and deductible/non-deductible split",
  "bas_version": "2025_v1.0",
  "rules": {
    "match": { "intent": "representation_meal" },
    "requires": [
      {"field": "attendees_count", "op": ">=", "value": 1},
      {"field": "purpose", "op": "exists"}
    ],
    "vat": { 
      "rate": 12, 
      "cap_sek_per_person": 300,
      "code": "12",
      "deductible_split": true
    },
    "posting": [
      {"account": "6071", "side": "D", "amount": "deductible_net", "description": "Representation, avdragsgill"},
      {"account": "6072", "side": "D", "amount": "non_deductible_net", "description": "Representation, ej avdragsgill"},
      {"account": "2641", "side": "D", "amount": "vat_deductible", "description": "Ingående moms, avdragsgill"},
      {"account": "1930", "side": "K", "amount": "gross", "description": "Cash/Bank"}
    ],
    "stoplight": { "on_missing_required": "YELLOW", "on_fail": "RED", "confidence_threshold": 0.8 }
  }
}
```

## Booking Model ✅ IMPLEMENTED
```
JournalEntry(id, company_id, date, series, number, notes)
  └─ JournalLines(entry_id, account, D/K, amount, dim_project, dim_cc)
```

## Data Contracts (Pydantic Models) ✅ IMPLEMENTED
```python
class ReceiptDoc(BaseModel):
    total: Decimal
    currency: Currency
    vat_lines: List[VATLine]
    vendor: Optional[str]
    date: date
    # Additional fields for enhanced processing

class Intent(BaseModel):
    name: str
    confidence: float
    slots: Dict[str, Any]

class PostingProposal(BaseModel):
    lines: List[PostingLine]
    vat_code: Optional[str]
    vat_mode: Optional[str]  # "standard", "reverse_charge"
    report_boxes: Optional[Dict[str, str]]  # VAT report box mappings
    confidence: float
    reason_codes: List[str]
    stoplight: StoplightDecision

class PostingLine(BaseModel):
    account: str
    side: Literal["D", "K"]
    amount: Decimal
    description: str
    dimensions: Optional[Dict[str, str]]

class StoplightDecision(str, Enum):
    GREEN = "GREEN"
    YELLOW = "YELLOW"
    RED = "RED"
```

## Current Implementation Status ✅ COMPLETED
- **8 Swedish Policies**: Complete coverage of common accounting scenarios
- **BAS Versioning**: Support for BAS 2025 v1.0 and v2.0
- **VAT Optimization**: Deductible splits and reverse charge VAT
- **Natural Language Processing**: AI-powered intent detection and entity extraction
- **Comprehensive Testing**: 90%+ test coverage
- **Production-Ready**: Complete documentation and Docker containerization
