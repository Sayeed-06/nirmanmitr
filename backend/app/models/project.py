"""Project model — represents an uploaded BOQ document."""

from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, String, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class ProjectStatus:
    """Project processing status constants."""

    UPLOADING = "uploading"
    PARSING = "parsing"
    COMPLETED = "completed"
    FAILED = "failed"


class Project(UUIDMixin, TimestampMixin, Base):
    """An uploaded BOQ document that becomes a project.

    Each uploaded BOQ file (PDF/Excel/CSV) is tracked as a project
    with its parsing status and match statistics.
    """

    __tablename__ = "projects"

    # ─── Ownership ───
    user_id: Mapped[str] = mapped_column(
        String(200), nullable=False, index=True,
        comment="Clerk user ID or dev user ID",
    )

    # ─── File Information ───
    name: Mapped[str] = mapped_column(
        String(500), nullable=False,
        comment="Original filename, e.g. 'Hospital BOQ.pdf'",
    )
    file_path: Mapped[str] = mapped_column(
        String(1000), nullable=False,
        comment="Storage path for the uploaded file",
    )
    file_type: Mapped[str] = mapped_column(
        String(10), nullable=False,
        comment="File extension: pdf, xlsx, csv",
    )
    file_size: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0,
        comment="File size in bytes",
    )

    # ─── Parsing Statistics ───
    total_items: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0,
        comment="Total number of parsed line items",
    )
    dsr_matches: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0,
        comment="Items with a DSR match",
    )
    unknown_items: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0,
        comment="Items without a DSR match",
    )

    # ─── Status ───
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=ProjectStatus.UPLOADING,
        comment="Processing status: uploading, parsing, completed, failed",
    )
    error_message: Mapped[str | None] = mapped_column(
        Text, nullable=True,
        comment="Error details if parsing failed",
    )

    # ─── Relationships ───
    parsed_items: Mapped[list["ParsedItem"]] = relationship(
        "ParsedItem",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Project {self.name} ({self.status})>"


# Import here to avoid circular imports
from app.models.parsed_item import ParsedItem  # noqa: E402
