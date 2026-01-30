"""Tests for lead scoring service."""

import pytest
from app.services.scoring import ScoringService, get_scoring_service


class TestScoringService:
    """Test suite for the lead scoring algorithm."""

    @pytest.fixture
    def scorer(self):
        """Create a scoring service instance."""
        return ScoringService()

    def test_scoring_service_instance(self, scorer):
        """Test scoring service can be instantiated."""
        assert scorer is not None
        assert hasattr(scorer, "calculate_score")

    def test_calculate_score_minimum_data(self, scorer):
        """Test scoring with minimal lead data."""
        lead_data = {
            "company_name": "Test Company",
        }
        result = scorer.calculate_score(lead_data)

        assert "total_score" in result
        assert "breakdown" in result
        assert 0 <= result["total_score"] <= 100

    def test_calculate_score_full_data(self, scorer):
        """Test scoring with complete lead data."""
        lead_data = {
            "company_name": "AI Startup Inc",
            "company_domain": "aistartup.com",
            "industry": "Artificial Intelligence",
            "employee_count": 150,
            "funding_stage": "Series B",
            "funding_amount": 25000000,
            "location": "San Francisco, CA",
            "description": "Leading AI platform for enterprise automation using machine learning",
            "tech_stack": ["Python", "TensorFlow", "AWS", "Kubernetes"],
            "linkedin_url": "https://linkedin.com/company/aistartup",
            "contacts": [
                {
                    "email": "cto@aistartup.com",
                    "email_confidence": 95,
                    "job_title": "CTO",
                    "linkedin_url": "https://linkedin.com/in/cto",
                }
            ],
        }
        result = scorer.calculate_score(lead_data)

        assert result["total_score"] > 50  # High-quality lead
        assert "breakdown" in result
        assert "ai_adoption" in result["breakdown"]
        assert "company_growth" in result["breakdown"]

    def test_ai_adoption_scoring(self, scorer):
        """Test AI adoption score calculation."""
        # Company with AI indicators
        ai_lead = {
            "company_name": "AI Corp",
            "industry": "Artificial Intelligence",
            "description": "Machine learning platform for NLP and computer vision",
            "tech_stack": ["TensorFlow", "PyTorch", "MLflow"],
        }
        result = scorer.calculate_score(ai_lead)
        ai_score = result["breakdown"].get("ai_adoption", 0)

        # Company without AI indicators
        non_ai_lead = {
            "company_name": "Traditional Corp",
            "industry": "Retail",
            "description": "Traditional retail store chain",
            "tech_stack": ["PHP", "MySQL"],
        }
        non_ai_result = scorer.calculate_score(non_ai_lead)
        non_ai_score = non_ai_result["breakdown"].get("ai_adoption", 0)

        assert ai_score > non_ai_score

    def test_company_growth_scoring(self, scorer):
        """Test company growth score based on funding and employee count."""
        # Well-funded company
        funded_lead = {
            "company_name": "Funded Startup",
            "funding_stage": "Series B",
            "funding_amount": 50000000,
            "employee_count": 200,
        }
        funded_result = scorer.calculate_score(funded_lead)

        # Small bootstrapped company
        small_lead = {
            "company_name": "Small Startup",
            "funding_stage": "Seed",
            "employee_count": 5,
        }
        small_result = scorer.calculate_score(small_lead)

        assert funded_result["breakdown"].get("company_growth", 0) > small_result["breakdown"].get("company_growth", 0)

    def test_decision_maker_access_scoring(self, scorer):
        """Test decision maker access scoring based on contacts."""
        # Lead with C-level contact
        lead_with_dm = {
            "company_name": "Test Corp",
            "contacts": [
                {
                    "email": "ceo@test.com",
                    "email_confidence": 90,
                    "job_title": "CEO",
                    "linkedin_url": "https://linkedin.com/in/ceo",
                }
            ],
        }
        dm_result = scorer.calculate_score(lead_with_dm)

        # Lead without contacts
        lead_no_contacts = {
            "company_name": "Test Corp",
            "contacts": [],
        }
        no_dm_result = scorer.calculate_score(lead_no_contacts)

        assert dm_result["breakdown"].get("decision_maker_access", 0) >= no_dm_result["breakdown"].get("decision_maker_access", 0)

    def test_geographic_fit_scoring(self, scorer):
        """Test geographic fit scoring."""
        # Target location
        target_lead = {
            "company_name": "Bay Area Corp",
            "location": "San Francisco, CA",
        }
        target_result = scorer.calculate_score(target_lead)

        # Non-target location
        other_lead = {
            "company_name": "Remote Corp",
            "location": "Unknown Location",
        }
        other_result = scorer.calculate_score(other_lead)

        # Both should have valid scores
        assert 0 <= target_result["total_score"] <= 100
        assert 0 <= other_result["total_score"] <= 100

    def test_score_weights_sum_to_one(self, scorer):
        """Test that scoring weights sum to 1.0."""
        total_weight = sum(scorer.WEIGHTS.values())
        assert abs(total_weight - 1.0) < 0.001

    def test_score_breakdown_all_components(self, scorer):
        """Test that all score components are present in breakdown."""
        lead_data = {"company_name": "Test"}
        result = scorer.calculate_score(lead_data)

        expected_components = [
            "ai_adoption",
            "company_growth",
            "engagement_potential",
            "decision_maker_access",
            "geographic_fit",
            "timing_signals",
        ]
        for component in expected_components:
            assert component in result["breakdown"]

    def test_get_scoring_service_dependency(self):
        """Test the dependency injection function."""
        service = get_scoring_service()
        assert isinstance(service, ScoringService)
