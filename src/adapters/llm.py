"""LLM adapter for natural language understanding."""

import json
from typing import Any

from openai import AsyncOpenAI


class LLMAdapter:
    """LLM adapter using OpenAI API."""

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.client = AsyncOpenAI(api_key=config.get("api_key"))
        self.model = config.get("model", "gpt-4")
        self.temperature = config.get("temperature", 0.1)

    async def detect_intent(self, context: dict[str, Any]) -> dict[str, Any]:
        """Detect intent and extract slots from context."""
        prompt = self._build_intent_prompt(context)

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert accounting assistant that analyzes receipts and user instructions to determine the business intent and extract relevant information."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.temperature,
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)
            return self._validate_intent_result(result)

        except Exception:
            # Fallback to rule-based intent detection
            return self._fallback_intent_detection(context)

    def _build_intent_prompt(self, context: dict[str, Any]) -> str:
        """Build prompt for intent detection."""
        receipt = context.get("receipt", {})
        user_text = context.get("user_text", "")

        prompt = f"""
Analyze this receipt and user instruction to determine the business intent and extract relevant information.

Receipt Information:
- Vendor: {receipt.get('vendor', 'Unknown')}
- Total: {receipt.get('total', 0)} {receipt.get('currency', 'SEK')}
- Date: {receipt.get('date', 'Unknown')}
- Raw text: {receipt.get('raw_text', '')[:500]}...

User instruction: "{user_text}"

Please respond with a JSON object containing:
1. "intent": One of these business intents:
   - "representation_meal" (business meals, client entertainment, lunch, dinner, fika)
   - "taxi_transport" (taxi, public transport, travel)
   - "saas_subscription" (software subscriptions, cloud services, AWS, Azure)
   - "office_supplies" (office materials, equipment, supplies, kontorsmaterial)
   - "travel_accommodation" (hotels, accommodation)
   - "mobile_phone_purchase" (mobile phones, smartphones, tablets, electronics, NetOnNet, Elgiganten, Media Markt)
   - "computer_purchase" (computers, laptops, IT equipment, dator)
   - "consulting_services" (consulting, konsulttjänst, EU services)
   - "employee_expense" (employee expenses, utlägg, private card)
   - "leasing" (leasing, kopiator, equipment rental)
   - "other_business" (other business expenses)
   - "personal" (personal expenses)

IMPORTANT: 
- If the text mentions mobile phones, smartphones, tablets, or electronics from stores like NetOnNet, Elgiganten, Media Markt, use "mobile_phone_purchase" intent.
- If the text mentions computers, laptops, or IT equipment, use "computer_purchase" intent.
- If the text mentions consulting services from EU, use "consulting_services" intent.
- If the text mentions employee expenses or utlägg, use "employee_expense" intent.
- If the text mentions leasing or kopiator, use "leasing" intent.

2. "confidence": A number between 0.0 and 1.0 indicating confidence

3. "slots": Extract relevant information as key-value pairs:
   - "attendees_count": Number of people (for meals)
   - "purpose": Business purpose/description
   - "project": Project code or name
   - "cost_center": Cost center code
   - "client": Client name (for representation)
   - "destination": Travel destination
   - "service_period": Service period (for subscriptions)
   - "installment_months": Number of months for installment payment
   - "total_amount": Total purchase amount
   - "device_type": Type of device (mobile phone, tablet, etc.)
   - "employee_name": Employee name (for expenses)
   - "lease_period": Lease period (for leasing)
   - "equipment_type": Type of equipment (for leasing)

Example response:
{{
  "intent": "representation_meal",
  "confidence": 0.9,
  "slots": {{
    "attendees_count": 3,
    "purpose": "Client meeting over lunch",
    "client": "Acme Corp"
  }}
}}
"""
        return prompt

    def _validate_intent_result(self, result: dict[str, Any]) -> dict[str, Any]:
        """Validate and clean intent detection result."""
        # Ensure required fields
        if "intent" not in result:
            result["intent"] = "other_business"

        if "confidence" not in result:
            result["confidence"] = 0.5

        if "slots" not in result:
            result["slots"] = {}

        # Validate intent
        valid_intents = [
            "representation_meal",
            "taxi_transport",
            "saas_subscription",
            "office_supplies",
            "travel_accommodation",
            "other_business",
            "personal"
        ]

        if result["intent"] not in valid_intents:
            result["intent"] = "other_business"

        # Validate confidence
        confidence = float(result["confidence"])
        result["confidence"] = max(0.0, min(1.0, confidence))

        # Clean slots
        slots = result["slots"]
        if not isinstance(slots, dict):
            result["slots"] = {}

        # Convert numeric slots
        if "attendees_count" in slots:
            try:
                result["slots"]["attendees_count"] = int(slots["attendees_count"])
            except:
                result["slots"]["attendees_count"] = 1

        return result

    def _fallback_intent_detection(self, context: dict[str, Any]) -> dict[str, Any]:
        """Fallback rule-based intent detection."""
        receipt = context.get("receipt", {})
        user_text = context.get("user_text", "").lower()
        vendor = receipt.get("vendor", "").lower()

        # Rule-based intent detection
        if any(word in user_text for word in ["meal", "lunch", "dinner", "restaurant", "representation"]):
            return {
                "intent": "representation_meal",
                "confidence": 0.7,
                "slots": {
                    "attendees_count": 1,
                    "purpose": "Business meal"  # Add default purpose
                }
            }

        if any(word in user_text for word in ["taxi", "transport", "travel", "uber"]):
            return {
                "intent": "taxi_transport",
                "confidence": 0.7,
                "slots": {"purpose": "Business transport"}
            }

        if any(word in user_text for word in ["subscription", "saas", "software", "cloud"]):
            return {
                "intent": "saas_subscription",
                "confidence": 0.7,
                "slots": {"service_period": "Monthly"}
            }

        # Vendor-based detection
        if any(word in vendor for word in ["restaurant", "cafe", "bar", "hotel"]):
            return {
                "intent": "representation_meal",
                "confidence": 0.6,
                "slots": {
                    "attendees_count": 1,
                    "purpose": "Business meal"  # Add default purpose
                }
            }

        if any(word in vendor for word in ["taxi", "uber", "transport"]):
            return {
                "intent": "taxi_transport",
                "confidence": 0.6,
                "slots": {}
            }

        # Default
        return {
            "intent": "other_business",
            "confidence": 0.3,
            "slots": {
                "purpose": user_text or "General business expense"
            }
        }

    async def generate_clarification_question(
        self,
        proposal: dict[str, Any],
        missing_fields: list[str]
    ) -> str:
        """Generate a clarifying question for missing information."""
        if not missing_fields:
            return "Please provide additional details for this expense."

        # Map field names to user-friendly questions
        field_questions = {
            "attendees_count": "How many people attended this meal?",
            "purpose": "What was the business purpose of this expense?",
            "project": "Which project should this expense be charged to?",
            "cost_center": "Which cost center should this expense be charged to?",
            "client": "Which client was this expense for?",
            "destination": "What was the travel destination?",
            "service_period": "What period does this subscription cover?"
        }

        # Use the first missing field for the question
        first_field = missing_fields[0]
        return field_questions.get(first_field, "Please provide additional details for this expense.")

    async def explain_booking_decision(
        self,
        proposal: dict[str, Any],
        receipt: dict[str, Any]
    ) -> str:
        """Generate explanation for booking decision."""
        stoplight = proposal.get("stoplight", "RED")
        policy_id = proposal.get("policy_id", "Unknown")
        reason_codes = proposal.get("reason_codes", [])

        if stoplight == "GREEN":
            return f"Automatically booked using policy {policy_id}. The expense was processed without manual intervention."
        elif stoplight == "YELLOW":
            return f"Requires clarification for policy {policy_id}. Please provide additional information to complete the booking."
        else:
            reasons = ", ".join(reason_codes) if reason_codes else "manual review required"
            return f"Manual review required: {reasons}. The system could not automatically process this expense."
