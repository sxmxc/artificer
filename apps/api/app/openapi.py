from __future__ import annotations

import re
from typing import Any, Callable, Dict, List, Optional

from fastapi import FastAPI

from app.config import Settings
from app.crud import list_endpoints
from app.db import session_scope
from app.services.schema_contract import sanitize_public_schema


BODY_METHODS = {"post", "put", "patch"}


def _schema_or_empty(schema: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    return sanitize_public_schema(schema or {"type": "object", "properties": {}})


def _path_parameters(path: str) -> List[Dict[str, Any]]:
    parameters: List[Dict[str, Any]] = []
    seen: set[str] = set()

    for match in re.finditer(r"\{([^}]+)\}", path):
        name = match.group(1).strip()
        if not name or name in seen:
            continue

        seen.add(name)
        parameters.append(
            {
                "in": "path",
                "name": name,
                "required": True,
                "schema": {"type": "string"},
            }
        )

    return parameters


def _build_operation(endpoint: Any) -> Dict[str, Any]:
    operation = {
        "summary": endpoint.summary or endpoint.name,
        "description": endpoint.description or "",
        "tags": endpoint.tags or [],
        "responses": {
            str(endpoint.success_status_code): {
                "description": "Successful response",
                "content": {
                    "application/json": {"schema": _schema_or_empty(endpoint.response_schema)}
                },
            }
        },
    }

    path_parameters = _path_parameters(endpoint.path or "")
    if path_parameters:
        operation["parameters"] = path_parameters

    if endpoint.method.lower() in BODY_METHODS and endpoint.request_schema:
        operation["requestBody"] = {
            "required": True,
            "content": {
                "application/json": {
                    "schema": _schema_or_empty(endpoint.request_schema),
                }
            },
        }

    return operation


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
            "description": "Mockingbird publishes a live OpenAPI document generated from the active public endpoint catalog.",
        },
        "paths": {},
    }

    with session_scope() as session:
        endpoints = list_endpoints(session, limit=1000)

    for endpoint in endpoints:
        if not endpoint.enabled:
            continue
        path = endpoint.path if endpoint.path.startswith("/") else f"/{endpoint.path}"
        method = endpoint.method.lower()
        operations = openapi["paths"].setdefault(path, {})
        operations[method] = _build_operation(endpoint)

    return openapi
