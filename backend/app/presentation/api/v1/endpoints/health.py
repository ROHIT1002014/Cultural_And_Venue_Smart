from typing import Any

from fastapi import APIRouter, Response
from sqlalchemy import text

from app.core.logging import get_logger
from app.infrastructure import database
from app.infrastructure.redis_client import get_redis

logger = get_logger(__name__)
router = APIRouter(tags=["Health & Readiness"])


@router.get("/health", summary="Basic service liveness check")
async def health_check() -> dict[str, str]:
    """Returns status OK immediately if service process is running."""
    return {"status": "OK", "service": "Cultural & Venue Smart Copilot Platform Backend"}


@router.get("/health/liveness", summary="Kubernetes liveness probe")
async def liveness_probe() -> dict[str, str]:
    """Liveness check confirming async event loop reactivity."""
    return {"status": "ALIVE"}


@router.get("/health/readiness", summary="Kubernetes readiness probe checking DB and Redis")
async def readiness_probe(response: Response) -> dict[str, Any]:
    """Verifies that database and Redis connections are alive and responding before receiving traffic."""
    db_status = "UNHEALTHY"
    redis_status = "UNHEALTHY"

    # Check Postgres Connection
    if database.async_session_factory is None:
        await database.init_db()
    if database.async_session_factory is not None:
        try:
            async with database.async_session_factory() as session:
                await session.execute(text("SELECT 1"))
                db_status = "HEALTHY"
        except Exception as exc:
            logger.error(f"Readiness probe DB check failed: {exc}")

    # Check Redis Connection
    try:
        redis = await get_redis()
        pong = await redis.ping()
        if pong:
            redis_status = "HEALTHY"
    except Exception as exc:
        logger.error(f"Readiness probe Redis check failed: {exc}")

    is_ready = db_status == "HEALTHY" and redis_status == "HEALTHY"
    status_code = 200 if is_ready else 503
    response.status_code = status_code

    return {
        "status": "READY" if is_ready else "UNREADY",
        "database": db_status,
        "redis": redis_status,
        "status_code": status_code,
    }
