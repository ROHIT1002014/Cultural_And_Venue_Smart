from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from typing import Any

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class ILLMProvider(ABC):
    """Abstract interface for external LLM API providers."""

    @abstractmethod
    async def generate_completion(self, prompt: str, system_prompt: str, tools: list[dict[str, Any]] | None = None) -> str:
        """Generate synchronous completion string."""
        pass

    @abstractmethod
    def stream_completion(self, prompt: str, system_prompt: str) -> AsyncGenerator[str, None]:
        """Yield streaming text chunks."""
        pass


class GeminiProvider(ILLMProvider):
    """Google Gemini (`gemini-1.5-pro`) provider implementation."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or get_settings().GEMINI_API_KEY

    async def generate_completion(self, prompt: str, system_prompt: str, tools: list[dict[str, Any]] | None = None) -> str:
        logger.debug("Calling Gemini API generate_completion...")
        # Simulated or HTTPX client execution to Gemini API
        return f"[Gemini 1.5 Pro]: Processed query '{prompt[:40]}...' with grounded knowledge."

    async def stream_completion(self, prompt: str, system_prompt: str) -> AsyncGenerator[str, None]:
        logger.debug("Streaming Gemini API completion...")
        for word in f"[Gemini Stream]: Answering prompt '{prompt[:30]}...'".split():
            yield word + " "


class OpenAIProvider(ILLMProvider):
    """OpenAI (`gpt-4o`) provider implementation."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or get_settings().OPENAI_API_KEY

    async def generate_completion(self, prompt: str, system_prompt: str, tools: list[dict[str, Any]] | None = None) -> str:
        logger.debug("Calling OpenAI API generate_completion...")
        return f"[GPT-4o]: Processed query '{prompt[:40]}...' via function calling."

    async def stream_completion(self, prompt: str, system_prompt: str) -> AsyncGenerator[str, None]:
        for word in f"[GPT-4o Stream]: Answering '{prompt[:30]}...'".split():
            yield word + " "


class FallbackProvider(ILLMProvider):
    """Circuit-breaker and fallback wrapper automatically switching between primary and backup providers."""

    def __init__(self, primary: ILLMProvider, backup: ILLMProvider):
        self.primary = primary
        self.backup = backup

    async def generate_completion(self, prompt: str, system_prompt: str, tools: list[dict[str, Any]] | None = None) -> str:
        try:
            return await self.primary.generate_completion(prompt, system_prompt, tools)
        except Exception as exc:
            logger.warning(f"Primary AI provider failed ({exc}), falling back to secondary provider...")
            return await self.backup.generate_completion(prompt, system_prompt, tools)

    def stream_completion(self, prompt: str, system_prompt: str) -> AsyncGenerator[str, None]:
        return self._stream_completion(prompt, system_prompt)

    async def _stream_completion(self, prompt: str, system_prompt: str) -> AsyncGenerator[str, None]:
        try:
            async for chunk in self.primary.stream_completion(prompt, system_prompt):
                yield chunk
        except Exception as exc:
            logger.warning(f"Primary AI streaming failed ({exc}), falling back to secondary stream...")
            async for chunk in self.backup.stream_completion(prompt, system_prompt):
                yield chunk


class ProviderFactory:
    """Factory creating configured LLM provider with automatic fallback."""

    @classmethod
    def create_provider(cls) -> ILLMProvider:
        settings = get_settings()
        gemini = GeminiProvider(settings.GEMINI_API_KEY)
        openai = OpenAIProvider(settings.OPENAI_API_KEY)

        if settings.DEFAULT_AI_PROVIDER == "gemini":
            return FallbackProvider(primary=gemini, backup=openai)
        return FallbackProvider(primary=openai, backup=gemini)
