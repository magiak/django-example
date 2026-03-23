# Module 6: Background Tasks (Dramatiq)

> **Goal:** Understand how async background processing works with Dramatiq + Redis.
>
> **Time:** 10 minutes
>
> **Files to open:** `triage/tasks.py`, `triage/services.py`

---

## 6.1 What Is Dramatiq?

A background task queue — like Hangfire in .NET. The flow:

```
Your code                 Redis queue              Worker process
    │                         │                         │
    │  .send(ticket_id)       │                         │
    ├────────────────────────>│                         │
    │                         │   picks up message      │
    │                         ├────────────────────────>│
    │                         │                         │  runs the function
    │                         │                         │  saves result to DB
```

- **Producer** — your Django app enqueues a task
- **Broker** — Redis holds the message
- **Consumer** — a separate `worker` process picks it up and runs it

---

## 6.2 Defining a Task (Actor)

```python
# triage/tasks.py
import dramatiq

@dramatiq.actor(max_retries=3, min_backoff=1000, max_backoff=60000)
def classify_ticket_task(ticket_id: str) -> None:
    from .services import classify_ticket       # lazy import
    classify_ticket(ticket_id=UUID(ticket_id))
```

C# Hangfire equivalent:
```csharp
[AutomaticRetry(Attempts = 3)]
public void ClassifyTicketTask(string ticketId) {
    _triageService.ClassifyTicket(Guid.Parse(ticketId));
}
```

---

## 6.3 Key Rules for Tasks

### Rule 1: Primitive arguments only

```python
# GOOD — string serializes cleanly to JSON
classify_ticket_task.send("550e8400-e29b-41d4-a716-446655440000")

# BAD — model instances can't be serialized to Redis
classify_ticket_task.send(ticket_object)
```

### Rule 2: Lazy imports inside the function

```python
def classify_ticket_task(ticket_id: str) -> None:
    from .services import classify_ticket    # imported HERE, not at top of file
```

Why? At startup, Django loads all apps. If tasks.py imports services.py at module level, and services.py imports models from another app that hasn't loaded yet → circular import error. Importing inside the function delays it until runtime.

### Rule 3: Tasks call services, never contain logic

```python
# GOOD — task delegates to service
def classify_ticket_task(ticket_id: str) -> None:
    classify_ticket(ticket_id=UUID(ticket_id))

# BAD — business logic in the task
def classify_ticket_task(ticket_id: str) -> None:
    ticket = Ticket.objects.get(id=ticket_id)
    result = call_llm(ticket.body)
    Classification.objects.create(...)
```

This way the same logic works synchronously (in tests) and asynchronously (in production).

---

## 6.4 Enqueuing a Task

```python
# Somewhere in your code (e.g., tickets/services.py)
from triage.tasks import classify_ticket_task

def create_ticket(*, subject, body, contact_email):
    ticket = Ticket.objects.create(...)
    classify_ticket_task.send(str(ticket.id))    # enqueue to Redis
    return ticket
```

`.send()` is non-blocking — it puts a message on Redis and returns immediately. The worker picks it up asynchronously.

---

## 6.5 Idempotency

What if a task fails and Dramatiq retries it? You don't want duplicate classifications.

```python
# triage/services.py
def classify_ticket(*, ticket_id: UUID) -> Classification:
    ticket = Ticket.objects.get(id=ticket_id)

    # Already classified for this version? Skip.
    existing = Classification.objects.filter(
        ticket=ticket,
        ticket_version=ticket.version
    ).first()
    if existing:
        return existing     # no duplicate work

    # ... call LLM and save
```

The `ticket_version` check ensures: if the ticket hasn't changed since last classification, don't re-classify.

---

## 6.6 Retry Configuration

```python
@dramatiq.actor(
    max_retries=3,           # retry up to 3 times on failure
    min_backoff=1000,        # first retry after 1 second
    max_backoff=60000,       # max wait between retries: 60 seconds
)
```

Dramatiq uses exponential backoff — waits longer between each retry. If all retries fail, the message is dead-lettered.

---

## 6.7 The Worker Process

In `docker-compose.yml`, the worker is a separate container running the same code:

```yaml
worker:
    build: ./backend
    command: python manage.py rundramatiq --processes 1 --threads 2
```

It's the same Django app but instead of serving HTTP, it listens on Redis for messages and runs task functions.

---

**Next:** [Module 7: Testing →](07-testing.md)
