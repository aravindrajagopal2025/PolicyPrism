"""Audit log model for tracking user actions."""
from datetime import datetime
from enum import Enum

from sqlalchemy import String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, UUIDMixin


class ActionType(str, Enum):
    """User action type enumeration."""
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    UPLOAD_DOCUMENT = "UPLOAD_DOCUMENT"
    DELETE_DOCUMENT = "DELETE_DOCUMENT"
    UPDATE_SCRAPING_CONFIG = "UPDATE_SCRAPING_CONFIG"
    MANUAL_REVIEW_COMPLETE = "MANUAL_REVIEW_COMPLETE"
    SEARCH_QUERY = "SEARCH_QUERY"
    POLICY_COMPARISON = "POLICY_COMPARISON"
    USER_CREATED = "USER_CREATED"
    USER_ROLE_CHANGED = "USER_ROLE_CHANGED"


class AuditLog(Base, UUIDMixin):
    """Audit log for tracking all user actions."""
    
    __tablename__ = "audit_logs"
    
    # User
    user_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
        comment="User who performed action, null if system"
    )
    
    # Action
    action_type: Mapped[ActionType] = mapped_column(
        SQLEnum(ActionType, name="action_type"),
        nullable=False
    )
    
    # Resource
    resource_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="e.g., 'PolicyDocument', 'User'"
    )
    
    resource_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True
    )
    
    # Details
    action_details: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="Additional context about the action"
    )
    
    # Request Context
    ip_address: Mapped[str | None] = mapped_column(
        String(45),
        nullable=True,
        comment="IPv4 or IPv6 address"
    )
    
    user_agent: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )
    
    # Timestamp
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
        index=True
    )
    
    # Composite Index for Resource Audit Trail
    __table_args__ = (
        {"comment": "Audit log for compliance and security"},
    )
    
    def __repr__(self) -> str:
        return f"<AuditLog(id={self.id}, action={self.action_type}, resource={self.resource_type})>"
