from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.config import get_settings
from app.core.logging import get_logger, setup_logging
from app.core.security.rate_limiter import limiter
from app.infrastructure.database import close_db, init_db
from app.infrastructure.redis_client import close_redis, init_redis
from app.presentation.api.v1.router import api_router
from app.presentation.middlewares.exception_handler import setup_exception_handlers
from app.presentation.middlewares.logging_middleware import LoggingMiddleware
from app.presentation.middlewares.security_headers import SecurityHeadersMiddleware
from app.presentation.middlewares.size_limit import RequestSizeLimitMiddleware

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan context managing startup and shutdown of DB/Redis pools."""
    settings = get_settings()
    setup_logging(settings.LOG_LEVEL)
    logger.info("Starting up Cultural & Venue Smart Copilot Platform Backend...", extra={"project": settings.PROJECT_NAME})

    # Initialize database and Redis pools
    await init_db()
    await init_redis()

    yield

    # Clean up connections
    logger.info("Shutting down application and closing connection pools...")
    await close_db()
    await close_redis()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance with Clean Architecture presentation layer."""
    settings = get_settings()

    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="Production-ready AI-Powered Multi-Agent Cultural & Venue Navigation and Operations API.",
        version="1.0.0",
        openapi_url="/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # Attach Rate Limiter state
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]

    # Setup Custom Exception Handlers
    setup_exception_handlers(app)

    # Add Middlewares (Order matters: outermost added last executes first)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestSizeLimitMiddleware, max_size_bytes=10 * 1024 * 1024)  # 10 MB limit
    app.add_middleware(LoggingMiddleware)

    # CORS Configuration
    origins = [origin.strip() for origin in settings.ALLOWED_ORIGINS.split(",") if origin.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins if origins else ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include Presentation Routers
    app.include_router(api_router, prefix="/api/v1")

    # Instrument with Prometheus metrics
    Instrumentator().instrument(app).expose(app, endpoint="/metrics")

    return app


app = create_app()
