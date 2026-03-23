# Module 5: API Layer (Django Ninja)

> **Goal:** Understand how HTTP endpoints work, how schemas validate data, and how responses are built.
>
> **Time:** 10 minutes
>
> **Files to open:** `tickets/api.py`, `tickets/schemas.py`

---

## 5.1 Router = Controller Group

```python
# tickets/api.py
from ninja import Router

router = Router(tags=["Tickets"])
```

C# equivalent: `app.MapGroup("/tickets").WithTags("Tickets")`

The router is registered in `config/urls.py`:
```python
api.add_router("/tickets/", tickets_router)
```

---

## 5.2 Endpoint = Controller Action

```python
@router.post("/", response={201: TicketOut})
def create_ticket(request, payload: TicketIn):
    ticket = services.create_ticket(
        subject=payload.subject,
        body=payload.body,
        contact_email=payload.contact_email,
    )
    return 201, ticket
```

| Part | What It Does | C# Equivalent |
|------|-------------|---------------|
| `@router.post("/")` | HTTP method + path | `[HttpPost]` or `app.MapPost()` |
| `response={201: TicketOut}` | Declares response schema | `[ProducesResponseType(201)]` |
| `request` | Always first param (rarely used) | `HttpContext` |
| `payload: TicketIn` | Auto-deserialize JSON body | `[FromBody] TicketRequest` |
| `return 201, ticket` | Status code + response body | `Results.Created(ticket)` |

---

## 5.3 Schemas = DTOs

**File: `tickets/schemas.py`**

```python
from ninja import Schema

class TicketIn(Schema):          # Request DTO
    subject: str
    body: str
    contact_email: str

class TicketOut(Schema):         # Response DTO
    id: UUID
    subject: str
    status: str
    priority: str | None
    created_at: datetime
```

C# equivalent:
```csharp
public record TicketRequest(string Subject, string Body, string ContactEmail);
public record TicketResponse(Guid Id, string Subject, string Status, string? Priority, DateTime CreatedAt);
```

**Auto-mapping:** When you return a `Ticket` model instance and the response type is `TicketOut`, Ninja reads matching fields from the model and builds JSON automatically. No manual mapping or AutoMapper needed.

**Nested objects work too:**
```python
class TicketDetailOut(Schema):
    comments: list[CommentOut]   # Ninja follows related_name from the model
```

---

## 5.4 Path Parameters

```python
@router.get("/{ticket_id}")
def get_ticket(request, ticket_id: UUID):    # UUID parsed from URL automatically
    ...
```

Ninja reads the type hint (`UUID`) and auto-converts the URL string. If someone sends `/api/tickets/not-a-uuid`, Ninja returns 422 automatically.

---

## 5.5 Query Parameters

```python
@router.get("/")
def list_tickets(request, status: str | None = None, priority: str | None = None):
    return services.list_tickets(status=status, priority=priority)
```

Parameters with defaults become query params: `GET /api/tickets/?status=open&priority=high`

---

## 5.6 Error Handling Pattern

```python
@router.get("/{ticket_id}", response={200: TicketDetailOut, 404: dict})
def get_ticket(request, ticket_id: UUID):
    try:
        return services.get_ticket(ticket_id=ticket_id)
    except NotFoundError as e:
        return 404, {"detail": e.message}
```

```python
@router.patch("/{ticket_id}/status", response={200: TicketOut, 400: dict, 404: dict})
def update_ticket_status(request, ticket_id: UUID, payload: TicketStatusIn):
    try:
        ticket = services.transition_ticket(ticket_id=ticket_id, new_status=payload.status)
        return ticket                    # 200 is default when no status code returned
    except NotFoundError as e:
        return 404, {"detail": e.message}
    except DomainException as e:
        return 400, {"detail": e.message}
```

**Pattern:** API catches domain exceptions → maps to HTTP status codes. The service layer never knows about HTTP.

---

## 5.7 Multiple Response Types

```python
response={200: TicketOut, 400: dict, 404: dict}
```

This tells Ninja (and OpenAPI docs) what each status code returns. `dict` means a plain JSON object. When you return `404, {"detail": "..."}`, Ninja matches it to the `404: dict` declaration.

---

## 5.8 OpenAPI Docs (Swagger)

Django Ninja generates OpenAPI docs automatically from your:
- Router tags
- Function names
- Schema definitions
- Response declarations
- Type hints

Visit `http://localhost:8000/api/docs` — you get a Swagger UI for free.

---

**Next:** [Module 6: Background Tasks →](06-background-tasks.md)
