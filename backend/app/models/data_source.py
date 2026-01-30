"""DataSource model for tracking where lead data came from."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.lead import Lead


class DataSource(Base):
    """
    DataSource model for tracking lead data provenance.

    Attributes:
        id: Unique identifier (UUID)
        lead_id: Foreign key to the lead/company
        source_type: Type of source (linkedin, apollo, hunter, crunchbase, etc.)
        source_url: Original URL where data was found
        raw_data: Raw JSON data from the source
        confidence_score: How confident we are in this data
        fetched_at: When the data was fetched
        created_at: Record creation timestamp
    """

    __tablename__ = "data_sources"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lead_id = Column(
        UUID(as_uuid=True),
        ForeignKey("leads.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    source_type = Column(String(50), nullable=False, index=True)
    source_url = Column(String(500))
    raw_data = Column(JSONB, default=dict)
    confidence_score = Column(String(20), default="medium")  # low, medium, high
    fetched_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    lead: "Lead" = relationship("Lead", back_populates="data_sources")

    # Valid source types
    VALID_SOURCES = [
        "linkedin",
        "apollo",
        "hunter",
        "crunchbase",
        "builtwith",
        "clearbit",
        "manual",
        "website",
        "other",
    ]

    def __repr__(self) -> str:
        return f"<DataSource(id={self.id}, type={self.source_type}, lead_id={self.lead_id})>"

    @property
    def is_fresh(self) -> bool:
        """Check if data was fetched within last 30 days."""
        if not self.fetched_at:
            return False
        age = datetime.utcnow() - self.fetched_at
        return age.days < 30
