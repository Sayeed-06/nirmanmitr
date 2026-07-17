"""Project service — project management and statistics."""

from __future__ import annotations

import uuid

from app.repositories.project_repository import ProjectRepository
from app.repositories.parsed_item_repository import ParsedItemRepository
from app.models.project import Project
from app.models.parsed_item import ParsedItem


class ProjectService:
    """Business logic for BOQ projects."""

    def __init__(
        self,
        project_repo: ProjectRepository,
        parsed_item_repo: ParsedItemRepository,
    ) -> None:
        self.project_repo = project_repo
        self.parsed_item_repo = parsed_item_repo

    async def get_user_projects(
        self,
        user_id: str,
        *,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Project], int]:
        """Get paginated projects for a user."""
        offset = (page - 1) * page_size
        projects = await self.project_repo.get_user_projects(
            user_id, offset=offset, limit=page_size
        )
        total = await self.project_repo.count_user_projects(user_id)
        return projects, total

    async def get_project_detail(
        self,
        project_id: uuid.UUID,
        user_id: str,
        *,
        page: int = 1,
        page_size: int = 50,
        matched_only: bool | None = None,
    ) -> tuple[Project, list[ParsedItem], int]:
        """Get project details with paginated parsed items.

        Returns:
            Tuple of (project, items, total_items).
        """
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise ValueError(f"Project not found: {project_id}")
        if project.user_id != user_id:
            raise PermissionError("Access denied to this project")

        offset = (page - 1) * page_size
        items = await self.parsed_item_repo.get_project_items(
            project_id, offset=offset, limit=page_size, matched_only=matched_only
        )
        total = await self.parsed_item_repo.count_project_items(
            project_id, matched_only=matched_only
        )
        return project, items, total

    async def get_dashboard_stats(self, user_id: str) -> dict:
        """Get dashboard statistics for a user."""
        return await self.project_repo.get_user_stats(user_id)
