# Contributing to Cultural & Venue Smart Copilot Platform

Thank you for investing your time in contributing to the **Cultural & Venue Smart Copilot Platform**! We adhere strictly to Clean Architecture, Domain-Driven Design (DDD), SOLID principles, and OWASP Top 10 security standards.

## Architecture Guidelines

Our backend codebase is organized into four distinct layers with unidirectional dependencies:
1. **`app.domain` (Zero Dependencies)**: Contains pure business domain entities and abstract repository/service interfaces. Never import FastAPI, SQLAlchemy, or external SDKs here.
2. **`app.application`**: Orchestrates use cases, DTO schemas (`pydantic`), and LangGraph agent pipelines (`OrchestratorAgent`, `sub_agents`). Depends only on `domain`.
3. **`app.infrastructure`**: Concrete implementations of domain interfaces (`SQLAlchemyGenericRepository`, `RedisClient`, `GeminiProvider`).
4. **`app.presentation`**: FastAPI routers, middleware (`SecurityHeadersMiddleware`), and dependency injection container (`deps.py`).

## Code Quality & Testing Standards

Before submitting a pull request, ensure your branch passes all local checks via our unified `Makefile`:

```bash
# Run auto-formatting and linting
make format
make lint

# Run strict Python type checking
make mypy

# Execute full 45+ test suite with coverage (>95% required)
make test
```

### Pull Request Checklist
- [ ] Every new endpoint includes formal request/response DTO schemas (`Pydantic v2`).
- [ ] Every domain operation is covered by unit and integration tests (`tests/`).
- [ ] Security guardrails (`PromptGuard`, `PIIDetector`, `sanitize_string`) are verified for any AI/user input changes.
- [ ] No TODOs, placeholder code, or hardcoded secrets are introduced.
- [ ] Docstrings and type annotations (`Python 3.12+`) are complete.
