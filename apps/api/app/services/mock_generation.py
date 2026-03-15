from __future__ import annotations

import hashlib
import random
from copy import deepcopy
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from faker import Faker

from app.services.schema_contract import normalize_schema_for_builder


DEFAULT_MAX_ITEMS = 3
MOCKING_TEXT_LINES = [
    "mock payload approved by the bird council and absolutely full of itself",
    "another fabricated payload just strutted into the room like it owns staging",
    "this value is fake, polished, and refusing to apologize for it",
    "certified believable enough for demos and just smug enough for QA",
    "side-eye calibrated, overconfident, and technically valid JSON",
    "this response rolled up late, looked amazing, and still passed type checks",
]
MOCKING_FIRST_NAMES = ["Moxie", "Echo", "Piper", "Nova", "Sage", "Jett", "Vex"]
MOCKING_LAST_NAMES = ["Mockwell", "Sideeye", "Payload", "Feather", "Byte", "Chirp", "Snark"]
MOCKING_COMPANIES = [
    "Mockingbird Labs",
    "Side-Eye Systems",
    "Featherweight API Co.",
    "Payload Theatre",
    "Too Real To Ship LLC",
]
MOCKING_CITIES = ["Snarkspur", "Payload Point", "Feather Falls", "Sidetone City", "Mock Harbor"]
MOCKING_STATES = ["Debug State", "Mockshire", "QA Plains", "Payload Province", "Side-Eye Territory"]
MOCKING_COUNTRIES = ["The United States of Placeholder", "Mockland", "Payload Republic", "The Federated States of Ship It"]
MOCKING_STREETS = ["404 Feather Lane", "13 Side-Eye Street", "42 Placeholder Plaza", "418 Teapot Terrace", "7 Hotfix Court"]
MOCKING_SLUG_PARTS = ["mock", "chirp", "payload", "side-eye", "feather", "stunt", "snark", "placeholder"]
MOCKING_PRICE_POINTS = [13.37, 42.42, 88.8, 101.01, 404.04]
MOCKING_INTEGERS = [7, 13, 42, 64, 101, 404, 418, 9001]
MOCK_VALUE_TYPE_ALIASES = {
    "id": "uuid",
    "guid": "uuid",
    "uuid": "uuid",
    "name": "full_name",
    "full_name": "full_name",
    "fullname": "full_name",
    "longtext": "long_text",
}


@dataclass
class GenerationContext:
    rng: random.Random
    faker: Faker


def _stable_seed(identity: str, seed_key: str | None) -> int:
    if seed_key:
        material = f"{identity}:{seed_key}"
    else:
        material = f"{identity}:{random.SystemRandom().randrange(0, 2 ** 63)}"

    digest = hashlib.sha256(material.encode("utf-8")).hexdigest()
    return int(digest[:16], 16)


def build_generation_context(identity: str, seed_key: str | None) -> GenerationContext:
    seed = _stable_seed(identity, seed_key)
    rng = random.Random(seed)
    faker = Faker()
    faker.seed_instance(rng.randint(0, 2 ** 31 - 1))
    return GenerationContext(rng=rng, faker=faker)


def _coerce_int(value: Any, default: int) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, (int, float)):
        return int(value)
    return default


def _coerce_float(value: Any, default: float) -> float:
    if isinstance(value, bool):
        return float(int(value))
    if isinstance(value, (int, float)):
        return float(value)
    return default


def _pick_generator(schema: dict[str, Any]) -> str | None:
    mock_config = schema.get("x-mock", {}) if isinstance(schema, dict) else {}
    value_type = mock_config.get("type") or mock_config.get("generator")
    if value_type:
        normalized = MOCK_VALUE_TYPE_ALIASES.get(str(value_type).strip().lower(), str(value_type).strip().lower())
        if normalized:
            return normalized

    schema_format = str(schema.get("format", "")).lower()
    if schema.get("enum"):
        return "enum"
    if schema_format == "email":
        return "email"
    if schema_format in {"uri", "url"}:
        return "url"
    if schema_format == "uuid":
        return "uuid"
    if schema_format == "date":
        return "date"
    if schema_format == "date-time":
        return "datetime"
    if schema_format == "time":
        return "time"
    schema_type = str(schema.get("type", "")).lower()
    if schema_type == "integer":
        return "integer"
    if schema_type == "number":
        return "number"
    if schema_type == "boolean":
        return "boolean"
    return None


def _mock_mode(schema: dict[str, Any]) -> str:
    if not isinstance(schema, dict):
        return "generate"
    mock_config = schema.get("x-mock", {}) if isinstance(schema.get("x-mock"), dict) else {}
    mode = str(mock_config.get("mode", "generate")).lower()
    return mode if mode in {"fixed", "generate", "mocking"} else "generate"


def _is_mocking_mode(schema: dict[str, Any]) -> bool:
    return _mock_mode(schema) == "mocking"


def _mocking_slug(context: GenerationContext, words: int = 3) -> str:
    return "-".join(context.rng.choice(MOCKING_SLUG_PARTS) for _ in range(max(words, 1)))


def _generate_string(schema: dict[str, Any], context: GenerationContext) -> str:
    generator = _pick_generator(schema) or "text"
    options = schema.get("x-mock", {}).get("options", {})
    min_length = max(_coerce_int(schema.get("minLength"), 0), 0)
    default_max_length = max(min_length, 280 if generator == "long_text" else 48)
    max_length = max(_coerce_int(schema.get("maxLength"), default_max_length), min_length)
    mocking_mode = _is_mocking_mode(schema)

    if generator == "enum" and schema.get("enum"):
        return str(context.rng.choice(schema["enum"]))

    if mocking_mode and generator == "email":
        value = f"{_mocking_slug(context, 2).replace('-', '.')}@mockingbird.test"
    elif mocking_mode and generator == "url":
        value = f"https://mockingbird.test/{_mocking_slug(context, 3)}"
    elif mocking_mode and generator == "uuid":
        value = str(context.faker.uuid4())
    elif mocking_mode and generator == "slug":
        words = max(_coerce_int(options.get("words"), 3), 1)
        value = _mocking_slug(context, words)
    elif mocking_mode and generator == "date":
        value = str(context.faker.date_object())
    elif mocking_mode and generator == "datetime":
        value = context.faker.date_time().isoformat()
    elif mocking_mode and generator == "time":
        value = context.faker.time()
    elif mocking_mode and generator == "first_name":
        value = context.rng.choice(MOCKING_FIRST_NAMES)
    elif mocking_mode and generator == "last_name":
        value = context.rng.choice(MOCKING_LAST_NAMES)
    elif mocking_mode and generator == "full_name":
        value = f"{context.rng.choice(MOCKING_FIRST_NAMES)} {context.rng.choice(MOCKING_LAST_NAMES)}"
    elif mocking_mode and generator == "company":
        value = context.rng.choice(MOCKING_COMPANIES)
    elif mocking_mode and generator == "phone":
        value = f"(555) 01{context.rng.randint(10, 99)}-{context.rng.randint(1000, 9999)}"
    elif mocking_mode and generator == "street_address":
        value = context.rng.choice(MOCKING_STREETS)
    elif mocking_mode and generator == "city":
        value = context.rng.choice(MOCKING_CITIES)
    elif mocking_mode and generator == "state":
        value = context.rng.choice(MOCKING_STATES)
    elif mocking_mode and generator == "country":
        value = context.rng.choice(MOCKING_COUNTRIES)
    elif mocking_mode and generator == "postal_code":
        value = f"{context.rng.randint(10000, 99999)}"
    elif mocking_mode and generator == "avatar_url":
        value = f"https://api.dicebear.com/7.x/fun-emoji/svg?seed={_mocking_slug(context, 2)}"
    elif mocking_mode:
        default_sentences = 2 if generator == "long_text" else 1
        sentences = max(_coerce_int(options.get("sentences"), default_sentences), 1)
        value = " ".join(context.rng.choice(MOCKING_TEXT_LINES) for _ in range(sentences))
    elif generator == "email":
        value = context.faker.email()
    elif generator == "url":
        value = context.faker.url()
    elif generator == "uuid":
        value = str(context.faker.uuid4())
    elif generator == "slug":
        words = max(_coerce_int(options.get("words"), 3), 1)
        value = "-".join(context.faker.words(nb=words))
    elif generator == "date":
        value = str(context.faker.date_object())
    elif generator == "datetime":
        value = context.faker.date_time().isoformat()
    elif generator == "time":
        value = context.faker.time()
    elif generator == "first_name":
        value = context.faker.first_name()
    elif generator == "last_name":
        value = context.faker.last_name()
    elif generator == "full_name":
        value = context.faker.name()
    elif generator == "company":
        value = context.faker.company()
    elif generator == "phone":
        value = context.faker.phone_number()
    elif generator == "street_address":
        value = context.faker.street_address()
    elif generator == "city":
        value = context.faker.city()
    elif generator == "state":
        value = context.faker.state()
    elif generator == "country":
        value = context.faker.country()
    elif generator == "postal_code":
        value = context.faker.postcode()
    elif generator == "avatar_url":
        seed = context.faker.uuid4()
        value = f"https://api.dicebear.com/7.x/fun-emoji/svg?seed={seed}"
    else:
        default_sentences = 3 if generator == "long_text" else 1
        sentences = max(_coerce_int(options.get("sentences"), default_sentences), 1)
        value = " ".join(context.faker.sentences(nb=sentences)).strip()

    if len(value) < min_length:
        filler = context.faker.lexify(text="?" * (min_length - len(value)))
        value = f"{value}{filler}"

    return value[:max_length]


def _generate_integer(schema: dict[str, Any], context: GenerationContext) -> int:
    if schema.get("enum"):
        return int(context.rng.choice(schema["enum"]))

    minimum = _coerce_int(schema.get("minimum"), 0)
    maximum = _coerce_int(schema.get("maximum"), max(minimum, 999))
    if maximum < minimum:
        maximum = minimum

    if _is_mocking_mode(schema):
        candidates = [value for value in MOCKING_INTEGERS if minimum <= value <= maximum]
        if candidates:
            return context.rng.choice(candidates)

    return context.rng.randint(minimum, maximum)


def _generate_number(schema: dict[str, Any], context: GenerationContext) -> float:
    if schema.get("enum"):
        return float(context.rng.choice(schema["enum"]))

    options = schema.get("x-mock", {}).get("options", {})
    generator = _pick_generator(schema) or "float"
    minimum = _coerce_float(schema.get("minimum"), 0.0)
    maximum = _coerce_float(schema.get("maximum"), max(minimum, 999.99))
    if maximum < minimum:
        maximum = minimum

    if _is_mocking_mode(schema):
        preferred = [value for value in MOCKING_PRICE_POINTS if minimum <= value <= maximum]
        if preferred:
            if generator == "price":
                precision = max(_coerce_int(options.get("precision"), 2), 0)
                quantize_pattern = Decimal("1") if precision == 0 else Decimal(f"1.{'0' * precision}")
                return float(Decimal(str(context.rng.choice(preferred))).quantize(quantize_pattern))
            return float(context.rng.choice(preferred))

    if generator == "price":
        precision = max(_coerce_int(options.get("precision"), 2), 0)
        value = Decimal(str(context.rng.uniform(minimum or 1.0, maximum or 999.99)))
        quantize_pattern = Decimal("1") if precision == 0 else Decimal(f"1.{'0' * precision}")
        return float(value.quantize(quantize_pattern))

    return round(context.rng.uniform(minimum, maximum), 2)


def _generate_boolean(context: GenerationContext) -> bool:
    return bool(context.rng.randint(0, 1))


def _generate_object(schema: dict[str, Any], context: GenerationContext) -> dict[str, Any]:
    properties = schema.get("properties", {}) or {}
    property_order = list(schema.get("x-builder", {}).get("order", []) or [])
    for key in properties.keys():
        if key not in property_order:
            property_order.append(key)

    return {
        property_name: generate_value(properties[property_name], context)
        for property_name in property_order
        if property_name in properties
    }


def _generate_array(schema: dict[str, Any], context: GenerationContext) -> list[Any]:
    items = schema.get("items") or {"type": "string"}
    min_items = max(_coerce_int(schema.get("minItems"), 1), 0)
    max_items = max(_coerce_int(schema.get("maxItems"), max(min_items, DEFAULT_MAX_ITEMS)), min_items)
    count = context.rng.randint(min_items, max_items)
    return [generate_value(items, context) for _ in range(count)]


def generate_value(schema: Any, context: GenerationContext) -> Any:
    if not isinstance(schema, dict):
        return deepcopy(schema)

    mock_config = schema.get("x-mock", {}) or {}
    if mock_config.get("mode") == "fixed" and "value" in mock_config:
        return deepcopy(mock_config["value"])

    if "const" in schema:
        return deepcopy(schema["const"])

    schema_type = schema.get("type")

    if schema_type == "object" or "properties" in schema:
        return _generate_object(schema, context)

    if schema_type == "array" or "items" in schema:
        return _generate_array(schema, context)

    if schema_type == "integer":
        return _generate_integer(schema, context)

    if schema_type == "number":
        return _generate_number(schema, context)

    if schema_type == "boolean":
        return _generate_boolean(context)

    return _generate_string(schema, context)


def preview_from_schema(response_schema: dict[str, Any] | None, *, seed_key: str | None, identity: str) -> Any:
    context = build_generation_context(identity, seed_key)
    normalized_schema = normalize_schema_for_builder(response_schema or {}, property_name="root", include_mock=True)
    return generate_value(normalized_schema, context)
