from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ParkingLotCreateDTO(BaseModel):
    """DTO for adding a new parking lot."""
    venue_id: UUID
    lot_name: str = Field(..., min_length=2, max_length=100)
    total_spots: int = Field(default=500, ge=1)
    accessible_spots_total: int = Field(default=25, ge=0)
    has_ev_charging: bool = Field(default=True)


class ParkingLotResponseDTO(BaseModel):
    """DTO reporting current parking lot availability."""
    id: UUID
    venue_id: UUID
    lot_name: str
    total_spots: int
    available_spots: int
    accessible_spots_total: int
    accessible_spots_available: int
    has_ev_charging: bool
    status: str  # e.g., "OPEN" or "FULL"

    model_config = {"from_attributes": True}


class ReservationCreateDTO(BaseModel):
    """DTO for reserving a parking spot."""
    lot_id: UUID
    vehicle_license: str = Field(..., min_length=3, max_length=20)
    requires_accessible_spot: bool = Field(default=False)
    requires_ev_charger: bool = Field(default=False)


class ReservationResponseDTO(BaseModel):
    """DTO reporting confirmed reservation details."""
    id: UUID
    lot_id: UUID
    user_id: UUID
    vehicle_license: str
    check_in_time: datetime
    status: str

    model_config = {"from_attributes": True}
