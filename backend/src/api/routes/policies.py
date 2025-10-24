"""Policies API routes for retrieving policy documents."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from typing import Optional

from ...database import get_db
from ...models.policy_document import PolicyDocument
from ...models.policy_section import PolicySection
from ...models.payer import Payer

router = APIRouter()


@router.get("")
async def list_policies(
    payer_id: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """
    List policy documents.
    
    Args:
        payer_id: Filter by payer UUID (optional)
        limit: Maximum number of results
        offset: Offset for pagination
        db: Database session
        
    Returns:
        List of policy documents
    """
    query = select(PolicyDocument).where(PolicyDocument.is_deleted == False)
    
    if payer_id:
        query = query.where(PolicyDocument.payer_id == UUID(payer_id))
    
    query = query.limit(limit).offset(offset)
    
    result = await db.execute(query)
    policies = result.scalars().all()
    
    # Get total count
    count_query = select(PolicyDocument).where(PolicyDocument.is_deleted == False)
    if payer_id:
        count_query = count_query.where(PolicyDocument.payer_id == UUID(payer_id))
    
    count_result = await db.execute(count_query)
    total = len(count_result.scalars().all())
    
    return {
        "total": total,
        "policies": [
            {
                "id": str(p.id),
                "payer_id": str(p.payer_id),
                "policy_name": p.policy_name,
                "policy_number": p.policy_number,
                "effective_date": p.effective_date.isoformat(),
                "expiration_date": p.expiration_date.isoformat() if p.expiration_date else None,
                "version": p.version,
                "document_type": p.document_type,
                "processing_status": p.processing_status,
                "extraction_confidence_score": p.extraction_confidence_score,
                "requires_manual_review": p.requires_manual_review,
                "created_at": p.created_at.isoformat()
            }
            for p in policies
        ]
    }


@router.get("/{policy_id}")
async def get_policy(
    policy_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get policy document details with sections.
    
    Args:
        policy_id: Policy document UUID
        db: Database session
        
    Returns:
        Policy document with sections
    """
    policy_uuid = UUID(policy_id)
    
    # Get policy
    result = await db.execute(
        select(PolicyDocument).where(
            PolicyDocument.id == policy_uuid,
            PolicyDocument.is_deleted == False
        )
    )
    policy = result.scalar_one_or_none()
    
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    
    # Get sections
    sections_result = await db.execute(
        select(PolicySection)
        .where(PolicySection.policy_document_id == policy_uuid)
        .order_by(PolicySection.order_index)
    )
    sections = sections_result.scalars().all()
    
    # Get payer info
    payer_result = await db.execute(select(Payer).where(Payer.id == policy.payer_id))
    payer = payer_result.scalar_one_or_none()
    
    return {
        "policy": {
            "id": str(policy.id),
            "payer_id": str(policy.payer_id),
            "payer_name": payer.name if payer else None,
            "policy_name": policy.policy_name,
            "policy_number": policy.policy_number,
            "effective_date": policy.effective_date.isoformat(),
            "expiration_date": policy.expiration_date.isoformat() if policy.expiration_date else None,
            "version": policy.version,
            "document_type": policy.document_type,
            "processing_status": policy.processing_status,
            "extraction_confidence_score": policy.extraction_confidence_score,
            "requires_manual_review": policy.requires_manual_review,
            "pdf_page_count": policy.pdf_page_count,
            "created_at": policy.created_at.isoformat()
        },
        "sections": [
            {
                "id": str(s.id),
                "section_type": s.section_type,
                "section_number": s.section_number,
                "title": s.title,
                "content_text": s.content_text[:500] + "..." if len(s.content_text) > 500 else s.content_text,
                "extraction_confidence_score": s.extraction_confidence_score,
                "order_index": s.order_index
            }
            for s in sections
        ]
    }


@router.get("/{policy_id}/sections/{section_id}")
async def get_policy_section(
    policy_id: str,
    section_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed policy section with extracted entities.
    
    Args:
        policy_id: Policy document UUID
        section_id: Policy section UUID
        db: Database session
        
    Returns:
        Section details with coverage criteria and exclusions
    """
    section_uuid = UUID(section_id)
    
    result = await db.execute(
        select(PolicySection).where(PolicySection.id == section_uuid)
    )
    section = result.scalar_one_or_none()
    
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
    
    if str(section.policy_document_id) != policy_id:
        raise HTTPException(status_code=404, detail="Section not found in this policy")
    
    return {
        "section": {
            "id": str(section.id),
            "section_type": section.section_type,
            "section_number": section.section_number,
            "title": section.title,
            "content_text": section.content_text,
            "content_structured": section.content_structured,
            "extraction_confidence_score": section.extraction_confidence_score,
            "page_numbers": section.page_numbers,
            "order_index": section.order_index
        },
        "coverage_criteria": [],  # TODO: Query from coverage_criteria table
        "exclusions": []  # TODO: Query from exclusions table
    }
