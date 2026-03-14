# DECISIONS

## 2026-03-14: Project bootstrap decisions
- **Tech stack**: FastAPI + SQLModel + Alembic for backend; React + Vite for frontend.
- **Persistence**: Postgres is the single source of truth for endpoint definitions.
- **OpenAPI**: Live generation on each request from DB-backed endpoint definitions.
- **Admin auth**: Basic username/password for v1.
- **Data format**: Use JSON Schema for request/response schemas; responses will be generated from templates.

*> Future decisions should append a dated entry with context and rationale.*
