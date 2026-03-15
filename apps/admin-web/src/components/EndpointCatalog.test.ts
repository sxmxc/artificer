import { fireEvent, render, screen } from "@testing-library/vue";
import EndpointCatalog from "./EndpointCatalog.vue";
import { vuetify } from "../plugins/vuetify";

describe("EndpointCatalog", () => {
  it("filters the visible routes by search text", async () => {
    render(EndpointCatalog, {
      props: {
        activeEndpointId: 1,
        endpoints: [
          {
            id: 1,
            name: "List users",
            slug: "list-users",
            method: "GET",
            path: "/api/users",
            category: "users",
            tags: ["users"],
            summary: null,
            description: null,
            enabled: true,
            auth_mode: "none",
            request_schema: {},
            response_schema: {},
            success_status_code: 200,
            error_rate: 0,
            latency_min_ms: 0,
            latency_max_ms: 0,
            seed_key: null,
            created_at: "2026-03-15T00:00:00Z",
            updated_at: "2026-03-15T00:00:00Z",
          },
          {
            id: 2,
            name: "List invoices",
            slug: "list-invoices",
            method: "GET",
            path: "/api/invoices",
            category: "billing",
            tags: ["billing"],
            summary: null,
            description: null,
            enabled: true,
            auth_mode: "none",
            request_schema: {},
            response_schema: {},
            success_status_code: 200,
            error_rate: 0,
            latency_min_ms: 0,
            latency_max_ms: 0,
            seed_key: null,
            created_at: "2026-03-15T00:00:00Z",
            updated_at: "2026-03-15T00:00:00Z",
          },
        ],
        error: null,
        loading: false,
      },
      global: {
        plugins: [vuetify],
      },
    });

    expect(screen.getByText("List users")).toBeInTheDocument();
    expect(screen.getByText("List invoices")).toBeInTheDocument();

    await fireEvent.update(screen.getByPlaceholderText("Search by name, path, method, or category"), "users");

    expect(screen.getByText("List users")).toBeInTheDocument();
    expect(screen.queryByText("List invoices")).not.toBeInTheDocument();
  });
});
