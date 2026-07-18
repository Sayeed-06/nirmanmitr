"""Dependency injection for FastAPI routes."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import async_session_factory


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield a database session per request."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_current_user(request: Request) -> dict:
    """Extract and verify the current user from Clerk JWT.

    In development mode without Clerk configured, returns a dev user.
    In production, validates the JWT token from the Authorization header.
    """
    from app.config import settings

    # Development fallback when Clerk is not configured
    if not settings.clerk_secret_key:
        return {
            "user_id": "dev_user_001",
            "email": "dev@nirmanmitr.com",
            "role": "admin",
        }

    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header",
        )

    token = auth_header.split(" ")[1]

    try:
        import jwt
        from jwt import PyJWKClient

        jwks_client = PyJWKClient(settings.clerk_jwks_url)
        signing_key = jwks_client.get_signing_key_from_jwt(token)

        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            options={"verify_exp": True},
        )

        return {
            "user_id": payload.get("sub", ""),
            "email": payload.get("email", ""),
            "role": payload.get("metadata", {}).get("role", "user"),
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {e!s}",
        )


async def require_admin(
    current_user: Annotated[dict, Depends(get_current_user)],
) -> dict:
    """Require admin role for access.
    NOTE: Relaxed for MVP so any authenticated user can add items to DB.
    """
    if not current_user.get("user_id"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    return current_user


# Type aliases for dependency injection
DbSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[dict, Depends(get_current_user)]
AdminUser = Annotated[dict, Depends(require_admin)]
