"""Tests for Hunter.io API client."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx

from app.services.hunter import HunterClient


class TestHunterClient:
    """Test suite for Hunter.io API client."""

    @pytest.fixture
    def client(self):
        """Create Hunter client with test API key."""
        return HunterClient(api_key="test_hunter_key")

    @pytest.fixture
    def mock_email_finder_response(self):
        """Mock Hunter email finder response."""
        return {
            "data": {
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com",
                "score": 92,
                "domain": "example.com",
                "position": "CTO",
                "sources": [
                    {"domain": "linkedin.com", "uri": "https://linkedin.com/in/johndoe"}
                ],
            },
            "meta": {
                "params": {
                    "first_name": "John",
                    "last_name": "Doe",
                    "domain": "example.com",
                }
            },
        }

    @pytest.fixture
    def mock_email_verifier_response(self):
        """Mock Hunter email verifier response."""
        return {
            "data": {
                "email": "john.doe@example.com",
                "result": "deliverable",
                "score": 95,
                "regexp": True,
                "gibberish": False,
                "disposable": False,
                "webmail": False,
                "mx_records": True,
                "smtp_server": True,
                "smtp_check": True,
                "accept_all": False,
                "block": False,
            },
            "meta": {
                "params": {"email": "john.doe@example.com"}
            },
        }

    @pytest.fixture
    def mock_domain_search_response(self):
        """Mock Hunter domain search response."""
        return {
            "data": {
                "domain": "example.com",
                "disposable": False,
                "webmail": False,
                "organization": "Example Inc",
                "pattern": "{first}.{last}",
                "emails": [
                    {
                        "value": "john.doe@example.com",
                        "type": "personal",
                        "confidence": 92,
                        "first_name": "John",
                        "last_name": "Doe",
                        "position": "CTO",
                        "department": "Engineering",
                        "linkedin": "https://linkedin.com/in/johndoe",
                    },
                    {
                        "value": "jane.smith@example.com",
                        "type": "personal",
                        "confidence": 88,
                        "first_name": "Jane",
                        "last_name": "Smith",
                        "position": "CEO",
                        "department": "Executive",
                        "linkedin": "https://linkedin.com/in/janesmith",
                    },
                ],
            },
            "meta": {
                "results": 2,
                "limit": 10,
                "offset": 0,
            },
        }

    def test_client_initialization(self, client):
        """Test client is initialized correctly."""
        assert client is not None
        assert client.api_key == "test_hunter_key"
        assert client.base_url == "https://api.hunter.io/v2"

    def test_client_no_api_key(self):
        """Test client raises error without API key."""
        with pytest.raises(ValueError, match="API key is required"):
            HunterClient(api_key="")

    @pytest.mark.asyncio
    async def test_find_email_success(self, client, mock_email_finder_response):
        """Test successful email finding."""
        with patch.object(client, "_make_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_email_finder_response

            result = await client.find_email(
                domain="example.com",
                first_name="John",
                last_name="Doe",
            )

            assert "email" in result
            assert result["email"] == "john.doe@example.com"
            assert result["confidence"] == 92

    @pytest.mark.asyncio
    async def test_find_email_not_found(self, client):
        """Test email finder when email not found."""
        with patch.object(client, "_make_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {
                "data": {"email": None, "score": 0},
                "errors": [{"details": "No email found"}],
            }

            result = await client.find_email(
                domain="example.com",
                first_name="Unknown",
                last_name="Person",
            )

            assert result.get("email") is None or result.get("confidence", 0) == 0

    @pytest.mark.asyncio
    async def test_verify_email_valid(self, client, mock_email_verifier_response):
        """Test email verification for valid email."""
        with patch.object(client, "_make_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_email_verifier_response

            result = await client.verify_email("john.doe@example.com")

            assert result["is_valid"] is True
            assert result["score"] == 95
            assert result["result"] == "deliverable"

    @pytest.mark.asyncio
    async def test_verify_email_invalid(self, client):
        """Test email verification for invalid email."""
        with patch.object(client, "_make_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {
                "data": {
                    "email": "invalid@fake.com",
                    "result": "undeliverable",
                    "score": 10,
                    "mx_records": False,
                    "smtp_check": False,
                },
            }

            result = await client.verify_email("invalid@fake.com")

            assert result["is_valid"] is False
            assert result["result"] == "undeliverable"

    @pytest.mark.asyncio
    async def test_domain_search_success(self, client, mock_domain_search_response):
        """Test successful domain search."""
        with patch.object(client, "_make_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_domain_search_response

            result = await client.domain_search("example.com")

            assert "emails" in result
            assert len(result["emails"]) == 2
            assert result["domain"] == "example.com"
            assert result["organization"] == "Example Inc"

    @pytest.mark.asyncio
    async def test_domain_search_with_filters(self, client, mock_domain_search_response):
        """Test domain search with department filter."""
        with patch.object(client, "_make_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_domain_search_response

            result = await client.domain_search(
                domain="example.com",
                department="executive",
                limit=5,
            )

            assert result is not None
            mock_request.assert_called_once()

    @pytest.mark.asyncio
    async def test_api_error_handling(self, client):
        """Test error handling for API failures."""
        with patch.object(client, "_make_request", new_callable=AsyncMock) as mock_request:
            mock_request.side_effect = httpx.HTTPStatusError(
                "API Error",
                request=MagicMock(),
                response=MagicMock(status_code=401),
            )

            result = await client.find_email(
                domain="example.com",
                first_name="Test",
                last_name="User",
            )
            assert "error" in result

    @pytest.mark.asyncio
    async def test_rate_limit_error(self, client):
        """Test rate limit handling."""
        with patch.object(client, "_make_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {
                "errors": [{"code": 429, "details": "Rate limit exceeded"}],
            }

            result = await client.verify_email("test@example.com")
            # Should return error info without crashing
            assert result is not None

    @pytest.mark.asyncio
    async def test_empty_domain_search(self, client):
        """Test domain search with no results."""
        with patch.object(client, "_make_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {
                "data": {
                    "domain": "unknown-domain-xyz.com",
                    "emails": [],
                },
                "meta": {"results": 0},
            }

            result = await client.domain_search("unknown-domain-xyz.com")
            assert result.get("emails", []) == []

    @pytest.mark.asyncio
    async def test_email_pattern_detection(self, client, mock_domain_search_response):
        """Test that email pattern is returned from domain search."""
        with patch.object(client, "_make_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_domain_search_response

            result = await client.domain_search("example.com")

            assert result.get("pattern") == "{first}.{last}"
