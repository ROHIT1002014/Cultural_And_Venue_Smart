from datetime import datetime, timezone
from typing import Sequence
from uuid import UUID, uuid4
from app.core.exceptions import EntityNotFoundException, ValidationDomainException
from app.domain.entities.parking import ParkingLot, ParkingReservation
from app.domain.repositories.parking_repo import IParkingLotRepository, IParkingReservationRepository
from app.application.schemas.parking import (
    ParkingLotCreateDTO,
    ParkingLotResponseDTO,
    ReservationCreateDTO,
    ReservationResponseDTO,
)
from app.application.services.audit_service import AuditLogService


class ParkingService:
    """Service handling parking lot management, real-time EV availability, and accessibility reservations."""

    def __init__(
        self,
        lot_repo: IParkingLotRepository,
        reservation_repo: IParkingReservationRepository,
        audit_service: AuditLogService | None = None,
    ):
        self.lot_repo = lot_repo
        self.reservation_repo = reservation_repo
        self.audit_service = audit_service or AuditLogService()

    async def add_lot(self, dto: ParkingLotCreateDTO, user_id: UUID | None = None) -> ParkingLotResponseDTO:
        """Create and register a new parking lot for a venue."""
        now = datetime.now(timezone.utc)
        lot = ParkingLot(
            id=uuid4(),
            venue_id=dto.venue_id,
            lot_name=dto.lot_name,
            total_spots=dto.total_spots,
            available_spots=dto.total_spots,
            accessible_spots_total=dto.accessible_spots_total,
            accessible_spots_available=dto.accessible_spots_total,
            has_ev_charging=dto.has_ev_charging,
            created_at=now,
            updated_at=now,
        )
        saved = await self.lot_repo.create(lot)

        await self.audit_service.log_event(
            user_id=user_id,
            action="PARKING_LOT_CREATED",
            entity_name="ParkingLot",
            entity_id=saved.id,
            changes={"lot_name": saved.lot_name, "total_spots": saved.total_spots},
        )
        return self._to_response_dto(saved)

    async def list_venue_lots(self, venue_id: UUID) -> Sequence[ParkingLotResponseDTO]:
        """Fetch real-time status of all parking lots belonging to a venue."""
        lots = await self.lot_repo.get_by_venue_id(venue_id)
        return [self._to_response_dto(lot) for lot in lots]

    async def reserve_spot(self, user_id: UUID, dto: ReservationCreateDTO) -> ReservationResponseDTO:
        """Reserve a parking spot, enforcing accessibility and capacity bounds."""
        lot = await self.lot_repo.get_by_id(dto.lot_id)
        if not lot:
            raise EntityNotFoundException("ParkingLot", dto.lot_id)

        if lot.available_spots <= 0:
            raise ValidationDomainException("Parking lot is currently FULL. No spots available.")

        if dto.requires_accessible_spot and lot.accessible_spots_available <= 0:
            raise ValidationDomainException("No reserved wheelchair-accessible spots remain in this lot.")

        if dto.requires_ev_charger and not lot.has_ev_charging:
            raise ValidationDomainException("This parking lot does not offer EV charging facilities.")

        # Deduct spot availability atomic check simulation
        lot.available_spots -= 1
        if dto.requires_accessible_spot:
            lot.accessible_spots_available -= 1
        lot.updated_at = datetime.now(timezone.utc)
        await self.lot_repo.update(lot)

        reservation = ParkingReservation(
            id=uuid4(),
            lot_id=lot.id,
            user_id=user_id,
            vehicle_license=dto.vehicle_license.upper(),
            check_in_time=datetime.now(timezone.utc),
            check_out_time=None,
            status="ACTIVE",
            created_at=datetime.now(timezone.utc),
        )
        saved_res = await self.reservation_repo.create(reservation)

        await self.audit_service.log_event(
            user_id=user_id,
            action="PARKING_RESERVED",
            entity_name="ParkingReservation",
            entity_id=saved_res.id,
            changes={"license": saved_res.vehicle_license, "lot_id": str(lot.id)},
        )

        return ReservationResponseDTO.model_validate(saved_res)

    def _to_response_dto(self, lot: ParkingLot) -> ParkingLotResponseDTO:
        status = "FULL" if lot.available_spots == 0 else "OPEN"
        return ParkingLotResponseDTO(
            id=lot.id,
            venue_id=lot.venue_id,
            lot_name=lot.lot_name,
            total_spots=lot.total_spots,
            available_spots=lot.available_spots,
            accessible_spots_total=lot.accessible_spots_total,
            accessible_spots_available=lot.accessible_spots_available,
            has_ev_charging=lot.has_ev_charging,
            status=status,
        )
