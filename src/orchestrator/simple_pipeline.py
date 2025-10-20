"""Simplified pipeline orchestrator for MVP functionality."""

import asyncio
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

from src.domain.models import PipelineRun, StoplightDecision
from src.domain.services import (
    ExtractionService,
    NLUService,
    ProposalService,
    StoplightService,
    BookingService,
)
from src.rules.engine import RuleEngine
from src.adapters.ocr import OCRAdapter
from src.adapters.llm import LLMAdapter
from src.app.booking_service_factory import BookingServiceFactory


class SimplePipelineOrchestrator:
    """Simplified orchestrator for document processing pipeline."""
    
    def __init__(self):
        # Store pipeline results in memory
        self.pipeline_results = {}
        # Initialize adapters
        ocr_config = {
            "tesseract": {
                "language": "swe+eng",
                "psm": 6,
            }
        }
        self.ocr_adapter = OCRAdapter(ocr_config)
        
        llm_config = {
            "api_key": "dummy-key",  # Will use fallback detection
            "model": "gpt-4",
            "temperature": 0.1,
        }
        self.llm_adapter = LLMAdapter(llm_config)
        
        # Initialize services
        self.extraction_service = ExtractionService(self.ocr_adapter)
        self.nlu_service = NLUService(self.llm_adapter)
        
        # Load policies and initialize rule engine
        self.rule_engine = self._load_rule_engine()
        self.proposal_service = ProposalService(self.rule_engine)
        
        stoplight_config = {
            "confidence_threshold": 0.8,
            "high_value_threshold": 10000,
        }
        self.stoplight_service = StoplightService(stoplight_config)
        
        # Booking service with pipeline integration
        self.booking_service = BookingServiceFactory.create_booking_service()
    
    def _load_rule_engine(self) -> RuleEngine:
        """Load policies and create rule engine."""
        policies = []
        try:
            import json
            import os
            
            policies_dir = "src/rules/policies"
            if os.path.exists(policies_dir):
                for filename in os.listdir(policies_dir):
                    if filename.endswith(".json"):
                        with open(os.path.join(policies_dir, filename), "r") as f:
                            policy = json.load(f)
                            policies.append(policy)
        except Exception as e:
            print(f"Warning: Could not load policies: {e}")
            # Use default policies
            policies = self._get_default_policies()
        
        return RuleEngine(policies)
    
    def _get_default_policies(self):
        """Get default policies for testing."""
        return [
            {
                "id": "SE_REPR_MEAL_V1",
                "version": "V1",
                "country": "SE",
                "effective_from": "2024-01-01",
                "name": "Swedish Representation Meal Policy",
                "description": "Policy for representation meals in Sweden",
                "rules": {
                    "match": {
                        "intent": "representation_meal"
                    },
                    "requires": [
                        {"field": "slots.attendees_count", "op": ">=", "value": 1},
                        {"field": "slots.purpose", "op": "exists"}
                    ],
                    "vat": {
                        "rate": 12,
                        "cap_sek_per_person": 300,
                        "code": "12"
                    },
                    "posting": [
                        {"account": "6071", "side": "D", "amount": "net_after_cap"},
                        {"account": "2641", "side": "D", "amount": "vat_allowed"},
                        {"account": "1930", "side": "K", "amount": "gross"}
                    ],
                    "stoplight": {
                        "on_missing_required": "YELLOW",
                        "on_fail": "RED",
                        "confidence_threshold": 0.8
                    }
                }
            },
            {
                "id": "SE_TAXI_TRANSPORT_V1",
                "version": "V1",
                "country": "SE",
                "effective_from": "2024-01-01",
                "name": "Swedish Taxi Transport Policy",
                "description": "Policy for taxi and transport expenses in Sweden",
                "rules": {
                    "match": {
                        "intent": "taxi_transport"
                    },
                    "requires": [
                        {"field": "slots.purpose", "op": "exists"}
                    ],
                    "vat": {
                        "rate": 25,
                        "code": "25"
                    },
                    "posting": [
                        {"account": "6540", "side": "D", "amount": "net_before_cap"},
                        {"account": "2640", "side": "D", "amount": "vat_before_cap"},
                        {"account": "1930", "side": "K", "amount": "gross"}
                    ],
                    "stoplight": {
                        "on_missing_required": "YELLOW",
                        "on_fail": "RED",
                        "confidence_threshold": 0.8
                    }
                }
            },
            {
                "id": "SE_SAAS_SUBSCRIPTION_V1",
                "version": "V1",
                "country": "SE",
                "effective_from": "2024-01-01",
                "name": "Swedish SaaS Subscription Policy",
                "description": "Policy for software subscriptions in Sweden",
                "rules": {
                    "match": {
                        "intent": "saas_subscription"
                    },
                    "requires": [
                        {"field": "slots.purpose", "op": "exists"}
                    ],
                    "vat": {
                        "rate": 25,
                        "code": "25"
                    },
                    "posting": [
                        {"account": "6541", "side": "D", "amount": "net_before_cap"},
                        {"account": "2640", "side": "D", "amount": "vat_before_cap"},
                        {"account": "1930", "side": "K", "amount": "gross"}
                    ],
                    "stoplight": {
                        "on_missing_required": "YELLOW",
                        "on_fail": "RED",
                        "confidence_threshold": 0.8
                    }
                }
            }
        ]
    
    async def run_pipeline(
        self,
        file_content: bytes,
        content_type: str,
        company_id: UUID,
        user_text: Optional[str] = None,
        user_id: Optional[UUID] = None
    ) -> dict:
        """Run the complete document processing pipeline."""
        pipeline_run_id = uuid4()
        
        try:
            # Step 1: Extract receipt data
            receipt_doc = await self.extraction_service.extract_receipt(
                file_content, 
                content_type
            )
            
            # Step 2: Detect intent
            intent = await self.nlu_service.detect_intent(receipt_doc, user_text)
            
            # Step 3: Create posting proposal
            proposal = await self.proposal_service.create_proposal(intent, receipt_doc)
            
            # Step 4: Make stoplight decision
            final_decision = self.stoplight_service.decide_stoplight(
                proposal, intent, receipt_doc
            )
            proposal.stoplight = final_decision
            
            # Step 5: Create booking if GREEN
            booking = None
            if final_decision == StoplightDecision.GREEN:
                booking = await self.booking_service.create_booking_from_pipeline(
                    pipeline_run_id=str(pipeline_run_id),
                    company_id=company_id,
                    proposal=proposal,
                    receipt=receipt_doc,
                    intent=intent,
                    created_by=user_id
                )
            
            result = {
                "pipeline_run_id": pipeline_run_id,
                "status": "completed",
                "booking_id": booking.journal_entry.id if booking else None,
                "receipt": {
                    "total": str(receipt_doc.total),
                    "currency": receipt_doc.currency,
                    "vendor": receipt_doc.vendor,
                    "receipt_date": receipt_doc.date.isoformat(),
                    "confidence": receipt_doc.confidence
                },
                "intent": {
                    "name": intent.name,
                    "confidence": intent.confidence,
                    "slots": intent.slots
                },
                "proposal": {
                    "lines": [
                        {
                            "account": line.account,
                            "side": line.side,
                            "amount": str(line.amount),
                            "dimension_project": line.dimension_project,
                            "dimension_cost_center": line.dimension_cost_center,
                            "description": line.description
                        }
                        for line in proposal.lines
                    ],
                    "vat_code": proposal.vat_code,
                    "confidence": proposal.confidence,
                    "reason_codes": proposal.reason_codes,
                    "stoplight": proposal.stoplight.value,
                    "policy_id": proposal.policy_id
                },
                "journal_entry": {
                    "id": booking.journal_entry.id if booking else None,
                    "posting_date": booking.journal_entry.posting_date.isoformat() if booking else None,
                    "series": booking.journal_entry.series if booking else None,
                    "number": booking.journal_entry.number if booking else None,
                    "notes": booking.journal_entry.notes if booking else None,
                    "created_at": booking.journal_entry.created_at.isoformat() if booking else None
                } if booking else None
            }
            
            # Store the result for later retrieval
            self.pipeline_results[str(pipeline_run_id)] = result
            return result
            
        except Exception as e:
            error_result = {
                "pipeline_run_id": pipeline_run_id,
                "status": "failed",
                "booking_id": None,
                "error": str(e)
            }
            # Store the error result for later retrieval
            self.pipeline_results[str(pipeline_run_id)] = error_result
            return error_result
    
    async def get_pipeline_status(self, run_id: UUID) -> Optional[Dict[str, Any]]:
        """Get pipeline run status from stored results."""
        return self.pipeline_results.get(str(run_id))


