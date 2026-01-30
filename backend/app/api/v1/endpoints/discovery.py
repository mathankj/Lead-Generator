"""Lead discovery API endpoints."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from app.services.apollo import get_apollo_client, ApolloClient
from app.services.enrichment import get_enrichment_service, EnrichmentService
from app.utils.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


class DiscoverySearchRequest(BaseModel):
    """Request schema for discovery search."""

    query: Optional[str] = Field(None, description="Search query keywords")
    locations: Optional[List[str]] = Field(None, description="Filter by locations")
    industries: Optional[List[str]] = Field(None, description="Filter by industries")
    employee_count_min: Optional[int] = Field(None, ge=0, description="Minimum employees")
    employee_count_max: Optional[int] = Field(None, description="Maximum employees")
    funding_stages: Optional[List[str]] = Field(None, description="Filter by funding stages")
    sources: Optional[List[str]] = Field(
        default=["apollo"],
        description="Data sources to search",
    )
    page: int = Field(1, ge=1, description="Page number")
    limit: int = Field(25, ge=1, le=100, description="Results per page")


class DiscoverySearchResult(BaseModel):
    """Individual search result."""

    company_name: str
    domain: Optional[str] = None
    industry: Optional[str] = None
    employee_count: Optional[int] = None
    location: Optional[str] = None
    funding_stage: Optional[str] = None
    description: Optional[str] = None
    linkedin_url: Optional[str] = None
    source: str


class DiscoverySearchResponse(BaseModel):
    """Response schema for discovery search."""

    results: List[DiscoverySearchResult]
    total: int
    page: int
    sources_queried: List[str]


@router.post("/search", response_model=DiscoverySearchResponse)
async def search_companies(
    request: DiscoverySearchRequest,
    apollo: ApolloClient = Depends(get_apollo_client),
):
    """
    Search for companies across multiple data sources.

    Uses Apollo.io to find companies matching the specified criteria.
    """
    results = []
    sources_queried = []

    # Search Apollo
    if "apollo" in request.sources and apollo.is_configured():
        sources_queried.append("apollo")

        # Build keyword list
        keywords = []
        if request.query:
            keywords.extend(request.query.split())
        if request.industries:
            keywords.extend(request.industries)

        apollo_result = await apollo.search_organizations(
            keywords=keywords if keywords else None,
            locations=request.locations,
            employee_count_min=request.employee_count_min,
            employee_count_max=request.employee_count_max,
            page=request.page,
            per_page=request.limit,
        )

        # Transform results
        for org in apollo_result.get("organizations", []):
            results.append(
                DiscoverySearchResult(
                    company_name=org.get("name", "Unknown"),
                    domain=org.get("primary_domain"),
                    industry=org.get("industry"),
                    employee_count=org.get("estimated_num_employees"),
                    location=org.get("primary_address_locality"),
                    funding_stage=org.get("latest_funding_stage"),
                    description=org.get("short_description"),
                    linkedin_url=org.get("linkedin_url"),
                    source="apollo",
                )
            )

        total = apollo_result.get("pagination", {}).get("total_entries", len(results))
    else:
        total = 0

    if not sources_queried:
        raise HTTPException(
            status_code=400,
            detail="No data sources configured. Please set APOLLO_API_KEY.",
        )

    logger.info(
        "Discovery search completed",
        query=request.query,
        sources=sources_queried,
        results_count=len(results),
    )

    return DiscoverySearchResponse(
        results=results,
        total=total,
        page=request.page,
        sources_queried=sources_queried,
    )


@router.get("/sources")
async def list_sources(
    enrichment: EnrichmentService = Depends(get_enrichment_service),
):
    """List available data sources and their configuration status."""
    return {
        "sources": enrichment.get_available_sources(),
    }


@router.post("/enrich-domain")
async def enrich_domain(
    domain: str = Query(..., description="Company domain to enrich"),
    sources: Optional[List[str]] = Query(None, description="Sources to use"),
    enrichment: EnrichmentService = Depends(get_enrichment_service),
):
    """
    Enrich a company by domain without creating a lead.

    Useful for previewing data before importing.
    """
    result = await enrichment.enrich_lead(
        domain=domain,
        sources=sources,
    )

    logger.info(
        "Domain enriched",
        domain=domain,
        sources=result.get("enrichment_sources"),
    )

    return result


@router.get("/people")
async def search_people(
    domain: str = Query(..., description="Company domain"),
    titles: Optional[List[str]] = Query(None, description="Job titles to filter"),
    seniorities: Optional[List[str]] = Query(
        None,
        description="Seniority levels (c_suite, vp, director, manager)",
    ),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=25),
    apollo: ApolloClient = Depends(get_apollo_client),
):
    """
    Search for people at a company.

    Finds decision makers and contacts at the specified company domain.
    """
    if not apollo.is_configured():
        raise HTTPException(
            status_code=400,
            detail="Apollo API not configured. Set APOLLO_API_KEY.",
        )

    result = await apollo.search_people(
        organization_domains=[domain],
        titles=titles,
        seniorities=seniorities or ["c_suite", "vp", "director"],
        page=page,
        per_page=limit,
    )

    people = [
        {
            "first_name": p.get("first_name"),
            "last_name": p.get("last_name"),
            "email": p.get("email"),
            "title": p.get("title"),
            "seniority": p.get("seniority"),
            "linkedin_url": p.get("linkedin_url"),
        }
        for p in result.get("people", [])
    ]

    logger.info(
        "People search completed",
        domain=domain,
        count=len(people),
    )

    return {
        "domain": domain,
        "people": people,
        "total": result.get("pagination", {}).get("total_entries", len(people)),
        "page": page,
    }
