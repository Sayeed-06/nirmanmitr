"""Health check endpoint."""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check() -> dict:
    """Application health check."""
    return {"status": "healthy", "service": "nirmanmitr-api", "version": "1.0.0"}
