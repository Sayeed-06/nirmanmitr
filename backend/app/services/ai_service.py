"""AI service for generating explanations for unmatched BOQ items."""

from __future__ import annotations

import json
import structlog
from google import genai
from google.genai import types
from app.config import settings

logger = structlog.get_logger()


class AIService:
    """Service to handle generative AI tasks for BOQ items."""

    def __init__(self) -> None:
        self.api_key = settings.gemini_api_key
        self.client = genai.Client(api_key=self.api_key) if self.api_key else None

    async def explain_boq_item(self, description: str, item_number: str | None = None) -> dict:
        """Use Gemini to explain an unmatched BOQ item and return structured data."""
        if not self.client:
            logger.warning("ai_service_disabled", reason="Missing GEMINI_API_KEY")
            return {
                "official_description": description,
                "simple_title": "AI Explanation Disabled",
                "summary": "The Gemini API key is not configured. Please add GEMINI_API_KEY to your environment to enable AI explanations.",
                "materials": [],
                "execution_steps": [],
                "common_mistakes": [],
                "where_used": [],
                "is_ai_generated": True
            }

        prompt = f"""You are an expert civil engineer and construction manager in India. 
I have a Bill of Quantities (BOQ) item that does not match a standard CPWD DSR code.
I need you to analyze the description and explain the work clearly.

Item Number: {item_number or 'N/A'}
Description: {description}

Provide your response strictly as a JSON object matching this schema:
{{
  "simple_title": "A short, readable title for this work (e.g., 'Brick Masonry Wall')",
  "summary": "A 2-3 sentence explanation of what this work is in BOTH simple English and Hindi (e.g., 'This involves laying bricks... यह काम ईंटों की चिनाई...').",
  "materials": [
    {{"name": "Material 1", "quantity": "Approx quantity/ratio if inferable"}},
    {{"name": "Material 2", "quantity": ""}}
  ],
  "execution_steps": [
    "Step 1...",
    "Step 2..."
  ],
  "common_mistakes": [
    "Mistake to avoid 1",
    "Mistake to avoid 2"
  ],
  "where_used": [
    "Location 1",
    "Location 2"
  ]
}}
"""

        try:
            logger.info("generating_ai_explanation", description=description[:50])
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.2,
                )
            )
            
            result = json.loads(response.text)
            result["official_description"] = description
            result["is_ai_generated"] = True
            
            return result
        except Exception as e:
            logger.error("ai_explanation_failed", error=str(e))
            return {
                "official_description": description,
                "simple_title": "AI Generation Failed",
                "summary": f"We encountered an error while generating the explanation: {str(e)}",
                "materials": [],
                "execution_steps": [],
                "common_mistakes": [],
                "where_used": [],
                "is_ai_generated": True
            }
