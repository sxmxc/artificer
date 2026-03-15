import { createDuplicateDraft } from "./endpointDrafts";
import type { Endpoint } from "../types/endpoints";

function createEndpoint(overrides: Partial<Endpoint> = {}): Endpoint {
  return {
    id: 1,
    name: "List devices",
    slug: "list-devices",
    method: "GET",
    path: "/api/devices/{deviceId}",
    category: "devices",
    tags: ["devices"],
    summary: "List devices",
    description: "Returns seeded devices.",
    enabled: true,
    auth_mode: "none",
    request_schema: {
      type: "object",
      properties: {
        limit: { type: "integer" },
      },
    },
    response_schema: {
      type: "object",
      properties: {
        deviceId: { type: "string" },
      },
    },
    success_status_code: 200,
    error_rate: 0,
    latency_min_ms: 0,
    latency_max_ms: 0,
    seed_key: "devices",
    created_at: "2026-03-15T00:00:00Z",
    updated_at: "2026-03-15T00:00:00Z",
    ...overrides,
  };
}

describe("createDuplicateDraft", () => {
  it("creates a disabled copy with unique identity fields", () => {
    const source = createEndpoint();
    const existingEndpoints = [
      source,
      createEndpoint({
        id: 2,
        name: "List devices copy",
        slug: "list-devices-copy",
        path: "/api/devices-copy/{deviceId}",
      }),
    ];

    const duplicate = createDuplicateDraft(source, existingEndpoints);

    expect(duplicate.name).toBe("List devices copy 2");
    expect(duplicate.slug).toBe("list-devices-copy-2");
    expect(duplicate.path).toBe("/api/devices-copy-2/{deviceId}");
    expect(duplicate.enabled).toBe(false);
    expect(duplicate.method).toBe(source.method);
    expect(duplicate.seed_key).toBe(source.seed_key);
  });

  it("deep clones request and response schemas so edits do not mutate the source endpoint", () => {
    const source = createEndpoint();
    const sourceRequestSchema = source.request_schema as {
      properties: Record<string, { type: string }>;
    };
    const sourceResponseSchema = source.response_schema as {
      properties: Record<string, { type: string }>;
    };

    const duplicate = createDuplicateDraft(source, [source]);
    (duplicate.request_schema.properties as Record<string, { type: string }>).limit.type = "number";
    (duplicate.response_schema.properties as Record<string, { type: string }>).deviceId.type = "integer";

    expect(sourceRequestSchema.properties.limit.type).toBe("integer");
    expect(sourceResponseSchema.properties.deviceId.type).toBe("string");
  });
});
