from collections.abc import Sequence
from typing import Annotated

from fastapi import APIRouter, Depends, Request

from app.application.schemas.assistant import (
    ChatRequestDTO,
    ChatResponseDTO,
    FAQSearchRequestDTO,
    FAQSearchResponseDTO,
    SessionResponseDTO,
)
from app.application.services.assistant_service import AssistantService
from app.core.security.rate_limiter import limiter
from app.domain.entities.user import User
from app.presentation.deps import get_assistant_service, get_current_user

router = APIRouter(prefix="/assistant", tags=["AI Copilot & Multi-Agent Engine"])


@router.post("/chat", response_model=ChatResponseDTO)
@limiter.limit("30/minute")
async def chat_with_copilot(
    request: Request,
    dto: ChatRequestDTO,
    current_user: Annotated[User, Depends(get_current_user)],
    assistant_service: Annotated[AssistantService, Depends(get_assistant_service)],
) -> ChatResponseDTO:
    """Process a natural language interaction with the multi-agent AI copilot (with RAG grounding and safety checks)."""
    return await assistant_service.chat(user_id=current_user.id, user_role=current_user.role, dto=dto)


@router.get("/sessions", response_model=Sequence[SessionResponseDTO])
async def list_my_sessions(
    current_user: Annotated[User, Depends(get_current_user)],
    assistant_service: Annotated[AssistantService, Depends(get_assistant_service)],
) -> Sequence[SessionResponseDTO]:
    """Retrieve all past conversation sessions of the authenticated user."""
    return await assistant_service.list_user_sessions(user_id=current_user.id)


@router.post("/faq/search", response_model=FAQSearchResponseDTO)
async def search_faq(
    dto: FAQSearchRequestDTO,
    assistant_service: Annotated[AssistantService, Depends(get_assistant_service)],
) -> FAQSearchResponseDTO:
    """Perform hybrid keyword/vector similarity search against verified venue guides and FAQs."""
    return await assistant_service.search_faq(dto=dto)
