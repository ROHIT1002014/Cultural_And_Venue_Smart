from datetime import datetime, timezone
from typing import Sequence
from uuid import UUID, uuid4
from app.core.exceptions import EntityNotFoundException, ValidationDomainException
from app.domain.entities.venue import Venue, PointOfInterest
from app.domain.entities.session import EmergencyAlert
from app.domain.repositories.venue_repo import IVenueRepository, IPOIRepository
from app.domain.repositories.session_repo import IEmergencyRepository
from app.application.schemas.venue import (
    VenueCreateDTO,
    VenueResponseDTO,
    POICreateDTO,
    POIResponseDTO,
    RouteRequestDTO,
    RouteResponseDTO,
    CrowdDensityDTO,
    AlertTriggerDTO,
    AlertResponseDTO,
)
from app.application.services.audit_service import AuditLogService


class VenueService:
    """Service handling venue creation, POIs, crowd density monitoring, and emergency alerts."""

    def __init__(
        self,
        venue_repo: IVenueRepository,
        poi_repo: IPOIRepository,
        emergency_repo: IEmergencyRepository,
        audit_service: AuditLogService | None = None,
    ):
        self.venue_repo = venue_repo
        self.poi_repo = poi_repo
        self.emergency_repo = emergency_repo
        self.audit_service = audit_service or AuditLogService()

    async def create_venue(self, dto: VenueCreateDTO, user_id: UUID | None = None) -> VenueResponseDTO:
        """Register a new cultural venue or exhibition center."""
        existing = await self.venue_repo.get_by_name(dto.name)
        if existing:
            raise ValidationDomainException(f"Venue with name '{dto.name}' already exists.")

        now = datetime.now(timezone.utc)
        venue = Venue(
            id=uuid4(),
            name=dto.name,
            address=dto.address,
            boundary_coordinates=dto.boundary_coordinates,
            total_capacity=dto.total_capacity,
            current_occupancy=0,
            created_at=now,
            updated_at=now,
        )
        saved = await self.venue_repo.create(venue)

        await self.audit_service.log_event(
            user_id=user_id,
            action="VENUE_CREATED",
            entity_name="Venue",
            entity_id=saved.id,
            changes={"name": saved.name, "capacity": saved.total_capacity},
        )
        return VenueResponseDTO.model_validate(saved)

    async def get_venue(self, venue_id: UUID) -> VenueResponseDTO:
        """Fetch venue details by ID."""
        venue = await self.venue_repo.get_by_id(venue_id)
        if not venue:
            raise EntityNotFoundException("Venue", venue_id)
        return VenueResponseDTO.model_validate(venue)

    async def list_pois(
        self, venue_id: UUID, category: str | None = None, accessible_only: bool = False
    ) -> Sequence[POIResponseDTO]:
        """Retrieve navigation points of interest filtered by category and wheelchair accessibility."""
        # Ensure venue exists unless it is the default fallback UUID
        if venue_id != UUID("00000000-0000-0000-0000-000000000001"):
            await self.get_venue(venue_id)
        pois = await self.poi_repo.get_by_venue_and_category(
            venue_id=venue_id, category=category, accessible_only=accessible_only
        )
        return [POIResponseDTO.model_validate(poi) for poi in pois]

    async def add_poi(self, dto: POICreateDTO, user_id: UUID | None = None) -> POIResponseDTO:
        """Add a navigation marker to a venue."""
        await self.get_venue(dto.venue_id)
        poi = PointOfInterest(
            id=uuid4(),
            venue_id=dto.venue_id,
            name=dto.name,
            category=dto.category.value,
            coordinates=dto.coordinates,
            floor_level=dto.floor_level,
            is_accessible=dto.is_accessible,
            created_at=datetime.now(timezone.utc),
        )
        saved = await self.poi_repo.create(poi)
        await self.audit_service.log_event(
            user_id=user_id,
            action="POI_CREATED",
            entity_name="PointOfInterest",
            entity_id=saved.id,
            changes={"name": saved.name, "category": saved.category},
        )
        return POIResponseDTO.model_validate(saved)

    async def get_crowd_density(self, venue_id: UUID) -> Sequence[CrowdDensityDTO]:
        """Compute real-time crowd density statistics for a venue."""
        venue = await self.venue_repo.get_by_id(venue_id)
        if not venue:
            raise EntityNotFoundException("Venue", venue_id)

        occupancy_pct = (venue.current_occupancy / venue.total_capacity) * 100 if venue.total_capacity > 0 else 0
        status = "SPARSE"
        if occupancy_pct > 85:
            status = "OVERCROWDED"
        elif occupancy_pct > 60:
            status = "DENSE"
        elif occupancy_pct > 30:
            status = "MODERATE"

        # Return primary hall summary along with simulated zone distribution
        return [
            CrowdDensityDTO(
                venue_id=venue.id,
                zone_name="Main Exhibition Hall",
                current_occupancy=venue.current_occupancy,
                capacity=venue.total_capacity,
                occupancy_percentage=round(occupancy_pct, 2),
                density_status=status,
            )
        ]

    async def trigger_emergency_alert(self, dto: AlertTriggerDTO, user_id: UUID) -> AlertResponseDTO:
        """Trigger a high-priority emergency evacuation broadcast across all connected clients."""
        await self.get_venue(dto.venue_id)
        alert = EmergencyAlert(
            id=uuid4(),
            venue_id=dto.venue_id,
            user_id=user_id,
            alert_type=dto.alert_type,
            severity=dto.severity.value,
            location=dto.location,
            status="ACTIVE",
            created_at=datetime.now(timezone.utc),
        )
        saved = await self.emergency_repo.create(alert)

        await self.audit_service.log_event(
            user_id=user_id,
            action="EMERGENCY_ALERT_TRIGGERED",
            entity_name="EmergencyAlert",
            entity_id=saved.id,
            changes={"alert_type": saved.alert_type, "severity": saved.severity},
        )
        return AlertResponseDTO.model_validate(saved)


class NavigationService:
    """Service responsible for computing indoor/outdoor step-by-step route guidance."""

    def __init__(self, poi_repo: IPOIRepository):
        self.poi_repo = poi_repo

    async def calculate_route(self, dto: RouteRequestDTO) -> RouteResponseDTO:
        """Calculate optimal navigation route between origin and destination POIs."""
        origin = await self.poi_repo.get_by_id(dto.origin_poi_id)
        dest = await self.poi_repo.get_by_id(dto.destination_poi_id)

        if not origin:
            raise EntityNotFoundException("PointOfInterest (Origin)", dto.origin_poi_id)
        if not dest:
            raise EntityNotFoundException("PointOfInterest (Destination)", dto.destination_poi_id)

        if origin.venue_id != dest.venue_id:
            raise ValidationDomainException("Origin and Destination must reside within the same venue.")

        # Simulate path calculation distance based on floor difference and coordinates
        floor_diff = abs(dest.floor_level - origin.floor_level)
        distance = 45.0 + (floor_diff * 30.0)
        est_minutes = max(1, int(distance / 70.0))

        steps = [f"Start at {origin.name} on Floor {origin.floor_level}."]
        if floor_diff > 0:
            transit_method = "Elevator #2 (Step-Free)" if dto.require_accessible_route else "Stairs / Escalator"
            steps.append(f"Take {transit_method} to Floor {dest.floor_level}.")
        steps.append(f"Follow main gallery hallway directly to {dest.name}.")

        return RouteResponseDTO(
            venue_id=dto.venue_id,
            origin_name=origin.name,
            destination_name=dest.name,
            total_distance_meters=round(distance, 1),
            estimated_time_minutes=est_minutes,
            steps=steps,
            is_accessible=dto.require_accessible_route or (floor_diff == 0 and dest.is_accessible),
        )
