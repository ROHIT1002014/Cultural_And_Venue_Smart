from typing import Any, Generic, Sequence, Type, TypeVar
from uuid import UUID
from sqlalchemy import select, func, delete as sa_delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.repositories.base import IGenericRepository

DomainEntityT = TypeVar("DomainEntityT")
ORMModelT = TypeVar("ORMModelT")


class SQLAlchemyGenericRepository(IGenericRepository[DomainEntityT], Generic[DomainEntityT, ORMModelT]):
    """Generic async repository base class converting cleanly between SQLAlchemy ORM rows and pure Domain Entities."""

    def __init__(self, session: AsyncSession, model_class: Type[ORMModelT]):
        self.session = session
        self.model_class = model_class

    def _to_domain(self, orm_obj: ORMModelT | None) -> DomainEntityT | None:
        """Convert an ORM model instance into a pure domain entity class. Must be overridden or mapped dynamically."""
        raise NotImplementedError

    def _to_orm(self, domain_entity: DomainEntityT) -> ORMModelT:
        """Convert a pure domain entity into an ORM model instance. Must be overridden or mapped dynamically."""
        raise NotImplementedError

    async def get_by_id(self, entity_id: UUID) -> DomainEntityT | None:
        result = await self.session.execute(select(self.model_class).where(getattr(self.model_class, "id") == entity_id))
        orm_obj = result.scalar_one_or_none()
        return self._to_domain(orm_obj) if orm_obj else None

    async def get_all(self, skip: int = 0, limit: int = 100, **filters: Any) -> Sequence[DomainEntityT]:
        stmt = select(self.model_class)
        for key, value in filters.items():
            if hasattr(self.model_class, key) and value is not None:
                stmt = stmt.where(getattr(self.model_class, key) == value)
        stmt = stmt.offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return [self._to_domain(row) for row in result.scalars().all() if self._to_domain(row) is not None]

    async def create(self, entity: DomainEntityT) -> DomainEntityT:
        orm_obj = self._to_orm(entity)
        self.session.add(orm_obj)
        await self.session.commit()
        await self.session.refresh(orm_obj)
        domain = self._to_domain(orm_obj)
        assert domain is not None
        return domain

    async def update(self, entity: DomainEntityT) -> DomainEntityT:
        orm_obj = self._to_orm(entity)
        merged = await self.session.merge(orm_obj)
        await self.session.commit()
        await self.session.refresh(merged)
        domain = self._to_domain(merged)
        assert domain is not None
        return domain

    async def delete(self, entity_id: UUID) -> bool:
        stmt = sa_delete(self.model_class).where(getattr(self.model_class, "id") == entity_id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0

    async def count(self, **filters: Any) -> int:
        stmt = select(func.count()).select_from(self.model_class)
        for key, value in filters.items():
            if hasattr(self.model_class, key) and value is not None:
                stmt = stmt.where(getattr(self.model_class, key) == value)
        result = await self.session.execute(stmt)
        return int(result.scalar() or 0)
