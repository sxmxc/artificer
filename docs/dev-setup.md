# Development Setup

## Prerequisites
- Docker Desktop (or equivalent Docker engine)
- Node.js 18+ (for local frontend development)
- Python 3.11+ (optional for running backend locally without Docker)

## Quickstart

1. Copy environment defaults:

```sh
cp .env.example .env
```

2. Start all services:

```sh
make up
```

3. Visit the UI:
- Admin UI: http://localhost:3000
- API docs: http://localhost:8000/docs

## Running tests

```sh
make test
```

## Local development (backend only)

You can run the backend directly:

```sh
cd apps/api
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Local development (frontend only)

```sh
cd apps/admin-web
npm install
npm run dev
```
