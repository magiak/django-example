# Support Ticket Triage System

AI-powered support ticket classification, routing, and lifecycle management.

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| API | Django 5.1 + Django Ninja | Typed HTTP endpoints with OpenAPI |
| Database | PostgreSQL 16 | Relational storage with migrations |
| Background Jobs | Dramatiq + Redis | Async classification & routing |
| Frontend | React 19 + TypeScript + Tailwind | Minimal dashboard SPA |
| Containerization | Docker Compose | Local dev environment |
| CI/CD | GitHub Actions | Lint, test, build pipeline |

## Documentation

### Learning (start here if you're a C#/.NET developer)
- [Learning Path](learning-path.md) — Roadmap and overview
  1. [Python Syntax](learning/01-python-syntax.md) — Indentation, functions, classes, imports
  2. [Project Structure](learning/02-project-structure.md) — Settings, URLs, app discovery
  3. [Models & ORM](learning/03-models-and-orm.md) — Fields, QuerySets, migrations
  4. [Services](learning/04-services.md) — Business logic, transactions, exceptions
  5. [API Layer](learning/05-api-layer.md) — Routers, schemas, error handling
  6. [Background Tasks](learning/06-background-tasks.md) — Dramatiq, Redis, idempotency
  7. [Testing](learning/07-testing.md) — pytest, factories, assertions
  8. [Putting It Together](learning/08-putting-it-together.md) — Full flow, mental model
- [Exercises](learning/exercises.md) — 4 hands-on practice tasks
- [Python Interview Questions](interview-python.md) — 30 questions with C# comparisons
- [Django Interview Questions](interview-django.md) — 30 questions with project examples

### Getting Started
- [Getting Started](getting-started.md) — Setup, first run, verify it works

### Architecture
- [System Overview](architecture/overview.md) — Diagram, bounded contexts, layer pattern
- [Domain Model](architecture/domain-model.md) — Entities, state machine, relationships
- [Architecture Decisions](architecture/decisions.md) — ADRs explaining key choices

### API Reference
- [API Endpoints](api/endpoints.md) — All endpoints with curl examples

### Backend
- [Project Structure](backend/project-structure.md) — File layout and conventions
- [Tickets Context](backend/tickets.md) — Ticket lifecycle management
- [Triage Context](backend/triage.md) — AI classification pipeline
- [Teams Context](backend/teams.md) — Routing and assignment

### Frontend
- [Frontend Overview](frontend/overview.md) — React app structure

### Operations
- [Docker](operations/docker.md) — Container services and configuration
- [CI/CD](operations/ci-cd.md) — GitHub Actions pipeline
- [Makefile](operations/makefile.md) — Development commands reference
