export type JsonValue = string | number | boolean | null | JsonObject | JsonValue[];

export interface JsonObject {
  [key: string]: JsonValue;
}

export interface AdminCredentials {
  username: string;
  password: string;
}

export interface EndpointPayload {
  name: string;
  slug: string;
  method: string;
  path: string;
  category: string | null;
  tags: string[];
  summary: string | null;
  description: string | null;
  enabled: boolean;
  auth_mode: string;
  request_schema: JsonObject | null;
  response_schema: JsonObject | null;
  success_status_code: number;
  error_rate: number;
  latency_min_ms: number;
  latency_max_ms: number;
  seed_key: string | null;
}

export interface Endpoint extends EndpointPayload {
  id: number;
  created_at: string;
  updated_at: string;
}

export interface EndpointDraft {
  name: string;
  slug: string;
  method: string;
  path: string;
  category: string;
  tags: string;
  summary: string;
  description: string;
  enabled: boolean;
  auth_mode: string;
  request_schema: JsonObject;
  response_schema: JsonObject;
  success_status_code: number;
  error_rate: number;
  latency_min_ms: number;
  latency_max_ms: number;
  seed_key: string;
}

export interface PreviewResponsePayload {
  preview: JsonValue;
}
