# Deployment Guide (Docker Compose & Production Environments)

This guide provides step-by-step instructions for deploying the **Cultural & Venue Smart Copilot Platform** across local development environments, staging servers, and hardened production clusters.

---

## 1. Environment Configuration (`.env`)

Before starting any stack, ensure your environment variables are securely configured. Copy `backend/.env.example` to `backend/.env` (or `.env.prod`) and verify key parameters:

```ini
# Core Application
PROJECT_NAME="Cultural & Venue Smart Copilot"
ENVIRONMENT="production"
LOG_LEVEL="INFO"
ALLOWED_ORIGINS="https://app.cultural-copilot.org,https://admin.cultural-copilot.org"

# Database & Cache
DATABASE_URL="postgresql+asyncpg://postgres_user:secure_password_here@db:5432/cultural_copilot_prod"
REDIS_URL="redis://:secure_redis_pass@redis:6379/0"
REDIS_PASSWORD="secure_redis_pass"

# Security Secrets (Must be 32+ characters high entropy)
JWT_SECRET_KEY="replace_this_with_a_64_char_hex_random_secret_string"
JWT_ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# AI Providers & Keys
OPENAI_API_KEY="sk-your-openai-api-key-here"
GEMINI_API_KEY="AIzaSy-your-google-gemini-api-key-here"
DEFAULT_AI_PROVIDER="gemini" # Options: gemini, openai
FALLBACK_AI_PROVIDER="openai"
```

---

## 2. Production Deployment via Hardened Docker Compose

For production deployments on virtual machines or bare-metal servers, we use our multi-stage, least-privilege `docker-compose.prod.yml` configuration:

```bash
# 1. Build and launch the production container stack in detached mode
docker compose -f docker-compose.prod.yml up -d --build

# 2. Verify container health status and restart policies
docker compose -f docker-compose.prod.yml ps

# 3. Apply latest async database migrations via Alembic
docker exec -it cultural_copilot_backend_prod alembic upgrade head
```

### Security Options Enabled in Production Container Stack:
- **`read_only: true`**: Root filesystem of backend containers is mounted read-only to prevent runtime malware modification.
- **`no-new-privileges:true`**: Prevents container processes from elevating permissions via setuid/setgid binaries.
- **Resource Limits**: CPU (`1.5` cores max) and Memory (`2GB` max) quotas prevent runaway processes or DoS memory exhaustion from impacting the host node.

---

## 3. Database Backup & Disaster Recovery Strategy

Automated PostgreSQL backups must be executed daily using continuous WAL archiving or pg_dump snapshots:
```bash
# Snapshot database backup command
docker exec -t cultural_copilot_postgres_prod pg_dump -U postgres_user -Fc cultural_copilot_prod > backup_$(date +%Y%m%d_%H%M%S).dump

# Restore from snapshot
docker exec -i cultural_copilot_postgres_prod pg_restore -U postgres_user -d cultural_copilot_prod --clean < backup_filename.dump
```
