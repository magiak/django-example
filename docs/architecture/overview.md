# System Overview

## Architecture Diagram

```
┌─────────────────┐     HTTP/JSON      ┌──────────────────────────────────┐
│                 │ ──────────────────> │         Django Ninja API         │
│   React SPA     │                    │          :8000                   │
│   (Vite)        │ <────────────────── │                                  │
│   :5173         │                    │  ┌─────────┬─────────┬────────┐ │
└─────────────────┘                    │  │ tickets │ triage  │ teams  │ │
                                       │  │  api    │  api    │  api   │ │
                                       │  ├─────────┼─────────┼────────┤ │
                                       │  │ services│ services│services│ │
                                       │  ├─────────┼─────────┼────────┤ │
                                       │  │ models  │ models  │ models │ │
                                       │  └─────────┴─────────┴────────┘ │
                                       │         shared kernel           │
                                       └──────────┬──────────┬──────────┘
                                                  │          │
                                           ┌──────▼──┐  ┌────▼─────┐
                                           │Postgres │  │  Redis   │
                                           │  :5432  │  │  :6379   │
                                           └─────────┘  └────┬─────┘
                                                             │
                                                    ┌────────▼────────┐
                                                    │ Dramatiq Worker │
                                                    │ (background)    │
                                                    └─────────────────┘
```

## Bounded Contexts

The backend is organized as three Django apps, each representing a DDD bounded context with clear responsibilities and boundaries.

| Context | Responsibility | Owns |
|---------|---------------|------|
| **tickets** | Ticket lifecycle — creation, status transitions, comments | `Ticket`, `Comment` |
| **triage** | AI classification — LLM integration, idempotent processing | `Classification` |
| **teams** | Routing & assignment — rule-based team matching | `Team`, `TeamMember`, `RoutingRule`, `Assignment` |

### Cross-Context Communication Rules

1. Contexts communicate through **Dramatiq task enqueuing** with primitive IDs (strings/UUIDs), never ORM objects.
2. A context may **read** another context's models by importing them directly (read-only access by ID).
3. A context must **never** import another context's `services.py` — this keeps business logic boundaries clean.

## Layer Pattern

Each bounded context follows the same layered structure:

```
api.py        Thin HTTP layer. Validates input (schemas), calls service, returns response.
    ↓
services.py   All business logic. Receives plain Python args, returns model instances.
    ↓
models.py     Django ORM models with domain methods (e.g., Ticket.transition_to()).
    ↓
tasks.py      Dramatiq actors. Receive primitive args (ticket_id: str), call services.
schemas.py    Pydantic schemas for typed request/response validation.
tests/        Unit + integration tests per layer.
```

**Key principle:** API endpoints are thin wrappers. They validate input, delegate to a service function, and format the output. All business rules, ORM queries, and side effects live in `services.py`.

## Tech Stack

| Component | Choice | Version |
|-----------|--------|---------|
| Language | Python | 3.12+ |
| Web Framework | Django | 5.1 |
| API Framework | Django Ninja | 1.3 |
| Database | PostgreSQL | 16 |
| Database Driver | psycopg | 3.2 |
| Task Queue | Dramatiq | 1.17 |
| Task Broker | Redis | 7 |
| Logging | structlog | 24.x |
| Frontend | React + TypeScript | 19.x |
| CSS | Tailwind CSS | 3.4 |
| Bundler | Vite | 6.x |
| Testing | pytest + factory_boy | 8.x |
| Linting | ruff | 0.8 |
| Type Checking | mypy + django-stubs | 1.13 |
| CI/CD | GitHub Actions | — |
