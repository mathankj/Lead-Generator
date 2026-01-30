"""Lead CRUD API endpoints."""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.lead import Lead
from app.schemas.lead import LeadCreate, LeadUpdate, LeadResponse, LeadListResponse
from app.services.enrichment import get_enrichment_service, EnrichmentService
from app.services.scoring import get_scoring_service, ScoringService
from app.utils.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("", response_model=LeadListResponse)
async def list_leads(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    min_score: Optional[float] = Query(None, ge=0, le=100),
    industry: Optional[str] = None,
    location: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    List leads with pagination and filtering.

    Args:
        page: Page number
        page_size: Results per page
        status: Filter by status (new, contacted, qualified, etc.)
        min_score: Minimum lead score
        industry: Filter by industry
        location: Filter by location
        search: Search in company name
    """
    query = db.query(Lead)

    # Apply filters
    if status:
        query = query.filter(Lead.status == status)
    if min_score is not None:
        query = query.filter(Lead.lead_score >= min_score)
    if industry:
        query = query.filter(Lead.industry.ilike(f"%{industry}%"))
    if location:
        query = query.filter(Lead.location.ilike(f"%{location}%"))
    if search:
        query = query.filter(Lead.company_name.ilike(f"%{search}%"))

    # Get total count
    total = query.count()

    # Paginate
    offset = (page - 1) * page_size
    leads = query.order_by(Lead.lead_score.desc()).offset(offset).limit(page_size).all()

    return LeadListResponse(
        items=[LeadResponse.model_validate(lead) for lead in leads],
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size,
    )


@router.post("", response_model=LeadResponse, status_code=201)
async def create_lead(
    lead_in: LeadCreate,
    db: Session = Depends(get_db),
    scorer: ScoringService = Depends(get_scoring_service),
):
    """Create a new lead."""
    # Check for duplicate domain
    if lead_in.company_domain:
        existing = db.query(Lead).filter(Lead.company_domain == lead_in.company_domain).first()
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Lead with domain {lead_in.company_domain} already exists",
            )

    # Create lead
    lead = Lead(**lead_in.model_dump())

    # Calculate initial score
    score_data = scorer.calculate_score(lead_in.model_dump())
    lead.lead_score = score_data["total_score"]
    lead.ai_adoption_score = score_data["breakdown"].get("ai_adoption", 0)

    db.add(lead)
    db.commit()
    db.refresh(lead)

    logger.info("Lead created", lead_id=str(lead.id), company=lead.company_name)
    return LeadResponse.model_validate(lead)


@router.get("/{lead_id}", response_model=LeadResponse)
async def get_lead(
    lead_id: UUID,
    db: Session = Depends(get_db),
):
    """Get lead by ID."""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return LeadResponse.model_validate(lead)


@router.put("/{lead_id}", response_model=LeadResponse)
async def update_lead(
    lead_id: UUID,
    lead_in: LeadUpdate,
    db: Session = Depends(get_db),
):
    """Update lead by ID."""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    # Update fields
    update_data = lead_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(lead, field, value)

    db.commit()
    db.refresh(lead)

    logger.info("Lead updated", lead_id=str(lead_id))
    return LeadResponse.model_validate(lead)


@router.delete("/{lead_id}", status_code=204)
async def delete_lead(
    lead_id: UUID,
    db: Session = Depends(get_db),
):
    """Delete lead by ID."""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    db.delete(lead)
    db.commit()

    logger.info("Lead deleted", lead_id=str(lead_id))
    return None


@router.post("/{lead_id}/enrich")
async def enrich_lead(
    lead_id: UUID,
    sources: Optional[List[str]] = Query(None),
    db: Session = Depends(get_db),
    enrichment: EnrichmentService = Depends(get_enrichment_service),
):
    """
    Enrich lead with data from external sources.

    Args:
        lead_id: Lead ID
        sources: List of sources to use (apollo, hunter)
    """
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    if not lead.company_domain:
        raise HTTPException(status_code=400, detail="Lead must have company_domain for enrichment")

    # Enrich
    result = await enrichment.enrich_lead(
        domain=lead.company_domain,
        company_name=lead.company_name,
        sources=sources,
    )

    # Update lead with enriched data
    company_data = result.get("company_data", {})
    if company_data:
        for field in ["industry", "employee_count", "location", "description", "funding_stage"]:
            if company_data.get(field) and not getattr(lead, field):
                setattr(lead, field, company_data[field])

        if company_data.get("tech_stack"):
            lead.tech_stack = company_data["tech_stack"]

    # Update scores
    if result.get("score"):
        lead.lead_score = result["score"].get("total_score", lead.lead_score)
        lead.ai_adoption_score = result["score"]["breakdown"].get("ai_adoption", lead.ai_adoption_score)

    db.commit()
    db.refresh(lead)

    logger.info(
        "Lead enriched",
        lead_id=str(lead_id),
        sources=result.get("enrichment_sources"),
        new_score=lead.lead_score,
    )

    return {
        "lead_id": str(lead_id),
        "enrichment_sources": result.get("enrichment_sources"),
        "contacts_found": len(result.get("contacts", [])),
        "new_score": lead.lead_score,
        "score_breakdown": result.get("score", {}).get("breakdown"),
        "errors": result.get("errors"),
    }


@router.post("/{lead_id}/score")
async def score_lead(
    lead_id: UUID,
    db: Session = Depends(get_db),
    scorer: ScoringService = Depends(get_scoring_service),
):
    """Recalculate lead score."""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    # Get contacts for scoring
    contacts = [
        {
            "email": c.email,
            "email_confidence": c.email_confidence,
            "job_title": c.job_title,
            "linkedin_url": c.linkedin_url,
        }
        for c in lead.contacts
    ]

    # Calculate score
    lead_data = {
        "company_name": lead.company_name,
        "company_domain": lead.company_domain,
        "industry": lead.industry,
        "employee_count": lead.employee_count,
        "funding_stage": lead.funding_stage,
        "funding_amount": lead.funding_amount,
        "location": lead.location,
        "description": lead.description,
        "tech_stack": lead.tech_stack or [],
        "linkedin_url": lead.linkedin_url,
        "contacts": contacts,
    }

    score_result = scorer.calculate_score(lead_data)

    # Update lead
    lead.lead_score = score_result["total_score"]
    lead.ai_adoption_score = score_result["breakdown"].get("ai_adoption", 0)

    db.commit()
    db.refresh(lead)

    logger.info("Lead scored", lead_id=str(lead_id), score=lead.lead_score)

    return {
        "lead_id": str(lead_id),
        "score": score_result,
    }
