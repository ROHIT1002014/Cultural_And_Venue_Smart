import pytest
from httpx import AsyncClient

import app.presentation.api.v1.endpoints.health as health_endpoint
from app.infrastructure import database


@pytest.mark.asyncio
async def test_health_and_liveness_probes(client: AsyncClient) -> None:
    """Test health and liveness probes return OK / ALIVE immediately."""
    resp = await client.get("/api/v1/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "OK"

    liveness_resp = await client.get("/api/v1/health/liveness")
    assert liveness_resp.status_code == 200
    assert liveness_resp.json()["status"] == "ALIVE"


@pytest.mark.asyncio
async def test_readiness_probe_healthy(client: AsyncClient) -> None:
    """Test readiness probe checks Postgres and Redis successfully."""
    resp = await client.get("/api/v1/health/readiness")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "READY"
    assert data["database"] == "HEALTHY"
    assert data["redis"] == "HEALTHY"


@pytest.mark.asyncio
async def test_readiness_probe_db_failure(client: AsyncClient, monkeypatch) -> None:
    """Test readiness probe reports UNREADY when database connection fails."""
    class FailingDBSession:
        async def __aenter__(self):
            return self
        async def __aexit__(self, *args):
            pass
        async def execute(self, *args, **kwargs):
            raise RuntimeError("Simulated database connection failure")

    def failing_factory():
        return FailingDBSession()

    monkeypatch.setattr(database, "async_session_factory", failing_factory)
    resp = await client.get("/api/v1/health/readiness")
    # Status code is 503 when unhealthy or unready
    assert resp.status_code == 503
    data = resp.json()
    assert data["status"] == "UNREADY"
    assert data["database"] == "UNHEALTHY"


@pytest.mark.asyncio
async def test_readiness_probe_redis_failure(client: AsyncClient, monkeypatch) -> None:
    """Test readiness probe reports UNREADY when Redis ping fails."""
    class FailingRedis:
        async def ping(self):
            raise RuntimeError("Simulated Redis connection failure")

    async def override_get_redis():
        return FailingRedis()

    monkeypatch.setattr(health_endpoint, "get_redis", override_get_redis)
    resp = await client.get("/api/v1/health/readiness")
    assert resp.status_code == 503
    data = resp.json()
    assert data["status"] == "UNREADY"
    assert data["redis"] == "UNHEALTHY"
