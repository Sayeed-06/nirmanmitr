"""Admin CRUD endpoints for DSR items."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException, Query, status

from app.dependencies import DbSession, AdminUser
from app.models.dsr_item import DSRItem
from app.repositories.dsr_repository import DSRRepository
from app.schemas import DSRItemCreate, DSRItemResponse, DSRItemSummary, DSRItemUpdate

router = APIRouter()


@router.get("/dsr", response_model=list[DSRItemSummary])
async def list_dsr_items(
    db: DbSession,
    admin: AdminUser,
    chapter: str | None = Query(None),
    q: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
) -> list[DSRItemSummary]:
    """List all DSR items (admin only)."""
    repo = DSRRepository(db)
    offset = (page - 1) * page_size

    if q:
        items = await repo.search(q, chapter=chapter, offset=offset, limit=page_size)
    elif chapter:
        items = await repo.get_by_chapter(chapter, offset=offset, limit=page_size)
    else:
        items = await repo.get_all(offset=offset, limit=page_size)

    return [
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
    ]


@router.post("/dsr", response_model=DSRItemResponse, status_code=status.HTTP_201_CREATED)
async def create_dsr_item(
    data: DSRItemCreate,
    db: DbSession,
    admin: AdminUser,
) -> DSRItemResponse:
    """Create a new DSR item (admin only)."""
    repo = DSRRepository(db)

    existing = await repo.get_by_item_number(data.item_number)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"DSR item {data.item_number} already exists",
        )

    item = DSRItem(**data.model_dump())
    created = await repo.create(item)
    return DSRItemResponse.model_validate(created)


@router.get("/dsr/{item_id}", response_model=DSRItemResponse)
async def get_dsr_item_admin(
    item_id: uuid.UUID,
    db: DbSession,
    admin: AdminUser,
) -> DSRItemResponse:
    """Get a DSR item by ID (admin only)."""
    repo = DSRRepository(db)
    item = await repo.get_by_id(item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="DSR item not found")
    return DSRItemResponse.model_validate(item)


@router.patch("/dsr/{item_id}", response_model=DSRItemResponse)
async def update_dsr_item(
    item_id: uuid.UUID,
    data: DSRItemUpdate,
    db: DbSession,
    admin: AdminUser,
) -> DSRItemResponse:
    """Update a DSR item (admin only)."""
    repo = DSRRepository(db)
    item = await repo.get_by_id(item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="DSR item not found")

    update_data = data.model_dump(exclude_unset=True)
    updated = await repo.update(item, update_data)
    return DSRItemResponse.model_validate(updated)


@router.delete("/dsr/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dsr_item(
    item_id: uuid.UUID,
    db: DbSession,
    admin: AdminUser,
) -> None:
    """Delete a DSR item (admin only)."""
    repo = DSRRepository(db)
    item = await repo.get_by_id(item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="DSR item not found")
    await repo.delete(item)


@router.get("/chapters")
async def list_chapters_admin(
    db: DbSession,
    admin: AdminUser,
) -> dict:
    """List all chapters (admin only)."""
    repo = DSRRepository(db)
    chapters = await repo.get_all_chapters()
    return {"chapters": chapters}
