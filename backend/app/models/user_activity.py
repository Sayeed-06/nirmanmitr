"""User activity tracking model."""

from __future__ import annotations

import uuid

from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class UserActivity(UUIDMixin, TimestampMixin, Base):
    """Tracks user activity for dashboard statistics and recent items.

    Records recently viewed DSR items and general usage statistics
    per user.
    """

    __tablename__ = "user_activities"

    user_id: Mapped[str] = mapped_column(
        String(200), nullable=False, index=True,
        comment="Clerk user ID",
    )
    activity_type: Mapped[str] = mapped_column(
        String(50), nullable=False,
        comment="Type: view_dsr, upload_boq, search",
    )
    reference_id: Mapped[str | None] = mapped_column(
        String(200), nullable=True,
        comment="ID of the referenced entity (DSR item number, project ID)",
    )
    reference_label: Mapped[str | None] = mapped_column(
        String(500), nullable=True,
        comment="Human-readable label for the referenced entity",
    )
