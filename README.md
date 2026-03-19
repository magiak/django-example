# Support Ticket Triage System

AI-powered support ticket classification, routing, and lifecycle management built with Django, React, and PostgreSQL.

## Architecture

```
React SPA (Vite)  →  Django Ninja API  →  PostgreSQL
     :5173              :8000               :5432
                         ↕
                    Dramatiq Worker (Redis)
```

Three bounded contexts following DDD principles:

| Context | Responsibility |
|---------|---------------|
| **tickets** | Ticket lifecycle — CRUD, status transitions, comments |
| **triage** | AI classification via LLM (async, idempotent) |
| **teams** | Rule-based routing and team assignment |

Each context follows a consistent layer pattern: `api.py` → `services.py` → `models.py` → `tasks.py`

## Tech Stack

| Layer | Technology |
|-------|-----------|
| API | Django 5.1 + Django Ninja |
| Database | PostgreSQL 16 |
| Background Jobs | Dramatiq + Redis |
| Frontend | React 19 + TypeScript + Tailwind |
| Containerization | Docker Compose |
| CI/CD | GitHub Actions |
| Testing | pytest + factory_boy |
| Linting | ruff + mypy |

## Quick Start

```bash
# Build and start all services
make build
make up

# Run database migrations
make migrate

# Verify
open http://localhost:8000/api/docs    # Swagger UI
open http://localhost:5173             # React dashboard
```

## Development

```bash
make test            # Run tests
make lint            # Lint check
make fmt             # Auto-format
make makemigrations  # After model changes
make migrate         # Apply migrations
make logs            # Tail container logs
make shell           # Django interactive shell
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/tickets/` | Create ticket |
| `GET` | `/api/tickets/` | List tickets (filterable) |
| `GET` | `/api/tickets/{id}` | Get ticket detail |
| `PATCH` | `/api/tickets/{id}/status` | Transition status |
| `POST` | `/api/tickets/{id}/comments` | Add comment |
| `GET` | `/api/triage/{id}/classification` | Get AI classification |
| `GET` | `/api/teams/` | List teams |
| `GET` | `/api/teams/assignments/{id}` | Get ticket assignment |

Full API docs with examples: [docs/api/endpoints.md](docs/api/endpoints.md)

## Documentation

- [Getting Started](docs/getting-started.md)
- [Architecture Overview](docs/architecture/overview.md)
- [Domain Model](docs/architecture/domain-model.md)
- [Architecture Decisions (ADRs)](docs/architecture/decisions.md)
- [Backend Structure](docs/backend/project-structure.md)
- [Docker & Operations](docs/operations/docker.md)
- [CI/CD Pipeline](docs/operations/ci-cd.md)

## Project Structure

```
├── backend/
│   ├── config/          # Django settings, URLs, WSGI
│   ├── shared/          # Base models, exceptions, middleware
│   ├── tickets/         # Ticket lifecycle (bounded context)
│   ├── triage/          # AI classification (bounded context)
│   └── teams/           # Routing & assignment (bounded context)
├── frontend/
│   └── src/             # React + TypeScript + Tailwind
├── docs/                # Project documentation
├── docker-compose.yml
├── Makefile
└── .github/workflows/   # CI pipeline
```
