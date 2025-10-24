"""Processing job model for document processing and scraping tasks."""
from datetime import datetime
from enum import Enum

from sqlalchemy import String, Integer, Text, DateTime, ForeignKey, Enum as SQLEnum, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, UUIDMixin, TimestampMixin


class JobType(str, Enum):
    """Processing job type enumeration."""
    INGESTION = "INGESTION"
    SCRAPING = "SCRAPING"


class JobStatus(str, Enum):
    """Processing job status enumeration."""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    RETRYING = "RETRYING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class ProcessingJob(Base, UUIDMixin, TimestampMixin):
    """Document processing or scraping task."""
    
    __tablename__ = "processing_jobs"
    
    # Job Type
    job_type: Mapped[JobType] = mapped_column(
        SQLEnum(JobType, name="job_type"),
        nullable=False,
        index=True
    )
    
    status: Mapped[JobStatus] = mapped_column(
        SQLEnum(JobStatus, name="job_status"),
        nullable=False,
        index=True
    )
    
    # Relationships
    payer_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("payers.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
        comment="For scraping jobs"
    )
    
    policy_document_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("policy_documents.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
        comment="For ingestion jobs"
    )
    
    # Timing
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    # Retry Logic
    retry_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    
    max_retries: Mapped[int] = mapped_column(
        Integer,
        default=3,
        nullable=False
    )
    
    # Error Information
    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
    
    error_stacktrace: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
    
    # Celery Integration
    celery_task_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True
    )
    
    # Creator
    created_by_user_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=True,
        comment="User who triggered job, null if scheduled"
    )
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "retry_count >= 0",
            name="check_retry_count_non_negative"
        ),
        CheckConstraint(
            "max_retries > 0",
            name="check_max_retries_positive"
        ),
        CheckConstraint(
            "retry_count <= max_retries",
            name="check_retry_count_within_max"
        ),
    )
    
    def __repr__(self) -> str:
        return f"<ProcessingJob(id={self.id}, type={self.job_type}, status={self.status})>"
