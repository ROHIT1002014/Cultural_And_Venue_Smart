from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class ParkingLot:
    """Domain entity representing a venue parking lot with EV and accessible spot tracking."""
    id: UUID
    venue_id: UUID
    lot_name: str
    total_spots: int
    available_spots: int
    accessible_spots_total: int
    accessible_spots_available: int
    has_ev_charging: bool
    created_at: datetime
    updated_at: datetime


@dataclass
class ParkingReservation:
    """Domain entity recording an accessible or EV spot reservation."""
    id: UUID
    lot_id: UUID
    user_id: UUID
    vehicle_license: str
    check_in_time: datetime
    check_out_time: datetime | None
    status: str  # e.g., "ACTIVE", "COMPLETED", "CANCELLED"
    created_at: datetime
