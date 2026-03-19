# Backend Project Structure

## Directory Layout

```
backend/
├── manage.py                       # Django CLI entrypoint
├── pyproject.toml                  # Dependencies and tool config
├── Dockerfile                      # Container build
│
├── config/                         # Django project configuration
│   ├── settings/
│   │   ├── base.py                 # Shared settings (DB, apps, Dramatiq)
│   │   ├── dev.py                  # Development overrides (DEBUG=True)
│   │   └── test.py                 # Test overrides (stub broker, test DB)
│   ├── urls.py                     # URL routing + NinjaAPI mount point
│   ├── wsgi.py                     # WSGI application
│   └── asgi.py                     # ASGI application
│
├── shared/                         # Shared kernel (cross-cutting concerns)
│   ├── models.py                   # UUIDModel, TimestampedModel base classes
│   ├── exceptions.py               # DomainException, NotFoundError, InvalidTransitionError
│   ├── middleware.py               # RequestIDMiddleware (X-Request-ID tracing)
│   └── apps.py                     # App config
│
├── tickets/                        # Bounded Context: Ticket Lifecycle
│   ├── models.py                   # Ticket, Comment, status/priority enums, state machine
│   ├── services.py                 # create_ticket, transition_ticket, add_comment, etc.
│   ├── api.py                      # Django Ninja router — /api/tickets/
│   ├── schemas.py                  # TicketIn, TicketOut, TicketDetailOut, CommentIn/Out
│   ├── tasks.py                    # Dramatiq actor: on_ticket_created
│   ├── admin.py                    # Django admin registration
│   ├── migrations/                 # Database migrations
│   └── tests/
│       ├── factories.py            # factory_boy factories
│       ├── test_models.py          # Domain method tests
│       ├── test_services.py        # Service layer tests
│       └── test_api.py             # HTTP integration tests
│
├── triage/                         # Bounded Context: AI Classification
│   ├── models.py                   # Classification model
│   ├── services.py                 # classify_ticket (idempotent), get_classification
│   ├── api.py                      # Django Ninja router — /api/triage/
│   ├── schemas.py                  # ClassificationOut
│   ├── tasks.py                    # Dramatiq actor: classify_ticket_task
│   ├── admin.py                    # Django admin
│   ├── migrations/
│   └── tests/
│
└── teams/                          # Bounded Context: Routing & Assignment
    ├── models.py                   # Team, TeamMember, RoutingRule, Assignment
    ├── services.py                 # route_ticket, list_teams, get_assignment
    ├── api.py                      # Django Ninja router — /api/teams/
    ├── schemas.py                  # TeamOut, AssignmentOut
    ├── tasks.py                    # Dramatiq actor: route_ticket_task
    ├── admin.py                    # Django admin
    ├── migrations/
    └── tests/
```

## Layer Pattern

Each bounded context follows a consistent layered architecture:

| File | Role | .NET Equivalent |
|------|------|-----------------|
| `api.py` | HTTP endpoints. Validates input, calls service, returns schema. | `[ApiController]` / Minimal API |
| `schemas.py` | Request/response types (Pydantic). | DTOs / Request/Response records |
| `services.py` | Business logic. All ORM queries and side effects. | Service classes (e.g., `ITicketService`) |
| `models.py` | Domain entities with ORM mapping and domain methods. | EF Core entities with domain logic |
| `tasks.py` | Async background jobs (Dramatiq actors). | Hangfire / Background Services |
| `tests/` | Pytest tests per layer. | xUnit / NUnit test projects |
| `admin.py` | Django admin panel configuration. | (no direct equivalent) |

## Adding a New Bounded Context

1. Create the app directory: `mkdir -p backend/newapp/{tests,migrations}`
2. Create the standard files: `__init__.py`, `apps.py`, `models.py`, `services.py`, `api.py`, `schemas.py`, `tasks.py`, `admin.py`
3. Add `__init__.py` to `migrations/` and `tests/`
4. Register in `config/settings/base.py` → `INSTALLED_APPS`
5. Add router in `config/urls.py` → `api.add_router("/newapp/", newapp_router)`
6. Run `make makemigrations` and `make migrate`

## Naming Conventions

| Item | Convention | Example |
|------|-----------|---------|
| App names | Plural nouns | `tickets`, `teams` |
| Model classes | Singular PascalCase | `Ticket`, `RoutingRule` |
| Service functions | verb_noun | `create_ticket()`, `route_ticket()` |
| Schemas | NounIn / NounOut | `TicketIn`, `TicketOut` |
| Tasks | verb_noun_task | `classify_ticket_task` |
| Test files | test_layer | `test_models.py`, `test_api.py` |
