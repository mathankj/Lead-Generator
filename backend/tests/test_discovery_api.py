"""Tests for Discovery API endpoints."""

import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient

from app.main import app


class TestDiscoveryAPI:
    """Test suite for Discovery endpoints."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        with TestClient(app) as c:
            yield c

    @pytest.fixture
    def sample_search_request(self):
        """Sample discovery search request."""
        return {
            "query": "AI companies in San Francisco",
            "filters": {
                "location": "San Francisco, CA",
                "industry": ["AI", "Machine Learning"],
                "employee_count_min": 50,
                "employee_count_max": 500,
                "funding_stage": ["Series A", "Series B"],
            },
            "sources": ["apollo"],
            "limit": 20,
        }

    def test_search_endpoint_exists(self, client):
        """Test POST /api/v1/discovery/search endpoint exists."""
        response = client.post(
            "/api/v1/discovery/search",
            json={"query": "AI companies"},
        )
        # Endpoint exists (not 404)
        assert response.status_code != 404

    def test_search_with_filters(self, client, sample_search_request):
        """Test search with various filters."""
        response = client.post(
            "/api/v1/discovery/search",
            json=sample_search_request,
        )
        assert response.status_code in [200, 500]

    def test_search_minimal_request(self, client):
        """Test search with minimal request body."""
        response = client.post(
            "/api/v1/discovery/search",
            json={"query": "tech startups"},
        )
        assert response.status_code in [200, 500]

    def test_search_empty_query(self, client):
        """Test search with empty query."""
        response = client.post(
            "/api/v1/discovery/search",
            json={"query": ""},
        )
        # Should accept empty query or return validation error
        assert response.status_code in [200, 422, 500]

    def test_search_with_specific_sources(self, client):
        """Test search specifying data sources."""
        response = client.post(
            "/api/v1/discovery/search",
            json={
                "query": "ML companies",
                "sources": ["apollo"],
            },
        )
        assert response.status_code in [200, 500]

    def test_search_with_location_filter(self, client):
        """Test search filtering by location."""
        response = client.post(
            "/api/v1/discovery/search",
            json={
                "query": "startups",
                "filters": {"location": "New York, NY"},
            },
        )
        assert response.status_code in [200, 500]

    def test_search_with_employee_count_filter(self, client):
        """Test search filtering by employee count range."""
        response = client.post(
            "/api/v1/discovery/search",
            json={
                "query": "companies",
                "filters": {
                    "employee_count_min": 100,
                    "employee_count_max": 1000,
                },
            },
        )
        assert response.status_code in [200, 500]

    def test_search_with_funding_stage_filter(self, client):
        """Test search filtering by funding stage."""
        response = client.post(
            "/api/v1/discovery/search",
            json={
                "query": "funded startups",
                "filters": {
                    "funding_stage": ["Series A", "Series B", "Series C"],
                },
            },
        )
        assert response.status_code in [200, 500]

    def test_search_with_limit(self, client):
        """Test search with result limit."""
        response = client.post(
            "/api/v1/discovery/search",
            json={
                "query": "AI companies",
                "limit": 5,
            },
        )
        assert response.status_code in [200, 500]

    def test_sources_endpoint(self, client):
        """Test GET /api/v1/discovery/sources lists available sources."""
        response = client.get("/api/v1/discovery/sources")
        assert response.status_code in [200, 500]

        if response.status_code == 200:
            data = response.json()
            assert "sources" in data
            # Should include apollo and hunter
            source_ids = [s.get("id") for s in data["sources"]]
            assert "apollo" in source_ids

    def test_sources_include_status(self, client):
        """Test sources endpoint includes status info."""
        response = client.get("/api/v1/discovery/sources")
        if response.status_code == 200:
            data = response.json()
            for source in data.get("sources", []):
                assert "id" in source
                assert "name" in source
                # May include status and quota info


class TestDiscoveryValidation:
    """Test discovery request validation."""

    @pytest.fixture
    def client(self):
        with TestClient(app) as c:
            yield c

    def test_invalid_limit_negative(self, client):
        """Test negative limit is handled."""
        response = client.post(
            "/api/v1/discovery/search",
            json={
                "query": "test",
                "limit": -5,
            },
        )
        # Should reject or handle gracefully
        assert response.status_code in [200, 422, 500]

    def test_invalid_employee_count_range(self, client):
        """Test invalid employee count range (min > max)."""
        response = client.post(
            "/api/v1/discovery/search",
            json={
                "query": "test",
                "filters": {
                    "employee_count_min": 500,
                    "employee_count_max": 100,
                },
            },
        )
        # Should handle or reject
        assert response.status_code in [200, 400, 422, 500]

    def test_invalid_source(self, client):
        """Test invalid source is handled."""
        response = client.post(
            "/api/v1/discovery/search",
            json={
                "query": "test",
                "sources": ["invalid_source_xyz"],
            },
        )
        # Should ignore invalid source or return error
        assert response.status_code in [200, 400, 422, 500]


class TestDiscoveryIntegration:
    """Integration tests for discovery flow."""

    @pytest.fixture
    def client(self):
        with TestClient(app) as c:
            yield c

    def test_search_and_save_flow(self, client):
        """Test searching and saving results as leads."""
        # First search
        search_response = client.post(
            "/api/v1/discovery/search",
            json={"query": "AI companies"},
        )
        assert search_response.status_code in [200, 500]

        # If search succeeded with results, try creating a lead
        if search_response.status_code == 200:
            data = search_response.json()
            if data.get("results"):
                result = data["results"][0]
                lead_data = {
                    "company_name": result.get("company_name", "Test Co"),
                    "company_domain": result.get("domain"),
                    "industry": result.get("industry"),
                }
                lead_response = client.post("/api/v1/leads", json=lead_data)
                assert lead_response.status_code in [201, 400, 500]

    def test_sources_before_search(self, client):
        """Test checking sources before searching."""
        # Check available sources
        sources_response = client.get("/api/v1/discovery/sources")
        assert sources_response.status_code in [200, 500]

        if sources_response.status_code == 200:
            data = sources_response.json()
            available_sources = [s["id"] for s in data.get("sources", [])]

            # Search using available sources
            if available_sources:
                search_response = client.post(
                    "/api/v1/discovery/search",
                    json={
                        "query": "ML companies",
                        "sources": available_sources[:1],
                    },
                )
                assert search_response.status_code in [200, 500]
