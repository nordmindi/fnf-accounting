# Design Specification – Fire & Forget AI Accounting

## Design Principles
- **Separation of concerns**: API vs. Services vs. Adapters vs. Rules.
- **Policy-driven automation**: All tax/VAT/representation logic lives in versioned policies.
- **Explainability**: Every booking carries reason codes and a verifiable audit chain.
- **Stoplight decisions**: GREEN (auto-book), YELLOW (one clarifying question), RED (park).
- **Nordic-ready**: Country policy layers (SE → NO/DK/FI) atop a shared core.

## Domain Services (Responsibilities)
| Service | Responsibility |
|---------|----------------|
| DocumentService | Intake, dedupe (hash+amount+date), storage metadata |
| ExtractionService | OCR + parsing → normalized `ReceiptDoc` JSON |
| NLUService | Intent & slot detection from user text + doc context |
| ProposalService | LLM suggestion + Rules application → posting proposal |
| StoplightService | Decide GREEN/YELLOW/RED based on confidence & policy requirements |
| BookingService | Create `JournalEntry` + `JournalLines`, handle dimensions |
| PolicyService | Load/validate policy DSL (JSON Schema) |
| ReasonService | Produce concise explanation tags (policy hits, VAT decisions) |

## Pipeline (run_pipeline)
1. Load document
2. OCR & parse (totals, VAT lines, vendor, date, currency)
3. Infer intent & slots (purpose, attendees, project/cost-center)
4. Apply policy DSL (country-specific rules)
5. Build posting proposal (accounts, VAT, amounts, dimensions)
6. Stoplight decision (conf thresholds, required fields)
7. If GREEN → post booking; If YELLOW → one question; If RED → park
8. Persist audit (WORM), link to original document

## Policy DSL (JSON Example – SE representation meal)
```json
{
  "id": "SE_REPR_MEAL_V1",
  "match": { "intent": "representation_meal" },
  "requires": [
    {"field": "slots.attendees_count", "op": ">=", "value": 1},
    {"field": "slots.purpose", "op": "exists"}
  ],
  "vat": { "rate": 12, "cap_sek_per_person": 300 },
  "posting": [
    {"account": "6071", "side": "D", "amount": "net_after_cap"},
    {"account": "2641", "side": "D", "amount": "vat_allowed"},
    {"account": "1930", "side": "K", "amount": "gross"}
  ],
  "stoplight": { "on_missing_required": "YELLOW", "on_fail": "RED" }
}
```

## Booking Model
```
JournalEntry(id, company_id, date, series, number, notes)
  └─ JournalLines(entry_id, account, D/K, amount, dim_project, dim_cc)
```

## Data Contracts (Pydantic Sketch)
```python
class ReceiptDoc(BaseModel):
    total: Decimal
    currency: str
    vat_lines: list[dict]
    vendor: str | None
    date: date

class Intent(BaseModel):
    name: str
    confidence: float
    slots: dict

class PostingProposal(BaseModel):
    lines: list[dict]         # [{account, side, amount, dims?}]
    vat_code: str | None
    confidence: float
    reason_codes: list[str]
    stoplight: Literal["GREEN","YELLOW","RED"]
```
