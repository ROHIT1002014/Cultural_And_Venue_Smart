from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List
from uuid import UUID


@dataclass
class ConversationSession:
    """Domain entity representing an AI chat session."""
    id: UUID
    user_id: UUID
    title: str
    last_active_at: datetime
    created_at: datetime


@dataclass
class ChatMessage:
    """Domain entity recording individual exchanges and tool executions inside an AI session."""
    id: UUID
    session_id: UUID
    role: str  # "user", "assistant", "system", "tool"
    content: str
    tool_calls: List[Dict[str, Any]] | None
    latency_seconds: float
    token_count: int
    created_at: datetime


@dataclass
class RAGDocument:
    """Domain entity representing an indexed knowledge source document."""
    id: UUID
    venue_id: UUID
    title: str
    source_url: str | None
    document_type: str
    created_at: datetime


@dataclass
class RAGChunk:
    """Domain entity representing semantic text chunks embedded in the vector store."""
    id: UUID
    document_id: UUID
    content: str
    embedding: List[float] | None
    metadata: Dict[str, Any]


@dataclass
class EmergencyAlert:
    """Domain entity tracking priority evacuation and emergency broadcasts."""
    id: UUID
    venue_id: UUID
    user_id: UUID
    alert_type: str
    severity: str
    location: Dict[str, Any]
    status: str
    created_at: datetime
