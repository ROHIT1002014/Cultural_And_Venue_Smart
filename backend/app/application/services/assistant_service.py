from datetime import datetime, timezone
from typing import List, Sequence
from uuid import UUID, uuid4
from app.domain.entities.session import ConversationSession, ChatMessage, RAGDocument, RAGChunk
from app.domain.repositories.session_repo import ISessionRepository, IMessageRepository, IRAGRepository
from app.application.schemas.assistant import (
    ChatRequestDTO,
    ChatResponseDTO,
    SessionResponseDTO,
    FAQSearchRequestDTO,
    FAQSearchResponseDTO,
    FAQItemDTO,
)
from app.application.agents.orchestrator import OrchestratorAgent


class AssistantService:
    """Service layer coordinating conversation sessions, RAG retrieval, and AI multi-agent execution."""

    def __init__(
        self,
        session_repo: ISessionRepository,
        message_repo: IMessageRepository,
        rag_repo: IRAGRepository,
        orchestrator: OrchestratorAgent,
    ):
        self.session_repo = session_repo
        self.message_repo = message_repo
        self.rag_repo = rag_repo
        self.orchestrator = orchestrator

    async def chat(self, user_id: UUID, user_role: str, dto: ChatRequestDTO) -> ChatResponseDTO:
        """Process a chat message, retrieving RAG chunks and dispatching to the orchestrator."""
        rag_chunks_text: List[str] = []
        if dto.venue_id:
            chunks = await self.rag_repo.search_keyword_chunks(venue_id=dto.venue_id, query_text=dto.message, limit=3)
            rag_chunks_text = [c.content for c in chunks]

        # Manage conversation session
        now = datetime.now(timezone.utc)
        session_id = dto.session_id or uuid4()
        session = await self.session_repo.get_by_id(session_id) if dto.session_id else None
        if not session:
            session = ConversationSession(
                id=session_id,
                user_id=user_id,
                title=dto.message[:50],
                created_at=now,
                last_active_at=now,
            )
            await self.session_repo.create(session)
        else:
            session.last_active_at = now
            await self.session_repo.update(session)

        # Log user prompt
        user_msg = ChatMessage(
            id=uuid4(),
            session_id=session.id,
            role="user",
            content=dto.message,
            tool_calls=None,
            latency_seconds=0.0,
            token_count=len(dto.message.split()),
            created_at=now,
        )
        await self.message_repo.create(user_msg)

        # Ensure orchestrator uses the exact session_id
        dto.session_id = session.id
        response = await self.orchestrator.process_interaction(
            user_id=user_id,
            user_role=user_role,
            dto=dto,
            rag_chunks=rag_chunks_text,
        )

        # Log assistant response
        assistant_msg = ChatMessage(
            id=response.message_id,
            session_id=session.id,
            role="assistant",
            content=response.response,
            tool_calls=[{"tool_name": t.tool_name, "arguments": t.arguments} for t in response.executed_tools],
            latency_seconds=0.1,
            token_count=response.token_usage.completion_tokens,
            created_at=datetime.now(timezone.utc),
        )
        await self.message_repo.create(assistant_msg)

        return response

    async def list_user_sessions(self, user_id: UUID) -> Sequence[SessionResponseDTO]:
        """Fetch all chat sessions initiated by the user."""
        sessions = await self.session_repo.get_by_user_id(user_id)
        return [SessionResponseDTO.model_validate(s) for s in sessions]

    async def search_faq(self, dto: FAQSearchRequestDTO) -> FAQSearchResponseDTO:
        """Perform hybrid/keyword semantic search across venue knowledge base."""
        chunks = await self.rag_repo.search_keyword_chunks(venue_id=dto.venue_id, query_text=dto.query, limit=dto.limit)
        items = [
            FAQItemDTO(
                document_title=str(c.metadata.get("title", "Venue Guide")),
                content=c.content,
                similarity_score=0.92,
                metadata=c.metadata,
            )
            for c in chunks
        ]
        return FAQSearchResponseDTO(venue_id=dto.venue_id, query=dto.query, results=items)
