import html
import re
from uuid import UUID

from app.core.exceptions import ValidationDomainException

# SQL injection keywords pattern check
SQL_INJECTION_PATTERN = re.compile(
    r"\b(UNION\s+ALL|SELECT\s+.*?\s+FROM|DROP\s+TABLE|ALTER\s+TABLE|INSERT\s+INTO|DELETE\s+FROM|UPDATE\s+.*?\s+SET)\b",
    re.IGNORECASE,
)

# XSS script/event tags pattern check
XSS_PATTERN = re.compile(
    r"(<\s*script\b[^>]*>|javascript:|on\w+\s*=)",
    re.IGNORECASE,
)


def sanitize_string(input_str: str, check_sql: bool = True, strip_html: bool = True) -> str:
    """Sanitize input strings against XSS and suspicious SQL injection patterns."""
    if not input_str:
        return input_str

    if check_sql and SQL_INJECTION_PATTERN.search(input_str):
        raise ValidationDomainException(message="Input rejected: Suspicious SQL syntax pattern detected.")

    if XSS_PATTERN.search(input_str):
        raise ValidationDomainException(message="Input rejected: Suspicious XSS script pattern detected.")

    cleaned = html.escape(input_str) if strip_html else input_str
    return cleaned.strip()


def validate_uuid(uuid_str: str) -> UUID:
    """Strictly validate and convert a string representation into a valid UUID v4."""
    try:
        return UUID(uuid_str)
    except (ValueError, TypeError, AttributeError) as exc:
        raise ValidationDomainException(message=f"Invalid UUID structure provided: '{uuid_str}'") from exc
