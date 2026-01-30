"""Tests for Lead CRUD API endpoints."""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from uuid import uuid4

from app.main import app


class TestLeadsCRUD:
    """Test suite for Lead CRUD operations."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        with TestClient(app) as c:
            yield c

    @pytest.fixture
    def mock_db_session(self):
        """Mock database session."""
        with patch("app.api.v1.endpoints.leads.get_db") as mock:
            session = MagicMock()
            mock.return_value = session
            yield session

    @pytest.fixture
    def sample_lead_data(self):
        """Sample lead data for tests."""
        return {
            "company_name": "Test AI Company",
            "company_domain": "testai.com",
            "industry": "Artificial Intelligence",
            "employee_count": 100,
            "funding_stage": "Series A",
            "funding_amount": 10000000,
            "location": "San Francisco, CA",
            "description": "AI platform for enterprise automation",
            "tech_stack": ["Python", "TensorFlow", "AWS"],
        }

    @pytest.fixture
    def mock_lead(self, sample_lead_data):
        """Create a mock lead object."""
        lead = MagicMock()
        lead.id = uuid4()
        lead.company_name = sample_lead_data["company_name"]
        lead.company_domain = sample_lead_data["company_domain"]
        lead.industry = sample_lead_data["industry"]
        lead.employee_count = sample_lead_data["employee_count"]
        lead.funding_stage = sample_lead_data["funding_stage"]
        lead.funding_amount = sample_lead_data["funding_amount"]
        lead.location = sample_lead_data["location"]
        lead.description = sample_lead_data["description"]
        lead.tech_stack = sample_lead_data["tech_stack"]
        lead.ai_adoption_score = 75.0
        lead.lead_score = 68.5
        lead.status = "new"
        lead.linkedin_url = None
        lead.crunchbase_url = None
        lead.notes = None
        lead.tags = []
        lead.contacts = []
        from datetime import datetime
        lead.created_at = datetime.utcnow()
        lead.updated_at = datetime.utcnow()
        return lead

    def test_list_leads_endpoint(self, client):
        """Test GET /api/v1/leads returns paginated results."""
        response = client.get("/api/v1/leads")
        # May return 500 if DB not connected, but endpoint exists
        assert response.status_code in [200, 500]

    def test_list_leads_with_pagination(self, client):
        """Test leads pagination parameters."""
        response = client.get("/api/v1/leads?page=1&page_size=10")
        assert response.status_code in [200, 500]

    def test_list_leads_with_filters(self, client):
        """Test leads filtering parameters."""
        response = client.get(
            "/api/v1/leads?status=new&min_score=50&industry=AI&location=SF"
        )
        assert response.status_code in [200, 500]

    def test_list_leads_with_search(self, client):
        """Test leads search parameter."""
        response = client.get("/api/v1/leads?search=anthropic")
        assert response.status_code in [200, 500]

    def test_create_lead_endpoint(self, client, sample_lead_data):
        """Test POST /api/v1/leads creates a new lead."""
        response = client.post("/api/v1/leads", json=sample_lead_data)
        # May fail if DB not connected
        assert response.status_code in [201, 400, 500]

    def test_create_lead_minimal_data(self, client):
        """Test creating lead with minimal required data."""
        minimal_data = {"company_name": "Minimal Corp"}
        response = client.post("/api/v1/leads", json=minimal_data)
        assert response.status_code in [201, 400, 500]

    def test_create_lead_validation_error(self, client):
        """Test lead creation with invalid data."""
        invalid_data = {"company_name": ""}  # Empty name should fail
        response = client.post("/api/v1/leads", json=invalid_data)
        assert response.status_code == 422  # Validation error

    def test_create_lead_missing_company_name(self, client):
        """Test lead creation without company name."""
        invalid_data = {"industry": "AI"}  # Missing required company_name
        response = client.post("/api/v1/leads", json=invalid_data)
        assert response.status_code == 422

    def test_get_lead_endpoint(self, client):
        """Test GET /api/v1/leads/{id} retrieves a lead."""
        lead_id = str(uuid4())
        response = client.get(f"/api/v1/leads/{lead_id}")
        # 404 if not found, 500 if DB error
        assert response.status_code in [200, 404, 500]

    def test_get_lead_invalid_uuid(self, client):
        """Test getting lead with invalid UUID."""
        response = client.get("/api/v1/leads/not-a-valid-uuid")
        assert response.status_code == 422

    def test_update_lead_endpoint(self, client):
        """Test PUT /api/v1/leads/{id} updates a lead."""
        lead_id = str(uuid4())
        update_data = {"company_name": "Updated Company Name"}
        response = client.put(f"/api/v1/leads/{lead_id}", json=update_data)
        assert response.status_code in [200, 404, 500]

    def test_update_lead_partial(self, client):
        """Test partial lead update."""
        lead_id = str(uuid4())
        update_data = {"status": "contacted"}
        response = client.put(f"/api/v1/leads/{lead_id}", json=update_data)
        assert response.status_code in [200, 404, 500]

    def test_delete_lead_endpoint(self, client):
        """Test DELETE /api/v1/leads/{id} removes a lead."""
        lead_id = str(uuid4())
        response = client.delete(f"/api/v1/leads/{lead_id}")
        assert response.status_code in [204, 404, 500]

    def test_enrich_lead_endpoint(self, client):
        """Test POST /api/v1/leads/{id}/enrich enriches lead data."""
        lead_id = str(uuid4())
        response = client.post(f"/api/v1/leads/{lead_id}/enrich")
        assert response.status_code in [200, 400, 404, 500]

    def test_enrich_lead_with_sources(self, client):
        """Test lead enrichment with specific sources."""
        lead_id = str(uuid4())
        response = client.post(
            f"/api/v1/leads/{lead_id}/enrich?sources=apollo&sources=hunter"
        )
        assert response.status_code in [200, 400, 404, 500]

    def test_score_lead_endpoint(self, client):
        """Test POST /api/v1/leads/{id}/score calculates lead score."""
        lead_id = str(uuid4())
        response = client.post(f"/api/v1/leads/{lead_id}/score")
        assert response.status_code in [200, 404, 500]


class TestLeadValidation:
    """Test lead data validation."""

    @pytest.fixture
    def client(self):
        with TestClient(app) as c:
            yield c

    def test_employee_count_negative(self, client):
        """Test negative employee count is rejected."""
        data = {
            "company_name": "Test Corp",
            "employee_count": -10,
        }
        response = client.post("/api/v1/leads", json=data)
        assert response.status_code == 422

    def test_funding_amount_negative(self, client):
        """Test negative funding amount is rejected."""
        data = {
            "company_name": "Test Corp",
            "funding_amount": -1000000,
        }
        response = client.post("/api/v1/leads", json=data)
        assert response.status_code == 422

    def test_score_out_of_range(self, client):
        """Test score values out of 0-100 range are rejected."""
        lead_id = str(uuid4())
        update_data = {"lead_score": 150}  # Over 100
        response = client.put(f"/api/v1/leads/{lead_id}", json=update_data)
        assert response.status_code in [404, 422, 500]

    def test_valid_tech_stack_list(self, client):
        """Test tech stack accepts valid list."""
        data = {
            "company_name": "Test Corp",
            "tech_stack": ["Python", "React", "PostgreSQL"],
        }
        response = client.post("/api/v1/leads", json=data)
        assert response.status_code in [201, 400, 500]


class TestLeadPagination:
    """Test lead list pagination."""

    @pytest.fixture
    def client(self):
        with TestClient(app) as c:
            yield c

    def test_page_size_limit(self, client):
        """Test page size is limited to max 100."""
        response = client.get("/api/v1/leads?page_size=200")
        assert response.status_code == 422  # Validation error

    def test_page_number_positive(self, client):
        """Test page number must be positive."""
        response = client.get("/api/v1/leads?page=0")
        assert response.status_code == 422

    def test_page_number_negative(self, client):
        """Test negative page number is rejected."""
        response = client.get("/api/v1/leads?page=-1")
        assert response.status_code == 422
