# Getting Started

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose
- [Make](https://www.gnu.org/software/make/) (included on macOS/Linux; on Windows use Git Bash or WSL)
- Git

## Quick Start

```bash
# Clone the repository
git clone <repo-url>
cd django-example

# Build and start all services
make build
make up

# Run database migrations
make migrate

# (Optional) Load seed data
make seed
```

## Verify It Works

### API (Django Ninja)

```bash
# OpenAPI docs (Swagger UI)
open http://localhost:8000/api/docs

# Create a ticket
curl -X POST http://localhost:8000/api/tickets/ \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Cannot login to dashboard",
    "body": "I get a 500 error when clicking the login button.",
    "contact_email": "user@example.com"
  }'

# List all tickets
curl http://localhost:8000/api/tickets/

# Get a specific ticket (replace {id} with a real UUID)
curl http://localhost:8000/api/tickets/{id}
```

### Frontend (React)

```bash
open http://localhost:5173
```

### Admin Panel (Django)

```bash
# Create a superuser first
docker compose exec backend python manage.py createsuperuser

open http://localhost:8000/admin/
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgres://triage:triage@db:5432/triage` | PostgreSQL connection string |
| `REDIS_URL` | `redis://redis:6379/0` | Redis connection for Dramatiq |
| `DJANGO_SETTINGS_MODULE` | `config.settings.dev` | Django settings module |
| `SECRET_KEY` | `dev-secret-key-not-for-production` | Django secret key |
| `OPENAI_API_KEY` | (empty) | API key for LLM classification |

Copy `.env.example` to `.env` and adjust values as needed.

## Running Tests

```bash
make test          # Run all tests
make test-cov      # Run with coverage report
```

## Useful Commands

```bash
make logs          # Tail all container logs
make shell         # Django interactive shell
make db-shell      # PostgreSQL shell
make down          # Stop all services
```

See [Makefile Reference](operations/makefile.md) for the complete list.
