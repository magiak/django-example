# Tickets — Bounded Context

**Location:** `backend/tickets/`

## Purpose

The tickets context is the core domain. It owns the Ticket aggregate — creation, status transitions, comments, and the full lifecycle from "open" to "closed."

## Domain Concepts

- **Ticket** — the central entity representing a support request
- **Comment** — internal notes or replies attached to a ticket
- **Status Machine** — enforces valid transitions (see [Domain Model](../architecture/domain-model.md))
- **Optimistic Concurrency** — `version` field increments on each status transition

## Models

### Ticket

```python
class Ticket(UUIDModel):
    subject: CharField(200)
    body: TextField
    contact_email: EmailField
    status: CharField  # open | triaged | in_progress | resolved | closed
    priority: CharField | None  # low | medium | high | critical (set by triage)
    version: PositiveIntegerField  # increments on status change
```

**Domain method:** `transition_to(new_status)` — validates against the state machine, increments version, raises `InvalidTransitionError` on invalid transitions.

### Comment

```python
class Comment(UUIDModel):
    ticket: ForeignKey(Ticket)
    body: TextField
    author_name: CharField(100)
```

## Services (`services.py`)

| Function | Signature | Description |
|----------|-----------|-------------|
| `create_ticket` | `(subject, body, contact_email) -> Ticket` | Creates a new ticket in OPEN status |
| `get_ticket` | `(ticket_id) -> Ticket` | Returns ticket with comments, raises `NotFoundError` |
| `list_tickets` | `(status?, priority?) -> list[Ticket]` | Lists tickets with optional filters |
| `transition_ticket` | `(ticket_id, new_status) -> Ticket` | Updates status with `select_for_update` (row lock) |
| `add_comment` | `(ticket_id, body, author_name) -> Comment` | Adds comment, raises `NotFoundError` if ticket missing |

## API Endpoints

| Method | Path | Response | Status Codes |
|--------|------|----------|-------------|
| `POST` | `/api/tickets/` | `TicketOut` | 201 |
| `GET` | `/api/tickets/` | `list[TicketOut]` | 200 |
| `GET` | `/api/tickets/{id}` | `TicketDetailOut` | 200, 404 |
| `PATCH` | `/api/tickets/{id}/status` | `TicketOut` | 200, 400, 404 |
| `POST` | `/api/tickets/{id}/comments` | `CommentOut` | 201, 404 |

## Tests

| File | What It Tests |
|------|--------------|
| `test_models.py` | Ticket creation, valid transitions, invalid transitions, full lifecycle |
| `test_services.py` | Service functions with real database, error cases |
| `test_api.py` | HTTP status codes, response shapes, CRUD operations |
| `factories.py` | `TicketFactory` using factory_boy |

## Data Flow

```
POST /api/tickets/
    → api.create_ticket() validates TicketIn schema
    → services.create_ticket() creates Ticket in DB
    → (future) enqueues triage.tasks.classify_ticket_task
    → returns 201 + TicketOut
```
