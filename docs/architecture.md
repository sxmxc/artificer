# Architecture

The platform is built as a **monorepo** with a backend API and a frontend admin UI.

## Core components

- **Backend (`apps/api/`)**
  - FastAPI application serving two sets of endpoints:
    - **Admin API**: CRUD operations for mock endpoints and configuration.
    - **Public mock API**: dynamically routed endpoints based on DB definitions.
  - **Postgres** is used as the single source of truth for endpoint definitions.
  - **OpenAPI generation** is performed at runtime from the active endpoint catalog.

- **Frontend (`apps/admin-web/`)**
  - React + Vite admin dashboard.
  - Provides endpoint catalog management, preview, and OpenAPI snippet visualization.

- **Orchestration**
  - Uses Docker Compose for local and QA profiles.
  - Services include: Postgres, backend, frontend.

## Data flow
1. Admin user creates/edits endpoint definitions via the UI.
2. Backend persists definitions in Postgres.
3. The mock API router uses definitions to route requests and generate responses.
4. OpenAPI schema is generated from the same definitions and served on `/openapi.json`.
