"""Exclusion model representing conditions or scenarios explicitly not covered."""
from sqlalchemy import String, Float, Text, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, UUIDMixin, TimestampMixin


class Exclusion(Base, UUIDMixin, TimestampMixin):
    """Conditions or scenarios explicitly not covered by policy."""
    
    __tablename__ = "exclusions"
    
    # Relationships
    policy_section_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("policy_sections.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    
    # Exclusion Information
    excluded_procedure: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )
    
    exclusion_rationale: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
    
    exceptions_to_exclusion: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Scenarios where exclusion doesn't apply"
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
            name="check_exclusion_confidence_score_range"
        ),
    )
    
    def __repr__(self) -> str:
        return f"<Exclusion(id={self.id}, excluded={self.excluded_procedure[:50]})>"
