"""Parsed BOQ item model — individual rows extracted from a BOQ document."""

from __future__ import annotations

import uuid
from decimal import Decimal

from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class ParsedItem(UUIDMixin, TimestampMixin, Base):
    """A single parsed line item from a BOQ document.

    Preserves the original BOQ data (item number, description, quantity,
    unit, rate, amount) along with the detected DSR reference and
    parent-child hierarchy.
    """

    __tablename__ = "parsed_items"

    # ─── Parent Project ───
    project_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="FK to the parent project",
    )

    # ─── BOQ Data ───
    order_index: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0,
        comment="Original position in BOQ for preserving order",
    )
    item_number: Mapped[str | None] = mapped_column(
        String(100), nullable=True,
        comment="Item number from the BOQ document",
    )
    description: Mapped[str] = mapped_column(
        Text, nullable=False, default="",
        comment="BOQ item description text",
    )
    quantity: Mapped[Decimal | None] = mapped_column(
        Numeric(precision=18, scale=4), nullable=True,
        comment="Quantity from BOQ",
    )
    unit: Mapped[str | None] = mapped_column(
        String(50), nullable=True,
        comment="Unit of measurement from BOQ",
    )
    rate: Mapped[Decimal | None] = mapped_column(
        Numeric(precision=18, scale=2), nullable=True,
        comment="Rate per unit from BOQ",
    )
    amount: Mapped[Decimal | None] = mapped_column(
        Numeric(precision=18, scale=2), nullable=True,
        comment="Total amount (qty × rate) from BOQ",
    )

    # ─── Hierarchy ───
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("parsed_items.id", ondelete="SET NULL"),
        nullable=True,
        comment="FK to parent item for hierarchy",
    )
    depth: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0,
        comment="Nesting level: 0 = root, 1 = child, etc.",
    )

    # ─── DSR Detection Result ───
    dsr_item_number: Mapped[str | None] = mapped_column(
        String(50), nullable=True, index=True,
        comment="Detected DSR item number reference",
    )
    dsr_match_confidence: Mapped[str] = mapped_column(
        String(20), nullable=False, default="none",
        comment="Match confidence: exact, partial, none",
    )
    is_matched: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False,
        comment="Quick boolean flag for DSR match filtering",
    )

    # ─── Relationships ───
    project: Mapped["Project"] = relationship(
        "Project",
        back_populates="parsed_items",
    )
    parent: Mapped["ParsedItem | None"] = relationship(
        "ParsedItem",
        remote_side="ParsedItem.id",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        match_str = f"→ DSR {self.dsr_item_number}" if self.is_matched else "(unmatched)"
        return f"<ParsedItem #{self.order_index}: {self.item_number} {match_str}>"


# Avoid circular import
from app.models.project import Project  # noqa: E402, F811
