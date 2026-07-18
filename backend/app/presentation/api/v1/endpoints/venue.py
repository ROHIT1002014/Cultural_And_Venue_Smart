from typing import Annotated, Sequence
from uuid import UUID
from fastapi import APIRouter, Depends
from app.core.security.permissions import PERMISSION_VENUE_CREATE, PERMISSION_EMERGENCY_TRIGGER
from app.domain.entities.user import User
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
from app.application.services.venue_service import VenueService, NavigationService
from app.presentation.deps import get_venue_service, get_nav_service, require_permission

router = APIRouter(prefix="/venues", tags=["Venues & Navigation"])


@router.post("", response_model=VenueResponseDTO, status_code=201)
async def create_venue(
    dto: VenueCreateDTO,
    current_user: Annotated[User, Depends(require_permission(PERMISSION_VENUE_CREATE))],
    venue_service: Annotated[VenueService, Depends(get_venue_service)],
) -> VenueResponseDTO:
    """Create a new cultural venue. Requires ADMIN permission."""
    return await venue_service.create_venue(dto=dto, user_id=current_user.id)


@router.get("/{venue_id}", response_model=VenueResponseDTO)
async def get_venue(
    venue_id: UUID,
    venue_service: Annotated[VenueService, Depends(get_venue_service)],
) -> VenueResponseDTO:
    """Fetch details of a specific cultural venue."""
    return await venue_service.get_venue(venue_id=venue_id)


@router.get("/{venue_id}/pois", response_model=Sequence[POIResponseDTO])
async def list_pois(
    venue_id: UUID,
    venue_service: Annotated[VenueService, Depends(get_venue_service)],
    category: str | None = None,
    accessible_only: bool = False,
) -> Sequence[POIResponseDTO]:
    """Retrieve indoor/outdoor points of interest filtered by category and accessibility."""
    return await venue_service.list_pois(venue_id=venue_id, category=category, accessible_only=accessible_only)


@router.post("/{venue_id}/pois", response_model=POIResponseDTO, status_code=201)
async def add_poi(
    venue_id: UUID,
    dto: POICreateDTO,
    current_user: Annotated[User, Depends(require_permission(PERMISSION_VENUE_CREATE))],
    venue_service: Annotated[VenueService, Depends(get_venue_service)],
) -> POIResponseDTO:
    """Register a new point of interest within a venue."""
    return await venue_service.add_poi(dto=dto, user_id=current_user.id)


@router.post("/{venue_id}/routes", response_model=RouteResponseDTO)
async def calculate_route(
    venue_id: UUID,
    dto: RouteRequestDTO,
    nav_service: Annotated[NavigationService, Depends(get_nav_service)],
) -> RouteResponseDTO:
    """Compute step-by-step navigation route between origin and destination markers."""
    return await nav_service.calculate_route(dto=dto)


@router.get("/{venue_id}/crowd-density", response_model=Sequence[CrowdDensityDTO])
async def get_crowd_density(
    venue_id: UUID,
    venue_service: Annotated[VenueService, Depends(get_venue_service)],
) -> Sequence[CrowdDensityDTO]:
    """Retrieve real-time crowd density statistics for venue zones."""
    return await venue_service.get_crowd_density(venue_id=venue_id)


@router.post("/{venue_id}/alerts", response_model=AlertResponseDTO, status_code=201)
async def trigger_emergency_alert(
    venue_id: UUID,
    dto: AlertTriggerDTO,
    current_user: Annotated[User, Depends(require_permission(PERMISSION_EMERGENCY_TRIGGER))],
    venue_service: Annotated[VenueService, Depends(get_venue_service)],
) -> AlertResponseDTO:
    """Trigger a high-priority evacuation or emergency alert across connected clients."""
    return await venue_service.trigger_emergency_alert(dto=dto, user_id=current_user.id)
