"""Policy document model representing complete payer policy documents."""
from datetime import datetime, date
from enum import Enum

from sqlalchemy import String, Integer, Float, Boolean, DateTime, Date, ForeignKey, Enum as SQLEnum, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, UUIDMixin, TimestampMixin, SoftDeleteMixin


class DocumentType(str, Enum):
    """Policy document type enumeration."""
    MEDICAL = "MEDICAL"
    PHARMACY = "PHARMACY"
    DENTAL = "DENTAL"
    VISION = "VISION"
    OTHER = "OTHER"


class ProcessingStatus(str, Enum):
    """Document processing status enumeration."""
    QUEUED = "QUEUED"
    EXTRACTING_TEXT = "EXTRACTING_TEXT"
    STRUCTURING_DATA = "STRUCTURING_DATA"
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"
    PENDING_REVIEW = "PENDING_REVIEW"


class PolicyDocument(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """Complete payer policy document model."""
    
    __tablename__ = "policy_documents"
    
    # Relationships
    payer_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("payers.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    
    previous_version_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("policy_documents.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Policy Information
    policy_name: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )
    
    policy_number: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )
    
    effective_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True
    )
    
    expiration_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True
    )
    
    version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1
    )
    
    document_type: Mapped[DocumentType] = mapped_column(
        SQLEnum(DocumentType, name="document_type"),
        nullable=False
    )
    
    # Source Information
    source_url: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True
    )
    
    # PDF Storage
    pdf_storage_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )
    
    pdf_file_size_bytes: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    
    pdf_page_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    
    # Processing Status
    processing_status: Mapped[ProcessingStatus] = mapped_column(
        SQLEnum(ProcessingStatus, name="processing_status"),
        nullable=False,
        index=True
    )
    
    processing_started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    processing_completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    # Extraction Quality
    extraction_confidence_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )
    
    requires_manual_review: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True
    )
    
    reviewed_by_user_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=True
    )
    
    reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    # Creator
    created_by_user_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=True
    )
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "version >= 1",
            name="check_version_positive"
        ),
        CheckConstraint(
            "extraction_confidence_score IS NULL OR (extraction_confidence_score >= 0.0 AND extraction_confidence_score <= 1.0)",
            name="check_confidence_score_range"
        ),
        CheckConstraint(
            "expiration_date IS NULL OR expiration_date >= effective_date",
            name="check_expiration_after_effective"
        ),
    )
    
    def __repr__(self) -> str:
        return f"<PolicyDocument(id={self.id}, policy_name={self.policy_name}, status={self.processing_status})>"
