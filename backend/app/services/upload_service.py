"""Upload service — file validation, storage, and project creation."""

from __future__ import annotations

import uuid
import structlog
from pathlib import Path

from fastapi import UploadFile

from app.config import settings
from app.models.project import Project, ProjectStatus
from app.repositories.project_repository import ProjectRepository

logger = structlog.get_logger()


class UploadService:
    """Handles file upload validation, storage, and project creation."""

    def __init__(self, project_repo: ProjectRepository) -> None:
        self.project_repo = project_repo

    async def upload_boq(
        self,
        file: UploadFile,
        user_id: str,
    ) -> Project:
        """Validate and store an uploaded BOQ file, create a project.

        Args:
            file: The uploaded file from the request.
            user_id: The authenticated user's ID.

        Returns:
            The created Project entity.

        Raises:
            ValueError: If validation fails.
        """
        # ─── Validation ───
        if not file.filename:
            raise ValueError("Filename is required")

        ext = Path(file.filename).suffix.lower()
        if ext not in settings.allowed_ext_list:
            raise ValueError(
                f"Unsupported file type: {ext}. "
                f"Allowed: {', '.join(settings.allowed_ext_list)}"
            )

        # Read file content
        content = await file.read()
        file_size = len(content)

        if file_size > settings.max_upload_bytes:
            raise ValueError(
                f"File too large: {file_size / 1024 / 1024:.1f}MB. "
                f"Maximum: {settings.max_upload_size_mb}MB"
            )

        if file_size == 0:
            raise ValueError("File is empty")

        # ─── Storage ───
        file_id = str(uuid.uuid4())
        storage_path = await self._store_file(content, file_id, ext)

        # ─── Create Project ───
        project = Project(
            user_id=user_id,
            name=file.filename,
            file_path=storage_path,
            file_type=ext.lstrip("."),
            file_size=file_size,
            status=ProjectStatus.UPLOADING,
        )

        project = await self.project_repo.create(project)
        logger.info(
            "boq_uploaded",
            project_id=str(project.id),
            filename=file.filename,
            size=file_size,
            type=ext,
        )

        return project

    async def _store_file(
        self,
        content: bytes,
        file_id: str,
        extension: str,
    ) -> str:
        """Store file to local filesystem.

        In production, this would use Supabase Storage.
        The storage abstraction makes switching seamless.
        """
        upload_dir = Path("uploads")
        upload_dir.mkdir(exist_ok=True)

        file_path = upload_dir / f"{file_id}{extension}"
        file_path.write_bytes(content)

        return str(file_path)
