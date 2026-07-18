import asyncio
from collections.abc import AsyncGenerator, Generator
from datetime import UTC

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.infrastructure.database import get_db
from app.infrastructure.models.base import Base
from app.infrastructure.redis_client import get_redis
from app.main import app

# Use SQLite in-memory async database for ultra-fast unit/integration testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=StaticPool,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_test_db() -> AsyncGenerator[None, None]:
    from app.core.security.rate_limiter import limiter
    try:
        limiter._storage.reset()
    except Exception:
        pass

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    async with TestingSessionLocal() as session:
        from datetime import datetime
        from uuid import UUID

        from app.infrastructure.models.venue_model import VenueORM
        default_venue = VenueORM(
            id=UUID("00000000-0000-0000-0000-000000000001"),
            name="Default Venue",
            address="123 Cultural Way",
            total_capacity=10000,
            current_occupancy=0,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        session.add(default_venue)
        await session.commit()
    try:
        redis = await get_redis()
        await redis.flushdb()
    except Exception:
        pass
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    try:
        redis = await get_redis()
        await redis.flushdb()
    except Exception:
        pass


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac
    app.dependency_overrides.clear()
