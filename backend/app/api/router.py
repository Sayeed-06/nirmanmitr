"""API router aggregation."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1 import health, upload, parse, projects, dsr, search, admin

api_router = APIRouter()

# Public
api_router.include_router(health.router, tags=["Health"])

# Authenticated
api_router.include_router(upload.router, tags=["Upload"])
api_router.include_router(parse.router, tags=["Parse"])
api_router.include_router(projects.router, tags=["Projects"])
api_router.include_router(dsr.router, tags=["DSR Knowledge"])
api_router.include_router(search.router, tags=["Search"])

# Admin
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
