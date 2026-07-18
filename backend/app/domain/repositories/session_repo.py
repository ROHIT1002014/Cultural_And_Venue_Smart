from abc import abstractmethod
from typing import Sequence
from uuid import UUID
from app.domain.entities.session import (
    ConversationSession,
    ChatMessage,
    RAGDocument,
    RAGChunk,
    EmergencyAlert,
)
from app.domain.entities.item import LostItem
from app.domain.repositories.base import IGenericRepository


class ISessionRepository(IGenericRepository[ConversationSession]):
    """Repository interface for AI chat sessions."""

    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> Sequence[ConversationSession]:
        """Retrieve all chat sessions initiated by a user."""
        pass


class IMessageRepository(IGenericRepository[ChatMessage]):
    """Repository interface for ChatMessage history."""

    @abstractmethod
    async def get_recent_messages(self, session_id: UUID, limit: int = 20) -> Sequence[ChatMessage]:
        """Retrieve the most recent chat messages in chronological order."""
        pass


class IRAGRepository(IGenericRepository[RAGDocument]):
    """Repository interface for RAG Documents and Semantic Chunk embeddings."""

    @abstractmethod
    async def search_similar_chunks(self, venue_id: UUID, query_embedding: Sequence[float], limit: int = 5) -> Sequence[RAGChunk]:
        """Perform vector similarity search against embedded RAG chunks."""
        pass

    @abstractmethod
    async def search_keyword_chunks(self, venue_id: UUID, query_text: str, limit: int = 5) -> Sequence[RAGChunk]:
        """Perform full-text keyword search across RAG chunks."""
        pass


class IEmergencyRepository(IGenericRepository[EmergencyAlert]):
    """Repository interface for Emergency Alerts."""

    @abstractmethod
    async def get_active_alerts(self, venue_id: UUID) -> Sequence[EmergencyAlert]:
        """Retrieve unresolved emergency broadcasts for a venue."""
        pass


class ILostItemRepository(IGenericRepository[LostItem]):
    """Repository interface for LostItem reporting."""

    @abstractmethod
    async def get_by_venue_id(self, venue_id: UUID, status: str | None = None) -> Sequence[LostItem]:
        """Retrieve lost items within a venue filtered by status."""
        pass
