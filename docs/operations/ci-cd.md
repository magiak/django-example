# CI/CD Pipeline

**File:** `.github/workflows/ci.yml`

**Triggers:** Push to `main`, Pull requests targeting `main`

## Pipeline Overview

```
┌────────────┐    ┌────────────┐    ┌────────────┐
│    Lint     │    │    Test     │    │  Frontend  │
│             │    │             │    │            │
│ ruff check  │    │ pytest +   │    │ npm ci     │
│ ruff format │    │ coverage   │    │ npm build  │
└────────────┘    └────────────┘    └────────────┘
     (parallel — all three jobs run simultaneously)
```

## Jobs

### lint

**Runs on:** ubuntu-latest
**Working directory:** `backend/`

| Step | Command | Purpose |
|------|---------|---------|
| Setup Python | `actions/setup-python@v5` (3.12) | Install Python |
| Install ruff | `pip install ruff` | Linter/formatter |
| Lint | `ruff check .` | Check for code issues |
| Format check | `ruff format --check .` | Verify code formatting |

### test

**Runs on:** ubuntu-latest
**Working directory:** `backend/`

**Services:**
- PostgreSQL 16 (service container with health check)

| Step | Command | Purpose |
|------|---------|---------|
| Setup Python | `actions/setup-python@v5` (3.12) | Install Python |
| Install deps | `uv pip install -r pyproject.toml && uv pip install ".[dev]"` | All dependencies |
| Run tests | `pytest -x -v --cov` | Tests with coverage |

**Environment:**
- `DJANGO_SETTINGS_MODULE=config.settings.test`
- `DATABASE_URL=postgres://triage:triage@localhost:5432/test_triage`

### frontend

**Runs on:** ubuntu-latest
**Working directory:** `frontend/`

| Step | Command | Purpose |
|------|---------|---------|
| Setup Node | `actions/setup-node@v4` (20) | Install Node.js |
| Install deps | `npm ci` | Clean install |
| Build | `npm run build` | TypeScript check + Vite build |

## Adding a New CI Step

1. Open `.github/workflows/ci.yml`
2. Add a step to an existing job, or create a new job
3. New jobs run in parallel by default — add `needs: [job_name]` for sequential execution

Example — adding mypy type checking to the lint job:

```yaml
- run: pip install mypy django-stubs
- run: mypy .
```
