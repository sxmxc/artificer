import type { Endpoint, RoutePublicationStatus } from "../types/endpoints";

const FALLBACK_ENABLED_STATUS: RoutePublicationStatus = {
  code: "legacy_mock",
  label: "Legacy mock",
  tone: "secondary",
  enabled: true,
  is_public: true,
  is_live: false,
  uses_legacy_mock: true,
  has_saved_implementation: false,
  has_runtime_history: false,
  has_deployment_history: false,
  has_active_deployment: false,
  active_deployment_environment: null,
  active_implementation_id: null,
  active_deployment_id: null,
};

const FALLBACK_DISABLED_STATUS: RoutePublicationStatus = {
  code: "disabled",
  label: "Disabled",
  tone: "error",
  enabled: false,
  is_public: false,
  is_live: false,
  uses_legacy_mock: false,
  has_saved_implementation: false,
  has_runtime_history: false,
  has_deployment_history: false,
  has_active_deployment: false,
  active_deployment_environment: null,
  active_implementation_id: null,
  active_deployment_id: null,
};

export function resolveRoutePublicationStatus(
  endpoint: Pick<Endpoint, "enabled" | "publication_status">,
): RoutePublicationStatus {
  if (endpoint.publication_status) {
    return endpoint.publication_status;
  }
  return endpoint.enabled ? FALLBACK_ENABLED_STATUS : FALLBACK_DISABLED_STATUS;
}

export function routePublicationColor(status: Pick<RoutePublicationStatus, "code" | "tone">): string {
  if (status.code === "published_live") {
    return "accent";
  }
  if (status.code === "disabled") {
    return "error";
  }
  if (status.code === "legacy_mock") {
    return "secondary";
  }
  if (status.code === "draft_only" || status.code === "live_disabled") {
    return "warning";
  }

  if (status.tone === "success") {
    return "accent";
  }
  if (status.tone === "error") {
    return "error";
  }
  if (status.tone === "warning") {
    return "warning";
  }
  return "secondary";
}
