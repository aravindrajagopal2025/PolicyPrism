"""Ingestion API routes for policy document upload."""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID, uuid4
from datetime import datetime

from ...database import get_db
from ...models.policy_document import PolicyDocument, ProcessingStatus, DocumentType
from ...models.processing_job import ProcessingJob, JobType, JobStatus
from ...models.payer import Payer
from ...services.ingestion.uploader import PDFUploader
# from ...services.ingestion.pdf_extractor import PDFExtractor  # Temporarily disabled - pymupdf not installed
from ...utils.azure_storage import storage_service

router = APIRouter()

# Initialize services
pdf_uploader = PDFUploader(storage_service)
# pdf_extractor = PDFExtractor()  # Temporarily disabled


@router.post("/upload")
async def upload_policy(
    file: UploadFile = File(...),
    payer_id: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload a policy document for processing.
    
    Args:
        file: PDF file upload
        payer_id: UUID of the payer
        db: Database session
        
    Returns:
        Upload confirmation with job ID
    """
    # Validate payer exists
    payer_uuid = UUID(payer_id)
    result = await db.execute(select(Payer).where(Payer.id == payer_uuid))
    payer = result.scalar_one_or_none()
    
    if not payer:
        raise HTTPException(status_code=404, detail="Payer not found")
    
    # Validate PDF
    validation = pdf_uploader.validate_pdf(file.file)
    if not validation["is_valid"]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid PDF: {', '.join(validation['errors'])}"
        )
    
    # Reset file pointer
    file.file.seek(0)
    
    # Upload PDF
    try:
        upload_result = pdf_uploader.upload_pdf(
            file.file,
            file.filename,
            str(payer_id),
            user_id=None  # TODO: Get from auth
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
    
    # Extract basic PDF info (temporarily disabled - pymupdf not installed)
    # file.file.seek(0)
    # temp_path = f"/tmp/{uuid4()}.pdf"
    # with open(temp_path, 'wb') as f:
    #     f.write(file.file.read())
    
    # try:
    #     pdf_info = pdf_extractor.extract_text(temp_path)
    # finally:
    #     import os
    #     if os.path.exists(temp_path):
    #         os.remove(temp_path)
    
    # Placeholder for now
    pdf_info = {"page_count": 1}
    
    # Create policy document record
    policy_doc = PolicyDocument(
        payer_id=payer_uuid,
        policy_name=file.filename,  # Will be updated after extraction
        effective_date=datetime.utcnow().date(),  # Placeholder
        version=1,
        document_type=DocumentType.MEDICAL,  # Default
        pdf_storage_path=upload_result["storage_path"],
        pdf_file_size_bytes=upload_result["file_size_bytes"],
        pdf_page_count=pdf_info["page_count"],
        processing_status=ProcessingStatus.QUEUED,
        requires_manual_review=False,
        created_by_user_id=None  # TODO: Get from auth
    )
    
    db.add(policy_doc)
    await db.flush()  # Get the ID
    
    # Create processing job
    job = ProcessingJob(
        job_type=JobType.INGESTION,
        status=JobStatus.PENDING,
        policy_document_id=policy_doc.id,
        created_by_user_id=None  # TODO: Get from auth
    )
    
    db.add(job)
    await db.commit()
    
    return {
        "policy_document_id": str(policy_doc.id),
        "processing_job_id": str(job.id),
        "status": "QUEUED",
        "message": "Document uploaded successfully and queued for processing"
    }


@router.get("/jobs/{job_id}")
async def get_job_status(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get processing job status.
    
    Args:
        job_id: Processing job UUID
        db: Database session
        
    Returns:
        Job status information
    """
    job_uuid = UUID(job_id)
    result = await db.execute(select(ProcessingJob).where(ProcessingJob.id == job_uuid))
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {
        "id": str(job.id),
        "job_type": job.job_type,
        "status": job.status,
        "started_at": job.started_at.isoformat() if job.started_at else None,
        "completed_at": job.completed_at.isoformat() if job.completed_at else None,
        "retry_count": job.retry_count,
        "error_message": job.error_message,
        "created_at": job.created_at.isoformat()
    }
