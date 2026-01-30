"""Lead enrichment service combining multiple data sources."""

from functools import lru_cache
from typing import Optional, Dict, Any, List
from datetime import datetime

from app.services.apollo import get_apollo_client, ApolloClient
from app.services.hunter import get_hunter_client, HunterClient
from app.services.scoring import get_scoring_service, ScoringService
from app.utils.logging import get_logger

logger = get_logger(__name__)


class EnrichmentService:
    """Service for enriching lead data from multiple sources."""

    def __init__(
        self,
        apollo: ApolloClient,
        hunter: HunterClient,
        scorer: ScoringService,
    ):
        """Initialize enrichment service with dependencies."""
        self.apollo = apollo
        self.hunter = hunter
        self.scorer = scorer

    async def enrich_lead(
        self,
        domain: str,
        company_name: Optional[str] = None,
        sources: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Enrich lead data from multiple sources.

        Args:
            domain: Company domain
            company_name: Company name (optional)
            sources: List of sources to use (default: all available)

        Returns:
            Enriched lead data with source attribution
        """
        if sources is None:
            sources = ["apollo", "hunter"]

        result = {
            "domain": domain,
            "company_name": company_name,
            "enrichment_sources": [],
            "company_data": {},
            "contacts": [],
            "emails": [],
            "errors": [],
            "enriched_at": datetime.utcnow().isoformat(),
        }

        # Enrich from Apollo
        if "apollo" in sources and self.apollo.is_configured():
            try:
                apollo_data = await self._enrich_from_apollo(domain)
                if apollo_data and "error" not in apollo_data:
                    result["enrichment_sources"].append("apollo")
                    result["company_data"].update(apollo_data.get("company", {}))
                    result["contacts"].extend(apollo_data.get("contacts", []))
                else:
                    result["errors"].append({"source": "apollo", "error": apollo_data.get("error")})
            except Exception as e:
                logger.error("Apollo enrichment failed", domain=domain, error=str(e))
                result["errors"].append({"source": "apollo", "error": str(e)})

        # Enrich from Hunter
        if "hunter" in sources and self.hunter.is_configured():
            try:
                hunter_data = await self._enrich_from_hunter(domain)
                if hunter_data and "error" not in hunter_data:
                    result["enrichment_sources"].append("hunter")
                    result["emails"].extend(hunter_data.get("emails", []))
                    # Merge contacts
                    for email_data in hunter_data.get("emails", []):
                        result["contacts"].append({
                            "email": email_data.get("email"),
                            "first_name": email_data.get("first_name"),
                            "last_name": email_data.get("last_name"),
                            "job_title": email_data.get("position"),
                            "email_confidence": email_data.get("confidence", 0),
                            "source": "hunter",
                        })
                else:
                    result["errors"].append({"source": "hunter", "error": hunter_data.get("error")})
            except Exception as e:
                logger.error("Hunter enrichment failed", domain=domain, error=str(e))
                result["errors"].append({"source": "hunter", "error": str(e)})

        # Calculate score
        score_data = self.scorer.calculate_score({
            **result["company_data"],
            "company_domain": domain,
            "contacts": result["contacts"],
        })
        result["score"] = score_data

        # Deduplicate contacts
        result["contacts"] = self._deduplicate_contacts(result["contacts"])

        logger.info(
            "Lead enrichment completed",
            domain=domain,
            sources=result["enrichment_sources"],
            contacts_found=len(result["contacts"]),
            score=score_data.get("total_score"),
        )

        return result

    async def _enrich_from_apollo(self, domain: str) -> Dict[str, Any]:
        """Get enrichment data from Apollo."""
        result = {"company": {}, "contacts": []}

        # Get organization data
        org_data = await self.apollo.enrich_organization(domain)
        if org_data and "error" not in org_data:
            result["company"] = {
                "company_name": org_data.get("name"),
                "industry": org_data.get("industry"),
                "employee_count": org_data.get("estimated_num_employees"),
                "location": org_data.get("primary_address_locality"),
                "description": org_data.get("short_description"),
                "tech_stack": org_data.get("technologies", []),
                "linkedin_url": org_data.get("linkedin_url"),
                "funding_stage": org_data.get("latest_funding_stage"),
                "funding_amount": org_data.get("total_funding"),
            }

        # Get people/contacts
        people_data = await self.apollo.search_people(
            organization_domains=[domain],
            seniorities=["c_suite", "vp", "director"],
        )
        if people_data.get("people"):
            for person in people_data["people"][:5]:  # Limit to top 5
                result["contacts"].append({
                    "first_name": person.get("first_name"),
                    "last_name": person.get("last_name"),
                    "email": person.get("email"),
                    "job_title": person.get("title"),
                    "linkedin_url": person.get("linkedin_url"),
                    "email_confidence": 80 if person.get("email") else 0,
                    "source": "apollo",
                })

        return result

    async def _enrich_from_hunter(self, domain: str) -> Dict[str, Any]:
        """Get enrichment data from Hunter."""
        result = {"emails": []}

        # Domain search
        search_data = await self.hunter.domain_search(
            domain=domain,
            limit=10,
            seniority="senior",
        )

        if search_data.get("emails"):
            result["emails"] = search_data["emails"]
            result["email_pattern"] = search_data.get("pattern")

        return result

    def _deduplicate_contacts(self, contacts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate contacts based on email."""
        seen_emails = set()
        unique_contacts = []

        for contact in contacts:
            email = contact.get("email", "").lower()
            if email and email not in seen_emails:
                seen_emails.add(email)
                unique_contacts.append(contact)
            elif not email:
                # Keep contacts without email (might have LinkedIn)
                unique_contacts.append(contact)

        return unique_contacts

    async def verify_contact_email(self, email: str) -> Dict[str, Any]:
        """
        Verify a contact's email address.

        Args:
            email: Email to verify

        Returns:
            Verification result
        """
        if not self.hunter.is_configured():
            return {"error": "Hunter API not configured"}

        result = await self.hunter.verify_email(email)
        return {
            "email": email,
            "status": result.get("status"),
            "score": result.get("score", 0),
            "is_valid": result.get("status") == "valid",
            "is_deliverable": result.get("smtp_check", False),
            "is_disposable": result.get("disposable", False),
        }

    async def find_contact_email(
        self,
        domain: str,
        first_name: str,
        last_name: str,
    ) -> Dict[str, Any]:
        """
        Find email for a specific contact.

        Args:
            domain: Company domain
            first_name: Contact's first name
            last_name: Contact's last name

        Returns:
            Email finding result
        """
        if not self.hunter.is_configured():
            return {"error": "Hunter API not configured"}

        result = await self.hunter.find_email(
            domain=domain,
            first_name=first_name,
            last_name=last_name,
        )
        return result

    def get_available_sources(self) -> List[Dict[str, Any]]:
        """Get list of available enrichment sources."""
        return [
            {
                "name": "apollo",
                "description": "Apollo.io - Company and contact data",
                "configured": self.apollo.is_configured(),
            },
            {
                "name": "hunter",
                "description": "Hunter.io - Email discovery and verification",
                "configured": self.hunter.is_configured(),
            },
        ]


# Singleton instance
_enrichment_service: Optional[EnrichmentService] = None


@lru_cache
def get_enrichment_service() -> EnrichmentService:
    """Get enrichment service instance."""
    global _enrichment_service
    if _enrichment_service is None:
        _enrichment_service = EnrichmentService(
            apollo=get_apollo_client(),
            hunter=get_hunter_client(),
            scorer=get_scoring_service(),
        )
    return _enrichment_service
