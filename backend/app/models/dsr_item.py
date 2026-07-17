"""DSR (Delhi Schedule of Rates) knowledge item model."""

from __future__ import annotations

from sqlalchemy import Index, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class DSRItem(UUIDMixin, TimestampMixin, Base):
    """CPWD Delhi Schedule of Rates item with structured knowledge.

    Each row represents a single DSR work item with its complete
    knowledge card data: official description, simplified explanation,
    materials, execution steps, and more.
    """

    __tablename__ = "dsr_items"

    # ─── Identification ───
    item_number: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True,
        comment="DSR item number, e.g. '5.33', '5.33.1'",
    )
    chapter: Mapped[str] = mapped_column(
        String(200), nullable=False, index=True,
        comment="DSR chapter name, e.g. 'Earth Work'",
    )

    # ─── Official Content ───
    official_description: Mapped[str] = mapped_column(
        Text, nullable=False,
        comment="Original DSR description text",
    )

    # ─── Human-Friendly Knowledge ───
    simple_title: Mapped[str | None] = mapped_column(
        String(300), nullable=True,
        comment="Short, human-friendly title",
    )
    summary: Mapped[str | None] = mapped_column(
        Text, nullable=True,
        comment="Plain English explanation of this work item",
    )
    purpose: Mapped[str | None] = mapped_column(
        Text, nullable=True,
        comment="Why this work is performed",
    )

    # ─── Structured JSON Fields ───
    where_used: Mapped[dict | None] = mapped_column(
        JSONB, nullable=True, server_default=text("'[]'::jsonb"),
        comment="Typical locations where this work applies",
    )
    materials: Mapped[dict | None] = mapped_column(
        JSONB, nullable=True, server_default=text("'[]'::jsonb"),
        comment="Materials used with grades and quantities",
    )
    execution_steps: Mapped[dict | None] = mapped_column(
        JSONB, nullable=True, server_default=text("'[]'::jsonb"),
        comment="Step-by-step execution procedure",
    )
    common_mistakes: Mapped[dict | None] = mapped_column(
        JSONB, nullable=True, server_default=text("'[]'::jsonb"),
        comment="Common mistakes and how to avoid them",
    )

    # ─── Technical Details ───
    measurement_unit: Mapped[str | None] = mapped_column(
        String(50), nullable=True,
        comment="Unit of measurement: Cum, Sqm, Rmt, etc.",
    )
    specification_reference: Mapped[str | None] = mapped_column(
        String(200), nullable=True,
        comment="Related CPWD specification clause",
    )

    # ─── Media ───
    images: Mapped[dict | None] = mapped_column(
        JSONB, nullable=True, server_default=text("'[]'::jsonb"),
        comment="Image URLs with captions",
    )
    future_video: Mapped[str | None] = mapped_column(
        String(500), nullable=True,
        comment="Placeholder for future video content URL",
    )

    # ─── Search ───
    search_keywords: Mapped[dict | None] = mapped_column(
        JSONB, nullable=True, server_default=text("'[]'::jsonb"),
        comment="Keywords for search indexing",
    )

    __table_args__ = (
        # GIN index on search_keywords for fast keyword containment queries
        Index(
            "ix_dsr_items_search_keywords",
            "search_keywords",
            postgresql_using="gin",
        ),
        # Full-text search index on description + title + summary
        Index(
            "ix_dsr_items_fulltext",
            text(
                "to_tsvector('english', "
                "coalesce(official_description, '') || ' ' || "
                "coalesce(simple_title, '') || ' ' || "
                "coalesce(summary, ''))"
            ),
            postgresql_using="gin",
        ),
        {"comment": "CPWD Delhi Schedule of Rates knowledge items"},
    )

    def __repr__(self) -> str:
        return f"<DSRItem {self.item_number}: {self.simple_title or self.official_description[:50]}>"
