import hashlib
from datetime import datetime, timedelta, timezone
from typing import Any, Dict
from uuid import UUID, uuid4
from jose import JWTError, jwt

from app.core.config import get_settings
from app.core.exceptions import UnauthorizedException
from app.core.constants import UserRole
from app.infrastructure.redis_client import get_redis


def create_access_token(user_id: UUID | str, role: UserRole | str, extra_claims: Dict[str, Any] | None = None) -> str:
    """Generate a short-lived JWT access token signed with HMAC or RSA algorithms."""
    settings = get_settings()
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    claims: Dict[str, Any] = {
        "sub": str(user_id),
        "role": str(role),
        "iat": now,
        "exp": expire,
        "type": "access",
        "jti": str(uuid4()),
    }
    if extra_claims:
        claims.update(extra_claims)

    encoded_jwt = jwt.encode(claims, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return str(encoded_jwt)


def create_refresh_token(user_id: UUID | str) -> tuple[str, str]:
    """Generate a high-entropy refresh token string along with its cryptographic hash."""
    raw_token = str(uuid4()) + str(uuid4())
    token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
    return raw_token, token_hash


def hash_refresh_token(raw_token: str) -> str:
    """Hash a raw refresh token using SHA-256."""
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


async def verify_access_token(token: str) -> Dict[str, Any]:
    """Verify and decode a JWT access token, ensuring it is not expired or blacklisted in Redis."""
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        if payload.get("type") != "access":
            raise UnauthorizedException("Invalid token type. Expected access token.")

        # Check if token JTI is blacklisted in Redis after logout or revocation
        jti = payload.get("jti")
        if jti:
            redis = await get_redis()
            is_blacklisted = await redis.exists(f"blacklist:jwt:{jti}")
            if is_blacklisted:
                raise UnauthorizedException("Token has been revoked or blacklisted.")

        return payload
    except JWTError as exc:
        raise UnauthorizedException(f"Token validation failed: {str(exc)}") from exc


async def revoke_access_token(token: str) -> None:
    """Add a JWT access token's JTI to the Redis blacklist until its expiration."""
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        jti = payload.get("jti")
        exp = payload.get("exp")
        if jti and exp:
            ttl = int(exp - datetime.now(timezone.utc).timestamp())
            if ttl > 0:
                redis = await get_redis()
                await redis.set(f"blacklist:jwt:{jti}", "revoked", ex=ttl)
    except JWTError:
        pass  # Token already invalid or expired
