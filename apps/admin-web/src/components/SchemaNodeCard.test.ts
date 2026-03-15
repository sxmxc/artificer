import { fireEvent, render } from "@testing-library/vue";
import SchemaNodeCard from "./SchemaNodeCard.vue";
import { createNode } from "../schemaBuilder";
import { vuetify } from "../plugins/vuetify";

describe("SchemaNodeCard", () => {
  it("keeps nested selection on the clicked child card", async () => {
    const childNode = createNode("string", "response", {
      id: "child-quote",
      mode: "mocking",
      name: "quote",
    });
    const rootNode = createNode("object", "response", {
      children: [childNode],
      id: "parent-root",
      name: "root",
    });

    const { container, emitted } = render(SchemaNodeCard, {
      props: {
        activeNodeId: "parent-root",
        node: rootNode,
        parentId: null,
        parentType: null,
        root: true,
        scope: "response",
      },
      global: {
        plugins: [vuetify],
      },
    });

    const childCard = container.querySelector('[data-node-id="child-quote"]');
    expect(childCard).not.toBeNull();

    await fireEvent.click(childCard as Element);

    expect(emitted().select?.at(-1)).toEqual(["child-quote"]);
  });
});
