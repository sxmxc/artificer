"""Reserve /api/health for the system health endpoint.

Revision ID: 20260319_0009
Revises: 20260319_0008
Create Date: 2026-03-19 18:05:00.000000
"""

from __future__ import annotations

import json

from alembic import op
import sqlalchemy as sa


revision = "20260319_0009"
down_revision = "20260319_0008"
branch_labels = None
depends_on = None


SYSTEM_HEALTH_PATH = "/api/health"


def upgrade() -> None:
    bind = op.get_bind()
    route_ids = bind.execute(
        sa.text("SELECT id FROM endpointdefinition WHERE path = :path"),
        {"path": SYSTEM_HEALTH_PATH},
    ).scalars().all()

    if not route_ids:
        return

    for route_id in route_ids:
        bind.execute(
            sa.text(
                """
                DELETE FROM executionstep
                WHERE run_id IN (
                    SELECT id
                    FROM executionrun
                    WHERE route_id = :route_id
                )
                """
            ),
            {"route_id": route_id},
        )
        bind.execute(
            sa.text("DELETE FROM executionrun WHERE route_id = :route_id"),
            {"route_id": route_id},
        )
        bind.execute(
            sa.text("DELETE FROM routedeployment WHERE route_id = :route_id"),
            {"route_id": route_id},
        )
        bind.execute(
            sa.text("DELETE FROM routeimplementation WHERE route_id = :route_id"),
            {"route_id": route_id},
        )
        bind.execute(
            sa.text("DELETE FROM endpointdefinition WHERE id = :route_id"),
            {"route_id": route_id},
        )


def downgrade() -> None:
    bind = op.get_bind()
    existing_id = bind.execute(
        sa.text("SELECT id FROM endpointdefinition WHERE path = :path"),
        {"path": SYSTEM_HEALTH_PATH},
    ).scalar_one_or_none()
    if existing_id is not None:
        return

    bind.execute(
        sa.text(
            """
            INSERT INTO endpointdefinition (
                name,
                slug,
                method,
                path,
                category,
                tags,
                summary,
                description,
                enabled,
                auth_mode,
                request_schema,
                response_schema,
                success_status_code,
                error_rate,
                latency_min_ms,
                latency_max_ms,
                seed_key,
                created_at,
                updated_at
            )
            VALUES (
                :name,
                :slug,
                :method,
                :path,
                :category,
                :tags,
                :summary,
                :description,
                :enabled,
                :auth_mode,
                :request_schema,
                :response_schema,
                :success_status_code,
                :error_rate,
                :latency_min_ms,
                :latency_max_ms,
                :seed_key,
                CURRENT_TIMESTAMP,
                CURRENT_TIMESTAMP
            )
            """
        ),
        {
            "name": "Health",
            "slug": "health",
            "method": "GET",
            "path": SYSTEM_HEALTH_PATH,
            "category": "system",
            "tags": json.dumps(["system"]),
            "summary": "Health check",
            "description": None,
            "enabled": True,
            "auth_mode": "none",
            "request_schema": json.dumps({}),
            "response_schema": json.dumps(
                {
                    "type": "object",
                    "properties": {
                        "status": {
                            "type": "string",
                            "x-mock": {"mode": "fixed", "value": "ok", "options": {}},
                        }
                    },
                    "required": ["status"],
                    "x-builder": {"order": ["status"]},
                    "x-mock": {"mode": "generate"},
                }
            ),
            "success_status_code": 200,
            "error_rate": 0.0,
            "latency_min_ms": 0,
            "latency_max_ms": 0,
            "seed_key": None,
        },
    )
