"""Tests for health check endpoints."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Create a test client."""
    with TestClient(app) as c:
        yield c


class TestHealthEndpoints:
    """Test suite for health check endpoints."""

    def test_root_endpoint(self, client):
        """Test root endpoint returns API info."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert data["name"] == "TechJays Lead AI"
        assert "version" in data
        assert "docs" in data

    def test_root_health(self, client):
        """Test quick health check at root level."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "version" in data

    def test_readiness_probe(self, client):
        """Test readiness probe for container orchestration."""
        response = client.get("/api/v1/health/ready")
        assert response.status_code == 200
        data = response.json()
        assert data["ready"] is True

    def test_liveness_probe(self, client):
        """Test liveness probe for container orchestration."""
        response = client.get("/api/v1/health/live")
        assert response.status_code == 200
        data = response.json()
        assert data["alive"] is True

    def test_detailed_health_check(self, client):
        """Test detailed health check endpoint."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()

        # Check response structure
        assert "status" in data
        assert "version" in data
        assert "environment" in data
        assert "services" in data
        assert "timestamp" in data

        # Check services structure
        services = data["services"]
        assert "database" in services
        assert "vector_db" in services
        assert "llm" in services


class TestConfigLoading:
    """Test configuration loading."""

    def test_settings_loaded(self):
        """Test that settings are loaded correctly."""
        from app.config import settings

        assert settings is not None
        assert settings.environment in ["development", "testing", "production"]
        assert settings.api_port > 0
        assert settings.api_prefix.startswith("/")
