import type { AdminCredentials, Endpoint, EndpointPayload, JsonObject, PreviewResponsePayload } from "../types/endpoints";

const REMEMBERED_SESSION_KEY = "mockingbird.admin-remembered-session";
const ACTIVE_SESSION_KEY = "mockingbird.admin-active-session";

interface RequestOptions {
  body?: string;
  headers?: Record<string, string>;
  method?: string;
}

export class AdminApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "AdminApiError";
    this.status = status;
  }
}

function buildAuthorizationHeader(credentials: AdminCredentials): string {
  return `Basic ${window.btoa(`${credentials.username}:${credentials.password}`)}`;
}

function parseJsonIfPossible(value: string): unknown {
  if (!value) {
    return null;
  }

  try {
    return JSON.parse(value);
  } catch {
    return value;
  }
}

function readStoredCredentials(storage: Storage | undefined): AdminCredentials | null {
  if (!storage) {
    return null;
  }

  try {
    const rawValue = storage.getItem(ACTIVE_SESSION_KEY) ?? storage.getItem(REMEMBERED_SESSION_KEY);
    if (!rawValue) {
      return null;
    }

    const parsed = JSON.parse(rawValue) as Partial<AdminCredentials>;
    const credentials = {
      username: parsed.username ?? "",
      password: parsed.password ?? "",
    };

    return hasCredentials(credentials) ? credentials : null;
  } catch {
    return null;
  }
}

async function request<T>(path: string, credentials: AdminCredentials, init: RequestOptions = {}): Promise<T> {
  if (!hasCredentials(credentials)) {
    throw new AdminApiError("Enter both username and password to talk to the admin API.", 400);
  }

  const headers = new Headers(init.headers);
  headers.set("Authorization", buildAuthorizationHeader(credentials));

  if (init.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(path, {
    ...init,
    headers,
  });
  const rawBody = await response.text();
  const parsedBody = parseJsonIfPossible(rawBody);

  if (!response.ok) {
    const detail =
      typeof parsedBody === "object" && parsedBody && "detail" in parsedBody
        ? String(parsedBody.detail)
        : rawBody || `${response.status} ${response.statusText}`;

    throw new AdminApiError(detail, response.status);
  }

  return parsedBody as T;
}

export function hasCredentials(credentials: AdminCredentials | null): credentials is AdminCredentials {
  return Boolean(credentials?.username.trim() && credentials.password);
}

export function loadStoredCredentials(): AdminCredentials | null {
  if (typeof window === "undefined") {
    return null;
  }

  return readStoredCredentials(window.sessionStorage) ?? readStoredCredentials(window.localStorage);
}

export function persistCredentials(credentials: AdminCredentials, rememberMe: boolean): void {
  if (typeof window === "undefined") {
    return;
  }

  const serialized = JSON.stringify(credentials);
  window.sessionStorage.setItem(ACTIVE_SESSION_KEY, serialized);

  if (rememberMe) {
    window.localStorage.setItem(REMEMBERED_SESSION_KEY, serialized);
  } else {
    window.localStorage.removeItem(REMEMBERED_SESSION_KEY);
  }
}

export function clearStoredCredentials(): void {
  if (typeof window === "undefined") {
    return;
  }

  window.sessionStorage.removeItem(ACTIVE_SESSION_KEY);
  window.localStorage.removeItem(REMEMBERED_SESSION_KEY);
}

export function listEndpoints(credentials: AdminCredentials): Promise<Endpoint[]> {
  return request<Endpoint[]>("/api/admin/endpoints", credentials);
}

export function getEndpoint(endpointId: number, credentials: AdminCredentials): Promise<Endpoint> {
  return request<Endpoint>(`/api/admin/endpoints/${endpointId}`, credentials);
}

export function createEndpoint(payload: EndpointPayload, credentials: AdminCredentials): Promise<Endpoint> {
  return request<Endpoint>("/api/admin/endpoints", credentials, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateEndpoint(
  endpointId: number,
  payload: EndpointPayload,
  credentials: AdminCredentials,
): Promise<Endpoint> {
  return request<Endpoint>(`/api/admin/endpoints/${endpointId}`, credentials, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export function deleteEndpoint(endpointId: number, credentials: AdminCredentials): Promise<null> {
  return request<null>(`/api/admin/endpoints/${endpointId}`, credentials, {
    method: "DELETE",
  });
}

export function previewResponse(
  responseSchema: JsonObject,
  seedKey: string | null,
  credentials: AdminCredentials,
): Promise<PreviewResponsePayload> {
  return request<PreviewResponsePayload>("/api/admin/endpoints/preview-response", credentials, {
    method: "POST",
    body: JSON.stringify({
      response_schema: responseSchema,
      seed_key: seedKey,
    }),
  });
}
