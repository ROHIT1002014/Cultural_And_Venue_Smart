from __future__ import annotations

from typing import Any

from redis.asyncio import Redis, from_url

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)

redis_pool: Redis[Any] | None = None


async def init_redis() -> None:
    """Initialize async Redis client pool."""
    global redis_pool
    settings = get_settings()
    redis_pool = from_url(
        settings.REDIS_URL,
        password=settings.REDIS_PASSWORD,
        decode_responses=True,
        max_connections=50,
    )
    logger.info("Initialized Async Redis client connection pool.")


async def close_redis() -> None:
    """Close Redis client connections."""
    global redis_pool
    if redis_pool:
        if hasattr(redis_pool.connection_pool, "disconnect"):
            await redis_pool.connection_pool.disconnect(inuse_connections=True)
        await redis_pool.aclose()  # type: ignore[attr-defined]
        redis_pool = None
        logger.info("Closed Redis connection pool.")


async def get_redis() -> Redis[Any]:
    """Return active async Redis client instance."""
    if redis_pool is None:
        await init_redis()
    assert redis_pool is not None
    return redis_pool
