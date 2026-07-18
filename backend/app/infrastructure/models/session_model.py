from datetime import datetime, timezone
from typing import Any, Dict, List
from uuid import UUID, uuid4
from sqlalchemy import DateTime, Float, Integer, String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.infrastructure.models.base import Base, JSONType, UUIDType


class ConversationSessionORM(Base):
    """SQLAlchemy ORM mapping for ConversationSession."""
    __tablename__ = "conversation_sessions"

    id: Mapped[UUID] = mapped_column(UUIDType, primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(UUIDType, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(200), default="New Conversation")
    last_active_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class ChatMessageORM(Base):
    """SQLAlchemy ORM mapping for ChatMessage."""
    __tablename__ = "chat_messages"

    id: Mapped[UUID] = mapped_column(UUIDType, primary_key=True, default=uuid4)
    session_id: Mapped[UUID] = mapped_column(UUIDType, ForeignKey("conversation_sessions.id", ondelete="CASCADE"), index=True, nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    tool_calls: Mapped[List[Dict[str, Any]] | None] = mapped_column(JSONType, nullable=True)
    latency_seconds: Mapped[float] = mapped_column(Float, default=0.0)
    token_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class RAGDocumentORM(Base):
    """SQLAlchemy ORM mapping for RAGDocument."""
    __tablename__ = "rag_documents"

    id: Mapped[UUID] = mapped_column(UUIDType, primary_key=True, default=uuid4)
    venue_id: Mapped[UUID] = mapped_column(UUIDType, ForeignKey("venues.id", ondelete="CASCADE"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    source_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    document_type: Mapped[str] = mapped_column(String(50), default="faq")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class RAGChunkORM(Base):
    """SQLAlchemy ORM mapping for RAGChunk."""
    __tablename__ = "rag_chunks"

    id: Mapped[UUID] = mapped_column(UUIDType, primary_key=True, default=uuid4)
    document_id: Mapped[UUID] = mapped_column(UUIDType, ForeignKey("rag_documents.id", ondelete="CASCADE"), index=True, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[Dict[str, Any]] = mapped_column("metadata", JSONType, default=dict)


class EmergencyAlertORM(Base):
    """SQLAlchemy ORM mapping for EmergencyAlert."""
    __tablename__ = "emergency_alerts"

    id: Mapped[UUID] = mapped_column(UUIDType, primary_key=True, default=uuid4)
    venue_id: Mapped[UUID] = mapped_column(UUIDType, ForeignKey("venues.id", ondelete="CASCADE"), index=True, nullable=False)
    user_id: Mapped[UUID] = mapped_column(UUIDType, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    alert_type: Mapped[str] = mapped_column(String(100), nullable=False)
    severity: Mapped[str] = mapped_column(String(50), default="HIGH")
    location: Mapped[Dict[str, Any]] = mapped_column(JSONType, default=dict)
    status: Mapped[str] = mapped_column(String(50), default="ACTIVE")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
