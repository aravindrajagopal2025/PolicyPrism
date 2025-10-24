"""Policy section model representing logical sections within policy documents."""
from enum import Enum

from sqlalchemy import String, Integer, Float, Text, ForeignKey, Enum as SQLEnum, ARRAY, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, UUIDMixin, TimestampMixin


class SectionType(str, Enum):
    """Policy section type enumeration."""
    COVERAGE_CRITERIA = "COVERAGE_CRITERIA"
    EXCLUSIONS = "EXCLUSIONS"
    REQUIREMENTS = "REQUIREMENTS"
    DEFINITIONS = "DEFINITIONS"
    PRIOR_AUTHORIZATION = "PRIOR_AUTHORIZATION"
    LIMITATIONS = "LIMITATIONS"
    APPEALS_PROCESS = "APPEALS_PROCESS"
    OTHER = "OTHER"


class PolicySection(Base, UUIDMixin, TimestampMixin):
    """Logical section within a policy document."""
    
    __tablename__ = "policy_sections"
    
    # Relationships
    policy_document_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("policy_documents.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    
    # Section Information
    section_type: Mapped[SectionType] = mapped_column(
        SQLEnum(SectionType, name="section_type"),
        nullable=False,
        index=True
    )
    
    section_number: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )
    
    title: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )
    
    # Content
    content_text: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    
    content_structured: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="Structured data extracted from section"
    )
    
    # Extraction Quality
    extraction_confidence_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )
    
    # Location in Document
    page_numbers: Mapped[list[int] | None] = mapped_column(
        ARRAY(Integer),
        nullable=True
    )
    
    order_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "extraction_confidence_score IS NULL OR (extraction_confidence_score >= 0.0 AND extraction_confidence_score <= 1.0)",
            name="check_section_confidence_score_range"
        ),
        CheckConstraint(
            "order_index >= 0",
            name="check_order_index_non_negative"
        ),
    )
    
    def __repr__(self) -> str:
        return f"<PolicySection(id={self.id}, type={self.section_type}, title={self.title[:50]})>"
