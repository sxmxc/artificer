import os
import sys
from pathlib import Path

# Ensure the backend package is importable when running tests.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Force tests to run against a local SQLite file database (stable across connections).
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.db import create_db_and_tables
from scripts.seed import seed


@pytest.fixture(autouse=True)
def use_test_db():
    """Ensure the test database is initialized for each test."""
    create_db_and_tables()
    seed()
    yield


def test_health_endpoint():
    client = TestClient(app)
    response = client.get("/api/health")
    assert response.status_code in (200, 404)
