# Changelog - Cultural & Venue Smart Copilot Platform

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-07-16

### Added
- **Clean Architecture Backend (`backend/`)**:
  - Implemented 4-layer DDD architecture: Core (`exceptions`, `config`, `security`), Domain (`entities`, `repositories`), Application (`schemas`, `services`, `agents`), and Infrastructure (`models`, `repositories`, `ai`).
  - Added FastAPI entry point with CORS, `SecurityHeadersMiddleware`, `RequestSizeLimitMiddleware`, and custom JSON domain exception handling.
  - Configured async PostgreSQL via SQLAlchemy 2.0 and Alembic migrations (`alembic.ini`, `env.py`).
  - Added Redis connection pool (`redis_client.py`) for JWT JTI blacklisting and distributed rate limiting.
- **Enterprise Security & Governance**:
  - Implemented JWT access and refresh token rotation with granular RBAC role hierarchy (`ADMIN`, `VOLUNTEER`, `USER`, `GUEST`).
  - Integrated `PromptGuard` regex-based jailbreak/injection interception.
  - Added `PIIDetector` for real-time redaction of emails, phone numbers, and SSNs.
  - Added `HallucinationGuard` verifying response grounding overlap against hybrid RAG vector chunks.
  - Configured SlowAPI rate limiter (`10/min` register, `20/min` login) with brute-force account locking after 5 failures.
  - Implemented strict input sanitization preventing XSS and SQL injection.
- **Multi-Agent AI Engine**:
  - Built LangGraph `OrchestratorAgent` routing natural language intents to specialized sub-agents (`NavigationAgent`, `ParkingAgent`, `EmergencyAgent`).
  - Created `ProviderFactory` with automatic circuit-breaking fallback (`GeminiProvider` -> `OpenAIProvider`).
  - Implemented `TokenCounter` and RAG hybrid search engine.
- **React + Vite Frontend (`frontend/`)**:
  - Created responsive, dark-mode first UI using Tailwind CSS (`glass-panel`, `glass-card`) and Outfit/Inter typography.
  - Built `ChatUI` with streaming simulated responses, active agent tags, RAG grounding indicators, and voice input trigger.
  - Built `MapUI` with multi-floor selection, POI marker grid, and certified step-free pathfinding directions.
  - Built `AdminDashboard` with zone crowd density status bars, parking lot live counters, and priority emergency broadcast modal.
  - Added Axios client with automatic JWT bearer attachment and refresh token rotation interceptor.
  - Added PWA offline web manifest (`manifest.json`) and Nginx production Dockerfile.
- **Test Suite & Observability**:
  - Generated 45+ pytest unit, integration, and security tests (`test_auth.py`, `test_security.py`, `test_venue.py`, `test_parking.py`, `test_agents.py`, `test_health.py`) with >95% target coverage using in-memory `aiosqlite`.
  - Configured multi-stage Docker builds (`docker-compose.yml`) with full observability stack (Prometheus, Grafana, Loki).
  - Created comprehensive documentation in `docs/`: `ARCHITECTURE.md`, `DEPLOYMENT_GUIDE.md`, `THREAT_MODEL_AND_SECURITY_GUIDE.md`, `PROMPT_ENGINEERING_GUIDE.md`, and `BENCHMARK_AND_PERFORMANCE_REPORT.md`.
