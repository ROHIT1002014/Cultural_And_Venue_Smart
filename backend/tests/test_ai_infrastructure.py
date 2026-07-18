from collections.abc import AsyncGenerator
from typing import Any, AsyncIterator
from uuid import uuid4

import pytest

from app.application.agents.tools import AVAILABLE_TOOLS, TOOL_FIND_POI
from app.core.config import get_settings
from app.domain.entities.session import RAGChunk
from app.infrastructure.ai.memory import RedisMemory
from app.infrastructure.ai.providers import (
    FallbackProvider,
    GeminiProvider,
    OpenAIProvider,
    ProviderFactory,
)
from app.infrastructure.ai.rag import RAGEngine
from app.infrastructure.ai.token_counter import CostTracker, TokenCounter


@pytest.mark.asyncio
async def test_gemini_provider_generate_and_stream() -> None:
    provider = GeminiProvider(api_key="test-key")
    result = await provider.generate_completion(
        prompt="Where is the restroom?",
        system_prompt="You are a guide.",
        tools=[{"name": "find_poi"}]
    )
    assert "[Gemini 1.5 Pro]" in result
    assert "Where is the restroom?"[:30] in result

    stream_chunks = []
    async for chunk in provider.stream_completion("Where is the restroom?", "system"):
        stream_chunks.append(chunk)
    assert len(stream_chunks) > 0
    assert any("[Gemini" in c for c in stream_chunks)


@pytest.mark.asyncio
async def test_openai_provider_generate_and_stream() -> None:
    provider = OpenAIProvider(api_key="test-key")
    result = await provider.generate_completion(
        prompt="Check parking status",
        system_prompt="You are a parking agent."
    )
    assert "[GPT-4o]" in result
    assert "Check parking status"[:30] in result

    stream_chunks = []
    async for chunk in provider.stream_completion("Check parking status", "system"):
        stream_chunks.append(chunk)
    assert len(stream_chunks) > 0
    assert any("[GPT-4o" in c for c in stream_chunks)


@pytest.mark.asyncio
async def test_fallback_provider_success_and_failover() -> None:
    primary = GeminiProvider("primary-key")
    backup = OpenAIProvider("backup-key")
    fallback = FallbackProvider(primary=primary, backup=backup)

    # Normal primary execution
    res = await fallback.generate_completion("Hello", "system")
    assert "[Gemini 1.5 Pro]" in res

    stream_res = [c async for c in fallback.stream_completion("Hello", "system")]
    assert any("[Gemini" in c for c in stream_res)

    # Now create a failing primary to verify fallback triggers
    class FailingProvider(GeminiProvider):
        async def generate_completion(self, prompt: str, system_prompt: str, tools: list[dict[str, Any]] | None = None) -> str:
            raise RuntimeError("Simulated API failure")

        async def stream_completion(self, prompt: str, system_prompt: str) -> AsyncGenerator[str, None]:
            raise RuntimeError("Simulated streaming failure")
            yield "never reached"

    failing_fallback = FallbackProvider(primary=FailingProvider(), backup=backup)
    failover_res = await failing_fallback.generate_completion("Help", "system")
    assert "[GPT-4o]" in failover_res

    stream_failover = [c async for c in failing_fallback.stream_completion("Help", "system")]
    assert any("[GPT-4o" in c for c in stream_failover)


def test_provider_factory_create(monkeypatch: pytest.MonkeyPatch) -> None:
    provider = ProviderFactory.create_provider()
    assert isinstance(provider, FallbackProvider)

    # Check both default branches
    monkeypatch.setattr(get_settings(), "DEFAULT_AI_PROVIDER", "openai")
    openai_first = ProviderFactory.create_provider()
    assert isinstance(openai_first, FallbackProvider) and isinstance(openai_first.primary, OpenAIProvider)

    monkeypatch.setattr(get_settings(), "DEFAULT_AI_PROVIDER", "gemini")
    gemini_first = ProviderFactory.create_provider()
    assert isinstance(gemini_first, FallbackProvider) and isinstance(gemini_first.primary, GeminiProvider)


@pytest.mark.asyncio
async def test_redis_memory_operations() -> None:
    session_id = uuid4()
    await RedisMemory.append_message(session_id, "user", "Hello Copilot")
    await RedisMemory.append_message(session_id, "assistant", "Hello User")

    window = await RedisMemory.get_conversation_window(session_id, max_messages=5)
    assert len(window) == 2
    assert window[0]["role"] == "user"
    assert window[0]["content"] == "Hello Copilot"
    assert window[1]["role"] == "assistant"

    await RedisMemory.clear_session_memory(session_id)
    cleared_window = await RedisMemory.get_conversation_window(session_id)
    assert len(cleared_window) == 0


def test_token_counter_and_cost_tracker() -> None:
    assert TokenCounter.estimate_tokens("") == 0
    text = "Where is the nearest wheelchair accessible restroom and parking lot?"
    tokens = TokenCounter.estimate_tokens(text)
    assert tokens > 0

    cost_gemini = CostTracker.calculate_cost(prompt_tokens=1000, completion_tokens=500, model="gemini-1.5-pro")
    assert cost_gemini == round(1.0 * 0.00125 + 0.5 * 0.00375, 6)

    cost_openai = CostTracker.calculate_cost(prompt_tokens=1000, completion_tokens=500, model="gpt-4o")
    assert cost_openai == round(1.0 * 0.00500 + 0.5 * 0.01500, 6)

    # Unknown model falls back to gemini rates
    cost_unknown = CostTracker.calculate_cost(prompt_tokens=1000, completion_tokens=500, model="unknown-model")
    assert cost_unknown == cost_gemini

    dto = CostTracker.create_usage_dto("Hello user prompt text", "Assistant reply text", model="gemini-1.5-pro")
    assert dto.prompt_tokens > 0
    assert dto.completion_tokens > 0
    assert dto.total_tokens == dto.prompt_tokens + dto.completion_tokens
    assert dto.estimated_cost_usd >= 0.0


@pytest.mark.asyncio
async def test_rag_engine_retrieve_grounding_context() -> None:
    class MockRAGRepository:
        async def search_keyword_chunks(self, venue_id: Any, query_text: str, limit: int = 4) -> list[RAGChunk]:
            return [
                RAGChunk(id=uuid4(), document_id=uuid4(), content="Gallery opens at 9am.", embedding=None, metadata={"title": "Guide"})
            ]

    engine = RAGEngine(rag_repo=MockRAGRepository())  # type: ignore[arg-type]
    chunks = await engine.retrieve_grounding_context(venue_id=uuid4(), query_text="hours", limit=2)
    assert len(chunks) == 1
    assert chunks[0].content == "Gallery opens at 9am."


def test_available_tools_specifications() -> None:
    assert len(AVAILABLE_TOOLS) >= 3
    names = [t.name for t in AVAILABLE_TOOLS]
    assert "find_poi" in names
    assert "check_parking_status" in names
    assert "trigger_emergency_alert" in names

    assert TOOL_FIND_POI.parameters["type"] == "object"
    assert "category" in TOOL_FIND_POI.parameters["properties"]
