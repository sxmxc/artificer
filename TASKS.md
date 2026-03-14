# TASKS

This file tracks the work needed to bootstrap and evolve the project.

## Now
- [x] Create repo scaffold and documentation skeleton
- [ ] Scaffold backend FastAPI app and ensure it runs inside Docker
- [ ] Scaffold frontend admin UI (Vite + React) and ensure it runs inside Docker
- [ ] Implement core endpoint definition model + CRUD API
- [ ] Implement runtime dispatch for mock endpoints driven by DB
- [ ] Implement live OpenAPI generation from DB definitions
- [ ] Seed initial endpoint catalog (15 endpoints)
- [ ] Add basic backend tests for CRUD and OpenAPI

## Next
- [ ] Build admin UI pages for endpoint list / edit / preview
- [ ] Add auth (basic username/password) for admin API and UI
- [ ] Add schema editor UI (JSON editor) for request/response schemas
- [ ] Add endpoint enable/disable and duplication support
- [ ] Add latency/error simulation controls

## Later
- [ ] Add advanced auth (API key, bearer token, scopes)
- [ ] Add role-based access to admin UI
- [ ] Improve OpenAPI caching strategy for performance
- [ ] Add multi-project support (namespaces)

## Blocked
- [ ] (none)

## Done
- [x] Create initial planning docs
- [x] Define project structure and high-level architecture
