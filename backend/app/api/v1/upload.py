"""Upload BOQ endpoint."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, UploadFile, File, status

from app.dependencies import DbSession, CurrentUser
from app.repositories.project_repository import ProjectRepository
from app.services.upload_service import UploadService
from app.schemas.project import UploadResponse

router = APIRouter()


@router.post("/upload", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_boq(
    db: DbSession,
    user: CurrentUser,
    file: UploadFile = File(..., description="BOQ file (PDF, Excel, or CSV)"),
) -> UploadResponse:
    """Upload a BOQ document.

    Validates the file, stores it, and creates a project.
    Parsing must be triggered separately via POST /parse/{project_id}.
    """
    try:
        project_repo = ProjectRepository(db)
        service = UploadService(project_repo)
        project = await service.upload_boq(file, user["user_id"])

        return UploadResponse(
            project_id=project.id,
            name=project.name,
            file_type=project.file_type,
            file_size=project.file_size,
            status=project.status,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
