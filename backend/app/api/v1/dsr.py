"""DSR Knowledge Card endpoint."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.dependencies import DbSession, CurrentUser
from app.repositories.dsr_repository import DSRRepository
from app.services.dsr_service import DSRService
from app.schemas import DSRItemResponse

router = APIRouter()


@router.get("/dsr/{item_number}", response_model=DSRItemResponse)
async def get_dsr_item(
    item_number: str,
    db: DbSession,
    user: CurrentUser,
) -> DSRItemResponse:
    """Get the complete Knowledge Card for a DSR item.

    Returns all structured knowledge data: official description,
    simple explanation, materials, execution steps, etc.
    """
    dsr_repo = DSRRepository(db)
    service = DSRService(dsr_repo)
    item = await service.get_knowledge_card(item_number)

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No DSR item found for: {item_number}",
        )

    return DSRItemResponse.model_validate(item)


@router.get("/dsr/{item_number}/exists")
async def check_dsr_exists(
    item_number: str,
    db: DbSession,
) -> dict:
    """Quick existence check for a DSR item number (no auth required for parser)."""
    dsr_repo = DSRRepository(db)
    item = await dsr_repo.get_by_item_number(item_number)
    return {"exists": item is not None, "item_number": item_number}
