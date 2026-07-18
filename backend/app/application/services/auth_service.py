from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4
from app.core.config import get_settings
from app.core.exceptions import (
    EntityNotFoundException,
    UnauthorizedException,
    ValidationDomainException,
)
from app.core.security.jwt import (
    create_access_token,
    create_refresh_token,
    hash_refresh_token,
    revoke_access_token,
)
from app.core.security.password import hash_password, verify_password
from app.core.security.rate_limiter import check_account_lockout, record_login_attempt
from app.domain.entities.user import User, RefreshToken
from app.domain.repositories.user_repo import IUserRepository, IRefreshTokenRepository
from app.application.schemas.auth import (
    UserCreateDTO,
    UserLoginDTO,
    TokenResponseDTO,
    UserResponseDTO,
)
from app.application.services.audit_service import AuditLogService


class AuthService:
    """Application use case service handling user authentication, token rotation, and RBAC assignment."""

    def __init__(
        self,
        user_repo: IUserRepository,
        refresh_repo: IRefreshTokenRepository,
        audit_service: AuditLogService | None = None,
    ):
        self.user_repo = user_repo
        self.refresh_repo = refresh_repo
        self.audit_service = audit_service or AuditLogService()

    async def register_user(self, dto: UserCreateDTO, ip_address: str = "127.0.0.1") -> TokenResponseDTO:
        """Register a new user, checking for existing email collisions securely."""
        existing = await self.user_repo.get_by_email(dto.email.lower())
        if existing:
            raise ValidationDomainException(message="A user with this email address is already registered.")

        now = datetime.now(timezone.utc)
        user = User(
            id=uuid4(),
            email=dto.email.lower(),
            hashed_password=hash_password(dto.password),
            full_name=dto.full_name,
            role=dto.role.value,
            is_active=True,
            is_verified=True,  # Auto-verified for immediate copilot usability
            created_at=now,
            updated_at=now,
        )
        saved_user = await self.user_repo.create(user)

        await self.audit_service.log_event(
            user_id=saved_user.id,
            action="USER_REGISTERED",
            entity_name="User",
            entity_id=saved_user.id,
            changes={"email": saved_user.email, "role": saved_user.role},
            ip_address=ip_address,
        )

        return await self._generate_tokens_for_user(saved_user, ip_address)

    async def login_user(self, dto: UserLoginDTO, ip_address: str = "127.0.0.1") -> TokenResponseDTO:
        """Authenticate credentials, verifying against brute-force lockouts and rotating tokens."""
        email_clean = dto.email.lower()
        await check_account_lockout(email_clean)

        user = await self.user_repo.get_by_email(email_clean)
        if not user or not verify_password(dto.password, user.hashed_password):
            await record_login_attempt(email_clean, success=False, ip_address=ip_address)
            raise UnauthorizedException("Invalid email or password credentials provided.")

        if not user.is_active:
            raise UnauthorizedException("User account has been deactivated. Please contact support.")

        await record_login_attempt(email_clean, success=True, ip_address=ip_address)
        return await self._generate_tokens_for_user(user, ip_address)

    async def refresh_tokens(self, raw_refresh_token: str, ip_address: str = "127.0.0.1") -> TokenResponseDTO:
        """Rotate tokens cleanly by validating the hashed refresh token and revoking old instances."""
        token_hash = hash_refresh_token(raw_refresh_token)
        stored_token = await self.refresh_repo.get_by_token_hash(token_hash)

        if not stored_token or stored_token.is_revoked:
            raise UnauthorizedException("Invalid or revoked refresh token provided.")

        now = datetime.now(timezone.utc)
        expires_at = stored_token.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if expires_at < now:
            raise UnauthorizedException("Refresh token has expired. Please log in again.")

        # Revoke old refresh token (Strict rotation check)
        stored_token.is_revoked = True
        await self.refresh_repo.update(stored_token)

        user = await self.user_repo.get_by_id(stored_token.user_id)
        if not user or not user.is_active:
            raise UnauthorizedException("Associated user account not found or deactivated.")

        return await self._generate_tokens_for_user(user, ip_address)

    async def logout_user(self, user_id: UUID, access_token: str) -> None:
        """Revoke active tokens and add access token to Redis blacklist."""
        await revoke_access_token(access_token)
        await self.refresh_repo.revoke_all_for_user(user_id)
        await self.audit_service.log_event(
            user_id=user_id,
            action="USER_LOGOUT",
            entity_name="User",
            entity_id=user_id,
        )

    async def get_user_profile(self, user_id: UUID) -> UserResponseDTO:
        """Fetch safe profile attributes of an authenticated user."""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise EntityNotFoundException("User", user_id)
        return UserResponseDTO.model_validate(user)

    async def _generate_tokens_for_user(self, user: User, ip_address: str) -> TokenResponseDTO:
        """Internal helper generating access + refresh tokens and persisting hashed refresh record."""
        settings = get_settings()
        access_token = create_access_token(user_id=user.id, role=user.role)
        raw_refresh, refresh_hash = create_refresh_token(user_id=user.id)

        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        token_entity = RefreshToken(
            id=uuid4(),
            user_id=user.id,
            token_hash=refresh_hash,
            expires_at=expires_at,
            is_revoked=False,
            ip_address=ip_address,
            created_at=datetime.now(timezone.utc),
        )
        await self.refresh_repo.create(token_entity)

        return TokenResponseDTO(
            access_token=access_token,
            refresh_token=raw_refresh,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponseDTO.model_validate(user),
        )
