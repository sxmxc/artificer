# Makefile for cuddly-octo-memory

.DEFAULT_GOAL := help

help:
	@echo "Available targets:"
	@echo "  make up         # Start services (docker compose up)"
	@echo "  make down       # Stop services (docker compose down)"
	@echo "  make build      # Build docker images"
	@echo "  make logs       # Tail logs for all services"
	@echo "  make test       # Run backend tests"
	@echo "  make lint       # Run linting (backend + frontend)"
	@echo "  make seed       # Seed the database (run migrations + seed)"
	@echo "  make clean      # Cleanup generated artifacts"

up:
	docker compose up --build

down:
	docker compose down --volumes

build:
	docker compose build

logs:
	docker compose logs -f

seed:
	docker compose run --rm api sh ./scripts/seed.sh

test:
	docker compose run --rm api pytest

lint:
	docker compose run --rm api black --check . && \
	docker compose run --rm admin-web npm run lint

clean:
	rm -rf .pytest_cache __pycache__ build dist
