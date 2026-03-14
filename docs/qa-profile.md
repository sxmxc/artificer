# QA Profile

This project supports two primary environments:

## Local (default)
Used during development.
- `docker compose up` starts Postgres, backend, and frontend.
- Uses `.env` values.
- Backend port: `8000`
- Frontend port: `3000`

## QA
A profile intended for a more production-like smoke test.
- Uses the same compose file but can be run with: `docker compose --profile qa up`.
- Can include additional checks such as schema validation or mock load tests.

> NOTE: The QA profile is a placeholder; add specific QA services (e.g., nginx reverse proxy) once the core platform stabilizes.
