"""AI explanation endpoint."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.dependencies import CurrentUser
from app.services.ai_service import AIService
from app.schemas import AIExplainRequest, AIExplainResponse

router = APIRouter()


@router.post("/ai/explain", response_model=AIExplainResponse)
async def explain_item(
    request: AIExplainRequest,
    user: CurrentUser,
) -> AIExplainResponse:
    """Generate an AI explanation for an unmatched BOQ item."""
    service = AIService()
    result = await service.explain_boq_item(request.description, request.item_number)
    
    return AIExplainResponse.model_validate(result)
