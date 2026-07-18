from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.application.schemas.common import ErrorResponseDTO
from app.core.exceptions import DomainException
from app.core.logging import get_logger

logger = get_logger(__name__)


def setup_exception_handlers(app: FastAPI) -> None:
    """Register uniform custom JSON exception handlers across the FastAPI application."""

    @app.exception_handler(DomainException)
    async def domain_exception_handler(request: Request, exc: DomainException) -> JSONResponse:
        logger.warning(
            f"Domain Exception occurred on {request.method} {request.url.path}: {exc.code} - {exc.message}",
            extra={"details": exc.details},
        )
        error_dto = ErrorResponseDTO(
            error=exc.code,
            message=exc.message,
            status_code=exc.status_code,
        )
        return JSONResponse(status_code=exc.status_code, content=error_dto.model_dump())

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        errors = exc.errors()
        error_msg = "; ".join([f"{'.'.join([str(loc) for loc in e['loc']])}: {e['msg']}" for e in errors])
        logger.warning(f"Request Validation failed on {request.method} {request.url.path}: {error_msg}")

        error_dto = ErrorResponseDTO(
            error="VALIDATION_ERROR",
            message=f"Request schema validation failed: {error_msg}",
            status_code=422,
        )
        return JSONResponse(status_code=422, content=error_dto.model_dump())

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        error_dto = ErrorResponseDTO(
            error="HTTP_ERROR",
            message=str(exc.detail),
            status_code=exc.status_code,
        )
        return JSONResponse(status_code=exc.status_code, content=error_dto.model_dump())

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.error(
            f"Unhandled server exception on {request.method} {request.url.path}: {exc}",
            exc_info=True,
        )
        error_dto = ErrorResponseDTO(
            error="INTERNAL_SERVER_ERROR",
            message="An unexpected internal server error occurred. Please try again later.",
            status_code=500,
        )
        return JSONResponse(status_code=500, content=error_dto.model_dump())
