from typing import Any


class DomainException(Exception):
    """Base class for all core domain logic exceptions."""
    def __init__(self, message: str, code: str = "DOMAIN_ERROR", status_code: int = 400, details: Any | None = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details


class EntityNotFoundException(DomainException):
    """Raised when a requested entity ID does not exist."""
    def __init__(self, entity_name: str, entity_id: str | Any):
        super().__init__(
            message=f"{entity_name} with ID '{entity_id}' not found.",
            code="ENTITY_NOT_FOUND",
            status_code=404
        )


class UnauthorizedException(DomainException):
    """Raised when user authentication fails or token is invalid."""
    def __init__(self, message: str = "Authentication required or invalid credentials."):
        super().__init__(message=message, code="UNAUTHORIZED", status_code=401)


class InsufficientPermissionsException(DomainException):
    """Raised when user lacks required RBAC permission."""
    def __init__(self, permission: str):
        super().__init__(
            message=f"User lacks required permission: '{permission}'.",
            code="INSUFFICIENT_PERMISSIONS",
            status_code=403
        )


class RateLimitExceededException(DomainException):
    """Raised when API or security rate limit is exceeded."""
    def __init__(self, message: str = "Too many requests. Please try again later."):
        super().__init__(message=message, code="RATE_LIMIT_EXCEEDED", status_code=429)


class SecurityGuardException(DomainException):
    """Raised when prompt injection, harmful payload, or PII policy violation is caught."""
    def __init__(self, message: str = "Request blocked by Security and AI Guardrails."):
        super().__init__(message=message, code="SECURITY_POLICY_VIOLATION", status_code=400)


class ValidationDomainException(DomainException):
    """Raised when strict business validation logic fails."""
    def __init__(self, message: str, details: Any | None = None):
        super().__init__(message=message, code="VALIDATION_ERROR", status_code=422, details=details)
