import { describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen, within } from "@testing-library/vue";

import ConnectionManagerCard from "./ConnectionManagerCard.vue";
import { vuetify } from "../plugins/vuetify";
import type { Connection } from "../types/endpoints";

function buildConnection(overrides: Partial<Connection>): Connection {
  return {
    id: 1,
    project: "project-alpha",
    environment: "production",
    name: "Alpha upstream",
    connector_type: "http",
    description: null,
    config: { base_url: "https://alpha.example.com" },
    is_active: true,
    created_at: "2026-03-19T00:00:00Z",
    updated_at: "2026-03-19T00:00:00Z",
    ...overrides,
  };
}

describe("ConnectionManagerCard", () => {
  it("realigns list filters when preferred scope props change", async () => {
    const connections: Connection[] = [
      buildConnection({
        id: 1,
        project: "project-alpha",
        environment: "production",
        name: "Alpha upstream",
      }),
      buildConnection({
        id: 2,
        project: "project-beta",
        environment: "staging",
        name: "Beta upstream",
        config: { base_url: "https://beta.example.com" },
      }),
    ];

    const view = render(ConnectionManagerCard, {
      props: {
        connections,
        preferredProject: "project-alpha",
        preferredEnvironment: "production",
      },
      global: {
        plugins: [vuetify],
      },
    });

    expect(screen.getByText("Alpha upstream")).toBeInTheDocument();
    expect(screen.queryByText("Beta upstream")).not.toBeInTheDocument();

    await view.rerender({
      connections,
      preferredProject: "project-beta",
      preferredEnvironment: "staging",
    });

    expect(screen.getByText("Beta upstream")).toBeInTheDocument();
    expect(screen.queryByText("Alpha upstream")).not.toBeInTheDocument();
  });

  it("keeps API save errors visible after a failed submit", async () => {
    const view = render(ConnectionManagerCard, {
      props: {
        canWrite: true,
        connections: [],
        errorMessage: null,
        isSaving: false,
        preferredProject: "project-alpha",
        preferredEnvironment: "production",
      },
      global: {
        plugins: [vuetify],
      },
    });

    await fireEvent.click(screen.getByRole("button", { name: "New credential" }));
    await fireEvent.update(screen.getByLabelText("Credential name"), "Duplicate name");
    await fireEvent.update(screen.getByLabelText("Base URL"), "https://api.example.com");
    await fireEvent.click(screen.getByRole("button", { name: "Save credential" }));

    await view.rerender({
      canWrite: true,
      connections: [],
      errorMessage: null,
      isSaving: true,
      preferredProject: "project-alpha",
      preferredEnvironment: "production",
    });

    await view.rerender({
      canWrite: true,
      connections: [],
      errorMessage: "Connection 'Duplicate name' is already in use for scope 'project-alpha/production'.",
      isSaving: false,
      preferredProject: "project-alpha",
      preferredEnvironment: "production",
    });

    const dialog = screen.getByRole("dialog");
    expect(
      within(dialog).getByText("Connection 'Duplicate name' is already in use for scope 'project-alpha/production'."),
    ).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Save credential" })).toBeInTheDocument();
  }, 10_000);

  it("emits delete when the operator confirms connection deletion", async () => {
    const confirmSpy = vi.spyOn(window, "confirm").mockReturnValue(true);
    const connection = buildConnection({
      id: 12,
      name: "Delete candidate",
      project: "project-alpha",
      environment: "production",
    });
    const view = render(ConnectionManagerCard, {
      props: {
        canWrite: true,
        connections: [connection],
        preferredProject: "project-alpha",
        preferredEnvironment: "production",
      },
      global: {
        plugins: [vuetify],
      },
    });

    await fireEvent.click(screen.getByRole("button", { name: "Delete" }));

    expect(confirmSpy).toHaveBeenCalledWith(
      'Delete credential "Delete candidate" from scope project-alpha/production? This cannot be undone.',
    );
    expect(view.emitted("delete")).toEqual([[12]]);

    confirmSpy.mockRestore();
  });

  it("preserves redacted HTTP header secrets when editing an existing connection", async () => {
    const connection = buildConnection({
      config: {
        base_url: "https://alpha.example.com",
        headers: {
          "x-api-key": "__ARTIFICER_REDACTED_SECRET__",
        },
      },
      secret_fields: ["config.headers"],
    });

    const view = render(ConnectionManagerCard, {
      props: {
        canWrite: true,
        connections: [connection],
        preferredProject: "project-alpha",
        preferredEnvironment: "production",
      },
      global: {
        plugins: [vuetify],
      },
    });

    await fireEvent.click(screen.getByRole("button", { name: "Edit" }));

    expect(screen.getByText(/Stored secret values are redacted after save/i)).toBeInTheDocument();
    expect(screen.getByLabelText("Shared headers JSON")).toHaveValue('{\n  "x-api-key": "<stored secret>"\n}');

    await fireEvent.click(screen.getByRole("button", { name: "Save credential" }));

    expect(view.emitted("update")).toEqual([
      [
        1,
        expect.objectContaining({
          config: {
            base_url: "https://alpha.example.com",
            headers: {
              "x-api-key": "__ARTIFICER_REDACTED_SECRET__",
            },
          },
        }),
      ],
    ]);
  });
});
