"""FastAPI application factory and startup configuration."""

from __future__ import annotations

import structlog
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.config import settings
from app.api.router import api_router
from app.models.base import init_db


logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application startup and shutdown events."""
    logger.info(
        "starting_application",
        app_name=settings.app_name,
        environment=settings.environment,
    )
    await init_db()
    yield
    logger.info("shutting_down_application")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    application = FastAPI(
        title=settings.app_name,
        description=(
            "BOQ Analysis & CPWD DSR Knowledge Platform. "
            "Upload BOQs, parse items, and access structured knowledge cards."
        ),
        version="1.0.0",
        docs_url="/api/docs" if not settings.is_production else None,
        redoc_url="/api/redoc" if not settings.is_production else None,
        openapi_url="/api/openapi.json" if not settings.is_production else None,
        lifespan=lifespan,
    )

    # ─── CORS ───
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_origin_regex=r"https://.*\.vercel\.app",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ─── Trusted Host (production) ───
    if settings.is_production:
        application.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*"], # Allow Render to handle routing
        )

    # ─── Routes ───
    application.include_router(api_router, prefix="/api/v1")

    return application


app = create_app()
