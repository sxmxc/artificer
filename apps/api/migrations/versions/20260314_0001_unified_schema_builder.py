"""Introduce unified schema builder contract."""

from __future__ import annotations

import json
from typing import Any

from alembic import op
import sqlalchemy as sa

from app.services.schema_contract import migrate_legacy_response_schema, sanitize_public_schema

# revision identifiers, used by Alembic.
revision = "20260314_0001"
down_revision = None
branch_labels = None
depends_on = None


def _create_current_endpoint_table(table_name: str) -> sa.Table:
    return op.create_table(
        table_name,
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("slug", sa.String(), nullable=False),
        sa.Column("method", sa.String(), nullable=False),
        sa.Column("path", sa.String(), nullable=False),
        sa.Column("category", sa.String(), nullable=True),
        sa.Column("tags", sa.JSON(), nullable=True),
        sa.Column("summary", sa.String(), nullable=True),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("auth_mode", sa.String(), nullable=False, server_default="none"),
        sa.Column("request_schema", sa.JSON(), nullable=True),
        sa.Column("response_schema", sa.JSON(), nullable=True),
        sa.Column("success_status_code", sa.Integer(), nullable=False, server_default="200"),
        sa.Column("error_rate", sa.Float(), nullable=False, server_default="0"),
        sa.Column("latency_min_ms", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("latency_max_ms", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("seed_key", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )


def _transform_legacy_row(row: dict[str, Any]) -> dict[str, Any]:
    request_schema = _coerce_jsonish(row.get("request_schema"), {})
    response_schema = _coerce_jsonish(row.get("response_schema"), {})
    example_template = _coerce_jsonish(row.get("example_template"), None)
    tags = _coerce_jsonish(row.get("tags"), [])

    return {
        "id": row.get("id"),
        "name": row.get("name"),
        "slug": row.get("slug"),
        "method": row.get("method"),
        "path": row.get("path"),
        "category": row.get("category"),
        "tags": tags or [],
        "summary": row.get("summary"),
        "description": row.get("description"),
        "enabled": bool(row.get("enabled", True)),
        "auth_mode": row.get("auth_mode") or "none",
        "request_schema": request_schema or {},
        "response_schema": migrate_legacy_response_schema(
            response_schema,
            example_template,
            row.get("response_mode"),
        ),
        "success_status_code": row.get("success_status_code") or 200,
        "error_rate": row.get("error_rate") or 0.0,
        "latency_min_ms": row.get("latency_min_ms") or 0,
        "latency_max_ms": row.get("latency_max_ms") or 0,
        "seed_key": row.get("seed_key"),
        "created_at": row.get("created_at"),
        "updated_at": row.get("updated_at"),
    }


def _transform_current_row_for_downgrade(row: dict[str, Any]) -> dict[str, Any]:
    response_schema = _coerce_jsonish(row.get("response_schema"), {}) or {}
    mock_config = response_schema.get("x-mock", {}) if isinstance(response_schema, dict) else {}
    example_template = mock_config.get("value") if mock_config.get("mode") == "fixed" else None
    response_mode = "fixed" if example_template is not None else "random"

    return {
        "id": row.get("id"),
        "name": row.get("name"),
        "slug": row.get("slug"),
        "method": row.get("method"),
        "path": row.get("path"),
        "category": row.get("category"),
        "tags": _coerce_jsonish(row.get("tags"), []) or [],
        "summary": row.get("summary"),
        "description": row.get("description"),
        "enabled": bool(row.get("enabled", True)),
        "auth_mode": row.get("auth_mode") or "none",
        "request_schema": _coerce_jsonish(row.get("request_schema"), {}) or {},
        "response_schema": sanitize_public_schema(response_schema),
        "example_template": example_template or {},
        "response_mode": response_mode,
        "success_status_code": row.get("success_status_code") or 200,
        "error_rate": row.get("error_rate") or 0.0,
        "latency_min_ms": row.get("latency_min_ms") or 0,
        "latency_max_ms": row.get("latency_max_ms") or 0,
        "seed_key": row.get("seed_key"),
        "created_at": row.get("created_at"),
        "updated_at": row.get("updated_at"),
    }


def _coerce_jsonish(value: Any, default: Any) -> Any:
    if value is None:
        return default
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return default
    return value


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("endpointdefinition"):
        _create_current_endpoint_table("endpointdefinition")
        return

    existing_columns = {column["name"] for column in inspector.get_columns("endpointdefinition")}
    if "example_template" not in existing_columns and "response_mode" not in existing_columns:
        return

    metadata = sa.MetaData()
    legacy_table = sa.Table("endpointdefinition", metadata, autoload_with=bind)
    rows = bind.execute(sa.select(legacy_table)).mappings().all()

    new_table = _create_current_endpoint_table("endpointdefinition_new")
    transformed_rows = [_transform_legacy_row(dict(row)) for row in rows]
    if transformed_rows:
        op.bulk_insert(new_table, transformed_rows)

    op.drop_table("endpointdefinition")
    op.rename_table("endpointdefinition_new", "endpointdefinition")


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("endpointdefinition"):
        return

    current_columns = {column["name"] for column in inspector.get_columns("endpointdefinition")}
    if "example_template" in current_columns or "response_mode" in current_columns:
        return

    current_table = sa.Table("endpointdefinition", sa.MetaData(), autoload_with=bind)
    rows = bind.execute(sa.select(current_table)).mappings().all()

    legacy_table = op.create_table(
        "endpointdefinition_legacy",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("slug", sa.String(), nullable=False),
        sa.Column("method", sa.String(), nullable=False),
        sa.Column("path", sa.String(), nullable=False),
        sa.Column("category", sa.String(), nullable=True),
        sa.Column("tags", sa.JSON(), nullable=True),
        sa.Column("summary", sa.String(), nullable=True),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("auth_mode", sa.String(), nullable=False, server_default="none"),
        sa.Column("request_schema", sa.JSON(), nullable=True),
        sa.Column("response_schema", sa.JSON(), nullable=True),
        sa.Column("example_template", sa.JSON(), nullable=True),
        sa.Column("response_mode", sa.String(), nullable=False, server_default="random"),
        sa.Column("success_status_code", sa.Integer(), nullable=False, server_default="200"),
        sa.Column("error_rate", sa.Float(), nullable=False, server_default="0"),
        sa.Column("latency_min_ms", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("latency_max_ms", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("seed_key", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )

    transformed_rows = [_transform_current_row_for_downgrade(dict(row)) for row in rows]
    if transformed_rows:
        op.bulk_insert(legacy_table, transformed_rows)

    op.drop_table("endpointdefinition")
    op.rename_table("endpointdefinition_legacy", "endpointdefinition")
