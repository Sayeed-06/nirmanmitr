"""Parsed item repository for individual BOQ line items."""

from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.parsed_item import ParsedItem
from app.repositories.base import BaseRepository


class ParsedItemRepository(BaseRepository[ParsedItem]):
    """Repository for parsed BOQ items."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(ParsedItem, session)

    async def get_project_items(
        self,
        project_id: uuid.UUID,
        *,
        offset: int = 0,
        limit: int = 50,
        matched_only: bool | None = None,
    ) -> list[ParsedItem]:
        """Fetch parsed items for a project with optional match filtering."""
        stmt = (
            select(ParsedItem)
            .where(ParsedItem.project_id == project_id)
        )

        if matched_only is True:
            stmt = stmt.where(ParsedItem.is_matched.is_(True))
        elif matched_only is False:
            stmt = stmt.where(ParsedItem.is_matched.is_(False))

        stmt = (
            stmt.order_by(ParsedItem.order_index)
            .offset(offset)
            .limit(limit)
        )
        return await self._execute_query(stmt)

    async def count_project_items(
        self,
        project_id: uuid.UUID,
        *,
        matched_only: bool | None = None,
    ) -> int:
        """Count items in a project with optional match filtering."""
        stmt = (
            select(func.count())
            .select_from(ParsedItem)
            .where(ParsedItem.project_id == project_id)
        )
        if matched_only is True:
            stmt = stmt.where(ParsedItem.is_matched.is_(True))
        elif matched_only is False:
            stmt = stmt.where(ParsedItem.is_matched.is_(False))

        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def bulk_create(self, items: list[ParsedItem]) -> list[ParsedItem]:
        """Efficiently insert many parsed items at once."""
        self.session.add_all(items)
        await self.session.flush()
        return items
