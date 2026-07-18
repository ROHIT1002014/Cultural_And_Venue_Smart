from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class User:
    """Domain entity representing a registered system user."""
    id: UUID
    email: str
    hashed_password: str
    full_name: str
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime


@dataclass
class RefreshToken:
    """Domain entity tracking refresh tokens for secure rotation."""
    id: UUID
    user_id: UUID
    token_hash: str
    expires_at: datetime
    is_revoked: bool
    ip_address: str | None
    created_at: datetime
