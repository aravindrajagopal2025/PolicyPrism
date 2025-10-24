"""Coverage criteria model representing conditions for medical service coverage."""
from sqlalchemy import String, Boolean, Float, Text, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, UUIDMixin, TimestampMixin


class CoverageCriteria(Base, UUIDMixin, TimestampMixin):
    """Specific conditions under which a medical service/procedure is covered."""
    
    __tablename__ = "coverage_criteria"
    
    # Relationships
    policy_section_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("policy_sections.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    
    # Procedure Information
    procedure_name: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        index=True
    )
    
    procedure_code: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        index=True,
        comment="CPT/HCPCS code if specified"
    )
    
    # Coverage Details
    covered_scenarios: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    
    required_documentation: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
    
    prior_authorization_required: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    
    age_restrictions: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
        comment="e.g., '18-65 years'"
    )
    
    frequency_limitations: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
        comment="e.g., 'once per year'"
    )
    
    # Extraction Quality
    extraction_confidence_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "extraction_confidence_score IS NULL OR (extraction_confidence_score >= 0.0 AND extraction_confidence_score <= 1.0)",
            name="check_coverage_confidence_score_range"
        ),
    )
    
    def __repr__(self) -> str:
        return f"<CoverageCriteria(id={self.id}, procedure={self.procedure_name})>"
