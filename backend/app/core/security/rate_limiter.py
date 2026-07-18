from datetime import datetime, timezone
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.exceptions import UnauthorizedException
from app.infrastructure.redis_client import get_redis

# SlowAPI Limiter instance using remote IP address as identifier
limiter = Limiter(key_func=get_remote_address)


async def record_login_attempt(email: str, success: bool, ip_address: str) -> None:
    """Track login attempts in Redis and enforce account lockout after 5 consecutive failures within 15 minutes."""
    redis = await get_redis()
    key = f"auth:attempts:{email.lower()}"
    lock_key = f"auth:locked:{email.lower()}"

    if success:
        # Clear failure counters upon successful login
        await redis.delete(key)
        await redis.delete(lock_key)
        return

    # Increment failure counter with 15 minute (900 seconds) expiration window
    attempts = await redis.incr(key)
    if attempts == 1:
        await redis.expire(key, 900)

    if attempts >= 5:
        # Lock account for 15 minutes
        await redis.set(lock_key, datetime.now(timezone.utc).isoformat(), ex=900)


async def check_account_lockout(email: str) -> None:
    """Verify if an account is currently locked out due to brute force login failures."""
    redis = await get_redis()
    lock_key = f"auth:locked:{email.lower()}"
    locked_since = await redis.get(lock_key)
    if locked_since:
        raise UnauthorizedException(
            message="Account is temporarily locked due to multiple failed login attempts. Please try again in 15 minutes."
        )
