# Docker

**File:** `docker-compose.yml`

## Services

| Service | Image | Port | Purpose |
|---------|-------|------|---------|
| `db` | postgres:16-alpine | 5432 | PostgreSQL database |
| `redis` | redis:7-alpine | 6379 | Dramatiq message broker |
| `backend` | ./backend (Dockerfile) | 8000 | Django API server |
| `worker` | ./backend (Dockerfile) | — | Dramatiq background worker |
| `frontend` | ./frontend (Dockerfile) | 5173 | Vite React dev server |

## Service Details

### db (PostgreSQL)

```yaml
image: postgres:16-alpine
environment:
  POSTGRES_DB: triage
  POSTGRES_USER: triage
  POSTGRES_PASSWORD: triage
volumes:
  - pgdata:/var/lib/postgresql/data    # persistent storage
healthcheck:
  test: pg_isready -U triage
```

Data is persisted in a named volume `pgdata`. To reset the database:
```bash
docker compose down -v   # -v removes volumes
make up
make migrate
```

### redis

```yaml
image: redis:7-alpine
healthcheck:
  test: redis-cli ping
```

Used as the Dramatiq message broker. No persistence configured (messages are transient).

### backend (Django)

```yaml
build: ./backend
command: python manage.py runserver 0.0.0.0:8000
volumes:
  - ./backend:/app    # live code reload
depends_on:
  db: { condition: service_healthy }
  redis: { condition: service_healthy }
```

Hot-reloads on code changes. Waits for db and redis health checks before starting.

### worker (Dramatiq)

```yaml
build: ./backend
command: python manage.py rundramatiq --processes 1 --threads 2
```

Same image as backend but runs the Dramatiq consumer instead of the web server. Processes background tasks (classification, routing).

### frontend (Vite)

```yaml
build: ./frontend
command: npm run dev -- --host 0.0.0.0
volumes:
  - ./frontend:/app
  - /app/node_modules    # prevents overwriting container's node_modules
```

## Environment Variables

All services share these environment variables:

| Variable | Value | Notes |
|----------|-------|-------|
| `DATABASE_URL` | `postgres://triage:triage@db:5432/triage` | Uses Docker service name `db` |
| `REDIS_URL` | `redis://redis:6379/0` | Uses Docker service name `redis` |
| `DJANGO_SETTINGS_MODULE` | `config.settings.dev` | Development settings |
| `SECRET_KEY` | `dev-secret-key-not-for-production` | Hardcoded for dev only |
| `OPENAI_API_KEY` | `${OPENAI_API_KEY:-}` | Passed from host env |

## Common Commands

```bash
# Start all services
docker compose up -d

# View logs
docker compose logs -f
docker compose logs -f backend    # single service

# Restart a service
docker compose restart backend

# Run a command in a container
docker compose exec backend python manage.py shell
docker compose exec db psql -U triage -d triage

# Rebuild after Dockerfile or dependency changes
docker compose build
docker compose up -d

# Full reset (removes database data)
docker compose down -v
```

## Volumes

| Volume | Purpose |
|--------|---------|
| `pgdata` | PostgreSQL data persistence |
| `./backend:/app` | Backend live code mount |
| `./frontend:/app` | Frontend live code mount |
| `/app/node_modules` | Anonymous volume to keep container's node_modules |
