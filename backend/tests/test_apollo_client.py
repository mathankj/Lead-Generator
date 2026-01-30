"""Tests for Apollo.io API client."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx

from app.services.apollo import ApolloClient


class TestApolloClient:
    """Test suite for Apollo.io API client."""

    @pytest.fixture
    def client(self):
        """Create Apollo client with test API key."""
        return ApolloClient(api_key="test_apollo_key")

    @pytest.fixture
    def mock_company_response(self):
        """Mock Apollo company search response."""
        return {
            "organizations": [
                {
                    "id": "org_123",
                    "name": "Anthropic",
                    "website_url": "https://anthropic.com",
                    "primary_domain": "anthropic.com",
                    "industry": "Artificial Intelligence",
                    "estimated_num_employees": 150,
                    "founded_year": 2021,
                    "city": "San Francisco",
                    "state": "California",
                    "country": "United States",
                    "linkedin_url": "https://linkedin.com/company/anthropic",
                    "short_description": "AI safety company",
                    "technologies": ["Python", "TensorFlow", "AWS"],
                    "funding": {
                        "total_funding": 1500000000,
                        "latest_funding_stage": "Series C",
                    },
                }
            ],
            "pagination": {
                "page": 1,
                "per_page": 25,
                "total_entries": 1,
            },
        }

    @pytest.fixture
    def mock_people_response(self):
        """Mock Apollo people search response."""
        return {
            "people": [
                {
                    "id": "person_123",
                    "first_name": "Dario",
                    "last_name": "Amodei",
                    "email": "dario@anthropic.com",
                    "title": "CEO",
                    "departments": ["Executive"],
                    "linkedin_url": "https://linkedin.com/in/dario-amodei",
                    "organization": {
                        "name": "Anthropic",
                        "primary_domain": "anthropic.com",
                    },
                }
            ],
            "pagination": {
                "page": 1,
                "per_page": 25,
                "total_entries": 1,
            },
        }

    def test_client_initialization(self, client):
        """Test client is initialized correctly."""
        assert client is not None
        assert client.api_key == "test_apollo_key"
        assert client.base_url == "https://api.apollo.io/v1"

    def test_client_no_api_key(self):
        """Test client raises error without API key."""
        with pytest.raises(ValueError, match="API key is required"):
            ApolloClient(api_key="")

    @pytest.mark.asyncio
    async def test_search_organizations_success(self, client, mock_company_response):
        """Test successful company search."""
        with patch.object(client, "_make_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_company_response

            result = await client.search_organizations(
                keywords="AI companies",
                locations=["San Francisco"],
                industries=["Artificial Intelligence"],
            )

            assert "organizations" in result
            assert len(result["organizations"]) == 1
            assert result["organizations"][0]["name"] == "Anthropic"
            mock_request.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_organizations_with_filters(self, client, mock_company_response):
        """Test company search with multiple filters."""
        with patch.object(client, "_make_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_company_response

            result = await client.search_organizations(
                keywords="machine learning",
                locations=["San Francisco", "New York"],
                industries=["AI", "Software"],
                employee_count_min=50,
                employee_count_max=500,
            )

            assert result is not None
            call_args = mock_request.call_args
            assert call_args is not None

    @pytest.mark.asyncio
    async def test_search_people_success(self, client, mock_people_response):
        """Test successful people search."""
        with patch.object(client, "_make_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_people_response

            result = await client.search_people(
                organization_domains=["anthropic.com"],
                titles=["CEO", "CTO"],
            )

            assert "people" in result
            assert len(result["people"]) == 1
            assert result["people"][0]["first_name"] == "Dario"

    @pytest.mark.asyncio
    async def test_enrich_organization_success(self, client, mock_company_response):
        """Test organization enrichment."""
        with patch.object(client, "_make_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"organization": mock_company_response["organizations"][0]}

            result = await client.enrich_organization(domain="anthropic.com")

            assert "organization" in result
            assert result["organization"]["name"] == "Anthropic"

    @pytest.mark.asyncio
    async def test_api_error_handling(self, client):
        """Test error handling for API failures."""
        with patch.object(client, "_make_request", new_callable=AsyncMock) as mock_request:
            mock_request.side_effect = httpx.HTTPStatusError(
                "API Error",
                request=MagicMock(),
                response=MagicMock(status_code=429),
            )

            result = await client.search_organizations(keywords="test")
            assert "error" in result

    @pytest.mark.asyncio
    async def test_rate_limit_handling(self, client):
        """Test rate limit error is handled gracefully."""
        with patch.object(client, "_make_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {
                "error": "Rate limit exceeded",
                "rate_limit_remaining": 0,
            }

            result = await client.search_organizations(keywords="test")
            # Should return the error response without crashing
            assert result is not None

    @pytest.mark.asyncio
    async def test_empty_search_results(self, client):
        """Test handling of empty search results."""
        with patch.object(client, "_make_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {
                "organizations": [],
                "pagination": {"total_entries": 0},
            }

            result = await client.search_organizations(keywords="nonexistent company xyz")
            assert result["organizations"] == []

    @pytest.mark.asyncio
    async def test_pagination_info(self, client, mock_company_response):
        """Test pagination information is returned."""
        with patch.object(client, "_make_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_company_response

            result = await client.search_organizations(keywords="AI", page=1, per_page=25)

            assert "pagination" in result
            assert result["pagination"]["page"] == 1
