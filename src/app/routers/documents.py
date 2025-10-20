"""Document management API router."""

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
import structlog

from src.app.dto import DocumentUploadRequest, DocumentUploadResponse, DocumentResponse, ErrorResponse
from src.app.dependencies import get_document_service, get_pipeline_orchestrator
from src.domain.services import DocumentService
from src.orchestrator.pipeline import PipelineOrchestrator

logger = structlog.get_logger()
router = APIRouter()

# Remove global instances - use dependency injection instead


@router.post("/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    user_text: str = Form(None),
    company_id: UUID = Form(...),
    user_id: UUID = Form(None),
    document_service: DocumentService = Depends(get_document_service),
    pipeline_orchestrator: PipelineOrchestrator = Depends(get_pipeline_orchestrator)
):
    """Upload a document and start processing pipeline."""
    try:
        logger.info("Document upload started", filename=file.filename, company_id=str(company_id))
        
        # Read file content
        file_content = await file.read()
        
        # Determine content type with fallback
        content_type = file.content_type or "application/octet-stream"
        if not content_type and file.filename:
            # Try to infer from filename extension
            if file.filename.lower().endswith(('.txt', '.text')):
                content_type = "text/plain"
            elif file.filename.lower().endswith(('.jpg', '.jpeg')):
                content_type = "image/jpeg"
            elif file.filename.lower().endswith('.png'):
                content_type = "image/png"
            elif file.filename.lower().endswith('.pdf'):
                content_type = "application/pdf"
            else:
                content_type = "application/octet-stream"
        
        # Upload document
        document = await document_service.upload_document(
            company_id=company_id,
            filename=file.filename,
            content_type=content_type,
            file_content=file_content,
            uploaded_by=user_id
        )
        
        # Run the pipeline with database-backed orchestrator
        pipeline_result = await pipeline_orchestrator.run_pipeline(
            document_id=document.id,
            company_id=company_id,
            user_text=user_text,
            user_id=user_id
        )
        
        logger.info(
            "Document uploaded and pipeline completed",
            document_id=str(document.id),
            pipeline_run_id=str(pipeline_result.id),
            status=pipeline_result.status,
            booking_id=pipeline_result.journal_entry_id
        )
        
        return DocumentUploadResponse(
            document_id=document.id,
            pipeline_run_id=pipeline_result.id,
            booking_id=pipeline_result.journal_entry_id,
            status=pipeline_result.status
        )
        
    except Exception as e:
        logger.error("Document upload failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents/{document_id}/result", response_model=dict)
async def get_document_result(
    document_id: UUID,
    document_service: DocumentService = Depends(get_document_service)
):
    """Get document processing result."""
    try:
        # For now, return a placeholder result
        # In a real implementation, this would fetch from the database
        return {
            "document_id": str(document_id),
            "status": "processed",
            "message": "Document processing completed. Use the pipeline endpoint to get detailed results."
        }
        
    except Exception as e:
        logger.error("Failed to get document result", document_id=str(document_id), error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: UUID,
    document_service: DocumentService = Depends(get_document_service)
):
    """Get document by ID."""
    try:
        document = await document_service.get_document(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return DocumentResponse(
            id=document.id,
            filename=document.filename,
            content_type=document.content_type,
            size=document.size,
            uploaded_at=document.uploaded_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get document", document_id=str(document_id), error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents", response_model=List[DocumentResponse])
async def list_documents(
    company_id: UUID,
    limit: int = 50,
    offset: int = 0,
    document_service: DocumentService = Depends(get_document_service)
):
    """List documents for a company."""
    try:
        documents = await document_service.list_documents(company_id, limit, offset)
        
        return [
            DocumentResponse(
                id=document.id,
                filename=document.filename,
                content_type=document.content_type,
                size=document.size,
                uploaded_at=document.uploaded_at
            )
            for document in documents
        ]
        
    except Exception as e:
        logger.error("Failed to list documents", company_id=str(company_id), error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents/{document_id}/download")
async def download_document(
    document_id: UUID,
    document_service: DocumentService = Depends(get_document_service)
):
    """Download document content."""
    try:
        document = await document_service.get_document(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        file_content = await document_service.download_document(document)
        
        from fastapi.responses import Response
        return Response(
            content=file_content,
            media_type=document.content_type,
            headers={"Content-Disposition": f"attachment; filename={document.filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to download document", document_id=str(document_id), error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
