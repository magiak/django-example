# Module 2: Project Structure

> **Goal:** Understand where everything lives and how Django discovers your code.
>
> **Time:** 10 minutes
>
> **Files to open:** `config/settings/base.py`, `config/urls.py`

---

## 2.1 Settings = Your `Program.cs`

**File: `backend/config/settings/base.py`**

In .NET you'd write:
```csharp
builder.Services.AddDbContext<AppDbContext>(o => o.UseNpgsql(conn));
builder.Services.AddControllers();
```

In Django, it's all declarative constants:

```python
INSTALLED_APPS = [          # Like builder.Services.Add___()
    "django.contrib.admin", # Built-in admin panel
    "django_dramatiq",      # Like builder.Services.AddHangfire()
    "tickets",              # Your app — registered here
    "triage",
    "teams",
]

MIDDLEWARE = [               # Like app.Use___() pipeline
    "django.middleware.security.SecurityMiddleware",
    "shared.middleware.RequestIDMiddleware",
]

DATABASES = {                # Like builder.Services.AddDbContext()
    "default": dj_database_url.config(
        default="postgres://triage:triage@localhost:5432/triage",
    ),
}
```

**Key insight:** There's no startup file with procedural code. Settings is a module of constants. Django reads them on boot and wires everything automatically.

---

## 2.2 URL Routing = Your `app.Map___()`

**File: `backend/config/urls.py`**

```python
from ninja import NinjaAPI

api = NinjaAPI(title="Support Ticket Triage")

api.add_router("/tickets/", tickets_router)    # Like app.MapGroup("/tickets")
api.add_router("/triage/", triage_router)
api.add_router("/teams/", teams_router)

urlpatterns = [
    path("admin/", admin.site.urls),           # Built-in admin panel
    path("api/", api.urls),                    # All API under /api/
]
```

---

## 2.3 `__init__.py` — What Is It?

A file that marks a directory as a Python package (importable). Can be empty.

```
tickets/
├── __init__.py     ← THIS makes it a package — without it, imports fail
├── models.py
└── services.py
```

C# equivalent: like having a `.csproj` — without it, the folder isn't a project.

---

## 2.4 Where Django Looks for Things

Django auto-discovers code by convention:

| Django Looks For | In This File | If Missing |
|-----------------|-------------|------------|
| Models (DB tables) | `models.py` | No table created |
| Admin registration | `admin.py` | Not in admin panel |
| Migrations | `migrations/` | Can't migrate |
| App config | `apps.py` | Uses defaults |

If you define a model in `services.py` instead of `models.py`, Django won't find it. No error — just no table.

---

## 2.5 Settings Split by Environment

```
config/settings/
├── base.py     # Shared settings (DB, apps, middleware)
├── dev.py      # DEBUG=True, CORS_ALLOW_ALL
└── test.py     # Test DB, stub Dramatiq broker
```

```python
# dev.py — imports everything from base, then overrides
from .base import *     # get all base settings
DEBUG = True            # override specific ones
```

C# equivalent: `appsettings.json` + `appsettings.Development.json` + `appsettings.Test.json`

Selected via environment variable: `DJANGO_SETTINGS_MODULE=config.settings.dev`

---

## 2.6 The Full Map

```
backend/
├── manage.py                  # CLI entry point (like dotnet CLI)
├── pyproject.toml             # Dependencies (like .csproj)
│
├── config/                    # Project config (NOT an app)
│   ├── settings/base.py       # = Program.cs + appsettings.json
│   ├── urls.py                # = app.MapControllers() / route registration
│   ├── wsgi.py                # = Kestrel entry point
│   └── asgi.py                # = Kestrel with async/WebSocket support
│
├── shared/                    # Shared kernel (cross-cutting code)
│   ├── models.py              # Base classes for all models
│   ├── exceptions.py          # Domain exception hierarchy
│   └── middleware.py          # Request ID middleware
│
├── tickets/                   # Bounded context (like a class library project)
│   ├── models.py              # Entity definitions (EF entities)
│   ├── services.py            # Business logic (service classes)
│   ├── api.py                 # HTTP endpoints (controllers)
│   ├── schemas.py             # Request/response DTOs
│   ├── tasks.py               # Background jobs (Hangfire jobs)
│   ├── admin.py               # Admin panel config
│   ├── migrations/            # DB migrations
│   └── tests/                 # Tests
│
├── triage/                    # Same structure
└── teams/                     # Same structure
```

---

**Next:** [Module 3: Models & ORM →](03-models-and-orm.md)
