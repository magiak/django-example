# 30 Django Interview Questions

For C# developers transitioning to Django. Answers reference this project's code where applicable.

---

## Fundamentals

### 1. What is Django and how does it differ from Flask/FastAPI?

| Framework | Type | C# Equivalent |
|-----------|------|---------------|
| **Django** | Full-stack ("batteries included") | ASP.NET Core MVC (full framework) |
| **Flask** | Micro-framework (minimal) | ASP.NET Core Minimal APIs (bare) |
| **FastAPI** | Async API framework (Pydantic-native) | ASP.NET Core Web API |

Django includes ORM, admin panel, auth, migrations, forms, and templating out of the box. Flask/FastAPI require you to pick and integrate each piece separately.

We use **Django + Django Ninja** — Django's full power (ORM, migrations, admin) with Ninja's FastAPI-style typed API layer.

### 2. Explain the Django request/response lifecycle

```
HTTP Request
  → URL routing (config/urls.py)
  → Middleware chain (settings MIDDLEWARE — top to bottom)
  → View function / Django Ninja endpoint
  → Middleware chain (bottom to top)
  → HTTP Response
```

In our project:
```
POST /api/tickets/
  → config/urls.py matches "api/" → NinjaAPI
  → NinjaAPI matches "/tickets/" → tickets.api.router
  → Router matches POST "/" → create_ticket(request, payload)
  → Returns response
```

C# equivalent: the ASP.NET Core middleware pipeline + endpoint routing.

### 3. What is the Django ORM?

Django's built-in Object-Relational Mapper. Every `models.Model` subclass maps to a database table.

```python
# Define (like EF Core entity)
class Ticket(models.Model):
    subject = models.CharField(max_length=200)

# Create (like db.Add + SaveChanges in one call)
ticket = Ticket.objects.create(subject="Help")

# Query (like LINQ)
open_tickets = Ticket.objects.filter(status="open").order_by("-created_at")

# Update
ticket.subject = "Updated"
ticket.save()

# Delete
ticket.delete()
```

Unlike EF Core, there's no separate `DbContext` — each model has its own `.objects` manager that handles queries directly.

### 4. What is `models.Manager` and `objects`?

Every model has a default manager called `objects`. It's the interface for database queries:

```python
Ticket.objects.all()              # SELECT * FROM tickets_ticket
Ticket.objects.filter(status="open")
Ticket.objects.get(id=uuid)       # single result or DoesNotExist
Ticket.objects.count()
```

You can create custom managers:
```python
class OpenTicketManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status="open")

class Ticket(models.Model):
    objects = models.Manager()          # default
    open_tickets = OpenTicketManager()  # custom: Ticket.open_tickets.all()
```

C# equivalent: like a repository pattern built into the model.

### 5. What are QuerySets? Are they lazy?

Yes, QuerySets are **lazy** — they don't hit the database until you evaluate them:

```python
# No SQL executed yet (building the query)
qs = Ticket.objects.filter(status="open").order_by("-created_at")

# SQL executes HERE:
list(qs)          # iteration
qs[0]             # indexing
len(qs)           # count
bool(qs)          # existence check
for t in qs:      # iteration
```

QuerySets are chainable (like IQueryable in LINQ):
```python
qs = Ticket.objects.all()
if status:
    qs = qs.filter(status=status)      # still no SQL
if priority:
    qs = qs.filter(priority=priority)  # still no SQL
return list(qs)                        # NOW SQL runs
```

### 6. What's the difference between `select_related` and `prefetch_related`?

```python
# select_related — SQL JOIN (for ForeignKey / OneToOne)
# One query with JOIN
tickets = Ticket.objects.select_related("assigned_team").all()

# prefetch_related — separate query (for reverse FK / ManyToMany)
# Two queries: one for tickets, one for comments WHERE ticket_id IN (...)
tickets = Ticket.objects.prefetch_related("comments").all()
```

| Method | SQL | Use For | C# EF Equivalent |
|--------|-----|---------|-------------------|
| `select_related` | JOIN | ForeignKey, OneToOne | `.Include()` (single join) |
| `prefetch_related` | Separate IN query | Reverse FK, ManyToMany | `.Include()` (separate query) |

In our project, `get_ticket()` in `tickets/services.py` uses `prefetch_related("comments")` to load a ticket with all its comments.

### 7. Explain Django migrations

Migrations are Python files that describe database schema changes, generated from model definitions.

```bash
# 1. Change your model
# 2. Generate migration file
python manage.py makemigrations     # like: dotnet ef migrations add

# 3. Apply to database
python manage.py migrate            # like: dotnet ef database update

# 4. Check status
python manage.py showmigrations     # list all migrations and their status
```

Each migration is a versioned Python file in `app/migrations/`. They run in order and track what's been applied in a `django_migrations` table.

Key difference from EF Core: Django generates migrations automatically from model changes. EF Core also does this, but Django's approach is more deterministic — it compares the current models to the last migration state.

### 8. What are Django apps?

A Django app is a Python package (directory with `__init__.py`) that contains models, views, tests, etc. It's a modular unit of functionality.

```python
# config/settings/base.py
INSTALLED_APPS = [
    "tickets",    # our bounded context
    "triage",
    "teams",
]
```

In our project, each app = a DDD bounded context. Apps are registered in `INSTALLED_APPS` so Django discovers their models, migrations, and admin registrations.

C# equivalent: like a class library project in a solution, but with auto-discovery.

### 9. What is Django Admin?

A free, auto-generated CRUD interface for your models. No code required beyond registration:

```python
# tickets/admin.py
@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("subject", "status", "priority", "created_at")
    list_filter = ("status", "priority")
    search_fields = ("subject", "body")
```

Access at `http://localhost:8000/admin/`. There's no C# equivalent — you'd have to build this yourself or use a third-party tool.

It's useful for:
- Quick data inspection during development
- Non-technical users managing reference data (teams, routing rules)
- Debugging production data

### 10. What is middleware in Django?

A hook that processes every request/response. Like ASP.NET Core middleware:

```python
# shared/middleware.py
class RequestIDMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response      # next middleware in chain

    def __call__(self, request):
        request.request_id = str(uuid.uuid4())   # before view
        response = self.get_response(request)     # call next
        response["X-Request-ID"] = request.request_id  # after view
        return response
```

Registered in `settings.py` as a list — order matters (processed top-to-bottom on request, bottom-to-top on response).

---

## Intermediate

### 11. How do you handle transactions in Django?

```python
from django.db import transaction

# Option 1: Decorator — whole function is atomic
@transaction.atomic
def transfer_money(from_acc, to_acc, amount):
    from_acc.balance -= amount
    from_acc.save()
    to_acc.balance += amount
    to_acc.save()

# Option 2: Context manager — specific block is atomic
def complex_operation():
    do_something()
    with transaction.atomic():
        # only this block is in a transaction
        model1.save()
        model2.save()
    do_something_else()
```

In our project, `transition_ticket()` in `tickets/services.py` uses `@transaction.atomic` with `select_for_update()` for row-level locking.

C# equivalent: `using var tx = db.Database.BeginTransaction();`

### 12. What is the N+1 query problem and how do you solve it?

```python
# BAD: N+1 queries — 1 query for tickets, then 1 per ticket for comments
tickets = Ticket.objects.all()
for ticket in tickets:
    print(ticket.comments.count())   # separate query each iteration!

# GOOD: 2 queries total
tickets = Ticket.objects.prefetch_related("comments").all()
for ticket in tickets:
    print(ticket.comments.count())   # no extra query — already loaded
```

Django Debug Toolbar can detect N+1 problems in development.

### 13. What's the difference between `null=True` and `blank=True`?

```python
# null=True  → database level: column allows NULL
# blank=True → validation level: field can be empty in forms/API

priority = models.CharField(null=True, blank=True)   # optional everywhere
subject = models.CharField(blank=False)               # required everywhere
notes = models.TextField(blank=True)                   # optional in forms, NOT NULL in DB
```

Rule of thumb:
- String fields: use `blank=True` alone (empty string `""` instead of NULL)
- Non-string fields (int, date, FK): use `null=True, blank=True` together

### 14. How does Django's URL routing work?

```python
# config/urls.py
urlpatterns = [
    path("admin/", admin.site.urls),           # prefix match
    path("api/", api.urls),                    # delegates to NinjaAPI
]
```

With Django Ninja, routing is done via decorators on the router:
```python
router = Router(tags=["Tickets"])

@router.get("/{ticket_id}")        # /api/tickets/{ticket_id}
def get_ticket(request, ticket_id: UUID):
    ...
```

C# equivalent: `app.MapGet("/tickets/{ticketId}", handler)` in Minimal APIs.

### 15. What are signals in Django?

Event hooks that fire when something happens to a model:

```python
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Ticket)
def on_ticket_saved(sender, instance, created, **kwargs):
    if created:
        classify_ticket_task.send(str(instance.id))
```

C# equivalent: like domain events or `INotificationHandler` in MediatR.

We don't use signals heavily in this project — we prefer explicit service calls over implicit signal-based coupling.

### 16. How do you handle file uploads in Django?

```python
class Attachment(models.Model):
    file = models.FileField(upload_to="attachments/%Y/%m/")
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
```

- `FileField` / `ImageField` handle upload storage
- `upload_to` defines the subdirectory
- `MEDIA_ROOT` setting defines where files are stored on disk
- In production, use cloud storage (S3) via `django-storages`

### 17. What are Django forms and when would you use them?

Forms validate and process user input:

```python
class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ["subject", "body", "contact_email"]
```

In our project, we DON'T use Django forms — we use Django Ninja schemas (Pydantic) instead. Forms are for server-rendered HTML (Django templates). Since we have a React frontend, schemas handle validation at the API layer.

### 18. Explain Django's authentication system

Built-in user model with auth, permissions, and groups:

```python
from django.contrib.auth.models import User

user = User.objects.create_user("alice", "alice@example.com", "password123")
user.is_authenticated   # True after login
user.has_perm("tickets.add_ticket")   # permission check
```

In our project, `teams/models.py` references the auth user model:
```python
user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
```

C# equivalent: ASP.NET Core Identity.

### 19. What is Django Ninja and how does it differ from DRF?

| Feature | Django REST Framework (DRF) | Django Ninja |
|---------|---------------------------|--------------|
| Schema | Serializers (custom) | Pydantic (standard) |
| Views | Class-based (verbose) | Function-based (concise) |
| Type safety | Manual | Automatic from type hints |
| OpenAPI | Needs drf-spectacular | Built-in |
| Performance | Slower | Faster |
| Community | Huge | Growing |

Django Ninja example (from our project):
```python
@router.post("/", response={201: TicketOut})
def create_ticket(request, payload: TicketIn):
    ticket = services.create_ticket(**payload.dict())
    return 201, ticket
```

We chose Ninja for its typed, concise API — see `docs/architecture/decisions.md` ADR-001.

### 20. How do you write tests in Django?

```python
import pytest
from django.test import Client

@pytest.mark.django_db                       # allows database access
class TestTicketAPI:
    def test_create_ticket(self):
        client = Client()                    # test HTTP client
        response = client.post(
            "/api/tickets/",
            data={"subject": "Help", "body": "...", "contact_email": "a@b.com"},
            content_type="application/json",
        )
        assert response.status_code == 201
        assert response.json()["subject"] == "Help"
```

Our project uses `pytest` + `pytest-django` (not Django's built-in `unittest`). We also use `factory_boy` for test data — see `tickets/tests/factories.py`.

---

## Advanced

### 21. What are `F()` and `Q()` objects?

```python
from django.db.models import F, Q

# F() — reference a field value in SQL (avoids race conditions)
Ticket.objects.filter(id=ticket_id).update(version=F("version") + 1)
# SQL: UPDATE ... SET version = version + 1 (atomic!)

# Q() — complex queries with OR and NOT
Ticket.objects.filter(
    Q(status="open") | Q(status="triaged"),    # OR
    ~Q(priority="low"),                         # NOT
)
# SQL: WHERE (status='open' OR status='triaged') AND NOT priority='low'
```

C# LINQ equivalent:
- `F()` — no direct equivalent, EF doesn't support field references in updates this way
- `Q()` — like building `Expression<Func<T, bool>>` dynamically

### 22. What are custom model managers and QuerySets?

```python
class TicketQuerySet(models.QuerySet):
    def open(self):
        return self.filter(status="open")

    def high_priority(self):
        return self.filter(priority__in=["high", "critical"])

class Ticket(models.Model):
    objects = TicketQuerySet.as_manager()

# Usage — chainable!
Ticket.objects.open().high_priority().order_by("-created_at")
```

This is like extension methods on `IQueryable<Ticket>` in C#.

### 23. Explain `select_for_update()` and database locking

```python
@transaction.atomic
def transition_ticket(*, ticket_id, new_status):
    # SELECT ... FOR UPDATE — locks the row until transaction commits
    ticket = Ticket.objects.select_for_update().get(id=ticket_id)
    ticket.transition_to(new_status)
    ticket.save()
```

Used in our `tickets/services.py` to prevent race conditions when two requests try to transition the same ticket simultaneously.

C# EF equivalent: `SET TRANSACTION ISOLATION LEVEL SERIALIZABLE` or explicit SQL hints.

### 24. What are database indexes in Django?

```python
class Ticket(models.Model):
    status = models.CharField(db_index=True)     # single-column index

    class Meta:
        indexes = [
            models.Index(fields=["status", "priority"]),         # composite
            models.Index(fields=["-created_at"], name="recent"),  # descending
        ]
```

Django generates the SQL `CREATE INDEX` in migrations automatically. Our project uses `db_index=True` on the `status` field for fast filtering.

### 25. How do you handle database schema changes safely?

1. **Never** rename/delete fields in one step — split into multiple migrations
2. Use `RunPython` for data migrations:

```python
# Generated migration file
from django.db import migrations

def populate_defaults(apps, schema_editor):
    Ticket = apps.get_model("tickets", "Ticket")
    Ticket.objects.filter(priority=None).update(priority="medium")

class Migration(migrations.Migration):
    operations = [
        migrations.RunPython(populate_defaults, migrations.RunPython.noop),
    ]
```

3. Add nullable fields first, backfill data, then make non-nullable
4. Use `--check` in CI: `python manage.py makemigrations --check` fails if models are out of sync

### 26. How does Django handle caching?

```python
# settings.py
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://redis:6379/1",
    }
}

# Usage
from django.core.cache import cache

cache.set("ticket_count", 42, timeout=300)    # 5 minutes
count = cache.get("ticket_count")             # returns 42 or None

# Decorator for view-level caching
from django.views.decorators.cache import cache_page

@cache_page(60 * 15)    # cache for 15 minutes
def list_tickets(request):
    ...
```

Our project uses Redis for Dramatiq but could easily add caching on the same instance.

### 27. What is ASGI vs WSGI?

| Protocol | Supports | Django File | C# Equivalent |
|----------|---------|-------------|---------------|
| **WSGI** | Synchronous only | `wsgi.py` | Kestrel (sync) |
| **ASGI** | Sync + Async + WebSockets | `asgi.py` | Kestrel (full) |

Our project has both `config/wsgi.py` and `config/asgi.py`. For development, `runserver` uses WSGI. For production with async/WebSocket support, you'd use ASGI with `uvicorn` or `daphne`.

### 28. How do you structure a large Django project?

Our project demonstrates the recommended approach:

```
backend/
├── config/          # Project config (NOT an app)
│   └── settings/    # Split settings by environment
├── shared/          # Shared kernel (base models, exceptions)
├── tickets/         # Bounded context — self-contained
├── triage/          # Bounded context — self-contained
└── teams/           # Bounded context — self-contained
```

Rules:
- Each app = bounded context with clear responsibility
- `config/` is the project, not an app (named `config` not `myproject`)
- Each app has: `models.py`, `services.py`, `api.py`, `schemas.py`, `tasks.py`, `tests/`
- Cross-app communication through task queues with primitive IDs
- Shared code in `shared/` kernel

See `docs/backend/project-structure.md` for the full breakdown.

### 29. What is `ContentType` framework and generic relations?

```python
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class AuditLog(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = GenericForeignKey("content_type", "object_id")
    action = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)
```

Allows a model to have a foreign key to ANY other model. Useful for audit logs, comments, tags. C# has no direct equivalent — you'd typically use a polymorphic pattern or separate tables.

### 30. How do you deploy Django in production?

```
                    ┌─────────────┐
Internet ──────────>│   Nginx     │ (reverse proxy, static files)
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │  Gunicorn   │ (WSGI server, multiple workers)
                    │  or Uvicorn │ (ASGI server)
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │   Django    │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
        ┌─────▼────┐ ┌────▼─────┐ ┌────▼─────┐
        │ Postgres │ │  Redis   │ │ Dramatiq │
        └──────────┘ └──────────┘ │ Worker   │
                                  └──────────┘
```

Key production settings:
- `DEBUG = False`
- `ALLOWED_HOSTS` set explicitly
- `SECRET_KEY` from environment variable
- `python manage.py collectstatic` to gather static files
- Gunicorn with multiple workers: `gunicorn config.wsgi -w 4`
- Database connection pooling (`CONN_MAX_AGE` or PgBouncer)

Our `docker-compose.yml` uses `runserver` (dev only). Production would swap to Gunicorn/Uvicorn behind Nginx or a cloud load balancer.
