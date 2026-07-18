from typing import Annotated, AsyncGenerator, Callable
from uuid import UUID
from fastapi import Depends, Header, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import InsufficientPermissionsException, UnauthorizedException
from app.core.security.jwt import verify_access_token
from app.core.security.permissions import has_permission
from app.domain.entities.user import User
from app.domain.repositories.user_repo import IUserRepository, IRefreshTokenRepository
from app.domain.repositories.venue_repo import IVenueRepository, IPOIRepository
from app.domain.repositories.parking_repo import IParkingLotRepository, IParkingReservationRepository
from app.domain.repositories.session_repo import (
    ISessionRepository,
    IMessageRepository,
    IRAGRepository,
    IEmergencyRepository,
)
from app.infrastructure.database import get_db
from app.infrastructure.repositories.sql_user_repo import SQLUserRepository, SQLRefreshTokenRepository
from app.infrastructure.repositories.sql_venue_repo import SQLVenueRepository, SQLPOIRepository
from app.infrastructure.repositories.sql_parking_repo import SQLParkingLotRepository, SQLParkingReservationRepository
from app.infrastructure.repositories.sql_session_repo import (
    SQLSessionRepository,
    SQLMessageRepository,
    SQLRAGRepository,
    SQLEmergencyRepository,
)
from app.application.services.audit_service import AuditLogService
from app.application.services.auth_service import AuthService
from app.application.services.venue_service import VenueService, NavigationService
from app.application.services.parking_service import ParkingService
from app.application.services.assistant_service import AssistantService
from app.application.agents.sub_agents import NavigationAgent, ParkingAgent, EmergencyAgent
from app.application.agents.orchestrator import OrchestratorAgent

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# --- Repository Dependencies ---
def get_user_repo(session: Annotated[AsyncSession, Depends(get_db)]) -> IUserRepository:
    return SQLUserRepository(session)

def get_refresh_repo(session: Annotated[AsyncSession, Depends(get_db)]) -> IRefreshTokenRepository:
    return SQLRefreshTokenRepository(session)

def get_venue_repo(session: Annotated[AsyncSession, Depends(get_db)]) -> IVenueRepository:
    return SQLVenueRepository(session)

def get_poi_repo(session: Annotated[AsyncSession, Depends(get_db)]) -> IPOIRepository:
    return SQLPOIRepository(session)

def get_lot_repo(session: Annotated[AsyncSession, Depends(get_db)]) -> IParkingLotRepository:
    return SQLParkingLotRepository(session)

def get_reservation_repo(session: Annotated[AsyncSession, Depends(get_db)]) -> IParkingReservationRepository:
    return SQLParkingReservationRepository(session)

def get_session_repo(session: Annotated[AsyncSession, Depends(get_db)]) -> ISessionRepository:
    return SQLSessionRepository(session)

def get_message_repo(session: Annotated[AsyncSession, Depends(get_db)]) -> IMessageRepository:
    return SQLMessageRepository(session)

def get_rag_repo(session: Annotated[AsyncSession, Depends(get_db)]) -> IRAGRepository:
    return SQLRAGRepository(session)

def get_emergency_repo(session: Annotated[AsyncSession, Depends(get_db)]) -> IEmergencyRepository:
    return SQLEmergencyRepository(session)

# --- Service Dependencies ---
def get_audit_service() -> AuditLogService:
    return AuditLogService()

def get_auth_service(
    user_repo: Annotated[IUserRepository, Depends(get_user_repo)],
    refresh_repo: Annotated[IRefreshTokenRepository, Depends(get_refresh_repo)],
    audit_service: Annotated[AuditLogService, Depends(get_audit_service)],
) -> AuthService:
    return AuthService(user_repo=user_repo, refresh_repo=refresh_repo, audit_service=audit_service)

def get_venue_service(
    venue_repo: Annotated[IVenueRepository, Depends(get_venue_repo)],
    poi_repo: Annotated[IPOIRepository, Depends(get_poi_repo)],
    emergency_repo: Annotated[IEmergencyRepository, Depends(get_emergency_repo)],
    audit_service: Annotated[AuditLogService, Depends(get_audit_service)],
) -> VenueService:
    return VenueService(
        venue_repo=venue_repo,
        poi_repo=poi_repo,
        emergency_repo=emergency_repo,
        audit_service=audit_service,
    )

def get_nav_service(poi_repo: Annotated[IPOIRepository, Depends(get_poi_repo)]) -> NavigationService:
    return NavigationService(poi_repo=poi_repo)

def get_parking_service(
    lot_repo: Annotated[IParkingLotRepository, Depends(get_lot_repo)],
    reservation_repo: Annotated[IParkingReservationRepository, Depends(get_reservation_repo)],
    audit_service: Annotated[AuditLogService, Depends(get_audit_service)],
) -> ParkingService:
    return ParkingService(lot_repo=lot_repo, reservation_repo=reservation_repo, audit_service=audit_service)

def get_orchestrator(
    venue_service: Annotated[VenueService, Depends(get_venue_service)],
    nav_service: Annotated[NavigationService, Depends(get_nav_service)],
    parking_service: Annotated[ParkingService, Depends(get_parking_service)],
) -> OrchestratorAgent:
    nav_agent = NavigationAgent(venue_service=venue_service, nav_service=nav_service)
    parking_agent = ParkingAgent(parking_service=parking_service)
    emergency_agent = EmergencyAgent()
    return OrchestratorAgent(nav_agent=nav_agent, parking_agent=parking_agent, emergency_agent=emergency_agent)

def get_assistant_service(
    session_repo: Annotated[ISessionRepository, Depends(get_session_repo)],
    message_repo: Annotated[IMessageRepository, Depends(get_message_repo)],
    rag_repo: Annotated[IRAGRepository, Depends(get_rag_repo)],
    orchestrator: Annotated[OrchestratorAgent, Depends(get_orchestrator)],
) -> AssistantService:
    return AssistantService(
        session_repo=session_repo,
        message_repo=message_repo,
        rag_repo=rag_repo,
        orchestrator=orchestrator,
    )

# --- Authentication & RBAC Dependencies ---
async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_repo: Annotated[IUserRepository, Depends(get_user_repo)],
) -> User:
    """Verify access token and fetch current active user entity."""
    payload = await verify_access_token(token)
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise UnauthorizedException("Invalid token subject.")

    user = await user_repo.get_by_id(UUID(user_id_str))
    if not user or not user.is_active:
        raise UnauthorizedException("User not found or deactivated.")
    return user

def require_permission(permission: str) -> Callable[[User], User]:
    """Dependency factory checking if current user possesses granular RBAC permission."""
    def permission_checker(current_user: Annotated[User, Depends(get_current_user)]) -> User:
        if not has_permission(current_user.role, permission):
            raise InsufficientPermissionsException(permission)
        return current_user
    return permission_checker
