"""Lead scoring service with ML-based algorithm."""

from functools import lru_cache
from typing import Optional, Dict, Any, List

from app.utils.logging import get_logger

logger = get_logger(__name__)


class ScoringService:
    """Service for calculating lead scores based on multiple factors."""

    # Scoring weights (total = 100%)
    WEIGHTS = {
        "ai_adoption": 0.30,      # 30% - Tech stack, AI job postings
        "company_growth": 0.20,   # 20% - Funding, employee growth
        "engagement_potential": 0.20,  # 20% - Social activity, recent news
        "decision_maker_access": 0.15,  # 15% - Contact quality
        "geographic_fit": 0.10,   # 10% - Target markets
        "timing_signals": 0.05,   # 5% - Recent hiring, funding
    }

    # AI-related keywords for scoring
    AI_KEYWORDS = [
        "ai", "artificial intelligence", "machine learning", "ml",
        "deep learning", "neural network", "nlp", "natural language",
        "computer vision", "llm", "large language model", "gpt",
        "generative ai", "genai", "transformers", "pytorch", "tensorflow",
        "openai", "anthropic", "data science", "mlops",
    ]

    # Target industries
    TARGET_INDUSTRIES = [
        "software", "technology", "ai", "machine learning",
        "saas", "fintech", "healthtech", "enterprise software",
        "data analytics", "cloud computing",
    ]

    # Target locations
    TARGET_LOCATIONS = [
        "united states", "usa", "us", "canada",
        "united kingdom", "uk", "germany", "france",
        "netherlands", "sweden", "switzerland",
    ]

    # Funding stage scores
    FUNDING_SCORES = {
        "seed": 60,
        "series a": 80,
        "series b": 90,
        "series c": 95,
        "series d": 90,
        "series e": 85,
        "ipo": 70,
        "acquired": 50,
        "bootstrapped": 65,
    }

    def calculate_score(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate comprehensive lead score.

        Args:
            lead_data: Lead information dict

        Returns:
            Dict with total score and breakdown
        """
        scores = {
            "ai_adoption": self._score_ai_adoption(lead_data),
            "company_growth": self._score_company_growth(lead_data),
            "engagement_potential": self._score_engagement(lead_data),
            "decision_maker_access": self._score_decision_maker(lead_data),
            "geographic_fit": self._score_geographic(lead_data),
            "timing_signals": self._score_timing(lead_data),
        }

        # Calculate weighted total
        total_score = sum(
            scores[factor] * self.WEIGHTS[factor]
            for factor in scores
        )

        # Determine lead tier
        if total_score >= 85:
            tier = "hot"
        elif total_score >= 65:
            tier = "warm"
        elif total_score >= 40:
            tier = "cold"
        else:
            tier = "low_priority"

        result = {
            "total_score": round(total_score, 2),
            "tier": tier,
            "breakdown": {k: round(v, 2) for k, v in scores.items()},
            "weights": self.WEIGHTS,
            "recommendations": self._get_recommendations(scores, tier),
        }

        logger.info(
            "Lead scored",
            company=lead_data.get("company_name"),
            score=result["total_score"],
            tier=tier,
        )

        return result

    def _score_ai_adoption(self, data: Dict[str, Any]) -> float:
        """Score based on AI/tech adoption signals."""
        score = 50.0  # Base score

        # Check tech stack
        tech_stack = data.get("tech_stack", [])
        if isinstance(tech_stack, str):
            tech_stack = [tech_stack]

        ai_tech_count = sum(
            1 for tech in tech_stack
            if any(kw in tech.lower() for kw in self.AI_KEYWORDS)
        )
        score += min(ai_tech_count * 10, 30)  # Up to +30

        # Check description for AI keywords
        description = (data.get("description") or "").lower()
        ai_mentions = sum(1 for kw in self.AI_KEYWORDS if kw in description)
        score += min(ai_mentions * 5, 20)  # Up to +20

        # Industry bonus
        industry = (data.get("industry") or "").lower()
        if any(ind in industry for ind in ["ai", "machine learning", "artificial intelligence"]):
            score += 20

        return min(score, 100)

    def _score_company_growth(self, data: Dict[str, Any]) -> float:
        """Score based on company growth indicators."""
        score = 50.0  # Base score

        # Funding stage
        funding_stage = (data.get("funding_stage") or "").lower()
        for stage, stage_score in self.FUNDING_SCORES.items():
            if stage in funding_stage:
                score = max(score, stage_score)
                break

        # Funding amount
        funding_amount = data.get("funding_amount", 0) or 0
        if funding_amount > 100:  # $100M+
            score += 15
        elif funding_amount > 50:  # $50M+
            score += 10
        elif funding_amount > 10:  # $10M+
            score += 5

        # Employee count (sweet spot: 50-500)
        employee_count = data.get("employee_count", 0) or 0
        if 50 <= employee_count <= 500:
            score += 15
        elif 20 <= employee_count <= 1000:
            score += 10
        elif employee_count > 1000:
            score += 5

        return min(score, 100)

    def _score_engagement(self, data: Dict[str, Any]) -> float:
        """Score based on engagement potential."""
        score = 50.0  # Base score

        # LinkedIn presence
        if data.get("linkedin_url"):
            score += 15

        # Website presence
        if data.get("company_domain"):
            score += 10

        # Recent activity indicators
        if data.get("recent_news"):
            score += 15

        # Social media activity
        if data.get("social_activity_score"):
            score += min(data["social_activity_score"] / 10, 10)

        return min(score, 100)

    def _score_decision_maker(self, data: Dict[str, Any]) -> float:
        """Score based on decision maker accessibility."""
        score = 40.0  # Base score

        contacts = data.get("contacts", [])
        if not contacts:
            return score

        for contact in contacts:
            # Email quality
            email_confidence = contact.get("email_confidence", 0)
            if email_confidence >= 90:
                score += 20
            elif email_confidence >= 70:
                score += 15
            elif email_confidence >= 50:
                score += 10

            # Decision maker title
            title = (contact.get("job_title") or "").lower()
            if any(t in title for t in ["cto", "ceo", "coo", "vp", "director", "head"]):
                score += 20
            elif any(t in title for t in ["manager", "lead", "senior"]):
                score += 10

            # LinkedIn profile
            if contact.get("linkedin_url"):
                score += 5

        return min(score, 100)

    def _score_geographic(self, data: Dict[str, Any]) -> float:
        """Score based on geographic fit."""
        score = 50.0  # Base score

        location = (data.get("location") or "").lower()

        # Check target locations
        for target in self.TARGET_LOCATIONS:
            if target in location:
                score = 90.0
                break

        # Tech hub bonus
        tech_hubs = ["san francisco", "new york", "seattle", "boston", "austin", "denver", "toronto", "london"]
        for hub in tech_hubs:
            if hub in location:
                score += 10
                break

        return min(score, 100)

    def _score_timing(self, data: Dict[str, Any]) -> float:
        """Score based on timing signals."""
        score = 50.0  # Base score

        # Recent funding
        if data.get("recent_funding"):
            score += 25

        # Hiring signals
        if data.get("hiring_ai_roles"):
            score += 25

        # Recent news/press
        if data.get("recent_press"):
            score += 15

        # Data freshness
        if data.get("data_fresh"):
            score += 10

        return min(score, 100)

    def _get_recommendations(self, scores: Dict[str, float], tier: str) -> List[str]:
        """Generate recommendations based on scores."""
        recommendations = []

        if scores["decision_maker_access"] < 60:
            recommendations.append("Find and verify decision maker contacts")

        if scores["ai_adoption"] < 50:
            recommendations.append("Research company's AI/tech initiatives")

        if scores["timing_signals"] < 50:
            recommendations.append("Monitor for funding/hiring announcements")

        if tier == "hot":
            recommendations.append("Prioritize immediate outreach")
        elif tier == "warm":
            recommendations.append("Add to nurture campaign")
        elif tier == "cold":
            recommendations.append("Continue monitoring for timing signals")
        else:
            recommendations.append("Archive and review quarterly")

        return recommendations

    def calculate_ai_adoption_score(self, tech_stack: List[str], description: str) -> float:
        """
        Calculate just the AI adoption score.

        Args:
            tech_stack: List of technologies
            description: Company description

        Returns:
            AI adoption score (0-100)
        """
        return self._score_ai_adoption({
            "tech_stack": tech_stack,
            "description": description,
        })


# Singleton instance
_scoring_service: Optional[ScoringService] = None


@lru_cache
def get_scoring_service() -> ScoringService:
    """Get scoring service instance."""
    global _scoring_service
    if _scoring_service is None:
        _scoring_service = ScoringService()
    return _scoring_service
