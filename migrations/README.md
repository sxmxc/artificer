# Migrations

This directory is reserved for Alembic migrations.

Currently the project uses SQLModel's `create_all()` for schema bootstrap. When the schema stabilizes, generate proper migrations:

```sh
cd apps/api
alembic init migrations
```
