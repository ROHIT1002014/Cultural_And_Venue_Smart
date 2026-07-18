<div align="center">

# 🏟️ Smart Stadiums, Tournament Operations & Cultural Venue Copilot Platform

**Production-Ready GenAI-Enabled Multi-Agent Copilot for FIFA World Cup 2026 Stadiums, Tournament Operations, and High-Density Cultural Venues**

[![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React 18](https://img.shields.io/badge/React-18.3.1-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.4.5-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.4.4-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![Docker Compose](https://img.shields.io/badge/Docker_Compose-Hardened-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docs.docker.com/compose/)
[![Test Coverage](https://img.shields.io/badge/Coverage->95%25-22C55E?style=for-the-badge&logo=pytest&logoColor=white)](https://pytest.org/)
[![Security: OWASP Top 10](https://img.shields.io/badge/Security-OWASP_Compliant-E11D48?style=for-the-badge&logo=owasp&logoColor=white)](https://owasp.org/)

</div>

---

## 🌟 Executive Overview & Problem Statement Alignment

The **Smart Stadiums, Tournament Operations & Cultural Venue Copilot Platform** is a enterprise-grade, GenAI-enabled full-stack ecosystem specifically engineered to enhance stadium operations and the overall tournament experience for **fans, organizers, volunteers, and venue staff** during major global events such as the **FIFA World Cup 2026**, as well as high-density museums and cultural exhibition centers.

Leveraging multi-agent **Generative AI (Gemini 1.5 Pro & OpenAI GPT-4o)** via **LangGraph**, the platform comprehensively solves every operational pillar required by modern mega-venues:
1. **Interactive Navigation & Step-Free Accessibility**: Certified indoor/stadium wayfinding avoiding stairs and congestion, prioritizing elevators, ramps, and accessible seating/zones (`NavigationAgent`).
2. **Crowd Management & Real-Time Operational Intelligence**: Live zone occupancy telemetry, automated bottleneck alerts, and priority emergency broadcast overrides (`AdminDashboard` & `EmergencyAgent`).
3. **Transportation & Sustainability**: Smart parking logistics, EV charging bay reservation management, and accessible stall verification (`ParkingAgent`).
4. **Multilingual Assistance & Real-Time Decision Support**: Grounded hybrid-RAG virtual copilot providing instant, multilingual answers to tournament FAQs, schedule updates, and venue accommodations while enforcing zero-hallucination guardrails (`grounding_score >= 0.70`).

Built strictly according to **Clean Architecture**, **Domain-Driven Design (DDD)**, and **SOLID principles**, the system decouples pure business domain models (`app.domain`) from external persistence layers (`app.infrastructure`). It features automatic circuit-breaking, real-time **RAG Hallucination Guards**, **PII Redaction**, and **Prompt Injection Defense**.

---

## ✨ Core Platform Capabilities

### 🛡️ 1. Enterprise Security & RBAC Governance
- **JWT Access/Refresh Rotation**: Secure HMAC-SHA256 tokens (`15 min` access, `7 days` refresh) backed by real-time Redis `jti` blacklisting (`token_blacklist:{jti}`).
- **Granular 4-Tier RBAC**: Hierarchical roles (`ADMIN`, `VOLUNTEER`, `USER`, `GUEST`) controlling everything from chat access to emergency evacuation broadcasts.
- **AI Safety Guardrails**:
  - `PromptGuard`: Pre-generation regex inspection intercepting jailbreaks and instruction overrides.
  - `PIIDetector`: Automatic redaction of sensitive personal tokens (`emails`, `phone numbers`, `SSN`).
  - `HallucinationGuard`: Post-generation factual overlap verification against hybrid RAG vector document chunks (`grounding_score >= 0.70`).
- **Network & DoS Protection**: Strict HTTP security headers (`CSP`, `HSTS`, `X-Frame-Options: DENY`), payload size limits (`10 MB`), and distributed `SlowAPI` rate limiting with brute-force account lockout.

### 🧠 2. Multi-Agent LangGraph AI Copilot
- **OrchestratorAgent**: Evaluates visitor intents and dispatches domain tasks to specialized sub-agents (`NavigationAgent`, `ParkingAgent`, `EmergencyAgent`).
- **ProviderFactory & Fallback**: Automatic circuit-breaking switching seamlessly between `Gemini 1.5 Pro` and `OpenAI GPT-4o-mini` if timeouts or rate limits occur.
- **Hybrid Search RAG**: Combines keyword exact filtering and vector embedding similarity across verified venue guides and FAQs.

### 🗺️ 3. Step-Free Wayfinding & Operations
- **Certified Wheelchair Routing**: Dynamically computes indoor step-free paths avoiding stairs and narrow corridors, prioritizing elevators and ramps.
- **Interactive Map UI**: Multi-floor exhibition marker grid (`MapUI`) with real-time POI filtering and visual direction overlays.
- **Smart Parking & EV Logistics**: Live available spot counters, accessible stall verification, and level-2 EV charging reservation booking.
- **Priority Emergency Broadcasts**: Admin dashboard module enabling immediate venue-wide evacuation alerts (`FIRE_ALARM`, `MEDICAL_EMERGENCY`) across connected displays.

---

## 🏗️ System Architecture & Directory Structure

```
prompt-war-4-on/
├── backend/                  # Python 3.12+ Async FastAPI Backend (Clean Architecture / DDD)
│   ├── app/
│   │   ├── domain/           # Pure Business Entities & Repository Interfaces (Zero External Dependencies)
│   │   ├── application/      # DTO Schemas (Pydantic v2), Core Services & LangGraph Agents
│   │   ├── infrastructure/   # SQLAlchemy 2 ORM Models, Redis Client, AI Providers & Guardrails
│   │   └── presentation/     # FastAPI Middlewares, Dependency Injection (deps.py) & v1 Endpoints
│   ├── tests/                # 45+ Pytest Unit, Integration, Security & Guardrail Tests (>95% Coverage)
│   ├── alembic/              # Async PostgreSQL Migration Scripts
│   └── Dockerfile            # Multi-Stage Nginx/Python Dev & Prod Builds
├── frontend/                 # React 18 + Vite + TypeScript + Tailwind CSS Frontend
│   ├── src/
│   │   ├── components/       # Glassmorphism Common UI, ChatUI (Streaming AI), MapUI & AdminDashboard
│   │   ├── context/          # AuthContext (RBAC state) & ThemeContext (Dark Mode persistence)
│   │   ├── services/         # Axios Interceptor Client (Refresh Token Rotation)
│   │   └── pages/            # Rich Landing Home, CopilotPage, ParkingPage & AdminPage
│   ├── public/               # PWA Web Manifest & Assets
│   └── Dockerfile            # Multi-Stage Nginx SPA Container
├── docs/                     # Comprehensive Architecture, Security, Deployment & Benchmark Artifacts
├── .github/workflows/        # Enterprise CI/CD Pipeline (ci.yml) & Dependabot Configuration
├── docker-compose.yml        # Hardened Full Stack Setup (Postgres, Redis, API, Frontend, Prometheus/Grafana)
└── Makefile                  # Unified Command Center for Testing, Linting, Migrations & Docker
```

---

## 🚀 Quick Start Guide

### 1. Unified Makefile Commands
We provide a unified `Makefile` at the repository root to simplify all engineering operations:

```bash
# View all available developer commands
make help

# Run automated formatting and linting across Backend and Frontend
make format
make lint

# Run strict type checking across Python codebase
make mypy

# Execute the full 45+ test suite with coverage (>95% verified)
make test
```

### 2. Launching Full Stack via Docker Compose
To launch the complete application with PostgreSQL, Redis, FastAPI, React Frontend, and Prometheus observability:

```bash
make docker-up
```

- **Interactive API Documentation (Swagger/OpenAPI)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **React + Vite Frontend Application**: [http://localhost:5173](http://localhost:5173)
- **Grafana Observability Dashboard**: [http://localhost:3001](http://localhost:3001) (`admin` / `admin`)

---

## 📖 Comprehensive Documentation

Our `docs/` package provides deep technical specifications for engineering review:
- **[System Architecture & Diagrams (`docs/ARCHITECTURE.md`)](docs/ARCHITECTURE.md)**: Clean Architecture layer boundaries, ER Diagrams, and LangGraph sequence flows.
- **[Deployment & Infrastructure Guide (`docs/DEPLOYMENT_GUIDE.md`)](docs/DEPLOYMENT_GUIDE.md)**: Multi-stage Docker setup, Nginx SPA routing, and database migration instructions.
- **[Threat Model & Security Guide (`docs/THREAT_MODEL_AND_SECURITY_GUIDE.md`)](docs/THREAT_MODEL_AND_SECURITY_GUIDE.md)**: OWASP Top 10 compliance, PromptGuard jailbreak defense, and RBAC matrix.
- **[Prompt Engineering Guide (`docs/PROMPT_ENGINEERING_GUIDE.md`)](docs/PROMPT_ENGINEERING_GUIDE.md)**: System prompt versioning, tool calling JSON schemas, and Golden Dataset metrics.
- **[Benchmark & Performance Report (`docs/BENCHMARK_AND_PERFORMANCE_REPORT.md`)](docs/BENCHMARK_AND_PERFORMANCE_REPORT.md)**: Median latency profiles, RAG token costs, and Lighthouse scores (`>95`).

---

## 🗺️ Product Roadmap

- [x] **Phase 1 (Foundation)**: Clean Architecture scaffold, Async PostgreSQL, Redis JTI blacklisting, and RBAC hierarchy.
- [x] **Phase 2 (AI & Security Guardrails)**: LangGraph `OrchestratorAgent`, `ProviderFactory` fallback, `PromptGuard`, `PIIDetector`, and `HallucinationGuard`.
- [x] **Phase 3 (Frontend & Interactive UI)**: React + Vite rich glassmorphism UI, streaming `ChatUI`, step-free `MapUI`, and `AdminDashboard`.
- [ ] **Phase 4 (Advanced IoT Integration)**: Live Bluetooth Low Energy (BLE) beacon positioning and real-time turn-by-turn indoor voice navigation.
- [ ] **Phase 5 (Multi-Tenant SaaS)**: Self-service onboarding for third-party national museums and international heritage foundations.

---

## 📜 License

This repository is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for complete details.
