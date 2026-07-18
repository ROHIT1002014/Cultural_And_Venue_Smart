import re
from typing import List
from app.core.exceptions import SecurityGuardException

# Regex patterns catching common prompt injection jailbreaks and instruction overrides
INJECTION_PATTERNS: List[re.Pattern[str]] = [
    re.compile(r"ignore\s+(all\s+)?(previous|prior)\s+instructions", re.IGNORECASE),
    re.compile(r"you\s+are\s+now\s+in\s+developer\s+mode", re.IGNORECASE),
    re.compile(r"system\s+prompt\s+override", re.IGNORECASE),
    re.compile(r"bypass\s+(all\s+)?guardrails", re.IGNORECASE),
    re.compile(r"do\s+anything\s+now|dan\s+mode", re.IGNORECASE),
    re.compile(r"<\s*/?\s*system\s*>", re.IGNORECASE),
]


class PromptGuard:
    """Guardrail inspecting incoming user prompts for jailbreak attacks and injection payloads."""

    @classmethod
    def inspect(cls, user_prompt: str) -> str:
        """Analyze input against injection signatures and raise SecurityGuardException if harmful patterns are found."""
        if not user_prompt or not user_prompt.strip():
            return user_prompt

        normalized = user_prompt.strip()
        for pattern in INJECTION_PATTERNS:
            if pattern.search(normalized):
                raise SecurityGuardException(
                    message="Prompt rejected: Potential prompt injection or instruction override detected."
                )

        # Escape any rogue XML/HTML delimiters that might disrupt structured template tags
        sanitized = normalized.replace("<", "&lt;").replace(">", "&gt;")
        return sanitized
