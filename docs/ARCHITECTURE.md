# System Architecture & Technical Specifications

The **Cultural & Venue Smart Copilot Platform** is built from the ground up to support high-scale, real-time indoor navigation and operations management for museums, galleries, and exhibition spaces. It strictly implements **Clean Architecture**, **Domain-Driven Design (DDD)**, and **SOLID** principles.

---

## 1. Clean Architecture Layer Separation

```mermaid
graph TD
    subgraph Presentation Layer ["Presentation Layer (FastAPI / Middlewares)"]
        Router["API v1 Routers (/auth, /venues, /parking, /assistant)"]
        Middlewares["SecurityHeaders, SizeLimit, Logging, ExceptionHandler"]
        Deps["Dependency Injection Container (deps.py)"]
    end

    subgraph Application Layer ["Application Layer (DTOs & Use Cases)"]
        Services["Domain Services (AuthService, VenueService, ParkingService, AssistantService)"]
        Schemas["Pydantic v2 Schemas & DTOs"]
        LangGraph["LangGraph Multi-Agent Orchestrator (Orchestrator, Navigation, Parking, Emergency)"]
    end

    subgraph Domain Layer ["Domain Layer (Pure Business Logic - Zero Dependencies)"]
        Entities["Domain Entities (User, Venue, POI, ParkingLot, Reservation, Session)"]
        RepoInterfaces["Repository Interfaces (IUserRepository, IVenueRepository, ISessionRepository)"]
        Exceptions["Pure Domain Exceptions (DomainException, UnauthorizedException)"]
    end

    subgraph Infrastructure Layer ["Infrastructure Layer (Persistence & External Providers)"]
        DB["Async PostgreSQL (SQLAlchemy 2.0 ORM + Alembic)"]
        Redis["Redis Client Pool (JTI Blacklist, Rate Limiting, Session Cache)"]
        AI["ProviderFactory (GeminiProvider with OpenAI Fallback + RAG Hybrid Search)"]
        Guardrails["PromptGuard, PIIDetector, HallucinationGuard"]
    end

    Router --> Deps
    Middlewares --> Router
    Deps --> Services
    Services --> RepoInterfaces
    LangGraph --> Services
    RepoInterfaces -. implemented by .-> DB & Redis
    Services --> Guardrails & AI
```

---

## 2. Entity-Relationship (ER) Diagram

```mermaid
erDiagram
    USERS ||--o{ REFRESH_TOKENS : owns
    USERS ||--o{ PARKING_RESERVATIONS : makes
    USERS ||--o{ SESSIONS : initiates
    USERS ||--o{ AUDIT_LOGS : generates
    VENUES ||--o{ POINTS_OF_INTEREST : contains
    VENUES ||--o{ PARKING_LOTS : operates
    VENUES ||--o{ RAG_DOCUMENTS : indexes
    VENUES ||--o{ EMERGENCY_ALERTS : broadcasts
    PARKING_LOTS ||--o{ PARKING_RESERVATIONS : manages
    SESSIONS ||--o{ CHAT_MESSAGES : stores

    USERS {
        uuid id PK
        string email UK
        string full_name
        string role
        boolean is_active
        timestamp created_at
    }

    VENUES {
        uuid id PK
        string name
        string address
        int total_capacity
        int current_occupancy
        jsonb boundary_coordinates
    }

    POINTS_OF_INTEREST {
        uuid id PK
        uuid venue_id FK
        string name
        string category
        int floor_level
        boolean is_accessible
        jsonb coordinates
    }

    PARKING_LOTS {
        uuid id PK
        uuid venue_id FK
        string lot_name
        int total_spots
        int available_spots
        int accessible_spots_total
        int accessible_spots_available
        boolean has_ev_charging
    }
```

---

## 3. LangGraph Multi-Agent Interaction Sequence

```mermaid
sequenceDiagram
    autonumber
    actor User as Client (Frontend UI)
    participant API as FastAPI Router (/chat)
    participant Guard as PromptGuard & PIIDetector
    participant Orch as OrchestratorAgent
    participant Sub as Specialized Sub-Agent (Navigation/Parking)
    participant RAG as RAG Hybrid Vector Store
    participant LLM as ProviderFactory (Gemini/OpenAI)
    participant Halluc as HallucinationGuard

    User->>API: POST /api/v1/assistant/chat { message, venue_id }
    API->>Guard: Inspect & Redact PII (PromptGuard.inspect + PIIDetector.mask_pii)
    Guard-->>API: Safe, redacted input query
    API->>Orch: execute(safe_query, session_context)
    Orch->>Orch: Analyze user intent via system prompt
    Orch->>Sub: Dispatch task to specialized agent (e.g., NavigationAgent)
    Sub->>RAG: search_hybrid(query, venue_id, top_k=3)
    RAG-->>Sub: Return top verified venue guide chunks
    Sub->>LLM: generate_with_tools(system_prompt, safe_query, tools=[calculate_route])
    LLM-->>Sub: Tool call / Natural language response
    Sub->>Halluc: verify_grounding(response, retrieved_chunks)
    Halluc-->>Sub: Grounding score (0.0 to 1.0)
    Sub-->>Orch: Synthesized agent result + grounding score
    Orch-->>API: Final multi-agent response packet
    API-->>User: JSON Response { response, active_agents, grounding_score }
```
