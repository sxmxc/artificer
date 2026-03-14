# Domain Model

## EndpointDefinition
Represents a managed mock API endpoint.

Fields:
- `id`: UUID
- `name`: human-friendly label
- `slug`: machine-friendly identifier (used in admin UI)
- `method`: HTTP method (GET, POST, etc.)
- `path`: URI path (e.g., `/api/quotes`)
- `category`: grouping (e.g., `quotes`, `users`)
- `tags`: list of tags
- `summary` / `description`: OpenAPI description fields
- `enabled`: boolean
- `auth_mode`: none/basic/api_key/bearer
- `request_schema`: JSON Schema for request body / parameters
- `response_schema`: JSON Schema for response body
- `example_template`: JSON template used to generate mock responses
- `response_mode`: `random` / `template` / `fixed`
- `success_status_code`: HTTP status for successful responses
- `error_rate`: ratio of requests that return an error
- `latency_min_ms`, `latency_max_ms`: for simulated delay
- `seed_key`: deterministic seed for repeatable random output
- `created_at`, `updated_at`: audit timestamps

## Response generation
The system generates mock responses by combining the `response_schema` with the `example_template`.
Random values are inserted in a way that keeps the shape consistent and provides humorous output.

## OpenAPI model
The OpenAPI schema is generated dynamically by mapping `EndpointDefinition` fields to OpenAPI path entries.
- `request_schema` becomes requestBody / parameters.
- `response_schema` becomes response schema.
- `summary` and `description` are used in the OpenAPI operation.
