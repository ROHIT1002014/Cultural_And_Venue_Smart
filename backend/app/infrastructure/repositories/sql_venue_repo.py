from typing import Sequence
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.entities.venue import Venue, PointOfInterest
from app.domain.repositories.venue_repo import IVenueRepository, IPOIRepository
from app.infrastructure.models.venue_model import VenueORM, PointOfInterestORM
from app.infrastructure.repositories.generic_repo import SQLAlchemyGenericRepository


class SQLVenueRepository(SQLAlchemyGenericRepository[Venue, VenueORM], IVenueRepository):
    """Async repository for Venue entity."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, VenueORM)

    def _to_domain(self, orm_obj: VenueORM | None) -> Venue | None:
        if not orm_obj:
            return None
        return Venue(
            id=orm_obj.id,
            name=orm_obj.name,
            address=orm_obj.address,
            boundary_coordinates=orm_obj.boundary_coordinates,
            total_capacity=orm_obj.total_capacity,
            current_occupancy=orm_obj.current_occupancy,
            created_at=orm_obj.created_at,
            updated_at=orm_obj.updated_at,
        )

    def _to_orm(self, domain_entity: Venue) -> VenueORM:
        return VenueORM(
            id=domain_entity.id,
            name=domain_entity.name,
            address=domain_entity.address,
            boundary_coordinates=domain_entity.boundary_coordinates,
            total_capacity=domain_entity.total_capacity,
            current_occupancy=domain_entity.current_occupancy,
            created_at=domain_entity.created_at,
            updated_at=domain_entity.updated_at,
        )

    async def get_by_name(self, name: str) -> Venue | None:
        stmt = select(VenueORM).where(VenueORM.name == name)
        result = await self.session.execute(stmt)
        return self._to_domain(result.scalar_one_or_none())


class SQLPOIRepository(SQLAlchemyGenericRepository[PointOfInterest, PointOfInterestORM], IPOIRepository):
    """Async repository for PointOfInterest."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, PointOfInterestORM)

    def _to_domain(self, orm_obj: PointOfInterestORM | None) -> PointOfInterest | None:
        if not orm_obj:
            return None
        return PointOfInterest(
            id=orm_obj.id,
            venue_id=orm_obj.venue_id,
            name=orm_obj.name,
            category=orm_obj.category,
            coordinates=orm_obj.coordinates,
            floor_level=orm_obj.floor_level,
            is_accessible=orm_obj.is_accessible,
            created_at=orm_obj.created_at,
        )

    def _to_orm(self, domain_entity: PointOfInterest) -> PointOfInterestORM:
        return PointOfInterestORM(
            id=domain_entity.id,
            venue_id=domain_entity.venue_id,
            name=domain_entity.name,
            category=domain_entity.category,
            coordinates=domain_entity.coordinates,
            floor_level=domain_entity.floor_level,
            is_accessible=domain_entity.is_accessible,
            created_at=domain_entity.created_at,
        )

    async def get_by_venue_and_category(
        self, venue_id: UUID, category: str | None = None, accessible_only: bool = False
    ) -> Sequence[PointOfInterest]:
        stmt = select(PointOfInterestORM).where(PointOfInterestORM.venue_id == venue_id)
        if category:
            stmt = stmt.where(PointOfInterestORM.category == category)
        if accessible_only:
            stmt = stmt.where(PointOfInterestORM.is_accessible == True)  # noqa: E712
        result = await self.session.execute(stmt)
        return [self._to_domain(row) for row in result.scalars().all() if self._to_domain(row) is not None]
