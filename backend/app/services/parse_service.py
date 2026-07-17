"""Parse service — orchestrates the full BOQ parsing pipeline."""

from __future__ import annotations

import uuid
import structlog
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.parsed_item import ParsedItem
from app.models.project import Project, ProjectStatus
from app.parser.base import ParsedRow
from app.parser.dsr_detector import DSRDetector
from app.parser.factory import create_parser
from app.parser.normalizer import normalize_rows
from app.repositories.dsr_repository import DSRRepository
from app.repositories.parsed_item_repository import ParsedItemRepository
from app.repositories.project_repository import ProjectRepository

logger = structlog.get_logger()


class ParseService:
    """Orchestrates the full BOQ parsing pipeline.

    Pipeline:
    1. Load file and select parser
    2. Extract raw rows from document
    3. Normalize and clean rows
    4. Detect DSR item numbers
    5. Store parsed items in database
    6. Update project statistics
    """

    def __init__(
        self,
        session: AsyncSession,
        project_repo: ProjectRepository,
        parsed_item_repo: ParsedItemRepository,
        dsr_repo: DSRRepository,
    ) -> None:
        self.session = session
        self.project_repo = project_repo
        self.parsed_item_repo = parsed_item_repo
        self.dsr_repo = dsr_repo

    async def parse_project(self, project_id: uuid.UUID) -> Project:
        """Run the full parsing pipeline for a project.

        Args:
            project_id: UUID of the project to parse.

        Returns:
            Updated Project with parsing results.

        Raises:
            ValueError: If project not found or already parsed.
        """
        # ─── Load Project ───
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise ValueError(f"Project not found: {project_id}")

        if project.status == ProjectStatus.COMPLETED:
            raise ValueError("Project already parsed")

        # ─── Update Status ───
        await self.project_repo.update(project, {"status": ProjectStatus.PARSING})

        try:
            # ─── Step 1: Parse File ───
            file_path = Path(project.file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")

            parser = create_parser(file_path)
            result = parser.parse(file_path)

            if not result.is_success:
                raise RuntimeError(result.error or "Parsing produced no results")

            logger.info(
                "parsing_raw_complete",
                project_id=str(project_id),
                raw_rows=len(result.rows),
            )

            # ─── Step 2: Normalize ───
            normalized = normalize_rows(result.rows)
            logger.info(
                "normalization_complete",
                project_id=str(project_id),
                normalized_rows=len(normalized),
            )

            # ─── Step 3: DSR Detection ───
            # Load known DSR item numbers for exact matching
            all_dsr = await self.dsr_repo.get_all(limit=100000)
            known_items = {item.item_number for item in all_dsr}
            detector = DSRDetector(known_items=known_items)

            # ─── Step 4: Create ParsedItem entities ───
            parsed_items: list[ParsedItem] = []
            match_count = 0
            unknown_count = 0

            for row in normalized:
                dsr_match = detector.detect(row.item_number, row.description)

                item = ParsedItem(
                    project_id=project_id,
                    order_index=row.order_index,
                    item_number=row.item_number,
                    description=row.description,
                    quantity=row.quantity,
                    unit=row.unit,
                    rate=row.rate,
                    amount=row.amount,
                    depth=row.depth,
                    dsr_item_number=dsr_match.detected_number,
                    dsr_match_confidence=dsr_match.confidence,
                    is_matched=dsr_match.confidence != "none",
                )
                parsed_items.append(item)

                if dsr_match.confidence != "none":
                    match_count += 1
                else:
                    unknown_count += 1

            # ─── Step 5: Bulk Insert ───
            await self.parsed_item_repo.bulk_create(parsed_items)

            # ─── Step 6: Update Project Stats ───
            await self.project_repo.update(project, {
                "status": ProjectStatus.COMPLETED,
                "total_items": len(parsed_items),
                "dsr_matches": match_count,
                "unknown_items": unknown_count,
            })

            logger.info(
                "parsing_complete",
                project_id=str(project_id),
                total=len(parsed_items),
                matches=match_count,
                unknown=unknown_count,
            )

            return project

        except Exception as e:
            await self.project_repo.update(project, {
                "status": ProjectStatus.FAILED,
                "error_message": str(e),
            })
            logger.error(
                "parsing_failed",
                project_id=str(project_id),
                error=str(e),
            )
            raise
