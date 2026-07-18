from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm

from app.application.schemas.auth import (
    RefreshTokenRequestDTO,
    TokenResponseDTO,
    UserCreateDTO,
    UserLoginDTO,
    UserResponseDTO,
)
from app.application.schemas.common import StatusResponseDTO
from app.application.services.auth_service import AuthService
from app.core.security.rate_limiter import limiter
from app.domain.entities.user import User
from app.presentation.deps import get_auth_service, get_current_user, oauth2_scheme

router = APIRouter(prefix="/auth", tags=["Authentication & Security"])


@router.post("/register", response_model=TokenResponseDTO, status_code=201)
@limiter.limit("10/minute")
async def register(
    request: Request,
    dto: UserCreateDTO,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenResponseDTO:
    """Register a new user profile with rate limiting (10 per minute)."""
    ip = request.client.host if request.client else "127.0.0.1"
    return await auth_service.register_user(dto=dto, ip_address=ip)


@router.post("/login", response_model=TokenResponseDTO)
@limiter.limit("20/minute")
async def login(
    request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenResponseDTO:
    """Authenticate credentials via OAuth2 form or JSON login, with brute-force lockout protection."""
    ip = request.client.host if request.client else "127.0.0.1"
    dto = UserLoginDTO(email=form_data.username, password=form_data.password)
    return await auth_service.login_user(dto=dto, ip_address=ip)


@router.post("/refresh", response_model=TokenResponseDTO)
@limiter.limit("30/minute")
async def refresh_tokens(
    request: Request,
    dto: RefreshTokenRequestDTO,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenResponseDTO:
    """Rotate refresh token securely."""
    ip = request.client.host if request.client else "127.0.0.1"
    return await auth_service.refresh_tokens(raw_refresh_token=dto.refresh_token, ip_address=ip)


@router.post("/logout", response_model=StatusResponseDTO)
async def logout(
    current_user: Annotated[User, Depends(get_current_user)],
    token: Annotated[str, Depends(oauth2_scheme)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> StatusResponseDTO:
    """Logout current user and blacklist JWT access token."""
    await auth_service.logout_user(user_id=current_user.id, access_token=token)
    return StatusResponseDTO(success=True, message="Successfully logged out and revoked tokens.")


@router.get("/me", response_model=UserResponseDTO)
async def get_my_profile(current_user: Annotated[User, Depends(get_current_user)]) -> UserResponseDTO:
    """Retrieve currently authenticated user profile."""
    return UserResponseDTO.model_validate(current_user)
