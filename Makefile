.PHONY: up down build migrate makemigrations seed test test-cov lint fmt typecheck shell logs db-shell

up:              ## Start all services
	docker compose up -d

down:            ## Stop all services
	docker compose down

build:           ## Rebuild images
	docker compose build

migrate:         ## Run Django migrations
	docker compose exec backend python manage.py migrate

makemigrations:  ## Generate new migrations
	docker compose exec backend python manage.py makemigrations

seed:            ## Load seed data
	docker compose exec backend python manage.py loaddata seed.json

test:            ## Run pytest
	docker compose exec backend python -m pytest -x -v

test-cov:        ## Run pytest with coverage
	docker compose exec backend python -m pytest --cov --cov-report=term-missing

lint:            ## Run ruff linter
	docker compose exec backend ruff check .

fmt:             ## Format with ruff
	docker compose exec backend ruff format .

typecheck:       ## Run mypy
	docker compose exec backend mypy .

shell:           ## Django shell
	docker compose exec backend python manage.py shell

logs:            ## Tail all logs
	docker compose logs -f

db-shell:        ## Postgres shell
	docker compose exec db psql -U triage -d triage
