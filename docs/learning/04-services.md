# Module 4: Services & Business Logic

> **Goal:** Understand where business logic lives and how the service layer pattern works.
>
> **Time:** 10 minutes
>
> **File to open:** `tickets/services.py`

---

## 4.1 Why a Service Layer?

Django traditionally puts logic in views ("fat views") or models ("fat models"). We use a separate `services.py` because:

- **Testable without HTTP** — test business logic directly, no request/response needed
- **Single place for rules** — not scattered across views, signals, and models
- **Familiar pattern** — same as `ITicketService` in .NET

```
api.py       → thin: validates input, calls service, returns response
services.py  → ALL business logic lives here
models.py    → domain methods only (like transition_to)
```

---

## 4.2 Service Function Anatomy

```python
# tickets/services.py

def create_ticket(*, subject: str, body: str, contact_email: str) -> Ticket:
    """Create a new support ticket and trigger async triage."""
    ticket = Ticket.objects.create(
        subject=subject,
        body=body,
        contact_email=contact_email,
    )
    return ticket
```

Key patterns:
- **`*` keyword-only args** — forces named parameters
- **Type hints** — documents the contract
- **Docstring** — `"""triple quotes"""` right after `def` = documentation
- **Returns a model instance** — not a dict, not a schema
- **No `request` parameter** — services don't know about HTTP

---

## 4.3 Error Handling

Services raise domain exceptions. The API layer catches and maps them to HTTP:

```python
# services.py — raises domain exception
def get_ticket(*, ticket_id: UUID) -> Ticket:
    try:
        return Ticket.objects.prefetch_related("comments").get(id=ticket_id)
    except Ticket.DoesNotExist:         # Django's built-in "not found" exception
        raise NotFoundError("Ticket", str(ticket_id))   # our domain exception
```

```python
# api.py — catches and maps to HTTP
@router.get("/{ticket_id}")
def get_ticket(request, ticket_id: UUID):
    try:
        return services.get_ticket(ticket_id=ticket_id)
    except NotFoundError as e:
        return 404, {"detail": e.message}
```

C# equivalent:
```csharp
// Service throws
throw new NotFoundException("Ticket", id);

// Controller catches (or uses exception middleware)
catch (NotFoundException ex) {
    return NotFound(new { detail = ex.Message });
}
```

---

## 4.4 Transactions

```python
from django.db import transaction

@transaction.atomic
def transition_ticket(*, ticket_id: UUID, new_status: str) -> Ticket:
    ticket = Ticket.objects.select_for_update().get(id=ticket_id)
    ticket.transition_to(new_status)
    ticket.save()
    return ticket
```

| Python | C# |
|--------|-----|
| `@transaction.atomic` | `using var tx = db.Database.BeginTransaction()` |
| `select_for_update()` | `SELECT ... FOR UPDATE` (row lock) |
| Exception → auto rollback | `tx.Rollback()` |
| Success → auto commit | `tx.Commit()` |

The `@transaction.atomic` decorator wraps the entire function in a transaction. If any exception occurs, it rolls back automatically.

---

## 4.5 Filtering with Optional Parameters

```python
def list_tickets(*, status: str | None = None, priority: str | None = None) -> list[Ticket]:
    qs = Ticket.objects.all()           # start with all
    if status:
        qs = qs.filter(status=status)   # conditionally narrow down
    if priority:
        qs = qs.filter(priority=priority)
    return list(qs)                     # execute query
```

QuerySets are lazy and chainable — exactly like building `IQueryable` in LINQ:

```csharp
var query = db.Tickets.AsQueryable();
if (status != null) query = query.Where(t => t.Status == status);
if (priority != null) query = query.Where(t => t.Priority == priority);
return query.ToList();
```

---

## 4.6 Cross-Context Reads

The triage service reads from the tickets context:

```python
# triage/services.py
from tickets.models import Ticket        # import another context's MODEL (read-only)
from .models import Classification       # import own model

def classify_ticket(*, ticket_id: UUID) -> Classification:
    ticket = Ticket.objects.get(id=ticket_id)    # read from tickets context
    # ... classify and save Classification
```

**Rules:**
- Reading another context's models → OK
- Importing another context's services → NOT OK (breaks boundaries)
- Communication between contexts → use Dramatiq tasks with primitive IDs

---

**Next:** [Module 5: API Layer →](05-api-layer.md)
