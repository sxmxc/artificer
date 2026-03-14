from __future__ import annotations

import os

from sqlmodel import create_engine, SQLModel, Session

from app.config import Settings

settings = Settings()

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    f"postgresql+asyncpg://{settings.postgres_user}:{settings.postgres_password}@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}",
)

# NOTE: SQLModel currently requires a sync engine for create_all and migrations.
engine = create_engine(
    DATABASE_URL.replace("+asyncpg", ""),
    echo=False,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
)


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    return Session(engine)
