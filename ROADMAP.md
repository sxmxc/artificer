# ROADMAP

This roadmap is organized into phases aligned with the bootstrap plan. Each phase is designed to deliver a working milestone.

## Phase 1: Bootstrap and scaffolding (current)
- Create repo structure and core documentation.
- Establish Docker Compose development environment.
- Define key artifacts: tasks, memory, decisions, agents.

## Phase 2: Core platform foundation
- Implement backend scaffolding (FastAPI app, Postgres, migrations).
- Implement admin CRUD API and endpoint definition model.
- Implement runtime dispatch for mock endpoints.
- Implement live OpenAPI generation.

## Phase 3: Seed + initial UX
- Add seed data for 15 example endpoints.
- Build admin UI for managing endpoints.
- Add preview and schema editing experiences.

## Phase 4: Testing and CI
- Add backend unit tests for core functionality.
- Add frontend build checks and linting.
- Add CI workflow for PR validation.

## Phase 5: Polish + extensions
- Add auth improvements and role management.
- Add performance optimizations for OpenAPI generation.
- Improve UX (template editor, error simulation, analytics).
