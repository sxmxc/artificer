from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

from fastapi import FastAPI

from app.config import Settings
from app.crud import list_endpoints
from app.db import get_session


def _schema_or_empty(schema: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    return schema or {"type": "object", "properties": {}}


def _build_operation(endpoint: Any) -> Dict[str, Any]:
    schema = _schema_or_empty(endpoint.response_schema)
    return {
        "summary": endpoint.summary or endpoint.name,
        "description": endpoint.description or "",
        "tags": endpoint.tags or [],
        "responses": {
            str(endpoint.success_status_code): {
                "description": "Successful response",
                "content": {
                    "application/json": {"schema": schema}
                },
            }
        },
    }


def get_openapi(
    app: FastAPI,
    settings: Settings,
    original_openapi: Callable[[], Dict[str, Any]],
) -> Dict[str, Any]:
    if not settings.enable_openapi:
        return original_openapi()

    openapi: Dict[str, Any] = {
        "openapi": "3.0.3",
        "info": {
            "title": app.title or "Mock API",
            "version": app.version or "0.0.0",
            "description": "Dynamic OpenAPI generated from stored mock endpoint definitions.",
        },
        "paths": {},
    }

    with get_session() as session:
        endpoints = list_endpoints(session, limit=1000)

    for endpoint in endpoints:
        if not endpoint.enabled:
            continue
        path = endpoint.path if endpoint.path.startswith("/") else f"/{endpoint.path}"
        method = endpoint.method.lower()
        operations = openapi["paths"].setdefault(path, {})
        operations[method] = _build_operation(endpoint)

    return openapi
