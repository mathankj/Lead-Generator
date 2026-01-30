"""Lead model for storing company/lead information."""

import uuid
from datetime import datetime
from typing import List, TYPE_CHECKING

from sqlalchemy import Column, String, Integer, Float, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.contact import Contact
    from app.models.data_source import DataSource


class Lead(Base):
    """
    Lead model representing a potential customer company.

    Attributes:
        id: Unique identifier (UUID)
        company_name: Name of the company
        company_domain: Company website domain
        industry: Industry category
        employee_count: Number of employees
        funding_stage: Funding round (Seed, Series A, etc.)
        location: Company headquarters location
        description: Company description
        tech_stack: Known technologies used (JSON array)
        ai_adoption_score: Score 0-100 indicating AI adoption level
        lead_score: Overall lead quality score 0-100
        status: Lead status (new, contacted, qualified, etc.)
        created_at: Record creation timestamp
        updated_at: Last update timestamp
    """

    __tablename__ = "leads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_name = Column(String(255), nullable=False, index=True)
    company_domain = Column(String(255), unique=True, index=True)
    industry = Column(String(100), index=True)
    employee_count = Column(Integer)
    funding_stage = Column(String(50))
    funding_amount = Column(Float)  # In millions USD
    location = Column(String(255))
    description = Column(Text)
    tech_stack = Column(JSONB, default=list)
    ai_adoption_score = Column(Float, default=0.0)
    lead_score = Column(Float, default=0.0)
    status = Column(String(50), default="new", index=True)
    linkedin_url = Column(String(500))
    crunchbase_url = Column(String(500))
    notes = Column(Text)
    tags = Column(JSONB, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    contacts: List["Contact"] = relationship(
        "Contact", back_populates="lead", cascade="all, delete-orphan"
    )
    data_sources: List["DataSource"] = relationship(
        "DataSource", back_populates="lead", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Lead(id={self.id}, company={self.company_name}, score={self.lead_score})>"

    @property
    def is_hot_lead(self) -> bool:
        """Check if lead is hot (score >= 85)."""
        return self.lead_score >= 85

    @property
    def is_qualified(self) -> bool:
        """Check if lead is qualified."""
        return self.status == "qualified"
