"""Project repository for BOQ project management."""

from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.repositories.base import BaseRepository


class ProjectRepository(BaseRepository[Project]):
    """Repository for BOQ project entities."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Project, session)

    async def get_user_projects(
        self,
        user_id: str,
        *,
        offset: int = 0,
        limit: int = 20,
    ) -> list[Project]:
        """Fetch projects belonging to a specific user."""
        stmt = (
            select(Project)
            .where(Project.user_id == user_id)
            .order_by(Project.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return await self._execute_query(stmt)

    async def count_user_projects(self, user_id: str) -> int:
        """Count total projects for a user."""
        stmt = (
            select(func.count())
            .select_from(Project)
            .where(Project.user_id == user_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def get_user_stats(self, user_id: str) -> dict:
        """Get aggregate statistics for a user's dashboard."""
        stmt = (
            select(
                func.count().label("total_projects"),
                func.coalesce(func.sum(Project.total_items), 0).label("total_items"),
                func.coalesce(func.sum(Project.dsr_matches), 0).label("total_matches"),
                func.coalesce(func.sum(Project.unknown_items), 0).label("total_unknown"),
            )
            .select_from(Project)
            .where(Project.user_id == user_id)
            .where(Project.status == "completed")
        )
        result = await self.session.execute(stmt)
        row = result.one()
        return {
            "total_projects": row.total_projects,
            "total_items": row.total_items,
            "total_matches": row.total_matches,
            "total_unknown": row.total_unknown,
        }
