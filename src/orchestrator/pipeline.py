"""Pipeline orchestrator for document processing."""

from datetime import datetime
from uuid import UUID

from celery import Celery
from celery.signals import task_postrun, task_prerun

from src.domain.models import PipelineRun, StoplightDecision
from src.domain.services import (
    BookingService,
    DocumentService,
    ExtractionService,
    NLUService,
    ProposalService,
    ReasonService,
    StoplightService,
)


class PipelineOrchestrator:
    """Orchestrates the document processing pipeline."""

    def __init__(
        self,
        document_service: DocumentService,
        extraction_service: ExtractionService,
        nlu_service: NLUService,
        proposal_service: ProposalService,
        stoplight_service: StoplightService,
        booking_service: BookingService,
        reason_service: ReasonService,
        repository
    ):
        self.document_service = document_service
        self.extraction_service = extraction_service
        self.nlu_service = nlu_service
        self.proposal_service = proposal_service
        self.stoplight_service = stoplight_service
        self.booking_service = booking_service
        self.reason_service = reason_service
        self.repository = repository

    async def run_pipeline(
        self,
        document_id: UUID,
        company_id: UUID,
        user_text: str | None = None,
        user_id: UUID | None = None
    ) -> PipelineRun:
        """Run the complete document processing pipeline."""
        # Create pipeline run record
        pipeline_run = PipelineRun(
            document_id=document_id,
            company_id=company_id,
            status="running",
            started_at=datetime.utcnow()
        )

        try:
            # Step 1: Load document
            pipeline_run.current_step = "load_document"
            await self.repository.save_pipeline_run(pipeline_run)

            document = await self.document_service.get_document(document_id)
            if not document:
                raise ValueError(f"Document {document_id} not found")

            # Step 2: Extract receipt data
            pipeline_run.current_step = "extract_receipt"

            file_content = await self.document_service.download_document(document)
            receipt_doc = await self.extraction_service.extract_receipt(
                file_content,
                document.content_type
            )
            pipeline_run.receipt_doc = receipt_doc

            # Step 3: Detect intent
            pipeline_run.current_step = "detect_intent"

            intent = await self.nlu_service.detect_intent(receipt_doc, user_text)
            pipeline_run.intent = intent

            # Step 4: Create posting proposal
            pipeline_run.current_step = "create_proposal"

            proposal = await self.proposal_service.create_proposal(intent, receipt_doc)
            pipeline_run.proposal = proposal

            # Step 5: Make stoplight decision
            pipeline_run.current_step = "stoplight_decision"

            final_decision = self.stoplight_service.decide_stoplight(
                proposal, intent, receipt_doc
            )
            pipeline_run.proposal.stoplight = final_decision

            # Step 6: Create booking if GREEN
            if final_decision == StoplightDecision.GREEN:
                pipeline_run.current_step = "create_booking"

                journal_entry = await self.booking_service.create_journal_entry(
                    company_id=company_id,
                    proposal=proposal,
                    receipt=receipt_doc,
                    intent=intent,
                    created_by=user_id
                )
                pipeline_run.journal_entry_id = journal_entry.id

            # Complete pipeline
            pipeline_run.status = "completed"
            pipeline_run.current_step = "completed"
            pipeline_run.completed_at = datetime.utcnow()

        except Exception as e:
            pipeline_run.status = "failed"
            pipeline_run.error_message = str(e)
            pipeline_run.completed_at = datetime.utcnow()

        # Save final state
        try:
            await self.repository.save_pipeline_run(pipeline_run)
        except Exception as save_error:
            # If save fails due to duplicate key, try to update instead
            if "duplicate key" in str(save_error).lower():
                # Pipeline run already exists, just return it
                pass
            else:
                # Re-raise if it's a different error
                raise save_error

        return pipeline_run

    async def get_pipeline_status(self, run_id: UUID) -> PipelineRun | None:
        """Get pipeline run status."""
        return await self.repository.get_pipeline_run(run_id)

    async def list_pipeline_runs(self, company_id: UUID, limit: int = 50, offset: int = 0) -> list[PipelineRun]:
        """List pipeline runs for a company."""
        return await self.repository.list_pipeline_runs(company_id, limit, offset)


# Celery configuration
celery_app = Celery(
    "fireforget_accounting",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes
    task_soft_time_limit=240,  # 4 minutes
)


@celery_app.task(bind=True)
def run_pipeline_task(self, document_id: str, company_id: str, user_text: str = None, user_id: str = None):
    """Celery task for running pipeline."""
    # This would be implemented to create the orchestrator and run the pipeline
    # For now, it's a placeholder
    pass


@task_prerun.connect
def task_prerun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, **kwds):
    """Handle task prerun."""
    pass


@task_postrun.connect
def task_postrun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, retval=None, state=None, **kwds):
    """Handle task postrun."""
    pass
