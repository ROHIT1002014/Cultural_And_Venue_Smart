from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)

engine: AsyncEngine | None = None
async_session_factory: async_sessionmaker[AsyncSession] | None = None


async def init_db() -> None:
    """Initialize Async SQLAlchemy engine and session pool."""
    global engine, async_session_factory
    settings = get_settings()

    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.LOG_LEVEL.upper() == "DEBUG",
        pool_pre_ping=True,
        pool_size=20,
        max_overflow=10,
    )
    async_session_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )
    logger.info("Initialized Async SQLAlchemy engine and connection pool.")


async def close_db() -> None:
    """Dispose Async SQLAlchemy engine cleanly."""
    global engine
    if engine:
        await engine.dispose()
        logger.info("Disposed Async SQLAlchemy database engine.")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency generator yielding an isolated AsyncSession."""
    if async_session_factory is None:
        await init_db()
    assert async_session_factory is not None
    async with async_session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
