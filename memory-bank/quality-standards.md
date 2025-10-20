# Quality Standards

## Coding
- Python 3.12+, FastAPI, Pydantic v2
- Clean Architecture boundaries; no business logic in routers/adapters
- Use `decimal.Decimal` for money, never float
- Timezones: store UTC, display local
- Docstrings for public functions; type hints everywhere

## Testing
| Level | Scope | Tools |
|------|-------|-------|
| Unit | Rule engine (VAT, caps), services | pytest |
| Integration | OCR→NLU→Rules on fixed fixtures | pytest + factory fixtures |
| E2E | Upload→Pipeline→Booking | httpx, docker-compose for env |
| Regression | Policy snapshots per country | pytest + jsonschema |

Targets:
- Unit coverage ≥ 80% for rules & booking
- E2E happy-paths for 3 MVP scenarios

## Reviews
- At least 1 reviewer per PR
- Any policy change must include test fixtures and changelog
- Max PR size ~500 LOC (split otherwise)
- CI must pass (lint, tests, policy-validate)

## CI/CD
- Black, isort, ruff
- Mypy strict
- Pytest (unit, integration, e2e)
- JSON Schema validation for policies
- Docker image build + vulnerability scan

## Security & Compliance
- Secrets via env/secret manager
- PII minimization + masking in logs
- EU/EES storage preference
- DPIA documented before pilot
- WORM-style audit chain for bookings
