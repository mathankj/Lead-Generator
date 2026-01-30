"""API v1 router combining all endpoint routers."""

from fastapi import APIRouter

from app.api.v1.endpoints import health, leads, contacts, discovery

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(leads.router, prefix="/leads", tags=["Leads"])
api_router.include_router(contacts.router, prefix="/contacts", tags=["Contacts"])
api_router.include_router(discovery.router, prefix="/discovery", tags=["Discovery"])
