"""Lead-related Pydantic schemas."""

from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, EmailStr


class LeadBase(BaseModel):
    """Base schema for lead data."""

    company_name: str = Field(..., min_length=1, max_length=255)
    company_domain: Optional[str] = Field(None, max_length=255)
    industry: Optional[str] = Field(None, max_length=100)
    employee_count: Optional[int] = Field(None, ge=0)
    funding_stage: Optional[str] = Field(None, max_length=50)
    funding_amount: Optional[float] = Field(None, ge=0)
    location: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    tech_stack: Optional[List[str]] = Field(default_factory=list)
    linkedin_url: Optional[str] = Field(None, max_length=500)
    crunchbase_url: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = None
    tags: Optional[List[str]] = Field(default_factory=list)


class LeadCreate(LeadBase):
    """Schema for creating a new lead."""

    pass


class LeadUpdate(BaseModel):
    """Schema for updating an existing lead."""

    company_name: Optional[str] = Field(None, min_length=1, max_length=255)
    company_domain: Optional[str] = Field(None, max_length=255)
    industry: Optional[str] = Field(None, max_length=100)
    employee_count: Optional[int] = Field(None, ge=0)
    funding_stage: Optional[str] = Field(None, max_length=50)
    funding_amount: Optional[float] = Field(None, ge=0)
    location: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    tech_stack: Optional[List[str]] = None
    ai_adoption_score: Optional[float] = Field(None, ge=0, le=100)
    lead_score: Optional[float] = Field(None, ge=0, le=100)
    status: Optional[str] = Field(None, max_length=50)
    linkedin_url: Optional[str] = Field(None, max_length=500)
    crunchbase_url: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = None
    tags: Optional[List[str]] = None


class LeadResponse(LeadBase):
    """Schema for lead response."""

    id: UUID
    ai_adoption_score: float = 0.0
    lead_score: float = 0.0
    status: str = "new"
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class LeadListResponse(BaseModel):
    """Schema for paginated lead list response."""

    items: List[LeadResponse]
    total: int
    page: int
    page_size: int
    pages: int


class ContactBase(BaseModel):
    """Base schema for contact data."""

    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    email: Optional[str] = Field(None, max_length=255)
    job_title: Optional[str] = Field(None, max_length=255)
    department: Optional[str] = Field(None, max_length=100)
    linkedin_url: Optional[str] = Field(None, max_length=500)
    phone: Optional[str] = Field(None, max_length=50)
    is_decision_maker: Optional[str] = Field(None, pattern="^(yes|no|unknown)$")
    notes: Optional[str] = None


class ContactCreate(ContactBase):
    """Schema for creating a new contact."""

    lead_id: UUID


class ContactResponse(ContactBase):
    """Schema for contact response."""

    id: UUID
    lead_id: UUID
    email_confidence: float = 0.0
    email_verified: str = "unverified"
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
