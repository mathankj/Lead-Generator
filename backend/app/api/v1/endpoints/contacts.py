"""Contact CRUD API endpoints."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.contact import Contact
from app.models.lead import Lead
from app.schemas.lead import ContactCreate, ContactResponse
from app.services.enrichment import get_enrichment_service, EnrichmentService
from app.utils.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("")
async def list_contacts(
    lead_id: Optional[UUID] = None,
    verified_only: bool = False,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    List contacts with optional filtering.

    Args:
        lead_id: Filter by lead ID
        verified_only: Only show verified emails
        page: Page number
        page_size: Results per page
    """
    query = db.query(Contact)

    if lead_id:
        query = query.filter(Contact.lead_id == lead_id)
    if verified_only:
        query = query.filter(Contact.email_verified == "valid")

    total = query.count()
    offset = (page - 1) * page_size
    contacts = query.offset(offset).limit(page_size).all()

    return {
        "items": [ContactResponse.model_validate(c) for c in contacts],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.post("", response_model=ContactResponse, status_code=201)
async def create_contact(
    contact_in: ContactCreate,
    db: Session = Depends(get_db),
):
    """Create a new contact."""
    # Verify lead exists
    lead = db.query(Lead).filter(Lead.id == contact_in.lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    # Check for duplicate email
    if contact_in.email:
        existing = db.query(Contact).filter(
            Contact.lead_id == contact_in.lead_id,
            Contact.email == contact_in.email,
        ).first()
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Contact with this email already exists for this lead",
            )

    contact = Contact(**contact_in.model_dump())
    db.add(contact)
    db.commit()
    db.refresh(contact)

    logger.info(
        "Contact created",
        contact_id=str(contact.id),
        lead_id=str(contact.lead_id),
    )
    return ContactResponse.model_validate(contact)


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id: UUID,
    db: Session = Depends(get_db),
):
    """Get contact by ID."""
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return ContactResponse.model_validate(contact)


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: UUID,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    email: Optional[str] = None,
    job_title: Optional[str] = None,
    phone: Optional[str] = None,
    linkedin_url: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Update contact by ID."""
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    if first_name is not None:
        contact.first_name = first_name
    if last_name is not None:
        contact.last_name = last_name
    if email is not None:
        contact.email = email
        contact.email_verified = "unverified"  # Reset verification
    if job_title is not None:
        contact.job_title = job_title
    if phone is not None:
        contact.phone = phone
    if linkedin_url is not None:
        contact.linkedin_url = linkedin_url

    db.commit()
    db.refresh(contact)

    logger.info("Contact updated", contact_id=str(contact_id))
    return ContactResponse.model_validate(contact)


@router.delete("/{contact_id}", status_code=204)
async def delete_contact(
    contact_id: UUID,
    db: Session = Depends(get_db),
):
    """Delete contact by ID."""
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    db.delete(contact)
    db.commit()

    logger.info("Contact deleted", contact_id=str(contact_id))
    return None


@router.post("/{contact_id}/verify-email")
async def verify_contact_email(
    contact_id: UUID,
    db: Session = Depends(get_db),
    enrichment: EnrichmentService = Depends(get_enrichment_service),
):
    """Verify contact's email address using Hunter.io."""
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    if not contact.email:
        raise HTTPException(status_code=400, detail="Contact has no email to verify")

    # Verify email
    result = await enrichment.verify_contact_email(contact.email)

    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    # Update contact
    contact.email_verified = "valid" if result.get("is_valid") else "invalid"
    contact.email_confidence = result.get("score", 0)

    db.commit()
    db.refresh(contact)

    logger.info(
        "Email verified",
        contact_id=str(contact_id),
        email=contact.email,
        status=contact.email_verified,
    )

    return {
        "contact_id": str(contact_id),
        "email": contact.email,
        "verification": result,
    }


@router.post("/{contact_id}/find-email")
async def find_contact_email(
    contact_id: UUID,
    db: Session = Depends(get_db),
    enrichment: EnrichmentService = Depends(get_enrichment_service),
):
    """Find contact's email using Hunter.io."""
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    if not contact.first_name or not contact.last_name:
        raise HTTPException(
            status_code=400,
            detail="Contact must have first_name and last_name to find email",
        )

    # Get lead for domain
    lead = db.query(Lead).filter(Lead.id == contact.lead_id).first()
    if not lead or not lead.company_domain:
        raise HTTPException(
            status_code=400,
            detail="Lead must have company_domain to find email",
        )

    # Find email
    result = await enrichment.find_contact_email(
        domain=lead.company_domain,
        first_name=contact.first_name,
        last_name=contact.last_name,
    )

    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    # Update contact if email found
    if result.get("email"):
        contact.email = result["email"]
        contact.email_confidence = result.get("confidence", 0)
        contact.email_source = "hunter"

        db.commit()
        db.refresh(contact)

    logger.info(
        "Email found",
        contact_id=str(contact_id),
        email=result.get("email"),
        confidence=result.get("confidence"),
    )

    return {
        "contact_id": str(contact_id),
        "result": result,
    }
