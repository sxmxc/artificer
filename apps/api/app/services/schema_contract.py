from __future__ import annotations

from copy import deepcopy
from typing import Any


DEFAULT_ROOT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {},
    "required": [],
    "x-builder": {"order": []},
}
MOCK_VALUE_TYPE_ALIASES = {
    "uuid": "id",
    "guid": "id",
    "full_name": "name",
    "fullname": "name",
    "float": "number",
    "longtext": "long_text",
    "keyboard": "keyboard_key",
    "keycap": "keyboard_key",
    "hotkey": "keyboard_key",
    "filename": "file_name",
    "mime": "mime_type",
    "contenttype": "mime_type",
    "mediatype": "mime_type",
    "systemverb": "verb",
}
STRING_FORMAT_BY_VALUE_TYPE = {
    "id": "uuid",
    "email": "email",
    "url": "uri",
    "date": "date",
    "datetime": "date-time",
    "time": "time",
}


def default_response_root() -> dict[str, Any]:
    root = deepcopy(DEFAULT_ROOT_SCHEMA)
    root["x-mock"] = {"mode": "generate"}
    return root


def _normalize_mock_mode(raw_mode: Any) -> str:
    normalized = str(raw_mode or "generate").lower()
    return normalized if normalized in {"generate", "fixed", "mocking"} else "generate"


def normalize_mock_value_type(raw_value_type: Any) -> str | None:
    normalized = str(raw_value_type or "").strip().lower()
    if not normalized:
        return None
    return MOCK_VALUE_TYPE_ALIASES.get(normalized, normalized)


def default_request_root() -> dict[str, Any]:
    return deepcopy(DEFAULT_ROOT_SCHEMA)


def sanitize_public_schema(schema: Any) -> Any:
    if isinstance(schema, list):
        return [sanitize_public_schema(item) for item in schema]

    if not isinstance(schema, dict):
        return schema

    sanitized: dict[str, Any] = {}
    for key, value in schema.items():
        if key in {"x-mock", "x-builder"}:
            continue
        sanitized[key] = sanitize_public_schema(value)
    return sanitized


def infer_schema_from_value(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        properties = {key: infer_schema_from_value(child) for key, child in value.items()}
        return {
            "type": "object",
            "properties": properties,
            "required": list(value.keys()),
            "x-builder": {"order": list(value.keys())},
        }

    if isinstance(value, list):
        item_schema = infer_schema_from_value(value[0]) if value else {"type": "string"}
        return {
            "type": "array",
            "items": item_schema,
            "minItems": len(value),
            "maxItems": len(value),
        }

    if isinstance(value, bool):
        return {"type": "boolean"}

    if isinstance(value, int) and not isinstance(value, bool):
        return {"type": "integer"}

    if isinstance(value, float):
        return {"type": "number"}

    if value is None:
        return {"type": "string"}

    return {"type": "string"}


def guess_mock_value_type(property_name: str, schema: dict[str, Any]) -> str | None:
    normalized_name = property_name.replace("-", "_").lower()
    schema_format = str(schema.get("format", "")).lower()
    schema_type = str(schema.get("type", "")).lower()

    if schema.get("enum"):
        return "enum"

    if schema_format == "email" or "email" in normalized_name:
        return "email"
    if schema_format in {"uri", "url"}:
        return "url"
    if schema_format == "uuid" or normalized_name in {"id", "uuid"} or normalized_name.endswith("_id"):
        return "id"
    if normalized_name in {"username", "user_name", "handle"}:
        return "username"
    if "password" in normalized_name:
        return "password"
    if normalized_name in {"keyboard_key", "keyboardkey", "shortcut", "shortcut_key", "shortcutkey", "hotkey", "key_name", "keyname", "keycap"}:
        return "keyboard_key"
    if normalized_name in {"verb", "action", "command", "operation", "job_action", "jobaction", "system_action", "systemaction"}:
        return "verb"
    if normalized_name in {"file_name", "filename", "document_name", "documentname", "attachment_name", "attachmentname"}:
        return "file_name"
    if normalized_name in {"mime_type", "mimetype", "content_type", "contenttype", "media_type", "mediatype"}:
        return "mime_type"
    if schema_format == "date":
        return "date"
    if schema_format == "date-time":
        return "datetime"
    if schema_format == "time":
        return "time"
    if "slug" in normalized_name:
        return "slug"
    if normalized_name in {"firstname", "first_name", "given_name"}:
        return "first_name"
    if normalized_name in {"lastname", "last_name", "surname"}:
        return "last_name"
    if normalized_name in {"name", "displayname", "display_name", "full_name", "fullname"}:
        return "name"
    if "company" in normalized_name or "organization" in normalized_name:
        return "company"
    if "phone" in normalized_name:
        return "phone"
    if "street" in normalized_name or "address" in normalized_name:
        return "street_address"
    if "city" in normalized_name:
        return "city"
    if "state" in normalized_name or "province" in normalized_name:
        return "state"
    if "country" in normalized_name:
        return "country"
    if "zip" in normalized_name or "postal" in normalized_name:
        return "postal_code"
    if "avatar" in normalized_name or "image" in normalized_name:
        return "avatar_url"
    if "price" in normalized_name or "amount" in normalized_name or "total" in normalized_name:
        return "price"
    if (
        "message" in normalized_name
        or "quote" in normalized_name
        or "details" in normalized_name
        or "description" in normalized_name
        or "content" in normalized_name
        or normalized_name == "body"
    ):
        return "long_text"
    if schema_type == "integer":
        return "integer"
    if schema_type == "number":
        return "number"
    if schema_type == "boolean":
        return "boolean"
    if schema_type == "string":
        return "text"

    return None


def _normalize_object_schema(schema: dict[str, Any], *, include_mock: bool) -> dict[str, Any]:
    properties = schema.get("properties", {})
    property_order = list(schema.get("x-builder", {}).get("order", []) or [])

    for key in properties.keys():
        if key not in property_order:
            property_order.append(key)

    normalized = dict(schema)
    normalized["type"] = "object"
    normalized["properties"] = {
        key: normalize_schema_for_builder(child, property_name=key, include_mock=include_mock)
        for key, child in properties.items()
    }
    normalized["required"] = list(schema.get("required", []))
    normalized["x-builder"] = {"order": property_order}

    if include_mock:
        normalized["x-mock"] = dict(schema.get("x-mock", {}) or {"mode": "generate"})
        normalized["x-mock"]["mode"] = _normalize_mock_mode(normalized["x-mock"].get("mode"))

    return normalized


def _normalize_array_schema(schema: dict[str, Any], *, property_name: str, include_mock: bool) -> dict[str, Any]:
    normalized = dict(schema)
    normalized["type"] = "array"
    normalized["items"] = normalize_schema_for_builder(
        schema.get("items") or {"type": "string"},
        property_name=property_name,
        include_mock=include_mock,
    )

    if include_mock:
        normalized["x-mock"] = dict(schema.get("x-mock", {}) or {"mode": "generate"})
        normalized["x-mock"]["mode"] = _normalize_mock_mode(normalized["x-mock"].get("mode"))

    return normalized


def normalize_schema_for_builder(
    schema: Any,
    *,
    property_name: str = "value",
    include_mock: bool,
) -> dict[str, Any]:
    if not isinstance(schema, dict) or not schema:
        return default_response_root() if include_mock and property_name == "root" else default_request_root()

    schema_type = schema.get("type")

    if schema_type == "object" or "properties" in schema:
        return _normalize_object_schema(schema, include_mock=include_mock)

    if schema_type == "array" or "items" in schema:
        return _normalize_array_schema(schema, property_name=property_name, include_mock=include_mock)

    normalized = dict(schema)
    if include_mock:
        mock_config = dict(schema.get("x-mock", {}) or {})
        mock_config["mode"] = _normalize_mock_mode(mock_config.get("mode"))
        mock_value_type = normalize_mock_value_type(mock_config.get("type") or mock_config.get("generator"))
        guessed_value_type = guess_mock_value_type(property_name, normalized)
        resolved_value_type = (
            guessed_value_type
            if mock_value_type == "text" and guessed_value_type == "long_text"
            else mock_value_type or guessed_value_type
        )
        if mock_config["mode"] in {"generate", "mocking"}:
            if resolved_value_type:
                mock_config["type"] = resolved_value_type
                # Keep the legacy alias populated so older records and tests still round-trip cleanly.
                mock_config["generator"] = resolved_value_type
            mock_config.setdefault("options", {})
        normalized["x-mock"] = mock_config
        if normalized.get("type") == "string" and "format" not in normalized and resolved_value_type in STRING_FORMAT_BY_VALUE_TYPE:
            normalized["format"] = STRING_FORMAT_BY_VALUE_TYPE[resolved_value_type]
    return normalized


def build_fixed_schema_from_example(value: Any) -> dict[str, Any]:
    inferred = infer_schema_from_value(value)
    normalized = normalize_schema_for_builder(inferred, property_name="root", include_mock=True)
    normalized["x-mock"] = {
        "mode": "fixed",
        "value": value,
        "options": {},
    }
    return normalized


def migrate_legacy_response_schema(
    response_schema: Any,
    example_template: Any,
    response_mode: str | None,
) -> dict[str, Any]:
    normalized_mode = (response_mode or "random").lower()
    has_schema = isinstance(response_schema, dict) and bool(response_schema)

    if normalized_mode in {"fixed", "template"} and example_template is not None:
        return build_fixed_schema_from_example(example_template)

    if has_schema:
        return normalize_schema_for_builder(response_schema, property_name="root", include_mock=True)

    if example_template is not None:
        if normalized_mode == "random":
            inferred = infer_schema_from_value(example_template)
            return normalize_schema_for_builder(inferred, property_name="root", include_mock=True)
        return build_fixed_schema_from_example(example_template)

    return default_response_root()
