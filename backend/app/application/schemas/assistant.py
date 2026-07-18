from datetime import datetime
from typing import Any, Dict, List
from uuid import UUID
from pydantic import BaseModel, Field


class ChatRequestDTO(BaseModel):
    """DTO for incoming multi-agent AI chat interactions."""
    session_id: UUID | None = Field(default=None, description="Optional existing session UUID")
    message: str = Field(..., min_length=1, max_length=2000, description="User prompt text")
    preferred_language: str = Field(default="en", description="ISO language code (e.g., en, es, hi)")
    venue_id: UUID | None = Field(default=None, description="Optional target venue UUID for RAG scoping")


class ExecutedToolDTO(BaseModel):
    """DTO reporting an invoked agent tool during conversation processing."""
    agent_name: str
    tool_name: str
    arguments: Dict[str, Any]
    output_summary: str


class TokenUsageDTO(BaseModel):
    """DTO summarizing token consumption and estimated cost."""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    estimated_cost_usd: float


class ChatResponseDTO(BaseModel):
    """DTO returned after multi-agent LangGraph execution and RAG grounding verification."""
    session_id: UUID
    message_id: UUID
    response: str
    active_agents: List[str]
    executed_tools: List[ExecutedToolDTO]
    grounding_score: float
    token_usage: TokenUsageDTO
    created_at: datetime


class SessionResponseDTO(BaseModel):
    """DTO representing a conversation session summary."""
    id: UUID
    user_id: UUID
    title: str
    last_active_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}


class FAQSearchRequestDTO(BaseModel):
    """DTO for semantic FAQ search requests."""
    venue_id: UUID
    query: str = Field(..., min_length=2, max_length=500)
    limit: int = Field(default=5, ge=1, le=20)


class FAQItemDTO(BaseModel):
    """DTO returning a single retrieved semantic FAQ match."""
    document_title: str
    content: str
    similarity_score: float
    metadata: Dict[str, Any]


class FAQSearchResponseDTO(BaseModel):
    """DTO wrapping FAQ search results."""
    venue_id: UUID
    query: str
    results: List[FAQItemDTO]
