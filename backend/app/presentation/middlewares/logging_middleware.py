import time
from uuid import uuid4
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.core.logging import get_logger

logger = get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware injecting unique trace_id across request/response lifecycle and logging latency metrics."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        trace_id = request.headers.get("x-trace-id", str(uuid4()))
        request.state.trace_id = trace_id

        start_time = time.time()
        logger.info(
            f"HTTP Request Started: {request.method} {request.url.path}",
            extra={"trace_id": trace_id, "client_ip": request.client.host if request.client else "UNKNOWN"},
        )

        try:
            response = await call_next(request)
            latency_ms = round((time.time() - start_time) * 1000, 2)
            response.headers["X-Trace-ID"] = trace_id
            logger.info(
                f"HTTP Request Completed: {request.method} {request.url.path} - Status {response.status_code} in {latency_ms}ms",
                extra={"trace_id": trace_id, "status_code": response.status_code, "latency_ms": latency_ms},
            )
            return response
        except Exception as exc:
            latency_ms = round((time.time() - start_time) * 1000, 2)
            logger.error(
                f"HTTP Request Failed: {request.method} {request.url.path} in {latency_ms}ms - Exception: {exc}",
                extra={"trace_id": trace_id, "latency_ms": latency_ms},
                exc_info=True,
            )
            raise
