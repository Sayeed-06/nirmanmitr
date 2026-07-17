"""Parse BOQ endpoint."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException, status

from app.dependencies import DbSession, CurrentUser
from app.repositories.dsr_repository import DSRRepository
from app.repositories.parsed_item_repository import ParsedItemRepository
from app.repositories.project_repository import ProjectRepository
from app.services.parse_service import ParseService
from app.schemas.project import ParseResponse

router = APIRouter()


@router.post("/parse/{project_id}", response_model=ParseResponse)
async def parse_boq(
    project_id: uuid.UUID,
    db: DbSession,
    user: CurrentUser,
) -> ParseResponse:
    """Trigger parsing of an uploaded BOQ.

    Runs the full pipeline: parse → normalize → detect DSR → store results.
    """
    try:
        project_repo = ProjectRepository(db)
        parsed_item_repo = ParsedItemRepository(db)
        dsr_repo = DSRRepository(db)

        service = ParseService(db, project_repo, parsed_item_repo, dsr_repo)
        project = await service.parse_project(project_id)

        return ParseResponse(
            project_id=project.id,
            status=project.status,
            total_items=project.total_items,
            dsr_matches=project.dsr_matches,
            unknown_items=project.unknown_items,
            message=f"Parsed {project.total_items} items. "
                    f"{project.dsr_matches} DSR matches, "
                    f"{project.unknown_items} unknown items.",
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )
