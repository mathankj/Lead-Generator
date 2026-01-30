"""Groq LLM client for AI-powered features."""

from functools import lru_cache
from typing import Optional, List, Dict, Any

from groq import Groq

from app.config import settings


class LLMClient:
    """Groq LLM client wrapper for conversational AI and text generation."""

    def __init__(self, api_key: str, model: str):
        """Initialize Groq client."""
        self.client = Groq(api_key=api_key)
        self.model = model

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1024,
        system_prompt: Optional[str] = None,
    ) -> str:
        """
        Send a chat completion request to Groq.

        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            system_prompt: Optional system prompt to prepend

        Returns:
            Generated response text
        """
        # Prepend system prompt if provided
        all_messages = []
        if system_prompt:
            all_messages.append({"role": "system", "content": system_prompt})
        all_messages.extend(messages)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=all_messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        return response.choices[0].message.content

    def generate_lead_insights(self, lead_data: Dict[str, Any]) -> str:
        """
        Generate AI insights about a lead.

        Args:
            lead_data: Dictionary containing lead information

        Returns:
            Generated insights text
        """
        prompt = f"""Analyze this company as a potential lead for AI services:

Company: {lead_data.get('company_name', 'Unknown')}
Industry: {lead_data.get('industry', 'Unknown')}
Size: {lead_data.get('employee_count', 'Unknown')} employees
Location: {lead_data.get('location', 'Unknown')}
Funding: {lead_data.get('funding_stage', 'Unknown')}
Tech Stack: {lead_data.get('tech_stack', 'Unknown')}

Provide:
1. Brief assessment of AI adoption potential
2. Key pain points they might have
3. Suggested approach for outreach
4. Risk factors to consider

Keep response concise (under 200 words)."""

        return self.chat(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=500,
        )

    def generate_outreach_message(
        self,
        lead_data: Dict[str, Any],
        contact_data: Dict[str, Any],
        tone: str = "professional",
    ) -> str:
        """
        Generate a personalized outreach message.

        Args:
            lead_data: Company information
            contact_data: Contact person information
            tone: Message tone (professional, casual, formal)

        Returns:
            Generated outreach message
        """
        prompt = f"""Write a personalized outreach email for:

Contact: {contact_data.get('first_name', '')} {contact_data.get('last_name', '')}
Title: {contact_data.get('job_title', 'Decision Maker')}
Company: {lead_data.get('company_name', 'their company')}
Industry: {lead_data.get('industry', '')}

We are TechJays, an AI solutions company.
Tone: {tone}
Length: 3-4 sentences max
Include a soft call-to-action.

Generate ONLY the email body, no subject line."""

        return self.chat(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            max_tokens=300,
        )

    def is_healthy(self) -> bool:
        """Check if Groq API is accessible."""
        try:
            # Simple test call
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=5,
            )
            return response.choices[0].message.content is not None
        except Exception:
            return False


# Singleton instance
_llm_client: Optional[LLMClient] = None


@lru_cache
def get_llm_client() -> LLMClient:
    """Get the LLM client instance."""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient(
            api_key=settings.groq_api_key,
            model=settings.groq_model,
        )
    return _llm_client
