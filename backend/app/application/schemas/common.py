from pydantic import BaseModel, Field
from datetime import datetime, timezone


class ErrorResponseDTO(BaseModel):
    """Standardized API error response payload."""
    error: str = Field(..., description="Error code string")
    message: str = Field(..., description="Human-readable description of error")
    status_code: int = Field(..., description="HTTP status code")
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class StatusResponseDTO(BaseModel):
    """Simple boolean/status response wrapper."""
    success: bool = Field(default=True)
    message: str = Field(default="Operation completed successfully")
