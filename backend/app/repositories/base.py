"""Generic base repository with common CRUD operations."""

from __future__ import annotations

import uuid
from typing import Any, Generic, TypeVar

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """Base repository providing generic async CRUD operations."""

    def __init__(self, model: type[ModelT], session: AsyncSession) -> None:
        self.model = model
        self.session = session

    async def get_by_id(self, entity_id: uuid.UUID) -> ModelT | None:
        """Fetch a single entity by primary key."""
        return await self.session.get(self.model, entity_id)

    async def get_all(
        self,
        *,
        offset: int = 0,
        limit: int = 50,
        order_by: Any | None = None,
    ) -> list[ModelT]:
        """Fetch all entities with pagination."""
        stmt = select(self.model)
        if order_by is not None:
            stmt = stmt.order_by(order_by)
        stmt = stmt.offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count(self, filters: list[Any] | None = None) -> int:
        """Count entities, optionally with filters."""
        stmt = select(func.count()).select_from(self.model)
        if filters:
            for f in filters:
                stmt = stmt.where(f)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def create(self, entity: ModelT) -> ModelT:
        """Insert a new entity."""
        self.session.add(entity)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    async def create_many(self, entities: list[ModelT]) -> list[ModelT]:
        """Insert multiple entities."""
        self.session.add_all(entities)
        await self.session.flush()
        return entities

    async def update(self, entity: ModelT, data: dict[str, Any]) -> ModelT:
        """Update an entity with the given data dict."""
        for key, value in data.items():
            if hasattr(entity, key):
                setattr(entity, key, value)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    async def delete(self, entity: ModelT) -> None:
        """Delete an entity."""
        await self.session.delete(entity)
        await self.session.flush()

    async def _execute_query(self, stmt: Select) -> list[ModelT]:
        """Execute a select statement and return results."""
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
