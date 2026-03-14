# AGENTS.md

## Purpose
This repository is designed for **AI-native collaboration**. AI agents (and humans) should be able to pick up work quickly, understand constraints, and make consistent changes without breaking the core platform.

## 🧭 First things an agent must do
1. **Read these four files before making changes**:
   - `AGENTS.md` (this file)
   - `MEMORY.md` (project context and assumptions)
   - `TASKS.md` (what to work on next)
   - `DECISIONS.md` (architecture/strategy log)
2. Confirm the current state by running the bootstrap scripts: `make up` (or target-specific tasks).
3. Work in small, reviewable increments and update the tracking docs after every meaningful change.

## 🧱 Architecture Guardrails
- **Backend is the source of truth** for all mock endpoints and OpenAPI generation.
- **OpenAPI must always reflect the active endpoint definitions** stored in the DB.
- **Endpoint behavior is config-driven**, not hard-coded per endpoint.
- Keep the system **Docker-first**: running `make up` should get a developer to a usable state.

## 🧩 Coding Standards
- Prefer clarity over cleverness.
- Avoid large abstractions early; make them when duplication becomes burdensome.
- Write tests for any behavior that might regress (CRUD, dispatch, OpenAPI sync).
- Keep business logic in the backend; frontend should remain UI + API wiring.

## 🧭 Backend Conventions
- Use FastAPI with SQLModel for schema + DB models.
- Put most logic under `apps/api/app/` (e.g., `models/`, `services/`, `routes/`).
- Use Alembic for migrations; keep migrations in `migrations/`.
- Any change that affects the runtime contract (endpoints, schemas, auth) must update docs.

## 🧭 Frontend Conventions
- Use Vite + React + TypeScript.
- Keep components in `apps/admin-web/src/components` and views in `apps/admin-web/src/pages`.
- Use `src/api/` for API client code.
- Prefer simple forms and JSON editors for schema editing.

## 🧠 Documentation Rules
- When code changes behavior, update `docs/` to reflect it.
- If you add a new feature, add a short entry to `TASKS.md` and `MEMORY.md` as needed.

## ✅ Task/Memo/Decision Protocol
- **TASKS.md**: update when you start/finish meaningful work.
- **MEMORY.md**: record assumptions, known risks, and current status.
- **DECISIONS.md**: add a dated entry for any architecture or platform decision.

## ✅ Definition of Done for a Task
- Code compiles and tests pass.
- Relevant docs updated.
- TASKS.md reflects completion.
- No regressions in Docker compose startup.

---

*If you're an automated agent: You are expected to keep this file up to date as you learn more about the project.*
