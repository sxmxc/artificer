import type { RouteFlowNodeType } from "../types/endpoints";

const ROUTE_FLOW_DRAG_SOURCE = "route-flow-palette";

export type RouteFlowDragPayload =
  | {
      source: typeof ROUTE_FLOW_DRAG_SOURCE;
      kind: "palette-node";
      nodeType: RouteFlowNodeType;
    }
  | {
      source: typeof ROUTE_FLOW_DRAG_SOURCE;
      kind: "reference-snippet";
      refPath: string;
    };

export type RouteFlowPaletteDragPayload = Extract<RouteFlowDragPayload, { kind: "palette-node" }>;
export type RouteFlowReferenceDragPayload = Extract<RouteFlowDragPayload, { kind: "reference-snippet" }>;

function isObjectRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

export function createRouteFlowPaletteDragPayload(nodeType: RouteFlowNodeType): RouteFlowPaletteDragPayload {
  return {
    source: ROUTE_FLOW_DRAG_SOURCE,
    kind: "palette-node",
    nodeType,
  };
}

export function createRouteFlowReferenceDragPayload(refPath: string): RouteFlowReferenceDragPayload {
  return {
    source: ROUTE_FLOW_DRAG_SOURCE,
    kind: "reference-snippet",
    refPath,
  };
}

export function getRouteFlowDragPayload(value: unknown): RouteFlowDragPayload | null {
  if (!isObjectRecord(value) || value.source !== ROUTE_FLOW_DRAG_SOURCE || typeof value.kind !== "string") {
    return null;
  }

  switch (value.kind) {
    case "palette-node":
      return typeof value.nodeType === "string" ? (value as RouteFlowDragPayload) : null;
    case "reference-snippet":
      return typeof value.refPath === "string" ? (value as RouteFlowDragPayload) : null;
    default:
      return null;
  }
}

export function getRouteFlowPaletteDragPayload(value: unknown): RouteFlowPaletteDragPayload | null {
  const payload = getRouteFlowDragPayload(value);
  return payload?.kind === "palette-node" ? payload : null;
}

export function getRouteFlowReferenceDragPayload(value: unknown): RouteFlowReferenceDragPayload | null {
  const payload = getRouteFlowDragPayload(value);
  return payload?.kind === "reference-snippet" ? payload : null;
}
