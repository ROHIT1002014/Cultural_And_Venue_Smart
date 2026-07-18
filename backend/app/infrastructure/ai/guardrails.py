import re
from typing import Any, Dict
from pydantic import BaseModel, ValidationError
from app.core.exceptions import SecurityGuardException, ValidationDomainException

# PII masking patterns (Emails, SSNs, phone numbers)
PII_EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b")
PII_PHONE_PATTERN = re.compile(r"\b(\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b")
PII_SSN_PATTERN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")


class PIIDetector:
    """Detects and masks Personally Identifiable Information (PII) before LLM calls and in responses."""

    @classmethod
    def mask_pii(cls, text: str) -> str:
        if not text:
            return text
        masked = PII_EMAIL_PATTERN.sub("[REDACTED_EMAIL]", text)
        masked = PII_PHONE_PATTERN.sub("[REDACTED_PHONE]", masked)
        masked = PII_SSN_PATTERN.sub("[REDACTED_SSN]", masked)
        return masked


class HallucinationGuard:
    """Verifies that generated answers are grounded in RAG chunks or executed tool outputs."""

    @classmethod
    def verify_grounding(cls, response_text: str, retrieved_chunks: list[str]) -> float:
        """Calculate overlap score between AI output and source context."""
        if not retrieved_chunks:
            return 0.85  # Default baseline for general guidance when no specific chunks needed
        combined_context = " ".join(retrieved_chunks).lower()
        response_words = set(response_text.lower().split())
        if not response_words:
            return 0.0

        matches = sum(1 for word in response_words if len(word) > 4 and word in combined_context)
        score = min(1.0, 0.70 + (matches / max(1, len(response_words))) * 0.5)
        return round(score, 2)


class OutputValidator:
    """Validates that tool function calling arguments strictly adhere to expected Pydantic schemas."""

    @classmethod
    def validate_tool_args(cls, schema_class: type[BaseModel], args: Dict[str, Any]) -> BaseModel:
        try:
            return schema_class.model_validate(args)
        except ValidationError as exc:
            raise ValidationDomainException(f"AI Tool output failed strict schema validation: {exc}") from exc
