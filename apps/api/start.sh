#!/usr/bin/env bash
set -euo pipefail

# Ensure the database is initialized before starting
python scripts/init_db.py

# Start FastAPI
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
