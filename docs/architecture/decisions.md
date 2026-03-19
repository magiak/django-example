# Architecture Decision Records

## ADR-001: Django Ninja over Django REST Framework

**Status:** Accepted

**Context:** We need a typed API framework for Django. The two main options are Django REST Framework (DRF) and Django Ninja.

**Decision:** Use Django Ninja.

**Rationale:**
- Native Pydantic schemas — same validation library used by FastAPI, provides automatic type inference
- Auto-generated OpenAPI 3.0 docs out of the box (no extra configuration)
- Significantly less boilerplate than DRF serializers
- Function-based views are simpler to reason about than DRF's class-based views
- Better alignment with typed Python (type hints drive the API contract)

**Consequences:**
- Smaller community and fewer third-party extensions compared to DRF
- Team members familiar with DRF will need to learn Ninja's patterns

---

## ADR-002: Bounded Contexts as Django Apps

**Status:** Accepted

**Context:** We need to organize backend code in a way that supports clean domain boundaries and independent evolution.

**Decision:** Each bounded context (tickets, triage, teams) is a separate Django app with its own models, services, API, schemas, tasks, and tests.

**Rationale:**
- Django apps naturally map to DDD bounded contexts — they have their own models, migrations, and admin
- Each app can evolve independently (new fields, new endpoints) without touching others
- Clear import boundaries: apps can read each other's models but never import each other's services
- Shared cross-cutting concerns live in a `shared/` kernel app

**Consequences:**
- Cross-context queries require explicit joins or separate queries (no implicit coupling)
- Need discipline to maintain boundaries as the project grows

---

## ADR-003: Service Layer for Business Logic

**Status:** Accepted

**Context:** Django encourages putting logic in views or models ("fat models"). We need a clear place for business logic that is testable without HTTP.

**Decision:** Each app has a `services.py` module containing all business logic as plain functions.

**Rationale:**
- API endpoints stay thin — validate input, call service, return output
- Services are testable without HTTP request/response overhead
- Business rules are centralized (not scattered across views, signals, and model methods)
- Dramatiq tasks call services, ensuring async and sync paths share the same logic
- Familiar pattern for developers coming from .NET/Java (service layer)

**Consequences:**
- Models remain relatively "thin" (only domain methods like `transition_to()` that enforce invariants)
- Need to be intentional about what goes in models vs. services

---

## ADR-004: UUID Primary Keys

**Status:** Accepted

**Context:** We need to choose a primary key strategy for all domain entities.

**Decision:** Use UUID v4 primary keys on all models via the shared `UUIDModel` base class.

**Rationale:**
- IDs can be generated client-side or in background tasks without database round-trips
- No sequential ID enumeration (minor security benefit)
- Safe for distributed systems and eventual cross-service communication
- Consistent across all bounded contexts

**Consequences:**
- Slightly larger storage and index size compared to auto-incrementing integers
- URLs are longer (UUIDs vs. numeric IDs)
- Worth it for the architectural flexibility

---

## ADR-005: Dramatiq over Celery

**Status:** Accepted

**Context:** We need a background task queue for async operations (LLM classification, ticket routing).

**Decision:** Use Dramatiq with Redis as the message broker.

**Rationale:**
- Simpler API and fewer footguns than Celery
- Built-in retry logic with configurable backoff
- Good Django integration via `django-dramatiq`
- Reliable message delivery with Redis
- Easier to reason about (no complex Celery beat scheduler needed at this scale)

**Consequences:**
- Smaller ecosystem than Celery
- For periodic/scheduled tasks, would need to add APScheduler or similar (not needed currently)

---

## ADR-006: Vite + React SPA over Next.js

**Status:** Accepted

**Context:** We need a frontend to validate the API and provide a minimal dashboard. The backend is API-first (Django Ninja).

**Decision:** Use Vite + React + TypeScript + Tailwind as a standalone SPA.

**Rationale:**
- Simpler setup — no SSR complexity needed for an internal dashboard
- Vite dev server is fast and requires minimal configuration
- The frontend's sole job is to call the Django API — no need for Next.js server components or API routes
- Tailwind provides utility-first styling without a design system overhead
- Can proxy `/api` requests to Django backend via Vite config

**Consequences:**
- No server-side rendering (fine for a dashboard, would revisit for SEO-critical pages)
- Frontend is a separate deployment unit from the backend
