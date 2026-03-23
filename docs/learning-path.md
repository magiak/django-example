# Learning Path: C# → Python/Django

A structured guide for .NET/C# developers. Each module is self-contained — read them in order or jump to what you need.

## Roadmap

```
Module 1: Python Syntax          "How do I read this code?"
    ↓
Module 2: Project Structure      "Where does everything live?"
    ↓
Module 3: Models & ORM           "How do I define and query data?"
    ↓
Module 4: Services & Logic       "Where does business logic go?"
    ↓
Module 5: API Layer              "How do HTTP endpoints work?"
    ↓
Module 6: Background Tasks       "How does async processing work?"
    ↓
Module 7: Testing                "How do I write tests?"
    ↓
Module 8: Putting It Together    "How does a request flow end-to-end?"
```

## Modules

| # | Module | What You'll Learn | Time |
|---|--------|-------------------|------|
| 1 | [Python for C# Developers](learning/01-python-syntax.md) | Indentation, functions, classes, imports, types, `self`, `*args/**kwargs` | 15 min |
| 2 | [Project Structure](learning/02-project-structure.md) | `settings.py` vs `Program.cs`, URL routing, `INSTALLED_APPS` | 10 min |
| 3 | [Models & ORM](learning/03-models-and-orm.md) | `models.Model`, fields, `class Meta`, QuerySets vs LINQ, migrations | 15 min |
| 4 | [Services & Business Logic](learning/04-services.md) | Service layer pattern, transactions, domain exceptions | 10 min |
| 5 | [API Layer (Django Ninja)](learning/05-api-layer.md) | Routers, schemas (DTOs), decorators, error handling | 10 min |
| 6 | [Background Tasks (Dramatiq)](learning/06-background-tasks.md) | Actors, Redis broker, idempotency, lazy imports | 10 min |
| 7 | [Testing (pytest)](learning/07-testing.md) | pytest vs xUnit, fixtures, factories, `@pytest.mark.django_db` | 10 min |
| 8 | [Putting It Together](learning/08-putting-it-together.md) | Full request flow, async pipeline, cross-context rules, mental model | 10 min |

**Total: ~90 minutes** for the full walkthrough.

## Quick Reference

- [ORM Cheat Sheet](learning/03-models-and-orm.md#orm-cheat-sheet) — Django ORM ↔ EF Core / LINQ
- [Django vs .NET Mental Model](learning/08-putting-it-together.md#django-vs-net-mental-model) — Complete comparison table
- [Python Interview Questions](interview-python.md) — 30 questions with C# comparisons
- [Django Interview Questions](interview-django.md) — 30 questions with project examples

## Hands-On Exercises

After completing the modules, try these to solidify your understanding:

| # | Exercise | Skills Practiced |
|---|----------|-----------------|
| 1 | [Add a field to Ticket](learning/exercises.md#exercise-1-add-a-field) | Models, schemas, migrations |
| 2 | [Add a DELETE endpoint](learning/exercises.md#exercise-2-add-a-new-endpoint) | Services, API, tests |
| 3 | [Create a new bounded context](learning/exercises.md#exercise-3-add-a-new-bounded-context) | Full DDD app from scratch |
| 4 | [Wire the async pipeline](learning/exercises.md#exercise-4-wire-the-async-pipeline) | Dramatiq tasks, cross-context flow |

## Suggested File Reading Order

If you prefer to just read the code directly, go in this order:

1. `backend/shared/models.py` — Base classes (3 min)
2. `backend/shared/exceptions.py` — Python classes/inheritance (2 min)
3. `backend/tickets/models.py` — Core domain model (10 min)
4. `backend/tickets/schemas.py` — DTOs / Pydantic (3 min)
5. `backend/tickets/services.py` — ORM queries, business logic (10 min)
6. `backend/tickets/api.py` — HTTP layer (5 min)
7. `backend/tickets/tests/test_models.py` — pytest patterns (5 min)
8. `backend/config/urls.py` — Router wiring (2 min)
9. `backend/config/settings/base.py` — Django configuration (5 min)
10. `backend/triage/services.py` — Cross-context, idempotency (5 min)
11. `backend/triage/tasks.py` — Dramatiq async tasks (3 min)
12. `backend/teams/services.py` — Routing logic (3 min)
