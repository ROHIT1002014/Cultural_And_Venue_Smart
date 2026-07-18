from collections.abc import Sequence
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from app.application.schemas.parking import (
    ParkingLotCreateDTO,
    ParkingLotResponseDTO,
    ReservationCreateDTO,
    ReservationResponseDTO,
)
from app.application.services.parking_service import ParkingService
from app.core.security.permissions import PERMISSION_PARKING_RESERVE, PERMISSION_PARKING_UPDATE
from app.domain.entities.user import User
from app.presentation.deps import get_parking_service, require_permission

router = APIRouter(prefix="/parking", tags=["Parking & Logistics"])


@router.post("/lots", response_model=ParkingLotResponseDTO, status_code=201)
async def create_parking_lot(
    dto: ParkingLotCreateDTO,
    current_user: Annotated[User, Depends(require_permission(PERMISSION_PARKING_UPDATE))],
    parking_service: Annotated[ParkingService, Depends(get_parking_service)],
) -> ParkingLotResponseDTO:
    """Create a new parking lot attached to a venue. Requires ADMIN/VOLUNTEER permission."""
    return await parking_service.add_lot(dto=dto, user_id=current_user.id)


@router.get("/lots/{venue_id}", response_model=Sequence[ParkingLotResponseDTO])
async def list_parking_lots(
    venue_id: UUID,
    parking_service: Annotated[ParkingService, Depends(get_parking_service)],
) -> Sequence[ParkingLotResponseDTO]:
    """Retrieve real-time available spots, EV chargers, and wheelchair spaces across all venue parking lots."""
    return await parking_service.list_venue_lots(venue_id=venue_id)


@router.post("/reserve", response_model=ReservationResponseDTO, status_code=201)
async def reserve_spot(
    dto: ReservationCreateDTO,
    current_user: Annotated[User, Depends(require_permission(PERMISSION_PARKING_RESERVE))],
    parking_service: Annotated[ParkingService, Depends(get_parking_service)],
) -> ReservationResponseDTO:
    """Reserve a parking spot, specifying accessible space or EV charging requirements."""
    return await parking_service.reserve_spot(user_id=current_user.id, dto=dto)
