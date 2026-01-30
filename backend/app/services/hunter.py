"""Hunter.io API client for email discovery and verification."""

from functools import lru_cache
from typing import Optional, List, Dict, Any

import httpx

from app.config import settings
from app.utils.logging import get_logger

logger = get_logger(__name__)


class HunterClient:
    """Client for Hunter.io API integration."""

    BASE_URL = "https://api.hunter.io/v2"

    def __init__(self, api_key: str):
        """Initialize Hunter client with API key."""
        self.api_key = api_key
        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            timeout=30.0,
        )

    async def find_email(
        self,
        domain: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        full_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Find email address for a person at a company.

        Args:
            domain: Company domain
            first_name: Person's first name
            last_name: Person's last name
            full_name: Person's full name (alternative to first/last)

        Returns:
            Dict with email and confidence score
        """
        params = {
            "api_key": self.api_key,
            "domain": domain,
        }

        if first_name and last_name:
            params["first_name"] = first_name
            params["last_name"] = last_name
        elif full_name:
            params["full_name"] = full_name
        else:
            return {"error": "Either first_name/last_name or full_name required"}

        try:
            response = await self.client.get("/email-finder", params=params)
            response.raise_for_status()
            data = response.json()

            result = data.get("data", {})
            logger.info(
                "Hunter email finder completed",
                domain=domain,
                found=bool(result.get("email")),
                confidence=result.get("score", 0),
            )

            return {
                "email": result.get("email"),
                "confidence": result.get("score", 0),
                "first_name": result.get("first_name"),
                "last_name": result.get("last_name"),
                "position": result.get("position"),
                "linkedin_url": result.get("linkedin"),
                "sources": result.get("sources", []),
            }
        except httpx.HTTPError as e:
            logger.error("Hunter email finder error", domain=domain, error=str(e))
            return {"error": str(e)}

    async def verify_email(self, email: str) -> Dict[str, Any]:
        """
        Verify an email address.

        Args:
            email: Email address to verify

        Returns:
            Dict with verification result
        """
        params = {
            "api_key": self.api_key,
            "email": email,
        }

        try:
            response = await self.client.get("/email-verifier", params=params)
            response.raise_for_status()
            data = response.json()

            result = data.get("data", {})
            logger.info(
                "Hunter email verification completed",
                email=email,
                status=result.get("status"),
                score=result.get("score"),
            )

            return {
                "email": result.get("email"),
                "status": result.get("status"),  # valid, invalid, accept_all, webmail, disposable, unknown
                "score": result.get("score", 0),
                "regexp": result.get("regexp"),
                "gibberish": result.get("gibberish"),
                "disposable": result.get("disposable"),
                "webmail": result.get("webmail"),
                "mx_records": result.get("mx_records"),
                "smtp_server": result.get("smtp_server"),
                "smtp_check": result.get("smtp_check"),
                "accept_all": result.get("accept_all"),
                "block": result.get("block"),
            }
        except httpx.HTTPError as e:
            logger.error("Hunter email verification error", email=email, error=str(e))
            return {"error": str(e), "status": "error"}

    async def domain_search(
        self,
        domain: str,
        limit: int = 10,
        offset: int = 0,
        department: Optional[str] = None,
        seniority: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Search for all emails at a domain.

        Args:
            domain: Company domain
            limit: Number of results (max 100)
            offset: Result offset for pagination
            department: Filter by department (executive, it, finance, etc.)
            seniority: Filter by seniority (junior, senior, executive)

        Returns:
            Dict with emails found at domain
        """
        params = {
            "api_key": self.api_key,
            "domain": domain,
            "limit": min(limit, 100),
            "offset": offset,
        }

        if department:
            params["department"] = department
        if seniority:
            params["seniority"] = seniority

        try:
            response = await self.client.get("/domain-search", params=params)
            response.raise_for_status()
            data = response.json()

            result = data.get("data", {})
            emails = result.get("emails", [])

            logger.info(
                "Hunter domain search completed",
                domain=domain,
                total=result.get("total", 0),
                returned=len(emails),
            )

            return {
                "domain": result.get("domain"),
                "organization": result.get("organization"),
                "emails": [
                    {
                        "email": e.get("value"),
                        "type": e.get("type"),
                        "confidence": e.get("confidence"),
                        "first_name": e.get("first_name"),
                        "last_name": e.get("last_name"),
                        "position": e.get("position"),
                        "seniority": e.get("seniority"),
                        "department": e.get("department"),
                        "linkedin": e.get("linkedin"),
                    }
                    for e in emails
                ],
                "total": result.get("total", 0),
                "pattern": result.get("pattern"),
            }
        except httpx.HTTPError as e:
            logger.error("Hunter domain search error", domain=domain, error=str(e))
            return {"error": str(e), "emails": []}

    async def get_account_info(self) -> Dict[str, Any]:
        """
        Get account information and remaining quota.

        Returns:
            Dict with account info and usage
        """
        params = {"api_key": self.api_key}

        try:
            response = await self.client.get("/account", params=params)
            response.raise_for_status()
            data = response.json()

            account = data.get("data", {})
            logger.info(
                "Hunter account info retrieved",
                email=account.get("email"),
                plan=account.get("plan_name"),
            )

            return {
                "email": account.get("email"),
                "plan_name": account.get("plan_name"),
                "plan_level": account.get("plan_level"),
                "requests_available": account.get("requests", {}).get("searches", {}).get("available", 0),
                "requests_used": account.get("requests", {}).get("searches", {}).get("used", 0),
                "verifications_available": account.get("requests", {}).get("verifications", {}).get("available", 0),
                "verifications_used": account.get("requests", {}).get("verifications", {}).get("used", 0),
                "reset_date": account.get("reset_date"),
            }
        except httpx.HTTPError as e:
            logger.error("Hunter account info error", error=str(e))
            return {"error": str(e)}

    def is_configured(self) -> bool:
        """Check if Hunter API key is configured."""
        return bool(self.api_key)

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


# Singleton instance
_hunter_client: Optional[HunterClient] = None


@lru_cache
def get_hunter_client() -> HunterClient:
    """Get Hunter client instance."""
    global _hunter_client
    if _hunter_client is None:
        _hunter_client = HunterClient(api_key=settings.hunter_api_key)
    return _hunter_client
