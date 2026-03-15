import {
  addNodeToContainer,
  createNode,
  createRootNode,
  defaultGeneratorForType,
  insertNewNodeAfterSibling,
  moveNodeAfterSibling,
  recommendedMaxLengthForValueType,
  schemaToTree,
  treeToSchema,
  updateNode,
} from "./schemaBuilder";

describe("schemaBuilder utilities", () => {
  it("round-trips response schemas with builder metadata", () => {
    const source = {
      type: "object",
      properties: {
        id: {
          type: "string",
          format: "uuid",
          "x-mock": { mode: "generate", type: "id", options: {} },
        },
        status: {
          type: "string",
          enum: ["ok", "queued"],
          "x-mock": { mode: "mocking", type: "enum", options: {} },
        },
      },
      required: ["id", "status"],
      "x-builder": { order: ["id", "status"] },
      "x-mock": { mode: "generate", options: {} },
    };

    const tree = schemaToTree(source, "response");
    const roundTripped = treeToSchema(tree, "response");

    expect(roundTripped).toMatchObject(source);
  });

  it("adds and reorders fields within object containers", () => {
    let tree = createRootNode("response");
    tree = addNodeToContainer(tree, tree.id, "string", "response");
    tree = addNodeToContainer(tree, tree.id, "number", "response");

    tree = updateNode(tree, tree.children[0].id, (node) => ({ ...node, name: "firstField" }));
    tree = updateNode(tree, tree.children[1].id, (node) => ({ ...node, name: "secondField" }));
    tree = moveNodeAfterSibling(tree, tree.children[0].id, tree.children[1].id);

    const schema = treeToSchema(tree, "response");
    expect((schema["x-builder"] as { order: string[] }).order).toEqual(["secondField", "firstField"]);
  });

  it("inserts a sibling after a selected row", () => {
    let tree = createRootNode("request");
    tree = addNodeToContainer(tree, tree.id, "string", "request");
    tree = updateNode(tree, tree.children[0].id, (node) => ({ ...node, name: "title" }));
    tree = insertNewNodeAfterSibling(tree, tree.children[0].id, "boolean", "request");

    expect(tree.children).toHaveLength(2);
    expect(tree.children[1].type).toBe("boolean");
  });

  it("uses the long-text generator and length defaults for quote-like fields", () => {
    expect(defaultGeneratorForType("string", "quote")).toBe("long_text");

    const node = createNode("string", "response", { name: "quote" });
    expect(node.generator).toBe("long_text");
    expect(node.maxLength).toBe(recommendedMaxLengthForValueType("long_text"));
  });

  it("upgrades legacy text generators on quote-like schemas inside the builder", () => {
    const tree = schemaToTree(
      {
        type: "object",
        properties: {
          quote: {
            type: "string",
            "x-mock": { mode: "mocking", type: "text", options: {} },
          },
        },
        required: ["quote"],
        "x-builder": { order: ["quote"] },
        "x-mock": { mode: "generate", options: {} },
      },
      "response",
    );

    expect(tree.children[0]?.generator).toBe("long_text");
    expect(tree.children[0]?.maxLength).toBe(recommendedMaxLengthForValueType("long_text"));
  });
});
