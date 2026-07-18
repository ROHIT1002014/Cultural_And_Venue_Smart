from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.parking import ParkingLot, ParkingReservation
from app.domain.repositories.parking_repo import IParkingLotRepository, IParkingReservationRepository
from app.infrastructure.models.parking_model import ParkingLotORM, ParkingReservationORM
from app.infrastructure.repositories.generic_repo import SQLAlchemyGenericRepository


class SQLParkingLotRepository(SQLAlchemyGenericRepository[ParkingLot, ParkingLotORM], IParkingLotRepository):
    """Async repository for ParkingLot."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, ParkingLotORM)

    def _to_domain(self, orm_obj: ParkingLotORM | None) -> ParkingLot | None:
        if not orm_obj:
            return None
        return ParkingLot(
            id=orm_obj.id,
            venue_id=orm_obj.venue_id,
            lot_name=orm_obj.lot_name,
            total_spots=orm_obj.total_spots,
            available_spots=orm_obj.available_spots,
            accessible_spots_total=orm_obj.accessible_spots_total,
            accessible_spots_available=orm_obj.accessible_spots_available,
            has_ev_charging=orm_obj.has_ev_charging,
            created_at=orm_obj.created_at,
            updated_at=orm_obj.updated_at,
        )

    def _to_orm(self, domain_entity: ParkingLot) -> ParkingLotORM:
        return ParkingLotORM(
            id=domain_entity.id,
            venue_id=domain_entity.venue_id,
            lot_name=domain_entity.lot_name,
            total_spots=domain_entity.total_spots,
            available_spots=domain_entity.available_spots,
            accessible_spots_total=domain_entity.accessible_spots_total,
            accessible_spots_available=domain_entity.accessible_spots_available,
            has_ev_charging=domain_entity.has_ev_charging,
            created_at=domain_entity.created_at,
            updated_at=domain_entity.updated_at,
        )

    async def get_by_venue_id(self, venue_id: UUID) -> Sequence[ParkingLot]:
        stmt = select(ParkingLotORM).where(ParkingLotORM.venue_id == venue_id)
        result = await self.session.execute(stmt)
        return [entity for row in result.scalars().all() if (entity := self._to_domain(row)) is not None]


class SQLParkingReservationRepository(
    SQLAlchemyGenericRepository[ParkingReservation, ParkingReservationORM], IParkingReservationRepository
):
    """Async repository for ParkingReservation."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, ParkingReservationORM)

    def _to_domain(self, orm_obj: ParkingReservationORM | None) -> ParkingReservation | None:
        if not orm_obj:
            return None
        return ParkingReservation(
            id=orm_obj.id,
            lot_id=orm_obj.lot_id,
            user_id=orm_obj.user_id,
            vehicle_license=orm_obj.vehicle_license,
            check_in_time=orm_obj.check_in_time,
            check_out_time=orm_obj.check_out_time,
            status=orm_obj.status,
            created_at=orm_obj.created_at,
        )

    def _to_orm(self, domain_entity: ParkingReservation) -> ParkingReservationORM:
        return ParkingReservationORM(
            id=domain_entity.id,
            lot_id=domain_entity.lot_id,
            user_id=domain_entity.user_id,
            vehicle_license=domain_entity.vehicle_license,
            check_in_time=domain_entity.check_in_time,
            check_out_time=domain_entity.check_out_time,
            status=domain_entity.status,
            created_at=domain_entity.created_at,
        )

    async def get_active_by_user(self, user_id: UUID) -> Sequence[ParkingReservation]:
        stmt = select(ParkingReservationORM).where(
            ParkingReservationORM.user_id == user_id, ParkingReservationORM.status == "ACTIVE"
        )
        result = await self.session.execute(stmt)
        return [entity for row in result.scalars().all() if (entity := self._to_domain(row)) is not None]
