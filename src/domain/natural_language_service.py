"""Natural Language Processing service for direct text input."""

import re
from datetime import date, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from src.domain.models import (
    Currency,
    Intent,
    PostingProposal,
    ReceiptDoc,
    StoplightDecision,
    VATLine,
)


class NaturalLanguageService:
    """Service for processing natural language input and creating bookings."""

    def __init__(self, llm_adapter, rule_engine):
        self.llm = llm_adapter
        self.rule_engine = rule_engine

    async def process_natural_language_input(
        self,
        user_input: str,
        company_id: UUID,
        user_id: UUID | None = None
    ) -> dict[str, Any]:
        """
        Process natural language input and create a booking.
        
        Example input: "Business lunch today with the project manager of Example AB 
        at Example restaurant, total amount 1500 SEK, paid with company credit card"
        """

        # Step 1: Parse the natural language input
        parsed_data = await self._parse_natural_language(user_input)

        # Step 2: Create a ReceiptDoc from parsed data
        receipt_doc = self._create_receipt_doc(parsed_data)

        # Step 3: Detect intent using LLM
        intent = await self._detect_intent_from_text(user_input, receipt_doc)

        # Step 4: Create posting proposal using rule engine
        proposal = await self._create_posting_proposal(intent, receipt_doc)

        # Step 5: Generate user feedback
        feedback = self._generate_user_feedback(proposal, receipt_doc, intent)

        return {
            "parsed_data": parsed_data,
            "receipt_doc": receipt_doc,
            "intent": intent,
            "proposal": proposal,
            "feedback": feedback,
            "company_id": company_id,
            "user_id": user_id
        }

    async def _parse_natural_language(self, user_input: str) -> dict[str, Any]:
        """Parse natural language input to extract structured data."""

        # Use LLM to parse the input
        prompt = f"""
        Parse this natural language input about a business expense and extract structured information.
        
        Input: "{user_input}"
        
        Please respond with a JSON object containing:
        1. "amount": The total amount as a number
        2. "currency": The currency code (SEK, NOK, DKK, EUR, USD)
        3. "vendor": The vendor/restaurant name
        4. "date": The date (use today's date if not specified: {date.today().isoformat()})
        5. "purpose": The business purpose
        6. "attendees_count": Number of people (for meals)
        7. "client": Client name if mentioned
        8. "project": Project name if mentioned
        9. "payment_method": How it was paid
        10. "location": Location if mentioned
        
        Example response:
        {{
            "amount": 1500,
            "currency": "SEK",
            "vendor": "Example restaurant",
            "date": "{date.today().isoformat()}",
            "purpose": "Business lunch with project manager",
            "attendees_count": 2,
            "client": "Example AB",
            "project": null,
            "payment_method": "company credit card",
            "location": null
        }}
        """

        try:
            response = await self.llm.client.chat.completions.create(
                model=self.llm.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at parsing business expense descriptions. Extract structured data accurately."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )

            result = self.llm._validate_intent_result(
                {"slots": {}}  # We'll handle the parsing result differently
            )

            import json
            parsed = json.loads(response.choices[0].message.content)
            return self._validate_parsed_data(parsed)

        except Exception:
            # Fallback to rule-based parsing
            return self._fallback_parse(user_input)

    def _validate_parsed_data(self, data: dict[str, Any]) -> dict[str, Any]:
        """Validate and clean parsed data."""

        # Ensure required fields
        if "amount" not in data:
            data["amount"] = 0.0

        if "currency" not in data:
            data["currency"] = "SEK"

        if "date" not in data:
            data["date"] = date.today().isoformat()

        if "vendor" not in data:
            data["vendor"] = "Unknown vendor"

        if "purpose" not in data:
            data["purpose"] = "Business expense"

        # Validate currency
        valid_currencies = ["SEK", "NOK", "DKK", "EUR", "USD"]
        if data["currency"] not in valid_currencies:
            data["currency"] = "SEK"

        # Validate amount
        try:
            data["amount"] = float(data["amount"])
        except (ValueError, TypeError):
            data["amount"] = 0.0

        # Validate attendees count
        if "attendees_count" in data:
            try:
                data["attendees_count"] = int(data["attendees_count"])
            except (ValueError, TypeError):
                data["attendees_count"] = 1
        else:
            data["attendees_count"] = 1

        return data

    def _fallback_parse(self, user_input: str) -> dict[str, Any]:
        """Fallback rule-based parsing."""

        # Extract amount and currency using regex
        amount_match = re.search(r'(\d+(?:\.\d{2})?)\s*(SEK|NOK|DKK|EUR|USD)?', user_input, re.IGNORECASE)
        amount = 0.0
        currency = "SEK"

        if amount_match:
            amount = float(amount_match.group(1))
            if amount_match.group(2):
                currency = amount_match.group(2).upper()

        # Extract vendor (look for various patterns)
        vendor = "Unknown vendor"
        vendor_patterns = [
            r'at\s+([^,]+?)(?:\s+restaurant|\s+cafe|\s+bar|,|$)',
            r'restaurant\s+([^,]+?)(?:,|$)',
            r'cafe\s+([^,]+?)(?:,|$)',
            r'bar\s+([^,]+?)(?:,|$)',
            r'from\s+([^,]+?)(?:\s+on|\s+for|,|$)',
            r'från\s+([^,]+?)(?:\s+på|\s+för|,|$)',
            r'köpt.*?från\s+([^,]+?)(?:\s+på|,|$)',
            r'bought.*?from\s+([^,]+?)(?:\s+for|,|$)'
        ]

        for pattern in vendor_patterns:
            match = re.search(pattern, user_input, re.IGNORECASE)
            if match:
                vendor = match.group(1).strip()
                break

        # Extract client (look for "of" or "with")
        client = None
        client_match = re.search(r'(?:with|of)\s+([^,]+?)(?:\s+at|,|$)', user_input, re.IGNORECASE)
        if client_match:
            client = client_match.group(1).strip()

        # Determine purpose and extract additional info
        purpose = "Business expense"
        installment_months = None
        device_type = None

        if "lunch" in user_input.lower():
            purpose = "Business lunch"
        elif "dinner" in user_input.lower():
            purpose = "Business dinner"
        elif "meal" in user_input.lower():
            purpose = "Business meal"
        elif any(word in user_input.lower() for word in ["mobil", "mobile", "telefon", "phone"]):
            purpose = "Mobile phone purchase"
            device_type = "mobile phone"

            # Extract installment months
            installment_match = re.search(r'(\d+)\s*(?:månader|months?)', user_input, re.IGNORECASE)
            if installment_match:
                installment_months = int(installment_match.group(1))

        return {
            "amount": amount,
            "currency": currency,
            "vendor": vendor,
            "date": date.today().isoformat(),
            "purpose": purpose,
            "attendees_count": 1,
            "client": client,
            "project": None,
            "payment_method": "company credit card",
            "location": None,
            "installment_months": installment_months,
            "device_type": device_type,
            "total_amount": amount
        }

    def _create_receipt_doc(self, parsed_data: dict[str, Any]) -> ReceiptDoc:
        """Create a ReceiptDoc from parsed data."""

        amount = Decimal(str(parsed_data["amount"]))
        currency = Currency(parsed_data["currency"])

        # Calculate VAT (assume 25% for now, will be refined by rule engine)
        vat_rate = Decimal("0.25")
        vat_amount = amount * vat_rate / (Decimal("1") + vat_rate)
        base_amount = amount - vat_amount

        vat_line = VATLine(
            rate=vat_rate,
            amount=vat_amount,
            base_amount=base_amount
        )

        return ReceiptDoc(
            total=amount,
            currency=currency,
            vat_lines=[vat_line],
            vendor=parsed_data["vendor"],
            date=datetime.fromisoformat(parsed_data["date"]).date(),
            raw_text=f"Natural language input: {parsed_data['purpose']}",
            confidence=0.9  # High confidence for manual input
        )

    async def _detect_intent_from_text(self, user_input: str, receipt_doc: ReceiptDoc) -> Intent:
        """Detect intent from natural language input."""

        # Use existing NLU service logic
        context = {
            "receipt": {
                "vendor": receipt_doc.vendor,
                "total": float(receipt_doc.total),
                "currency": receipt_doc.currency,
                "date": receipt_doc.date.isoformat(),
                "raw_text": receipt_doc.raw_text
            },
            "user_text": user_input
        }

        try:
            intent_result = await self.llm.detect_intent(context)
            # If LLM returns other_business with low confidence, try fallback
            if intent_result.get("intent") == "other_business" and intent_result.get("confidence", 0) < 0.5:
                fallback_result = self._fallback_intent_detection(user_input, receipt_doc)
                if fallback_result.get("intent") != "other_business":
                    intent_result = fallback_result
        except Exception:
            # Fallback to rule-based intent detection
            intent_result = self._fallback_intent_detection(user_input, receipt_doc)

        return Intent(
            name=intent_result["intent"],
            confidence=intent_result["confidence"],
            slots=intent_result["slots"]
        )

    def _fallback_intent_detection(self, user_input: str, receipt_doc: ReceiptDoc) -> dict[str, Any]:
        """Fallback intent detection using rule-based approach."""

        user_lower = user_input.lower()

        # Check for mobile phone purchase
        if any(word in user_lower for word in ["mobil", "mobile", "telefon", "phone"]):
            return {
                "intent": "mobile_phone_purchase",
                "confidence": 0.8,
                "slots": {
                    "installment_months": self._extract_installment_months(user_input),
                    "total_amount": float(receipt_doc.total),
                    "device_type": "mobile phone"
                }
            }

        # Check for representation meal
        elif any(word in user_lower for word in ["lunch", "dinner", "meal", "måltid", "lunch"]):
            return {
                "intent": "representation_meal",
                "confidence": 0.8,
                "slots": {
                    "attendees_count": self._extract_attendees_count(user_input),
                    "purpose": "Business meal"
                }
            }

        # Check for computer purchase
        elif any(word in user_lower for word in ["dator", "computer", "laptop", "pc", "it-utrustning"]):
            return {
                "intent": "computer_purchase",
                "confidence": 0.8,
                "slots": {
                    "total_amount": float(receipt_doc.total),
                    "device_type": "computer"
                }
            }

        # Check for office supplies
        elif any(word in user_lower for word in ["kontorsmaterial", "office supplies", "papper", "penna", "material"]):
            return {
                "intent": "office_supplies",
                "confidence": 0.8,
                "slots": {
                    "purpose": "Office supplies"
                }
            }

        # Check for consulting services
        elif any(word in user_lower for word in ["konsult", "consulting", "rådgivning", "tjänst"]):
            return {
                "intent": "consulting_services",
                "confidence": 0.8,
                "slots": {
                    "service_period": "monthly"
                }
            }

        # Check for employee expense
        elif any(word in user_lower for word in ["utlägg", "anställd", "employee", "privat kort"]):
            return {
                "intent": "employee_expense",
                "confidence": 0.8,
                "slots": {
                    "employee_name": "Unknown employee"
                }
            }

        # Check for leasing
        elif any(word in user_lower for word in ["leasing", "kopiator", "hyra", "rental"]):
            return {
                "intent": "leasing",
                "confidence": 0.8,
                "slots": {
                    "lease_period": "monthly",
                    "equipment_type": "equipment"
                }
            }

        # Check for SaaS subscription
        elif any(word in user_lower for word in ["subscription", "saas", "cloud", "software", "prenumeration"]):
            return {
                "intent": "saas_subscription",
                "confidence": 0.8,
                "slots": {
                    "service_period": "monthly"
                }
            }

        # Default to other business
        else:
            return {
                "intent": "other_business",
                "confidence": 0.6,
                "slots": {}
            }

    def _extract_installment_months(self, user_input: str) -> int:
        """Extract installment months from user input."""
        import re
        match = re.search(r'(\d+)\s*(?:månader|months?)', user_input, re.IGNORECASE)
        return int(match.group(1)) if match else 1

    def _extract_attendees_count(self, user_input: str) -> int:
        """Extract attendees count from user input."""
        import re
        match = re.search(r'(\d+)\s*(?:people|personer|person|människor)', user_input, re.IGNORECASE)
        return int(match.group(1)) if match else 1

    async def _create_posting_proposal(self, intent: Intent, receipt_doc: ReceiptDoc) -> PostingProposal:
        """Create posting proposal using rule engine."""

        # Find matching policies
        policy_matches = self.rule_engine.find_matching_policies(intent, receipt_doc)

        if not policy_matches:
            return PostingProposal(
                lines=[],
                vat_code=None,
                confidence=0.0,
                reason_codes=["No matching policy found"],
                stoplight=StoplightDecision.RED,
                policy_id=None
            )

        # Use the best matching policy
        best_match = policy_matches[0]
        return self.rule_engine.create_posting_proposal(best_match, intent, receipt_doc)

    def _generate_user_feedback(self, proposal: PostingProposal, receipt_doc: ReceiptDoc, intent: Intent) -> dict[str, Any]:
        """Generate user feedback about the booking."""

        feedback = {
            "status": proposal.stoplight.value,
            "message": "",
            "booking_details": {
                "debit_accounts": [],
                "credit_accounts": [],
                "vat_details": {},
                "total_amount": float(receipt_doc.total),
                "currency": receipt_doc.currency.value,
                "deductible_breakdown": {}
            },
            "reason_codes": proposal.reason_codes,
            "policy_used": proposal.policy_id,
            "receipt_attachment_prompt": "Would you like to attach a receipt for this booking?"
        }

        # Organize posting lines by debit/credit
        for line in proposal.lines:
            line_info = {
                "account": line.account,
                "amount": float(line.amount),
                "description": line.description or ""
            }

            if line.side == "D":
                feedback["booking_details"]["debit_accounts"].append(line_info)
            else:
                feedback["booking_details"]["credit_accounts"].append(line_info)

        # VAT details
        if proposal.vat_code:
            vat_info = {
                "code": proposal.vat_code,
                "rate": "12%" if "12" in proposal.vat_code else "25%"
            }
            if proposal.vat_mode:
                vat_info["mode"] = proposal.vat_mode
            if proposal.report_boxes:
                vat_info["report_boxes"] = proposal.report_boxes
            feedback["booking_details"]["vat_details"] = vat_info

        # Calculate deductible breakdown for representation meals
        if intent.name == "representation_meal" and proposal.vat_mode == "standard":
            self._add_deductible_breakdown(feedback, proposal, receipt_doc, intent)

        # Generate status message
        if proposal.stoplight == StoplightDecision.GREEN:
            feedback["message"] = f"✅ Booking created successfully! {intent.name.replace('_', ' ').title()} expense of {receipt_doc.total} {receipt_doc.currency.value} has been automatically booked."
        elif proposal.stoplight == StoplightDecision.YELLOW:
            feedback["message"] = f"⚠️ Booking requires clarification. Please provide additional information to complete the {intent.name.replace('_', ' ').title()} expense booking."
        else:
            feedback["message"] = f"❌ Manual review required. The {intent.name.replace('_', ' ').title()} expense could not be automatically processed."

        return feedback

    def _add_deductible_breakdown(self, feedback: dict[str, Any], proposal: PostingProposal, receipt_doc: ReceiptDoc, intent: Intent) -> None:
        """Add deductible vs non-deductible breakdown for representation meals."""

        # Find deductible and non-deductible amounts from posting lines
        deductible_net = 0.0
        non_deductible_net = 0.0
        vat_deductible = 0.0

        for line in proposal.lines:
            if line.account == "6071":  # Representation, avdragsgill
                deductible_net = float(line.amount)
            elif line.account == "6072":  # Representation, ej avdragsgill
                non_deductible_net = float(line.amount)
            elif line.account == "2641":  # Ingående moms, avdragsgill
                vat_deductible = float(line.amount)

        attendees_count = intent.slots.get("attendees_count", 1)
        max_deductible_per_person = 300.0
        max_deductible_total = max_deductible_per_person * attendees_count

        feedback["booking_details"]["deductible_breakdown"] = {
            "max_deductible_per_person_sek": max_deductible_per_person,
            "attendees_count": attendees_count,
            "max_deductible_total_sek": max_deductible_total,
            "deductible_net": deductible_net,
            "non_deductible_net": non_deductible_net,
            "vat_deductible": vat_deductible,
            "total_deductible": deductible_net + vat_deductible,
            "total_non_deductible": non_deductible_net,
            "tax_benefit_sek": deductible_net + vat_deductible,
            "explanation": f"Representation meals are deductible up to {max_deductible_per_person} SEK per person (including VAT). For {attendees_count} person(s), maximum deductible amount is {max_deductible_total} SEK."
        }
