"""DSR item repository with full-text search and keyword filtering."""

from __future__ import annotations

from sqlalchemy import Select, func, or_, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dsr_item import DSRItem
from app.repositories.base import BaseRepository


class DSRRepository(BaseRepository[DSRItem]):
    """Repository for CPWD DSR knowledge items."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(DSRItem, session)

    async def get_by_item_number(self, item_number: str) -> DSRItem | None:
        """Fetch a DSR item by its exact item number."""
        normalized = item_number.strip()
        stmt = select(DSRItem).where(DSRItem.item_number == normalized)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_chapter(
        self,
        chapter: str,
        *,
        offset: int = 0,
        limit: int = 50,
    ) -> list[DSRItem]:
        """Fetch all items in a given chapter."""
        stmt = (
            select(DSRItem)
            .where(DSRItem.chapter == chapter)
            .order_by(DSRItem.item_number)
            .offset(offset)
            .limit(limit)
        )
        return await self._execute_query(stmt)

    async def search(
        self,
        query: str,
        *,
        chapter: str | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> list[DSRItem]:
        """Full-text search across DSR items.

        Searches official_description, simple_title, summary, and
        search_keywords using PostgreSQL full-text search.
        """
        stmt = select(DSRItem)

        if query:
            # Check if query looks like an item number (contains digits and dots)
            if any(c.isdigit() for c in query) and "." in query:
                stmt = stmt.where(DSRItem.item_number.ilike(f"%{query}%"))
            else:
                # Full-text search on combined text fields
                ts_query = func.plainto_tsquery("english", query)
                ts_vector = func.to_tsvector(
                    "english",
                    func.coalesce(DSRItem.official_description, "")
                    + " "
                    + func.coalesce(DSRItem.simple_title, "")
                    + " "
                    + func.coalesce(DSRItem.summary, ""),
                )
                stmt = stmt.where(ts_vector.op("@@")(ts_query))

        if chapter:
            stmt = stmt.where(DSRItem.chapter == chapter)

        stmt = stmt.order_by(DSRItem.item_number).offset(offset).limit(limit)
        return await self._execute_query(stmt)

    async def search_count(
        self,
        query: str,
        *,
        chapter: str | None = None,
    ) -> int:
        """Count search results for pagination."""
        stmt = select(func.count()).select_from(DSRItem)

        if query:
            if any(c.isdigit() for c in query) and "." in query:
                stmt = stmt.where(DSRItem.item_number.ilike(f"%{query}%"))
            else:
                ts_query = func.plainto_tsquery("english", query)
                ts_vector = func.to_tsvector(
                    "english",
                    func.coalesce(DSRItem.official_description, "")
                    + " "
                    + func.coalesce(DSRItem.simple_title, "")
                    + " "
                    + func.coalesce(DSRItem.summary, ""),
                )
                stmt = stmt.where(ts_vector.op("@@")(ts_query))

        if chapter:
            stmt = stmt.where(DSRItem.chapter == chapter)

        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def get_all_chapters(self) -> list[str]:
        """Get a distinct list of all chapters."""
        stmt = (
            select(DSRItem.chapter)
            .distinct()
            .order_by(DSRItem.chapter)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def item_numbers_exist(self, item_numbers: list[str]) -> dict[str, bool]:
        """Check which item numbers exist in the database.

        Returns a dict mapping item_number → exists (True/False).
        Used by the DSR detector to validate matches against the DB.
        """
        if not item_numbers:
            return {}

        stmt = select(DSRItem.item_number).where(
            DSRItem.item_number.in_(item_numbers)
        )
        result = await self.session.execute(stmt)
        existing = set(result.scalars().all())
        return {num: num in existing for num in item_numbers}

    async def upsert(self, data: dict) -> DSRItem:
        """Insert or update a DSR item by item_number."""
        item_number = data["item_number"]
        existing = await self.get_by_item_number(item_number)
        if existing:
            return await self.update(existing, data)
        entity = DSRItem(**data)
        return await self.create(entity)
