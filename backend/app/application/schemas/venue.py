from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.core.constants import AlertSeverity, POICategory


class VenueCreateDTO(BaseModel):
    """DTO for creating a new cultural venue."""
    name: str = Field(..., min_length=2, max_length=150)
    address: str = Field(..., min_length=5, max_length=300)
    boundary_coordinates: dict[str, Any] = Field(default_factory=dict)
    total_capacity: int = Field(default=5000, ge=10, le=200000)


class VenueResponseDTO(BaseModel):
    """DTO representing venue details and current occupancy."""
    id: UUID
    name: str
    address: str
    boundary_coordinates: dict[str, Any]
    total_capacity: int
    current_occupancy: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class POICreateDTO(BaseModel):
    """DTO for registering an indoor/outdoor Point of Interest."""
    venue_id: UUID
    name: str = Field(..., min_length=2, max_length=100)
    category: POICategory
    coordinates: dict[str, Any] = Field(default_factory=dict)
    floor_level: int = Field(default=1, ge=-5, le=150)
    is_accessible: bool = Field(default=True)


class POIResponseDTO(BaseModel):
    """DTO representing a Point of Interest."""
    id: UUID
    venue_id: UUID
    name: str
    category: str
    coordinates: dict[str, Any]
    floor_level: int
    is_accessible: bool

    model_config = {"from_attributes": True}


class RouteRequestDTO(BaseModel):
    """DTO requesting indoor/outdoor pathfinding directions."""
    venue_id: UUID
    origin_poi_id: UUID
    destination_poi_id: UUID
    require_accessible_route: bool = Field(default=False, description="Enforce step-free pathfinding avoiding escalators/stairs")


class RouteResponseDTO(BaseModel):
    """DTO returning step-by-step route directions."""
    venue_id: UUID
    origin_name: str
    destination_name: str
    total_distance_meters: float
    estimated_time_minutes: int
    steps: list[str]
    is_accessible: bool


class CrowdDensityDTO(BaseModel):
    """DTO reporting live crowd density statistics across venue zones."""
    venue_id: UUID
    zone_name: str
    current_occupancy: int
    capacity: int
    occupancy_percentage: float
    density_status: str  # "SPARSE", "MODERATE", "DENSE", "OVERCROWDED"


class AlertTriggerDTO(BaseModel):
    """DTO to raise an emergency broadcast or evacuation notice."""
    venue_id: UUID
    alert_type: str = Field(..., description="e.g., FIRE_ALARM, MEDICAL_EMERGENCY, SECURITY_THREAT")
    severity: AlertSeverity = Field(default=AlertSeverity.HIGH)
    location: dict[str, Any] = Field(default_factory=dict)


class AlertResponseDTO(BaseModel):
    """DTO representing an active emergency broadcast."""
    id: UUID
    venue_id: UUID
    user_id: UUID
    alert_type: str
    severity: str
    location: dict[str, Any]
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
