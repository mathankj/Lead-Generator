"""Health check response schemas."""

from datetime import datetime
from typing import Dict

from pydantic import BaseModel, Field


class ServiceStatus(BaseModel):
    """Status of an individual service."""

    database: str = Field(description="Database connection status")
    vector_db: str = Field(description="Vector database status")
    llm: str = Field(description="LLM service status")


class HealthResponse(BaseModel):
    """Health check endpoint response."""

    status: str = Field(description="Overall health status")
    version: str = Field(description="Application version")
    environment: str = Field(description="Current environment")
    services: ServiceStatus = Field(description="Status of each service")
    timestamp: datetime = Field(description="Response timestamp")

    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "healthy",
                "version": "0.1.0",
                "environment": "development",
                "services": {
                    "database": "connected",
                    "vector_db": "connected",
                    "llm": "available",
                },
                "timestamp": "2026-01-30T12:00:00Z",
            }
        }
    }
