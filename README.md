# cuddly-octo-memory

A Docker-first mock API platform with a dynamic OpenAPI spec, admin dashboard, and configurable endpoint mocking. Designed for developers who want to define realistic API shapes and return funny/random mock data.

## 🚀 Quickstart (Local)

1. Copy `.env.example` to `.env` and adjust as desired.
2. Start services:

```sh
make up
```

3. Open the admin dashboard:

- Frontend UI: http://localhost:3000
- API docs: http://localhost:8000/docs
- OpenAPI JSON: http://localhost:8000/openapi.json

## 🧠 What You Get

- **Dynamic mock API**: endpoints defined in Postgres are served dynamically.
- **Live OpenAPI**: `/openapi.json` reflects the active endpoint catalog.
- **Admin UI**: create/edit/enable/disable endpoints from a React dashboard.
- **Docker-first**: one command to bring up the full stack.

## 📦 Architecture

- **Backend**: FastAPI + SQLModel + Postgres
- **Frontend**: React + Vite + TypeScript
- **DB migrations**: Alembic
- **Orchestration**: Docker Compose

## 📁 Repo layout

- `apps/api/` - Backend implementation
- `apps/admin-web/` - Admin UI
- `migrations/` - Alembic migrations
- `seed/` - Seed data and scripts
- `docs/` - Architecture, strategy, and how-tos
- `tasks/` - Work tracking

## 🧩 Next steps

Check `TASKS.md` for what to work on next.
