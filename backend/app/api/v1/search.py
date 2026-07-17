"""Search DSR database endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Query

from app.dependencies import DbSession, CurrentUser
from app.repositories.dsr_repository import DSRRepository
from app.services.dsr_service import DSRService
from app.schemas import DSRItemSummary
from app.schemas.project import SearchResponse

router = APIRouter()


@router.get("/search", response_model=SearchResponse)
async def search_dsr(
    db: DbSession,
    user: CurrentUser,
    q: str = Query(..., min_length=1, max_length=500, description="Search query"),
    chapter: str | None = Query(None, description="Filter by chapter"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> SearchResponse:
    """Search the DSR knowledge database.

    Supports searching by:
    - Item number (e.g., "5.33")
    - Description keywords
    - Material names
    - Chapter names

    Uses PostgreSQL full-text search for fast results.
    """
    dsr_repo = DSRRepository(db)
    service = DSRService(dsr_repo)

    offset = (page - 1) * page_size
    items, total = await service.search(
        q, chapter=chapter, offset=offset, limit=page_size
    )

    return SearchResponse(
        items=[
            DSRItemSummary(
                id=item.id,
                item_number=item.item_number,
                chapter=item.chapter,
                simple_title=item.simple_title,
                official_description=item.official_description,
                measurement_unit=item.measurement_unit,
                is_populated=bool(item.summary),
            )
            for item in items
        ],
        total=total,
        page=page,
        page_size=page_size,
        query=q,
    )


@router.get("/chapters")
async def list_chapters(
    db: DbSession,
    user: CurrentUser,
) -> dict:
    """List all DSR chapters."""
    dsr_repo = DSRRepository(db)
    service = DSRService(dsr_repo)
    chapters = await service.get_chapters()
    return {"chapters": chapters}
