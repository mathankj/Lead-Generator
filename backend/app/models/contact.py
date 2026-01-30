"""Contact model for storing decision maker information."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.lead import Lead


class Contact(Base):
    """
    Contact model representing a decision maker at a lead company.

    Attributes:
        id: Unique identifier (UUID)
        lead_id: Foreign key to the lead/company
        first_name: Contact's first name
        last_name: Contact's last name
        email: Email address
        email_confidence: Confidence score 0-100 for email validity
        job_title: Job title/position
        department: Department (Engineering, Sales, etc.)
        linkedin_url: LinkedIn profile URL
        phone: Phone number
        is_decision_maker: Whether this contact is a decision maker
        last_contacted_at: When we last reached out
        created_at: Record creation timestamp
    """

    __tablename__ = "contacts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lead_id = Column(
        UUID(as_uuid=True),
        ForeignKey("leads.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    first_name = Column(String(100))
    last_name = Column(String(100))
    email = Column(String(255), index=True)
    email_confidence = Column(Float, default=0.0)
    email_verified = Column(String(20), default="unverified")  # unverified, valid, invalid
    job_title = Column(String(255))
    department = Column(String(100))
    linkedin_url = Column(String(500))
    phone = Column(String(50))
    is_decision_maker = Column(String(10), default="unknown")  # yes, no, unknown
    notes = Column(Text)
    last_contacted_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    lead: "Lead" = relationship("Lead", back_populates="contacts")

    def __repr__(self) -> str:
        return f"<Contact(id={self.id}, name={self.full_name}, email={self.email})>"

    @property
    def full_name(self) -> str:
        """Get contact's full name."""
        parts = [self.first_name, self.last_name]
        return " ".join(p for p in parts if p) or "Unknown"

    @property
    def is_email_valid(self) -> bool:
        """Check if email is verified and valid."""
        return self.email_verified == "valid" and self.email_confidence >= 80
