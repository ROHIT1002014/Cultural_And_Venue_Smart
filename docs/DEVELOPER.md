# Developer Onboarding & Architecture Walkthrough

Welcome! This guide walks you through the internal mechanics of our **Clean Architecture** stack, explaining how to add new entities, repositories, use case services, API routes, and LangGraph AI sub-agents cleanly and safely.

---

## 1. Clean Architecture & DDD Flow Walkthrough

Whenever you implement a new domain feature (e.g., adding a `LostAndFound` service), you must build from the inside out:

```
[1. Domain Layer] -> [2. Application Layer] -> [3. Infrastructure Layer] -> [4. Presentation Layer]
```

### Step 1: Define the Domain Entity & Repository Interface (`app/domain/`)
In `app/domain/entities/lost_item.py`:
```python
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

@dataclass
class LostItem:
    id: UUID
    venue_id: UUID
    title: str
    description: str
    status: str  # "lost", "found", "claimed"
    created_at: datetime
```
In `app/domain/repositories/lost_item_repository.py`:
```python
from abc import ABC, abstractmethod
from uuid import UUID
from app.domain.entities.lost_item import LostItem

class ILostItemRepository(ABC):
    @abstractmethod
    async def get_by_id(self, item_id: UUID) -> LostItem | None:
        pass

    @abstractmethod
    async def create(self, item: LostItem) -> LostItem:
        pass
```

### Step 2: Implement the Service Use Case & DTOs (`app/application/`)
In `app/application/schemas/lost_item_dto.py`:
```python
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime

class LostItemCreateDTO(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., max_length=1000)

class LostItemResponseDTO(BaseModel):
    id: UUID
    title: str
    status: str
    created_at: datetime
```
In `app/application/services/lost_item_service.py`:
```python
from uuid import uuid4
from datetime import datetime, timezone
from app.domain.repositories.lost_item_repository import ILostItemRepository
from app.domain.entities.lost_item import LostItem
from app.application.schemas.lost_item_dto import LostItemCreateDTO, LostItemResponseDTO

class LostItemService:
    def __init__(self, repo: ILostItemRepository):
        self.repo = repo

    async def report_item(self, venue_id: UUID, dto: LostItemCreateDTO) -> LostItemResponseDTO:
        entity = LostItem(
            id=uuid4(),
            venue_id=venue_id,
            title=dto.title,
            description=dto.description,
            status="lost",
            created_at=datetime.now(timezone.utc)
        )
        saved = await self.repo.create(entity)
        return LostItemResponseDTO(id=saved.id, title=saved.title, status=saved.status, created_at=saved.created_at)
```

### Step 3: Implement ORM Model & Repository (`app/infrastructure/`)
In `app/infrastructure/models/lost_item_model.py` (SQLAlchemy 2.0 ORM class) and `app/infrastructure/repositories/sql_lost_item_repository.py` (inheriting from `ILostItemRepository` and `SQLAlchemyGenericRepository`).

### Step 4: Expose FastAPI Route & Dependency Injection (`app/presentation/`)
In `app/presentation/api/v1/endpoints/lost_items.py`, inject `LostItemService` via `app/presentation/deps.py` and enforce required RBAC permissions (`require_permissions("venue:read")`).

---

## 2. Adding a New AI Agent & Tool to LangGraph

To add a new sub-agent or tool to the multi-agent AI system:
1. **Define the Tool Method**: In `app/application/agents/tools.py`, create an async function with exact Pydantic parameter schemas and docstrings so the LLM provider can generate clean schema metadata (`Function Calling`).
2. **Register in Orchestrator Routing**: Update `OrchestratorAgent` in `app/application/agents/orchestrator.py` and `prompts.py` to recognize when to dispatch queries to the new sub-agent.
3. **Write Unit & Prompt Tests**: Add evaluation benchmarks in `tests/ai/` to ensure tool calling accuracy and check that output passes `HallucinationGuard`.
