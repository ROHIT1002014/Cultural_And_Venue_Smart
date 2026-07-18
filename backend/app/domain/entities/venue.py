from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID


@dataclass
class Venue:
    """Domain entity representing a cultural venue or exhibition hall complex."""
    id: UUID
    name: str
    address: str
    boundary_coordinates: dict[str, Any]
    total_capacity: int
    current_occupancy: int
    created_at: datetime
    updated_at: datetime


@dataclass
class PointOfInterest:
    """Domain entity representing specific indoor/outdoor features (restrooms, exits, seating)."""
    id: UUID
    venue_id: UUID
    name: str
    category: str
    coordinates: dict[str, Any]
    floor_level: int
    is_accessible: bool
    created_at: datetime
