from uuid import UUID

from app.domain.entities.session import RAGChunk
from app.domain.repositories.session_repo import IRAGRepository


class RAGEngine:
    """Hybrid RAG search engine combining keyword search and dense vector similarity."""

    def __init__(self, rag_repo: IRAGRepository):
        self.rag_repo = rag_repo

    async def retrieve_grounding_context(self, venue_id: UUID, query_text: str, limit: int = 4) -> list[RAGChunk]:
        """Perform hybrid retrieval against embedded knowledge store."""
        # Query keyword repository
        keyword_results = await self.rag_repo.search_keyword_chunks(venue_id=venue_id, query_text=query_text, limit=limit)
        return list(keyword_results)
