from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.types import ASGIApp


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """Enforce strict payload size bounds to prevent Denial of Service (DoS) memory exhaustion attacks."""

    def __init__(self, app: ASGIApp, max_size_bytes: int = 10 * 1024 * 1024):
        super().__init__(app)
        self.max_size_bytes = max_size_bytes

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> JSONResponse | Any:
        content_length_header = request.headers.get("content-length")
        if content_length_header and content_length_header.isdigit():
            if int(content_length_header) > self.max_size_bytes:
                return JSONResponse(
                    status_code=413,
                    content={
                        "error": "PAYLOAD_TOO_LARGE",
                        "message": f"Request body exceeds allowed limit of {self.max_size_bytes // (1024 * 1024)} MB.",
                        "status_code": 413,
                    },
                )
        return await call_next(request)
