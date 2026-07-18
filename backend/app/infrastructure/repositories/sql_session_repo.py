from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.session import (
    ChatMessage,
    ConversationSession,
    EmergencyAlert,
    RAGChunk,
    RAGDocument,
)
from app.domain.repositories.session_repo import (
    IEmergencyRepository,
    IMessageRepository,
    IRAGRepository,
    ISessionRepository,
)
from app.infrastructure.models.session_model import (
    ChatMessageORM,
    ConversationSessionORM,
    EmergencyAlertORM,
    RAGChunkORM,
    RAGDocumentORM,
)
from app.infrastructure.repositories.generic_repo import SQLAlchemyGenericRepository


class SQLSessionRepository(SQLAlchemyGenericRepository[ConversationSession, ConversationSessionORM], ISessionRepository):
    """Async repository for ConversationSession."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, ConversationSessionORM)

    def _to_domain(self, orm_obj: ConversationSessionORM | None) -> ConversationSession | None:
        if not orm_obj:
            return None
        return ConversationSession(
            id=orm_obj.id,
            user_id=orm_obj.user_id,
            title=orm_obj.title,
            last_active_at=orm_obj.last_active_at,
            created_at=orm_obj.created_at,
        )

    def _to_orm(self, domain_entity: ConversationSession) -> ConversationSessionORM:
        return ConversationSessionORM(
            id=domain_entity.id,
            user_id=domain_entity.user_id,
            title=domain_entity.title,
            last_active_at=domain_entity.last_active_at,
            created_at=domain_entity.created_at,
        )

    async def get_by_user_id(self, user_id: UUID) -> Sequence[ConversationSession]:
        stmt = select(ConversationSessionORM).where(ConversationSessionORM.user_id == user_id).order_by(ConversationSessionORM.last_active_at.desc())
        result = await self.session.execute(stmt)
        return [entity for row in result.scalars().all() if (entity := self._to_domain(row)) is not None]


class SQLMessageRepository(SQLAlchemyGenericRepository[ChatMessage, ChatMessageORM], IMessageRepository):
    """Async repository for ChatMessage."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, ChatMessageORM)

    def _to_domain(self, orm_obj: ChatMessageORM | None) -> ChatMessage | None:
        if not orm_obj:
            return None
        return ChatMessage(
            id=orm_obj.id,
            session_id=orm_obj.session_id,
            role=orm_obj.role,
            content=orm_obj.content,
            tool_calls=orm_obj.tool_calls,
            latency_seconds=orm_obj.latency_seconds,
            token_count=orm_obj.token_count,
            created_at=orm_obj.created_at,
        )

    def _to_orm(self, domain_entity: ChatMessage) -> ChatMessageORM:
        return ChatMessageORM(
            id=domain_entity.id,
            session_id=domain_entity.session_id,
            role=domain_entity.role,
            content=domain_entity.content,
            tool_calls=domain_entity.tool_calls,
            latency_seconds=domain_entity.latency_seconds,
            token_count=domain_entity.token_count,
            created_at=domain_entity.created_at,
        )

    async def get_recent_messages(self, session_id: UUID, limit: int = 20) -> Sequence[ChatMessage]:
        stmt = select(ChatMessageORM).where(ChatMessageORM.session_id == session_id).order_by(ChatMessageORM.created_at.asc()).limit(limit)
        result = await self.session.execute(stmt)
        return [entity for row in result.scalars().all() if (entity := self._to_domain(row)) is not None]


class SQLRAGRepository(SQLAlchemyGenericRepository[RAGDocument, RAGDocumentORM], IRAGRepository):
    """Async repository for RAG documents and vector chunks."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, RAGDocumentORM)

    def _to_domain(self, orm_obj: RAGDocumentORM | None) -> RAGDocument | None:
        if not orm_obj:
            return None
        return RAGDocument(
            id=orm_obj.id,
            venue_id=orm_obj.venue_id,
            title=orm_obj.title,
            source_url=orm_obj.source_url,
            document_type=orm_obj.document_type,
            created_at=orm_obj.created_at,
        )

    def _to_orm(self, domain_entity: RAGDocument) -> RAGDocumentORM:
        return RAGDocumentORM(
            id=domain_entity.id,
            venue_id=domain_entity.venue_id,
            title=domain_entity.title,
            source_url=domain_entity.source_url,
            document_type=domain_entity.document_type,
            created_at=domain_entity.created_at,
        )

    async def search_similar_chunks(self, venue_id: UUID, query_embedding: Sequence[float], limit: int = 5) -> Sequence[RAGChunk]:
        stmt = select(RAGChunkORM).limit(limit)
        result = await self.session.execute(stmt)
        return [
            RAGChunk(id=row.id, document_id=row.document_id, content=row.content, embedding=None, metadata=row.metadata_json)
            for row in result.scalars().all()
        ]

    async def search_keyword_chunks(self, venue_id: UUID, query_text: str, limit: int = 5) -> Sequence[RAGChunk]:
        stmt = select(RAGChunkORM).where(RAGChunkORM.content.ilike(f"%{query_text[:20]}%")).limit(limit)
        result = await self.session.execute(stmt)
        return [
            RAGChunk(id=row.id, document_id=row.document_id, content=row.content, embedding=None, metadata=row.metadata_json)
            for row in result.scalars().all()
        ]


class SQLEmergencyRepository(SQLAlchemyGenericRepository[EmergencyAlert, EmergencyAlertORM], IEmergencyRepository):
    """Async repository for EmergencyAlerts."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, EmergencyAlertORM)

    def _to_domain(self, orm_obj: EmergencyAlertORM | None) -> EmergencyAlert | None:
        if not orm_obj:
            return None
        return EmergencyAlert(
            id=orm_obj.id,
            venue_id=orm_obj.venue_id,
            user_id=orm_obj.user_id,
            alert_type=orm_obj.alert_type,
            severity=orm_obj.severity,
            location=orm_obj.location,
            status=orm_obj.status,
            created_at=orm_obj.created_at,
        )

    def _to_orm(self, domain_entity: EmergencyAlert) -> EmergencyAlertORM:
        return EmergencyAlertORM(
            id=domain_entity.id,
            venue_id=domain_entity.venue_id,
            user_id=domain_entity.user_id,
            alert_type=domain_entity.alert_type,
            severity=domain_entity.severity,
            location=domain_entity.location,
            status=domain_entity.status,
            created_at=domain_entity.created_at,
        )

    async def get_active_alerts(self, venue_id: UUID) -> Sequence[EmergencyAlert]:
        stmt = select(EmergencyAlertORM).where(EmergencyAlertORM.venue_id == venue_id, EmergencyAlertORM.status == "ACTIVE")
        result = await self.session.execute(stmt)
        return [entity for row in result.scalars().all() if (entity := self._to_domain(row)) is not None]
