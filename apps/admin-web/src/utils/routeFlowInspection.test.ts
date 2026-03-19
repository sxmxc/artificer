import { describe, expect, it } from "vitest";
import type { Connection, JsonObject, RouteFlowDefinition } from "../types/endpoints";
import { buildRouteFlowInspectionSnapshot } from "./routeFlowInspection";

function createRouteContext(overrides: Partial<Parameters<typeof buildRouteFlowInspectionSnapshot>[1]> = {}) {
  return {
    routeId: 7,
    routeMethod: "POST",
    routeName: "Create health",
    routePath: "/api/health/{service}",
    requestSchema: {
      type: "object",
      properties: {
        healthy: {
          type: "boolean",
        },
      },
      "x-request": {
        query: {
          type: "object",
          properties: {
            mode: {
              type: "string",
              enum: ["simple", "verbose"],
            },
          },
          required: ["mode"],
          "x-builder": {
            order: ["mode"],
          },
        },
      },
    } as JsonObject,
    responseSchema: {
      type: "object",
      properties: {
        ok: {
          type: "boolean",
        },
      },
      required: ["ok"],
      "x-builder": {
        order: ["ok"],
      },
    } as JsonObject,
    successStatusCode: 200,
    ...overrides,
  };
}

describe("routeFlowInspection", () => {
  it("treats request contract data as the entry scope and resolves transform refs against it", () => {
    const definition: RouteFlowDefinition = {
      schema_version: 1,
      nodes: [
        { id: "trigger", type: "api_trigger", name: "API Trigger", config: {} },
        {
          id: "transform",
          type: "transform",
          name: "Transform",
          config: {
            output: {
              method: { $ref: "route.method" },
              service: { $ref: "request.path.service" },
              mode: { $ref: "request.query.mode" },
              healthy: { $ref: "request.body.healthy" },
            },
          },
        },
        {
          id: "response",
          type: "set_response",
          name: "Set Response",
          config: {
            status_code: 200,
            body: { $ref: "state.transform" },
          },
        },
      ],
      edges: [
        { source: "trigger", target: "transform" },
        { source: "transform", target: "response" },
      ],
    };

    const snapshot = buildRouteFlowInspectionSnapshot(definition, createRouteContext());

    expect(snapshot.generatedRequestSample.path).toEqual({ service: "sample-service" });
    expect(snapshot.generatedRequestSample.query).toEqual({ mode: "simple" });
    expect(snapshot.generatedRequestSample.body).toEqual({ healthy: true });
    expect(snapshot.nodesById.transform.scopeEntries.map((entry) => entry.refPath)).toEqual([
      "route",
      "request.path",
      "request.query",
      "request.body",
      "state.trigger",
    ]);
    expect(snapshot.nodesById.transform.outputSample).toEqual({
      method: "POST",
      service: "sample-service",
      mode: "simple",
      healthy: true,
    });
  });

  it("makes Set Response comparison explicit when live flow output diverges from response_schema", () => {
    const definition: RouteFlowDefinition = {
      schema_version: 1,
      nodes: [
        { id: "trigger", type: "api_trigger", name: "API Trigger", config: {} },
        {
          id: "transform",
          type: "transform",
          name: "Transform",
          config: {
            output: {
              route: {
                method: { $ref: "route.method" },
                path: { $ref: "route.path" },
              },
              message: "Replace this starter flow in the Flow tab before deploying to production.",
            },
          },
        },
        {
          id: "response",
          type: "set_response",
          name: "Set Response",
          config: {
            status_code: 200,
            body: { $ref: "state.transform" },
          },
        },
      ],
      edges: [
        { source: "trigger", target: "transform" },
        { source: "transform", target: "response" },
      ],
    };

    const snapshot = buildRouteFlowInspectionSnapshot(definition, createRouteContext());
    const responseInspection = snapshot.nodesById.response;

    expect(responseInspection.outputSample).toEqual({
      body: {
        route: {
          method: "POST",
          path: "/api/health/{service}",
        },
        message: "Replace this starter flow in the Flow tab before deploying to production.",
      },
      status_code: 200,
    });
    expect(responseInspection.responseComparison?.matchesContract).toBe(false);
    expect(responseInspection.responseComparison?.message).toContain("differ");
    expect(responseInspection.boundaryMessage).toContain("Deploy returns this Set Response body");
  });

  it("uses explicit placeholder samples for connector nodes until live execution data exists", () => {
    const connections: Connection[] = [
      {
        id: 12,
        name: "Health upstream",
        connector_type: "http",
        description: null,
        config: {
          base_url: "https://status.example.test",
        },
        is_active: true,
        created_at: "2026-03-19T00:00:00Z",
        updated_at: "2026-03-19T00:00:00Z",
      },
    ];
    const definition: RouteFlowDefinition = {
      schema_version: 1,
      nodes: [
        { id: "trigger", type: "api_trigger", name: "API Trigger", config: {} },
        {
          id: "http-request-1",
          type: "http_request",
          name: "HTTP Request",
          config: {
            connection_id: 12,
            method: "GET",
            path: "/services/{{request.path.service}}",
            query: {
              mode: { $ref: "request.query.mode" },
            },
          },
        },
      ],
      edges: [{ source: "trigger", target: "http-request-1" }],
    };

    const snapshot = buildRouteFlowInspectionSnapshot(definition, createRouteContext(), connections);
    const inspection = snapshot.nodesById["http-request-1"];

    expect(inspection.outputSample).toMatchObject({
      connection: {
        id: 12,
        name: "Health upstream",
      },
      request: {
        method: "GET",
        query: { mode: "simple" },
        url: "https://status.example.test/services/sample-service",
      },
      response: {
        body: {
          _sample: "Connector output is not executed in the editor.",
        },
      },
    });
    expect(inspection.notes[0]).toContain("do not call the upstream service");
  });

  it("treats empty object request schemas as body-less request contracts", () => {
    const definition: RouteFlowDefinition = {
      schema_version: 1,
      nodes: [
        { id: "trigger", type: "api_trigger", name: "API Trigger", config: {} },
      ],
      edges: [],
    };

    const snapshot = buildRouteFlowInspectionSnapshot(
      definition,
      createRouteContext({
        routeMethod: "GET",
        routePath: "/api/health",
        requestSchema: {
          type: "object",
          properties: {},
          required: [],
          "x-builder": {
            order: [],
          },
        } as JsonObject,
      }),
    );

    expect(snapshot.generatedRequestSample.body).toBeNull();
    expect(snapshot.nodesById.trigger.outputSample).toMatchObject({
      request: {
        body_present: false,
      },
    });
  });
});
