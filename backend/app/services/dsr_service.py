"""DSR service — knowledge card lookup and search."""

from __future__ import annotations

from app.repositories.dsr_repository import DSRRepository
from app.models.dsr_item import DSRItem


class DSRService:
    """Business logic for DSR knowledge items."""

    def __init__(self, dsr_repo: DSRRepository) -> None:
        self.dsr_repo = dsr_repo

    async def get_knowledge_card(self, item_number: str) -> DSRItem | None:
        """Fetch the complete knowledge card for a DSR item."""
        return await self.dsr_repo.get_by_item_number(item_number)

    async def search(
        self,
        query: str,
        *,
        chapter: str | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[DSRItem], int]:
        """Search DSR database with pagination.

        Returns:
            Tuple of (items, total_count).
        """
        items = await self.dsr_repo.search(
            query, chapter=chapter, offset=offset, limit=limit
        )
        total = await self.dsr_repo.search_count(query, chapter=chapter)
        return items, total

    async def get_chapters(self) -> list[str]:
        """Get all available DSR chapters."""
        return await self.dsr_repo.get_all_chapters()
