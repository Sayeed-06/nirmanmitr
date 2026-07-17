"""Projects endpoints — list and detail views."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException, Query, status

from app.dependencies import DbSession, CurrentUser
from app.repositories.project_repository import ProjectRepository
from app.repositories.parsed_item_repository import ParsedItemRepository
from app.services.project_service import ProjectService
from app.schemas.project import (
    DashboardStats,
    ParsedItemResponse,
    ProjectDetailResponse,
    ProjectListResponse,
    ProjectResponse,
)

router = APIRouter()


@router.get("/projects", response_model=ProjectListResponse)
async def list_projects(
    db: DbSession,
    user: CurrentUser,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> ProjectListResponse:
    """List the current user's BOQ projects."""
    project_repo = ProjectRepository(db)
    parsed_item_repo = ParsedItemRepository(db)
    service = ProjectService(project_repo, parsed_item_repo)

    projects, total = await service.get_user_projects(
        user["user_id"], page=page, page_size=page_size
    )

    return ProjectListResponse(
        items=[ProjectResponse.model_validate(p) for p in projects],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/project/{project_id}", response_model=ProjectDetailResponse)
async def get_project(
    project_id: uuid.UUID,
    db: DbSession,
    user: CurrentUser,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    matched_only: bool | None = Query(None, description="Filter: True=matched, False=unmatched, None=all"),
) -> ProjectDetailResponse:
    """Get a project with its parsed BOQ items (paginated)."""
    project_repo = ProjectRepository(db)
    parsed_item_repo = ParsedItemRepository(db)
    service = ProjectService(project_repo, parsed_item_repo)

    try:
        project, items, total = await service.get_project_detail(
            project_id,
            user["user_id"],
            page=page,
            page_size=page_size,
            matched_only=matched_only,
        )
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    except PermissionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return ProjectDetailResponse(
        project=ProjectResponse.model_validate(project),
        items=[ParsedItemResponse.model_validate(i) for i in items],
        total_items=total,
        page=page,
        page_size=page_size,
    )


@router.get("/stats", response_model=DashboardStats)
async def get_stats(
    db: DbSession,
    user: CurrentUser,
) -> DashboardStats:
    """Get dashboard statistics for the current user."""
    project_repo = ProjectRepository(db)
    parsed_item_repo = ParsedItemRepository(db)
    service = ProjectService(project_repo, parsed_item_repo)
    stats = await service.get_dashboard_stats(user["user_id"])
    return DashboardStats(**stats)
