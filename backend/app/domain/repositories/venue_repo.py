from abc import abstractmethod
from collections.abc import Sequence
from uuid import UUID

from app.domain.entities.venue import PointOfInterest, Venue
from app.domain.repositories.base import IGenericRepository


class IVenueRepository(IGenericRepository[Venue]):
    """Repository interface for Venue entity."""

    @abstractmethod
    async def get_by_name(self, name: str) -> Venue | None:
        """Find a venue by its exact name."""
        pass


class IPOIRepository(IGenericRepository[PointOfInterest]):
    """Repository interface for Point of Interest navigation markers."""

    @abstractmethod
    async def get_by_venue_and_category(
        self, venue_id: UUID, category: str | None = None, accessible_only: bool = False
    ) -> Sequence[PointOfInterest]:
        """Retrieve POIs filtered by category and wheelchair accessibility within a venue."""
        pass
