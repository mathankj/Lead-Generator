"""Apollo.io API client for company and contact discovery."""

from functools import lru_cache
from typing import Optional, List, Dict, Any

import httpx

from app.config import settings
from app.utils.logging import get_logger

logger = get_logger(__name__)


class ApolloClient:
    """Client for Apollo.io API integration."""

    BASE_URL = "https://api.apollo.io/api/v1"

    def __init__(self, api_key: str):
        """Initialize Apollo client with API key."""
        if not api_key:
            raise ValueError("API key is required")
        self.api_key = api_key
        self.base_url = self.BASE_URL
        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers={
                "Content-Type": "application/json",
                "Cache-Control": "no-cache",
            },
            timeout=30.0,
        )

    async def _make_request(
        self, endpoint: str, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Make API request to Apollo."""
        payload["api_key"] = self.api_key
        response = await self.client.post(endpoint, json=payload)
        response.raise_for_status()
        return response.json()

    async def search_organizations(
        self,
        keywords: Optional[List[str]] = None,
        locations: Optional[List[str]] = None,
        employee_count_min: Optional[int] = None,
        employee_count_max: Optional[int] = None,
        funding_stages: Optional[List[str]] = None,
        industries: Optional[List[str]] = None,
        page: int = 1,
        per_page: int = 25,
    ) -> Dict[str, Any]:
        """
        Search for organizations/companies on Apollo.

        Args:
            keywords: Keywords to search (company name, tech, etc.)
            locations: List of locations (city, state, country)
            employee_count_min: Minimum employee count
            employee_count_max: Maximum employee count
            funding_stages: List of funding stages (Seed, Series A, etc.)
            industries: List of industries
            page: Page number
            per_page: Results per page (max 25 for free tier)

        Returns:
            Dict with organizations and pagination info
        """
        payload = {
            "api_key": self.api_key,
            "page": page,
            "per_page": min(per_page, 25),  # Apollo free tier limit
        }

        # Build organization filters
        if keywords:
            payload["q_organization_keyword_tags"] = keywords

        if locations:
            payload["organization_locations"] = locations

        if employee_count_min or employee_count_max:
            payload["organization_num_employees_ranges"] = []
            if employee_count_min and employee_count_max:
                payload["organization_num_employees_ranges"].append(
                    f"{employee_count_min},{employee_count_max}"
                )

        if industries:
            payload["organization_industry_tag_ids"] = industries

        try:
            response = await self.client.post(
                "/mixed_companies/search",
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

            logger.info(
                "Apollo organization search completed",
                total=data.get("pagination", {}).get("total_entries", 0),
                page=page,
            )

            return {
                "organizations": data.get("organizations", []),
                "pagination": data.get("pagination", {}),
            }
        except httpx.HTTPError as e:
            logger.error("Apollo API error", error=str(e))
            return {"organizations": [], "pagination": {}, "error": str(e)}

    async def search_people(
        self,
        organization_domains: Optional[List[str]] = None,
        titles: Optional[List[str]] = None,
        seniorities: Optional[List[str]] = None,
        page: int = 1,
        per_page: int = 25,
    ) -> Dict[str, Any]:
        """
        Search for people/contacts on Apollo.

        Args:
            organization_domains: Company domains to search within
            titles: Job titles to filter
            seniorities: Seniority levels (owner, c_suite, vp, director, manager)
            page: Page number
            per_page: Results per page

        Returns:
            Dict with people and pagination info
        """
        payload = {
            "api_key": self.api_key,
            "page": page,
            "per_page": min(per_page, 25),
        }

        if organization_domains:
            payload["q_organization_domains"] = "\n".join(organization_domains)

        if titles:
            payload["person_titles"] = titles

        if seniorities:
            payload["person_seniorities"] = seniorities

        try:
            response = await self.client.post(
                "/mixed_people/search",
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

            logger.info(
                "Apollo people search completed",
                total=data.get("pagination", {}).get("total_entries", 0),
                page=page,
            )

            return {
                "people": data.get("people", []),
                "pagination": data.get("pagination", {}),
            }
        except httpx.HTTPError as e:
            logger.error("Apollo API error", error=str(e))
            return {"people": [], "pagination": {}, "error": str(e)}

    async def enrich_organization(self, domain: str) -> Dict[str, Any]:
        """
        Enrich organization data by domain.

        Args:
            domain: Company domain (e.g., "anthropic.com")

        Returns:
            Enriched organization data
        """
        payload = {
            "api_key": self.api_key,
            "domain": domain,
        }

        try:
            response = await self.client.post(
                "/organizations/enrich",
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

            logger.info("Apollo organization enrichment completed", domain=domain)
            return data.get("organization", {})
        except httpx.HTTPError as e:
            logger.error("Apollo enrichment error", domain=domain, error=str(e))
            return {"error": str(e)}

    async def get_person_email(self, person_id: str) -> Optional[str]:
        """
        Get person's email by Apollo person ID.

        Args:
            person_id: Apollo person ID

        Returns:
            Email address if available
        """
        payload = {
            "api_key": self.api_key,
            "id": person_id,
        }

        try:
            response = await self.client.post(
                "/people/match",
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

            person = data.get("person", {})
            return person.get("email")
        except httpx.HTTPError as e:
            logger.error("Apollo email lookup error", person_id=person_id, error=str(e))
            return None

    def is_configured(self) -> bool:
        """Check if Apollo API key is configured."""
        return bool(self.api_key)

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


# Singleton instance
_apollo_client: Optional[ApolloClient] = None


@lru_cache
def get_apollo_client() -> ApolloClient:
    """Get Apollo client instance."""
    global _apollo_client
    if _apollo_client is None:
        _apollo_client = ApolloClient(api_key=settings.apollo_api_key)
    return _apollo_client
