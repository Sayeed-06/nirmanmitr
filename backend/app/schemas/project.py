"""Pydantic schemas for projects and parsed items."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


# ─── Project Schemas ───


class ProjectResponse(BaseModel):
    """Project summary response."""

    id: uuid.UUID
    name: str
    file_type: str
    file_size: int
    total_items: int
    dsr_matches: int
    unknown_items: int
    status: str
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProjectListResponse(BaseModel):
    """Paginated project list."""

    items: list[ProjectResponse]
    total: int
    page: int
    page_size: int


# ─── Parsed Item Schemas ───


class ParsedItemResponse(BaseModel):
    """Individual parsed BOQ item."""

    id: uuid.UUID
    order_index: int
    item_number: str | None
    description: str
    quantity: Decimal | None
    unit: str | None
    rate: Decimal | None
    amount: Decimal | None
    depth: int
    dsr_item_number: str | None
    dsr_match_confidence: str
    is_matched: bool

    model_config = {"from_attributes": True}


class ProjectDetailResponse(BaseModel):
    """Project detail with parsed items (paginated)."""

    project: ProjectResponse
    items: list[ParsedItemResponse]
    total_items: int
    page: int
    page_size: int


# ─── Upload Schemas ───


class UploadResponse(BaseModel):
    """Response after file upload."""

    project_id: uuid.UUID
    name: str
    file_type: str
    file_size: int
    status: str
    message: str = "File uploaded successfully. Parsing will begin shortly."


class ParseResponse(BaseModel):
    """Response after parsing is triggered."""

    project_id: uuid.UUID
    status: str
    total_items: int
    dsr_matches: int
    unknown_items: int
    message: str


# ─── Search Schemas ───


class SearchRequest(BaseModel):
    """Search query parameters."""

    q: str = Field(..., min_length=1, max_length=500, description="Search query")
    chapter: str | None = Field(None, description="Filter by chapter")
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(20, ge=1, le=100, description="Items per page")


class SearchResponse(BaseModel):
    """Search results with pagination."""

    items: list["DSRItemSummary"]
    total: int
    page: int
    page_size: int
    query: str


# ─── Stats Schemas ───


class DashboardStats(BaseModel):
    """Dashboard statistics."""

    total_projects: int
    total_items: int
    total_matches: int
    total_unknown: int


# Circular import resolution
from app.schemas import DSRItemSummary  # noqa: E402

SearchResponse.model_rebuild()
