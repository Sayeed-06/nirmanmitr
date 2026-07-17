"""Pydantic schemas for DSR item API requests and responses."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class DSRItemBase(BaseModel):
    """Base schema with shared DSR item fields."""

    item_number: str = Field(..., description="DSR item number, e.g. '5.33'")
    chapter: str = Field(..., description="Chapter name")
    official_description: str = Field(..., description="Official DSR description")
    simple_title: str | None = Field(None, description="Human-friendly title")
    summary: str | None = Field(None, description="Plain English explanation")
    purpose: str | None = Field(None, description="Why this work is done")
    where_used: list[str] | None = Field(default_factory=list)
    materials: list[dict] | None = Field(default_factory=list)
    execution_steps: list[str] | None = Field(default_factory=list)
    common_mistakes: list[str] | None = Field(default_factory=list)
    measurement_unit: str | None = None
    specification_reference: str | None = None
    images: list[dict] | None = Field(default_factory=list)
    future_video: str | None = None
    search_keywords: list[str] | None = Field(default_factory=list)


class DSRItemCreate(DSRItemBase):
    """Schema for creating a new DSR item."""

    pass


class DSRItemUpdate(BaseModel):
    """Schema for updating a DSR item (all fields optional)."""

    chapter: str | None = None
    official_description: str | None = None
    simple_title: str | None = None
    summary: str | None = None
    purpose: str | None = None
    where_used: list[str] | None = None
    materials: list[dict] | None = None
    execution_steps: list[str] | None = None
    common_mistakes: list[str] | None = None
    measurement_unit: str | None = None
    specification_reference: str | None = None
    images: list[dict] | None = None
    future_video: str | None = None
    search_keywords: list[str] | None = None


class DSRItemResponse(DSRItemBase):
    """Full DSR item response — the Knowledge Card data."""

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DSRItemSummary(BaseModel):
    """Compact DSR item for list views and search results."""

    id: uuid.UUID
    item_number: str
    chapter: str
    simple_title: str | None
    official_description: str
    measurement_unit: str | None
    is_populated: bool = Field(
        description="Whether knowledge fields are filled"
    )

    model_config = {"from_attributes": True}
