from abc import ABC, abstractmethod
from typing import Any, Generic, Sequence, TypeVar
from uuid import UUID

T = TypeVar("T")


class IGenericRepository(ABC, Generic[T]):
    """Abstract generic repository interface defining core async CRUD operations."""

    @abstractmethod
    async def get_by_id(self, entity_id: UUID) -> T | None:
        """Retrieve an entity by its unique UUID."""
        pass

    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100, **filters: Any) -> Sequence[T]:
        """Retrieve a list of entities matching optional filter parameters."""
        pass

    @abstractmethod
    async def create(self, entity: T) -> T:
        """Persist a new domain entity."""
        pass

    @abstractmethod
    async def update(self, entity: T) -> T:
        """Update an existing domain entity."""
        pass

    @abstractmethod
    async def delete(self, entity_id: UUID) -> bool:
        """Delete an entity by its UUID. Return true if deleted."""
        pass

    @abstractmethod
    async def count(self, **filters: Any) -> int:
        """Return total count of entities matching filter parameters."""
        pass
