# Module 8: Putting It Together

> **Goal:** See how all the pieces connect end-to-end.
>
> **Time:** 10 minutes

---

## 8.1 Request Flow: POST /api/tickets/

Follow a single request through every layer:

```
1. HTTP POST /api/tickets/ hits Django
         │
         ▼
2. config/urls.py
   path("api/", api.urls) → NinjaAPI matches "/tickets/" → tickets.api.router
         │
         ▼
3. tickets/api.py: create_ticket(request, payload: TicketIn)
   • Ninja deserializes JSON body → validates against TicketIn schema
   • If validation fails → 422 response automatically
         │
         ▼
4. tickets/services.py: create_ticket(subject=..., body=..., contact_email=...)
   • Ticket.objects.create() → INSERT INTO tickets_ticket (...)
   • (future) classify_ticket_task.send(str(ticket.id)) → Redis queue
         │
         ▼
5. tickets/api.py: return 201, ticket
   • Ninja reads Ticket model fields → matches to TicketOut schema → JSON
         │
         ▼
6. HTTP 201 response with JSON body
```

---

## 8.2 Async Pipeline: Ticket → Classification → Assignment

```
1. Ticket created in DB
         │
         │  classify_ticket_task.send(ticket_id)
         ▼
2. Redis queue holds the message
         │
         │  worker picks it up
         ▼
3. triage/tasks.py: classify_ticket_task(ticket_id)
         │
         ▼
4. triage/services.py: classify_ticket(ticket_id)
   • Load ticket from DB
   • Check idempotency (skip if already classified for this version)
   • Call LLM (currently mock)
   • Save Classification to DB
         │
         │  route_ticket_task.send(ticket_id, category, priority)
         ▼
5. teams/tasks.py: route_ticket_task(ticket_id, category, priority)
         │
         ▼
6. teams/services.py: route_ticket(ticket_id, category, priority)
   • Match RoutingRule by category + priority
   • Create/update Assignment
   • Ticket is now assigned to a team
```

---

## 8.3 Cross-Context Rules

```
tickets/    knows NOTHING about triage or teams
                    │
                    │ (enqueues task with ticket_id string)
                    ▼
triage/     reads tickets.models.Ticket (by ID, read-only)
                    │
                    │ (enqueues task with ticket_id + classification results)
                    ▼
teams/      reads ticket by UUID (not even a FK — loose coupling)
```

| Rule | Why |
|------|-----|
| Never import another context's `services.py` | Keeps business logic boundaries clean |
| Read another context's models by ID only | Minimal coupling — just needs the PK |
| Communicate via Dramatiq tasks with primitives | Async, decoupled, retryable |

---

## 8.4 Django vs .NET Mental Model

| Concept | .NET Core | Django |
|---------|----------|-------|
| Project config | `Program.cs` + `appsettings.json` | `config/settings/base.py` |
| Service registration | `builder.Services.AddScoped<T>()` | `INSTALLED_APPS` list |
| Middleware pipeline | `app.UseAuthentication()` | `MIDDLEWARE` list |
| Route registration | `app.MapControllers()` | `urlpatterns` + `api.add_router()` |
| Entity definition | EF Core entity + `DbContext` | `models.Model` subclass |
| Migrations | `dotnet ef migrations add` | `python manage.py makemigrations` |
| Apply migrations | `dotnet ef database update` | `python manage.py migrate` |
| Query data | `db.Tickets.Where(...)` | `Ticket.objects.filter(...)` |
| Dependency injection | Constructor injection | Direct imports |
| Background jobs | Hangfire / BackgroundService | Dramatiq actors |
| API DTOs | Records / classes | Pydantic Schema classes |
| Test framework | xUnit / NUnit | pytest |
| Test data | Bogus / AutoFixture | factory_boy |
| Package manager | NuGet | pip / uv |
| Project file | `.csproj` | `pyproject.toml` |
| Linter | Roslyn analyzers | ruff |
| Type checker | Built into compiler | mypy (optional) |

---

## 8.5 What Makes This Project "DDD"

| DDD Concept | How We Do It |
|------------|-------------|
| **Bounded Contexts** | Each Django app (tickets, triage, teams) is a context |
| **Aggregates** | Ticket is the aggregate root — owns Comments |
| **Domain Methods** | `Ticket.transition_to()` enforces state machine rules |
| **Domain Exceptions** | `InvalidTransitionError`, `NotFoundError` |
| **Service Layer** | `services.py` — all business logic |
| **Anti-corruption** | Contexts communicate via task queues, not direct imports |
| **Ubiquitous Language** | Code uses domain terms: "ticket", "triage", "classification", "routing rule" |

---

## You're Done!

You now understand every layer of this project. Next steps:

- Try the [Hands-On Exercises](exercises.md) to practice
- Review [Python Interview Questions](../interview-python.md) for syntax deep-dives
- Review [Django Interview Questions](../interview-django.md) for framework knowledge
- Read the [Architecture Decisions](../architecture/decisions.md) for "why" behind each choice

---

**Back to:** [Learning Path Overview →](../learning-path.md)
