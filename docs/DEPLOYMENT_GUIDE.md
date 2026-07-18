# Deployment Guide - Cultural & Venue Smart Copilot Platform

This deployment guide covers setting up the Cultural & Venue Smart Copilot Platform across local development, multi-stage Docker containerization, and enterprise production environments with full observability.

---

## 1. Local Environment Setup

### Prerequisites
- **Operating System**: Linux / macOS / Windows Subsystem for Linux (WSL2)
- **Runtime Dependencies**: Python 3.12+, Node.js 20+, Docker & Docker Compose
- **Package Managers**: `pip` / `poetry`, `npm`

### Quick Start via Unified Makefile
1. **Clone and Configure Environment**:
   ```bash
   cp backend/.env.example backend/.env
   # Update GEMINI_API_KEY and OPENAI_API_KEY inside backend/.env
   ```
2. **Start Local Development Servers**:
   ```bash
   # Terminal 1: Start FastAPI backend server with hot-reload (Port 8000)
   make dev-backend

   # Terminal 2: Start React + Vite frontend dev server (Port 5173)
   make dev-frontend
   ```

---

## 2. Docker Compose Production Infrastructure

Our `docker-compose.yml` orchestrates the entire application alongside an enterprise observability stack:

| Container | Service Name | Internal Port | Exposed Port | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **PostgreSQL 16** | `postgres` | `5432` | `5432` | Primary async transactional database |
| **Redis 7 Alpine** | `redis` | `6379` | `6379` | JWT JTI blacklist, distributed rate limits, session cache |
| **FastAPI Backend** | `backend` | `8000` | `8000` | Multi-agent AI engine and API endpoints |
| **Prometheus** | `prometheus` | `9090` | `9090` | Metrics scraping engine (`/metrics` endpoints) |
| **Grafana** | `grafana` | `3000` | `3001` | Visual monitoring dashboards (`admin/admin`) |
| **Loki** | `loki` | `3100` | `3100` | Structured log aggregation engine |

### Launching Docker Environment
```bash
# Build and launch all services in detached mode
make docker-up

# Check container health and logs
docker compose logs -f backend
```

---

## 3. Database Migrations & Backup Strategy

### Alembic Migration Management
```bash
# Run pending migrations to create initial tables
make migrate

# Generate a new migration after modifying ORM models in app/infrastructure/models/
make create-migration msg="add index on poi category"
```

### Automated Backup Procedure
To perform a live, zero-downtime backup of the PostgreSQL database inside Docker:
```bash
docker exec -t prompt-war-4-on-postgres-1 pg_dumpall -c -U postgres > backup_$(date +%Y%m%d_%H%M%S).sql
```
