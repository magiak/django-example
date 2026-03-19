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
