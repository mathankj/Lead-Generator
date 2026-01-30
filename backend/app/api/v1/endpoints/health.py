"""Health check endpoints."""

from datetime import datetime

from fastapi import APIRouter

from app import __version__
from app.config import settings
from app.schemas.health import HealthResponse, ServiceStatus
from app.core.database import check_database_connection
from app.core.vector_db import get_vector_db
from app.core.llm import get_llm_client

router = APIRouter()


@router.get(
    "",
    response_model=HealthResponse,
    summary="Health Check",
    description="Check the health status of all services",
)
async def health_check() -> HealthResponse:
    """
    Comprehensive health check endpoint.

    Returns status of:
    - Database connection
    - Vector database (ChromaDB)
    - LLM service (Groq)
    """
    # Check database
    try:
        db_healthy = await check_database_connection()
        db_status = "connected" if db_healthy else "disconnected"
    except Exception:
        db_status = "error"

    # Check vector database
    try:
        vector_db = get_vector_db()
        vector_status = "connected" if vector_db.is_healthy() else "disconnected"
    except Exception:
        vector_status = "error"

    # Check LLM (only if API key is configured)
    llm_status = "not_configured"
    if settings.groq_api_key:
        try:
            llm = get_llm_client()
            llm_status = "available" if llm.is_healthy() else "unavailable"
        except Exception:
            llm_status = "error"

    # Determine overall status
    all_services = [db_status, vector_status]
    if settings.groq_api_key:
        all_services.append(llm_status)

    if all(s in ["connected", "available", "not_configured"] for s in all_services):
        overall_status = "healthy"
    elif any(s == "error" for s in all_services):
        overall_status = "unhealthy"
    else:
        overall_status = "degraded"

    return HealthResponse(
        status=overall_status,
        version=__version__,
        environment=settings.environment,
        services=ServiceStatus(
            database=db_status,
            vector_db=vector_status,
            llm=llm_status,
        ),
        timestamp=datetime.utcnow(),
    )


@router.get(
    "/ready",
    summary="Readiness Check",
    description="Simple readiness probe for container orchestration",
)
async def readiness() -> dict:
    """Simple readiness check for Kubernetes/Docker."""
    return {"ready": True}


@router.get(
    "/live",
    summary="Liveness Check",
    description="Simple liveness probe for container orchestration",
)
async def liveness() -> dict:
    """Simple liveness check for Kubernetes/Docker."""
    return {"alive": True}
