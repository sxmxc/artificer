import { createRootNode, schemaToTree, treeToSchema, validateTree } from "../schemaBuilder";
import type { BuilderScope } from "../schemaBuilder";
import type { Endpoint, EndpointDraft, EndpointPayload, JsonObject } from "../types/endpoints";

function createDefaultSchema(scope: BuilderScope): JsonObject {
  return treeToSchema(createRootNode(scope), scope);
}

function normalizeOptionalString(value: string): string | null {
  const trimmed = value.trim();
  return trimmed ? trimmed : null;
}

function pluralize(count: number, noun: string): string {
  return `${count} ${noun}${count === 1 ? "" : "s"}`;
}

function countNodeFields(schema: JsonObject | null | undefined, scope: BuilderScope): number {
  const tree = schemaToTree(schema, scope);

  const visit = (node: ReturnType<typeof schemaToTree>): number => {
    if (node.type === "object") {
      return node.children.reduce((total, child) => total + 1 + visit(child), 0);
    }

    if (node.type === "array" && node.item) {
      return 1 + visit(node.item);
    }

    return 0;
  };

  return visit(tree);
}

export function describeSchema(schema: JsonObject | null | undefined, scope: BuilderScope): string {
  const tree = schemaToTree(schema, scope);

  if (tree.type === "object") {
    return `${pluralize(tree.children.length, "root field")} across ${pluralize(countNodeFields(schema, scope), "node")}`;
  }

  if (tree.type === "array") {
    return `Array root with ${tree.item ? tree.item.type : "empty"} items`;
  }

  return `${tree.type} root`;
}

export function createEmptyDraft(): EndpointDraft {
  return {
    name: "",
    slug: "",
    method: "GET",
    path: "/api/",
    category: "",
    tags: "",
    summary: "",
    description: "",
    enabled: true,
    auth_mode: "none",
    request_schema: createDefaultSchema("request"),
    response_schema: createDefaultSchema("response"),
    success_status_code: 200,
    error_rate: 0,
    latency_min_ms: 0,
    latency_max_ms: 0,
    seed_key: "",
  };
}

export function draftFromEndpoint(endpoint: Endpoint): EndpointDraft {
  return {
    name: endpoint.name,
    slug: endpoint.slug,
    method: endpoint.method,
    path: endpoint.path,
    category: endpoint.category ?? "",
    tags: endpoint.tags.join(", "),
    summary: endpoint.summary ?? "",
    description: endpoint.description ?? "",
    enabled: endpoint.enabled,
    auth_mode: endpoint.auth_mode,
    request_schema: endpoint.request_schema ?? createDefaultSchema("request"),
    response_schema: endpoint.response_schema ?? createDefaultSchema("response"),
    success_status_code: endpoint.success_status_code,
    error_rate: endpoint.error_rate,
    latency_min_ms: endpoint.latency_min_ms,
    latency_max_ms: endpoint.latency_max_ms,
    seed_key: endpoint.seed_key ?? "",
  };
}

export function endpointToPayload(endpoint: Endpoint, overrides: Partial<EndpointPayload> = {}): EndpointPayload {
  return {
    name: endpoint.name,
    slug: endpoint.slug,
    method: endpoint.method,
    path: endpoint.path,
    category: endpoint.category,
    tags: endpoint.tags,
    summary: endpoint.summary,
    description: endpoint.description,
    enabled: endpoint.enabled,
    auth_mode: endpoint.auth_mode,
    request_schema: endpoint.request_schema,
    response_schema: endpoint.response_schema,
    success_status_code: endpoint.success_status_code,
    error_rate: endpoint.error_rate,
    latency_min_ms: endpoint.latency_min_ms,
    latency_max_ms: endpoint.latency_max_ms,
    seed_key: endpoint.seed_key,
    ...overrides,
  };
}

export function buildPayload(draft: EndpointDraft): { errors: Record<string, string>; payload?: EndpointPayload } {
  const errors: Record<string, string> = {};

  if (!draft.name.trim()) {
    errors.name = "Name is required.";
  }

  if (!draft.slug.trim()) {
    errors.slug = "Slug is required.";
  }

  if (!draft.path.trim()) {
    errors.path = "Path is required.";
  }

  if (!draft.path.startsWith("/")) {
    errors.path = "Path must start with '/'.";
  }

  if (draft.success_status_code < 100 || draft.success_status_code > 599) {
    errors.success_status_code = "Use a valid HTTP status code.";
  }

  if (draft.error_rate < 0 || draft.error_rate > 1) {
    errors.error_rate = "Error rate must stay between 0 and 1.";
  }

  if (draft.latency_max_ms < draft.latency_min_ms) {
    errors.latency_max_ms = "Latency max must be greater than or equal to latency min.";
  }

  const requestTreeError = validateTree(schemaToTree(draft.request_schema, "request"));
  if (requestTreeError) {
    errors.request_schema = requestTreeError;
  }

  const responseTreeError = validateTree(schemaToTree(draft.response_schema, "response"));
  if (responseTreeError) {
    errors.response_schema = responseTreeError;
  }

  if (Object.keys(errors).length > 0) {
    return { errors };
  }

  return {
    errors,
    payload: {
      name: draft.name.trim(),
      slug: draft.slug.trim(),
      method: draft.method.toUpperCase(),
      path: draft.path.trim(),
      category: normalizeOptionalString(draft.category),
      tags: draft.tags
        .split(",")
        .map((tag) => tag.trim())
        .filter(Boolean),
      summary: normalizeOptionalString(draft.summary),
      description: normalizeOptionalString(draft.description),
      enabled: draft.enabled,
      auth_mode: draft.auth_mode,
      request_schema: draft.request_schema,
      response_schema: draft.response_schema,
      success_status_code: draft.success_status_code,
      error_rate: draft.error_rate,
      latency_min_ms: draft.latency_min_ms,
      latency_max_ms: draft.latency_max_ms,
      seed_key: normalizeOptionalString(draft.seed_key),
    },
  };
}

export function describeAdminError(error: unknown, fallbackMessage: string): string {
  return error instanceof Error ? error.message : fallbackMessage;
}
