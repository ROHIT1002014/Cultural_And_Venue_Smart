from typing import Any
from datetime import datetime, timezone
from uuid import uuid4
from app.domain.entities.user import User
from app.domain.entities.venue import Venue, PointOfInterest
from app.domain.entities.parking import ParkingLot, ParkingReservation
from app.core.security.password import hash_password
from app.core.constants import UserRole, POICategory


class UserFactory:
    """Factory generating realistic User domain entities for unit and integration testing."""
    @staticmethod
    def build(
        email: str = "testuser@example.com",
        password: str = "StrongPassword123!",
        role: UserRole = UserRole.USER,
        is_active: bool = True,
    ) -> User:
        now = datetime.now(timezone.utc)
        return User(
            id=uuid4(),
            email=email.lower(),
            hashed_password=hash_password(password),
            full_name="Test User",
            role=role.value,
            is_active=is_active,
            is_verified=True,
            created_at=now,
            updated_at=now,
        )


class VenueFactory:
    """Factory generating Venue and PointOfInterest domain entities."""
    @staticmethod
    def build(name: str = "Grand National Cultural Museum", total_capacity: int = 5000) -> Venue:
        now = datetime.now(timezone.utc)
        return Venue(
            id=uuid4(),
            name=name,
            address="100 Cultural Blvd, Metropolis",
            boundary_coordinates={"lat": 40.7128, "lng": -74.0060},
            total_capacity=total_capacity,
            current_occupancy=0,
            created_at=now,
            updated_at=now,
        )

    @staticmethod
    def build_poi(venue_id: Any, name: str = "Main Gallery Restroom", category: str = POICategory.RESTROOM.value) -> PointOfInterest:
        return PointOfInterest(
            id=uuid4(),
            venue_id=venue_id,
            name=name,
            category=category,
            coordinates={"floor": 1, "section": "West Wing"},
            floor_level=1,
            is_accessible=True,
            created_at=datetime.now(timezone.utc),
        )


class ParkingFactory:
    """Factory generating ParkingLot and ParkingReservation domain entities."""
    @staticmethod
    def build_lot(venue_id: Any, lot_name: str = "East Wing Structure", total_spots: int = 200) -> ParkingLot:
        now = datetime.now(timezone.utc)
        return ParkingLot(
            id=uuid4(),
            venue_id=venue_id,
            lot_name=lot_name,
            total_spots=total_spots,
            available_spots=total_spots,
            accessible_spots_total=10,
            accessible_spots_available=10,
            has_ev_charging=True,
            created_at=now,
            updated_at=now,
        )
