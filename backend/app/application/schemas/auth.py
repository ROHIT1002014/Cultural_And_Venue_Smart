from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.core.constants import UserRole


class UserCreateDTO(BaseModel):
    """DTO for registering a new user account."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=12, max_length=128, description="Strong password (min 12 chars)")
    full_name: str = Field(..., min_length=2, max_length=100, description="User full name")
    role: UserRole = Field(default=UserRole.USER, description="Assigned role level")


class UserLoginDTO(BaseModel):
    """DTO for user login requests."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="Plaintext account password")


class RefreshTokenRequestDTO(BaseModel):
    """DTO for rotating refresh tokens."""
    refresh_token: str = Field(..., description="Existing raw refresh token string")


class UserResponseDTO(BaseModel):
    """Safe DTO returned when retrieving user profile details (excludes password hash)."""
    id: UUID
    email: EmailStr
    full_name: str
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponseDTO(BaseModel):
    """DTO returned upon successful authentication or token refresh."""
    access_token: str
    refresh_token: str
    token_type: Literal["bearer"] = "bearer"  # noqa: S105
    expires_in: int
    user: UserResponseDTO
