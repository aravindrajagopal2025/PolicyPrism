"""Payer model representing healthcare payer organizations."""
from datetime import datetime

from sqlalchemy import String, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, UUIDMixin, TimestampMixin


class Payer(Base, UUIDMixin, TimestampMixin):
    """Healthcare payer organization model."""
    
    __tablename__ = "payers"
    
    # Basic Information
    name: Mapped[str] = mapped_column(
        String(200),
        unique=True,
        nullable=False,
        index=True
    )
    
    website_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )
    
    # Scraping Configuration
    scraping_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True
    )
    
    scraping_config: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="JSON configuration for web scraping: base_url, selectors, auth, schedule"
    )
    
    last_scrape_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    next_scrape_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True
    )
    
    # Status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )
    
    def __repr__(self) -> str:
        return f"<Payer(id={self.id}, name={self.name}, scraping_enabled={self.scraping_enabled})>"
