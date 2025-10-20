"""Pipeline management API router."""

from datetime import datetime
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, HTTPException

from src.app.dependencies import get_pipeline_orchestrator
from src.app.dto import PipelineResponse, PipelineStartRequest
from src.orchestrator.pipeline import PipelineOrchestrator

logger = structlog.get_logger()
router = APIRouter()


@router.post("/pipelines/start", response_model=PipelineResponse)
async def start_pipeline(
    request: PipelineStartRequest,
    company_id: UUID,
    user_id: UUID = None,
    orchestrator: PipelineOrchestrator = Depends(get_pipeline_orchestrator)
):
    """Start document processing pipeline."""
    try:
        logger.info(
            "Pipeline start requested",
            document_id=str(request.document_id),
            company_id=str(company_id)
        )

        # Start the actual pipeline processing
        pipeline_run = await orchestrator.run_pipeline(
            document_id=request.document_id,
            company_id=company_id,
            user_id=user_id
        )

        return PipelineResponse(
            id=pipeline_run.id,
            document_id=pipeline_run.document_id,
            status=pipeline_run.status,
            current_step=pipeline_run.current_step,
            started_at=pipeline_run.started_at or datetime.utcnow(),
            completed_at=pipeline_run.completed_at,
            error_message=pipeline_run.error_message,
            booking_id=pipeline_run.journal_entry_id
        )

    except Exception as e:
        logger.error("Pipeline start failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pipelines/{run_id}", response_model=PipelineResponse)
async def get_pipeline_status(
    run_id: UUID,
    orchestrator: PipelineOrchestrator = Depends(get_pipeline_orchestrator)
):
    """Get pipeline run status."""
    try:
        # Get the actual pipeline result from the orchestrator
        pipeline_result = await orchestrator.get_pipeline_status(run_id)

        if pipeline_result:
            return PipelineResponse(
                id=run_id,
                document_id=pipeline_result.document_id,
                status=pipeline_result.status,
                current_step=pipeline_result.current_step,
                started_at=pipeline_result.started_at or datetime.utcnow(),
                completed_at=pipeline_result.completed_at,
                error_message=pipeline_result.error_message,
                booking_id=pipeline_result.journal_entry_id
            )
        else:
            # Pipeline not found
            raise HTTPException(status_code=404, detail="Pipeline run not found")

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get pipeline status", run_id=str(run_id), error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pipelines/{run_id}/debug", response_model=dict)
async def get_pipeline_debug(
    run_id: UUID,
    orchestrator: PipelineOrchestrator = Depends(get_pipeline_orchestrator)
):
    """Get detailed debug information for a pipeline run."""
    try:
        # Get the actual pipeline result from the orchestrator
        pipeline_result = await orchestrator.get_pipeline_status(run_id)

        if pipeline_result:
            return pipeline_result.dict()
        else:
            # Pipeline not found
            raise HTTPException(status_code=404, detail="Pipeline run not found")

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get pipeline debug info", run_id=str(run_id), error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pipelines", response_model=list[PipelineResponse])
async def list_pipelines(
    company_id: UUID,
    limit: int = 50,
    offset: int = 0,
    orchestrator: PipelineOrchestrator = Depends(get_pipeline_orchestrator)
):
    """List pipeline runs for a company."""
    try:
        # Get pipeline runs from the orchestrator
        pipeline_runs = await orchestrator.list_pipeline_runs(company_id, limit, offset)

        # Convert to response format
        return [
            PipelineResponse(
                id=run.id,
                document_id=run.document_id,
                status=run.status,
                current_step=run.current_step,
                started_at=run.started_at or datetime.utcnow(),
                completed_at=run.completed_at,
                error_message=run.error_message,
                booking_id=run.journal_entry_id
            )
            for run in pipeline_runs
        ]

    except Exception as e:
        logger.error("Failed to list pipelines", company_id=str(company_id), error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
