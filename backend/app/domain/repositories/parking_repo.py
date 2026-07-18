from abc import abstractmethod
from typing import Sequence
from uuid import UUID
from app.domain.entities.parking import ParkingLot, ParkingReservation
from app.domain.repositories.base import IGenericRepository


class IParkingLotRepository(IGenericRepository[ParkingLot]):
    """Repository interface for ParkingLot capacity tracking."""

    @abstractmethod
    async def get_by_venue_id(self, venue_id: UUID) -> Sequence[ParkingLot]:
        """Retrieve all parking lots attached to a venue."""
        pass


class IParkingReservationRepository(IGenericRepository[ParkingReservation]):
    """Repository interface for ParkingReservation."""

    @abstractmethod
    async def get_active_by_user(self, user_id: UUID) -> Sequence[ParkingReservation]:
        """List active reservations belonging to a user."""
        pass
