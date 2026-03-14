# MEMORY

## Project Purpose
Provide a Docker-first platform to define and serve configurable mock APIs with realistic shapes and funny output values. The platform is centered around a clean admin UI and live OpenAPI generation.

## Current Architecture
- **Backend**: FastAPI with SQLModel + Alembic, running in Docker
- **Database**: Postgres for endpoint definitions and persistence
- **Frontend**: React + Vite admin dashboard
- **Orchestration**: Docker Compose (local + QA profiles)

## Constraints
- Must be Docker-first and easy to run.
- Must use Postgres (no SQLite).
- Endpoint definitions are stored in DB and drive both runtime behavior and OpenAPI.
- Keep implementation pragmatic and “good enough” for v1.

## Active Assumptions
- Admin auth uses Basic Auth for v1.
- OpenAPI can be rebuilt on every request; caching is secondary.
- Endpoint template/responses will be JSON Schema based with a simple templating layer.

## Current Status Snapshot
- Repo scaffold exists with root docs and baseline Compose setup.
- Backend and frontend scaffolds still need implementation.

## Known Risks
- Live OpenAPI generation may become slow if not cached.
- JSON schema editor UX can be complex; start with simple JSON editor.
- Admin UI and backend need to stay in sync on model schemas.

## Notes for Next Agent
- Start by bootstrapping backend FastAPI app inside `apps/api` and ensure `make up` starts all services.
- Keep tasks updated in `TASKS.md` as progress is made.
- Add a seed script that can run during docker-compose startup if desired.
