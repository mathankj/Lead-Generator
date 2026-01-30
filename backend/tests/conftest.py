"""Pytest fixtures and configuration."""

import pytest
from unittest.mock import MagicMock, AsyncMock
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def mock_settings(monkeypatch):
    """Override settings for testing."""
    monkeypatch.setenv("ENVIRONMENT", "testing")
    monkeypatch.setenv("DEBUG", "false")
    monkeypatch.setenv("DATABASE_URL", "postgresql://test:test@localhost:5432/test")
    monkeypatch.setenv("GROQ_API_KEY", "test_key")
    monkeypatch.setenv("APOLLO_API_KEY", "test_apollo_key")
    monkeypatch.setenv("HUNTER_API_KEY", "test_hunter_key")


@pytest.fixture
def mock_apollo_client():
    """Mock Apollo.io client for testing."""
    client = MagicMock()
    client.search_organizations = AsyncMock(return_value={
        "organizations": [
            {
                "name": "Test AI Corp",
                "primary_domain": "testai.com",
                "industry": "Artificial Intelligence",
                "estimated_num_employees": 100,
            }
        ],
        "pagination": {"total_entries": 1},
    })
    client.search_people = AsyncMock(return_value={
        "people": [],
        "pagination": {"total_entries": 0},
    })
    client.enrich_organization = AsyncMock(return_value={
        "organization": {"name": "Test AI Corp"},
    })
    return client


@pytest.fixture
def mock_hunter_client():
    """Mock Hunter.io client for testing."""
    client = MagicMock()
    client.find_email = AsyncMock(return_value={
        "email": "test@example.com",
        "confidence": 90,
    })
    client.verify_email = AsyncMock(return_value={
        "is_valid": True,
        "score": 95,
        "result": "deliverable",
    })
    client.domain_search = AsyncMock(return_value={
        "emails": [],
        "domain": "example.com",
    })
    return client


@pytest.fixture
def mock_enrichment_service(mock_apollo_client, mock_hunter_client):
    """Mock enrichment service for testing."""
    service = MagicMock()
    service.enrich_lead = AsyncMock(return_value={
        "company_data": {"industry": "AI"},
        "contacts": [],
        "score": {"total_score": 75, "breakdown": {}},
        "enrichment_sources": ["apollo"],
    })
    service.verify_contact_email = AsyncMock(return_value={
        "is_valid": True,
        "score": 95,
    })
    service.find_contact_email = AsyncMock(return_value={
        "email": "found@example.com",
        "confidence": 85,
    })
    return service


@pytest.fixture
def sample_lead_dict():
    """Sample lead data dictionary for testing."""
    return {
        "company_name": "Test AI Company",
        "company_domain": "testai.com",
        "industry": "Artificial Intelligence",
        "employee_count": 100,
        "funding_stage": "Series A",
        "funding_amount": 10000000.0,
        "location": "San Francisco, CA",
        "description": "AI platform for enterprise automation",
        "tech_stack": ["Python", "TensorFlow", "AWS"],
    }


@pytest.fixture
def sample_contact_dict():
    """Sample contact data dictionary for testing."""
    return {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@testai.com",
        "job_title": "CTO",
        "department": "Engineering",
        "linkedin_url": "https://linkedin.com/in/johndoe",
        "is_decision_maker": "yes",
    }
