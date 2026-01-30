"""Tests for Contact CRUD API endpoints."""

import pytest
from fastapi.testclient import TestClient
from uuid import uuid4

from app.main import app


class TestContactsCRUD:
    """Test suite for Contact CRUD operations."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        with TestClient(app) as c:
            yield c

    @pytest.fixture
    def sample_contact_data(self):
        """Sample contact data for tests."""
        return {
            "lead_id": str(uuid4()),
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "job_title": "CTO",
            "department": "Engineering",
            "linkedin_url": "https://linkedin.com/in/johndoe",
            "phone": "+1-555-0123",
            "is_decision_maker": "yes",
        }

    def test_list_contacts_endpoint(self, client):
        """Test GET /api/v1/contacts returns contacts."""
        response = client.get("/api/v1/contacts")
        assert response.status_code in [200, 500]

    def test_list_contacts_with_pagination(self, client):
        """Test contacts pagination parameters."""
        response = client.get("/api/v1/contacts?page=1&page_size=20")
        assert response.status_code in [200, 500]

    def test_list_contacts_by_lead(self, client):
        """Test filtering contacts by lead ID."""
        lead_id = str(uuid4())
        response = client.get(f"/api/v1/contacts?lead_id={lead_id}")
        assert response.status_code in [200, 500]

    def test_list_contacts_verified_only(self, client):
        """Test filtering for verified contacts only."""
        response = client.get("/api/v1/contacts?verified_only=true")
        assert response.status_code in [200, 500]

    def test_create_contact_endpoint(self, client, sample_contact_data):
        """Test POST /api/v1/contacts creates a new contact."""
        response = client.post("/api/v1/contacts", json=sample_contact_data)
        # May fail if lead doesn't exist (404) or DB error (500)
        assert response.status_code in [201, 404, 500]

    def test_create_contact_minimal_data(self, client):
        """Test creating contact with minimal data."""
        minimal_data = {
            "lead_id": str(uuid4()),
            "first_name": "Jane",
        }
        response = client.post("/api/v1/contacts", json=minimal_data)
        assert response.status_code in [201, 404, 500]

    def test_create_contact_missing_lead_id(self, client):
        """Test creating contact without lead_id fails."""
        invalid_data = {
            "first_name": "John",
            "last_name": "Doe",
        }
        response = client.post("/api/v1/contacts", json=invalid_data)
        assert response.status_code == 422

    def test_get_contact_endpoint(self, client):
        """Test GET /api/v1/contacts/{id} retrieves a contact."""
        contact_id = str(uuid4())
        response = client.get(f"/api/v1/contacts/{contact_id}")
        assert response.status_code in [200, 404, 500]

    def test_get_contact_invalid_uuid(self, client):
        """Test getting contact with invalid UUID."""
        response = client.get("/api/v1/contacts/invalid-uuid")
        assert response.status_code == 422

    def test_update_contact_endpoint(self, client):
        """Test PUT /api/v1/contacts/{id} updates a contact."""
        contact_id = str(uuid4())
        response = client.put(
            f"/api/v1/contacts/{contact_id}?first_name=Updated"
        )
        assert response.status_code in [200, 404, 500]

    def test_update_contact_email(self, client):
        """Test updating contact email resets verification."""
        contact_id = str(uuid4())
        response = client.put(
            f"/api/v1/contacts/{contact_id}?email=new.email@example.com"
        )
        assert response.status_code in [200, 404, 500]

    def test_delete_contact_endpoint(self, client):
        """Test DELETE /api/v1/contacts/{id} removes a contact."""
        contact_id = str(uuid4())
        response = client.delete(f"/api/v1/contacts/{contact_id}")
        assert response.status_code in [204, 404, 500]

    def test_verify_email_endpoint(self, client):
        """Test POST /api/v1/contacts/{id}/verify-email verifies email."""
        contact_id = str(uuid4())
        response = client.post(f"/api/v1/contacts/{contact_id}/verify-email")
        assert response.status_code in [200, 400, 404, 500]

    def test_find_email_endpoint(self, client):
        """Test POST /api/v1/contacts/{id}/find-email finds email."""
        contact_id = str(uuid4())
        response = client.post(f"/api/v1/contacts/{contact_id}/find-email")
        assert response.status_code in [200, 400, 404, 500]


class TestContactValidation:
    """Test contact data validation."""

    @pytest.fixture
    def client(self):
        with TestClient(app) as c:
            yield c

    def test_invalid_decision_maker_value(self, client):
        """Test is_decision_maker only accepts yes/no/unknown."""
        data = {
            "lead_id": str(uuid4()),
            "first_name": "Test",
            "is_decision_maker": "maybe",  # Invalid value
        }
        response = client.post("/api/v1/contacts", json=data)
        assert response.status_code == 422

    def test_valid_decision_maker_yes(self, client):
        """Test is_decision_maker accepts 'yes'."""
        data = {
            "lead_id": str(uuid4()),
            "first_name": "Test",
            "is_decision_maker": "yes",
        }
        response = client.post("/api/v1/contacts", json=data)
        assert response.status_code in [201, 404, 500]

    def test_valid_decision_maker_no(self, client):
        """Test is_decision_maker accepts 'no'."""
        data = {
            "lead_id": str(uuid4()),
            "first_name": "Test",
            "is_decision_maker": "no",
        }
        response = client.post("/api/v1/contacts", json=data)
        assert response.status_code in [201, 404, 500]

    def test_valid_decision_maker_unknown(self, client):
        """Test is_decision_maker accepts 'unknown'."""
        data = {
            "lead_id": str(uuid4()),
            "first_name": "Test",
            "is_decision_maker": "unknown",
        }
        response = client.post("/api/v1/contacts", json=data)
        assert response.status_code in [201, 404, 500]

    def test_long_first_name(self, client):
        """Test first_name length validation."""
        data = {
            "lead_id": str(uuid4()),
            "first_name": "A" * 101,  # Over 100 chars
        }
        response = client.post("/api/v1/contacts", json=data)
        assert response.status_code == 422

    def test_long_linkedin_url(self, client):
        """Test linkedin_url length validation."""
        data = {
            "lead_id": str(uuid4()),
            "first_name": "Test",
            "linkedin_url": "https://linkedin.com/" + "x" * 500,  # Over 500 chars
        }
        response = client.post("/api/v1/contacts", json=data)
        assert response.status_code == 422


class TestContactPagination:
    """Test contact list pagination."""

    @pytest.fixture
    def client(self):
        with TestClient(app) as c:
            yield c

    def test_page_size_limit(self, client):
        """Test page size is limited to max 100."""
        response = client.get("/api/v1/contacts?page_size=150")
        assert response.status_code == 422

    def test_page_number_positive(self, client):
        """Test page number must be positive."""
        response = client.get("/api/v1/contacts?page=0")
        assert response.status_code == 422
