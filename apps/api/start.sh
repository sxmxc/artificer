#!/bin/sh
set -eu

# Ensure the database is initialized before starting
python -m scripts.init_db

# Start FastAPI
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
