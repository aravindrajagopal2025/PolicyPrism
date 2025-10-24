"""User model for authentication and authorization."""
from datetime import datetime
from enum import Enum

from sqlalchemy import String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, UUIDMixin, TimestampMixin


class UserRole(str, Enum):
    """User role enumeration."""
    ANALYST = "ANALYST"
    ADMINISTRATOR = "ADMINISTRATOR"


class User(Base, UUIDMixin, TimestampMixin):
    """User model with role-based access control."""
    
    __tablename__ = "users"
    
    # Authentication
    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )
    
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )
    
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    
    # Authorization
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole, name="user_role"),
        nullable=False,
        index=True
    )
    
    # Profile
    first_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )
    
    last_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )
    
    # Status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )
    
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, username={self.username}, role={self.role})>"
