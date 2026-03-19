# Makefile Reference

**File:** `Makefile`

All commands run inside Docker containers via `docker compose exec`.

## Service Management

| Target | Command | Description |
|--------|---------|-------------|
| `make up` | `docker compose up -d` | Start all services in background |
| `make down` | `docker compose down` | Stop all services |
| `make build` | `docker compose build` | Rebuild Docker images |
| `make logs` | `docker compose logs -f` | Tail logs from all services |

## Database

| Target | Command | Description |
|--------|---------|-------------|
| `make migrate` | `manage.py migrate` | Apply database migrations |
| `make makemigrations` | `manage.py makemigrations` | Generate new migrations from model changes |
| `make seed` | `manage.py loaddata seed.json` | Load seed/fixture data |
| `make db-shell` | `psql -U triage -d triage` | Open PostgreSQL interactive shell |

## Testing

| Target | Command | Description |
|--------|---------|-------------|
| `make test` | `pytest -x -v` | Run all tests (stop on first failure) |
| `make test-cov` | `pytest --cov --cov-report=term-missing` | Run tests with coverage report |

## Code Quality

| Target | Command | Description |
|--------|---------|-------------|
| `make lint` | `ruff check .` | Run linter (find issues) |
| `make fmt` | `ruff format .` | Auto-format code |
| `make typecheck` | `mypy .` | Run type checker |

## Development

| Target | Command | Description |
|--------|---------|-------------|
| `make shell` | `manage.py shell` | Open Django interactive shell |

## Typical Workflow

```bash
# First time setup
make build
make up
make migrate

# Daily development
make up                    # start services
# ... write code ...
make test                  # run tests
make lint                  # check style
make fmt                   # auto-fix formatting

# After model changes
make makemigrations        # generate migration files
make migrate               # apply to database

# Debugging
make logs                  # see what's happening
make shell                 # interactive Python with Django context
make db-shell              # inspect database directly
```
