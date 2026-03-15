import { getPageTransitionKey } from "./routeTransitions";

describe("getPageTransitionKey", () => {
  it("reuses the same key for routes that share a transition shell", () => {
    expect(
      getPageTransitionKey({
        name: "endpoints-browse",
        path: "/endpoints",
        meta: { transitionShell: "endpoint-workspace" },
      }),
    ).toBe("endpoint-workspace");

    expect(
      getPageTransitionKey({
        name: "endpoints-edit",
        path: "/endpoints/42",
        meta: { transitionShell: "endpoint-workspace" },
      }),
    ).toBe("endpoint-workspace");
  });

  it("falls back to the route name when no transition shell is configured", () => {
    expect(
      getPageTransitionKey({
        name: "schema-editor",
        path: "/endpoints/42/schema",
        meta: {},
      }),
    ).toBe("schema-editor");
  });

  it("falls back to the path when the route has no string name", () => {
    expect(
      getPageTransitionKey({
        name: Symbol("preview"),
        path: "/preview",
        meta: {},
      }),
    ).toBe("/preview");
  });
});
