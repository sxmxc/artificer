<script setup lang="ts">
import { computed, ref } from "vue";
import { isScalarNode, nodeLabel, valueTypeLabel, type BuilderNodeType, type BuilderScope, type SchemaBuilderNode } from "../schemaBuilder";
import { setPillDragImage } from "../utils/dragGhost";

const props = defineProps<{
  activeNodeId: string;
  node: SchemaBuilderNode;
  parentId: string | null;
  parentType: BuilderNodeType | null;
  root?: boolean;
  scope: BuilderScope;
}>();

const emit = defineEmits<{
  dropContainer: [containerId: string];
  dropRow: [nodeId: string];
  dropValue: [nodeId: string];
  select: [nodeId: string];
  startDrag: [nodeId: string, event?: DragEvent];
}>();

const isRowOver = ref(false);
const isTailOver = ref(false);
const isValueOver = ref(false);

const isSelected = computed(() => props.activeNodeId === props.node.id);
const hasValueLane = computed(() => props.scope === "response" && isScalarNode(props.node));
const nodeSummary = computed(() => props.node.description || (props.root ? "Top-level schema" : `${props.node.type} field`));
const nodeIcon = computed(() => {
  switch (props.node.type) {
    case "array":
      return "mdi-code-brackets";
    case "boolean":
      return "mdi-toggle-switch-outline";
    case "enum":
      return "mdi-format-list-bulleted-square";
    case "integer":
      return "mdi-pound";
    case "number":
      return "mdi-decimal";
    case "object":
      return "mdi-code-braces";
    case "string":
    default:
      return "mdi-format-letter-case";
  }
});
const rowInsertTitle = computed(() => `Insert or move a field before ${nodeLabel(props.node, Boolean(props.root)).toLowerCase()}`);
const tailInsertTitle = computed(() => {
  if (props.node.type === "array") {
    return props.node.item ? "Replace the array item shape" : "Set the array item shape";
  }

  return props.node.children.length ? `Add a field to the end of ${nodeLabel(props.node, Boolean(props.root)).toLowerCase()}` : "Add the first field";
});
const valueDropTitle = computed(() => `Set the response value for ${nodeLabel(props.node, Boolean(props.root)).toLowerCase()}`);
const valueModeLabel = computed(() => {
  if (props.node.parameterSource) {
    return "Route";
  }

  if (props.node.mode === "fixed") {
    return "Static";
  }

  if (props.node.mode === "mocking") {
    return "Mocking";
  }

  return "Random";
});
const valueSlotLabel = computed(() => (
  props.node.parameterSource
    ? props.node.parameterSource
    : props.node.mode === "fixed"
      ? "Fixed value"
      : valueTypeLabel(props.node.generator)
));
const valueModeClass = computed(() => `schema-value-slot-${props.node.parameterSource ? "parameter" : props.node.mode}`);

function startDrag(event: DragEvent): void {
  if (props.root) {
    return;
  }

  if (event.dataTransfer) {
    event.dataTransfer.effectAllowed = "move";
    event.dataTransfer.dropEffect = "move";
    event.dataTransfer.setData("text/plain", props.node.id);
  }

  const source = event.currentTarget;
  if (source instanceof HTMLElement) {
    source.classList.add("schema-node-pill-drag-source");
    source.addEventListener("dragend", () => {
      source.classList.remove("schema-node-pill-drag-source");
    }, { once: true });
  }

  setPillDragImage(event, {
    eyebrow: props.node.type,
    label: nodeLabel(props.node, Boolean(props.root)),
    tone: "node",
  });

  emit("startDrag", props.node.id, event);
}

function dropOnContainer(): void {
  isTailOver.value = false;
  emit("dropContainer", props.node.id);
}

function dropOnRow(): void {
  isRowOver.value = false;
  emit("dropRow", props.node.id);
}

function dropOnValue(): void {
  isValueOver.value = false;
  emit("dropValue", props.node.id);
}

function forwardStartDrag(nodeId: string, event?: DragEvent): void {
  emit("startDrag", nodeId, event);
}
</script>

<template>
  <div class="schema-tree-node" :class="{ 'schema-tree-node-branch': !root, 'schema-tree-node-root': root }">
    <div v-if="!root && parentType === 'object'" class="schema-insert-anchor-slot schema-insert-anchor-slot-top">
      <button
        class="schema-insert-anchor schema-insert-anchor-key"
        :class="{ 'schema-insert-anchor-active': isRowOver }"
        :aria-label="rowInsertTitle"
        :title="rowInsertTitle"
        data-drop-zone="row"
        :data-drop-target="node.id"
        type="button"
        @dragenter.prevent="isRowOver = true"
        @dragleave.prevent="isRowOver = false"
        @dragover.prevent
        @drop.prevent="dropOnRow"
      >
        <v-icon icon="mdi-plus" size="16" />
      </button>
    </div>

    <div class="schema-tree-row" :class="{ 'schema-tree-row-selected': isSelected, 'schema-tree-row-root': root }">
      <button
        class="schema-node-pill"
        :class="{ 'schema-node-pill-root': root, 'schema-node-pill-selected': isSelected }"
        :data-node-id="node.id"
        :draggable="!root"
        :title="nodeSummary"
        type="button"
        @click.stop="emit('select', node.id)"
        @dragstart.stop="startDrag"
      >
        <span class="schema-node-pill-handle">
          <v-icon :icon="nodeIcon" size="16" />
        </span>
        <span class="schema-node-pill-label">
          {{ nodeLabel(node, Boolean(root)) }}
        </span>
      </button>

      <v-chip class="schema-node-kind-pill" label size="small" variant="tonal">
        {{ node.type }}
      </v-chip>

      <button
        v-if="hasValueLane"
        class="schema-value-slot"
        :class="[valueModeClass, { 'schema-value-slot-active': isValueOver }]"
        :aria-label="valueDropTitle"
        :title="valueDropTitle"
        data-drop-zone="value"
        :data-drop-target="node.id"
        type="button"
        @dragenter.prevent="isValueOver = true"
        @dragleave.prevent="isValueOver = false"
        @dragover.prevent
        @drop.prevent="dropOnValue"
      >
        <span class="schema-value-slot-mode">{{ valueModeLabel }}</span>
        <span class="schema-value-slot-label">{{ valueSlotLabel }}</span>
      </button>

      <v-chip v-if="!root && node.required" class="schema-node-required-pill" color="accent" label size="small" variant="tonal">
        required
      </v-chip>
    </div>

    <div v-if="node.type === 'object'" class="schema-tree-children">
      <SchemaNodeCard
        v-for="child in node.children"
        :key="child.id"
        :active-node-id="activeNodeId"
        :node="child"
        :parent-id="node.id"
        :parent-type="node.type"
        :scope="scope"
        @drop-container="emit('dropContainer', $event)"
        @drop-row="emit('dropRow', $event)"
        @drop-value="emit('dropValue', $event)"
        @select="emit('select', $event)"
        @start-drag="forwardStartDrag"
      />

      <div class="schema-insert-anchor-slot schema-insert-anchor-slot-bottom">
        <button
          class="schema-insert-anchor schema-insert-anchor-key"
          :class="{ 'schema-insert-anchor-active': isTailOver }"
          :aria-label="tailInsertTitle"
          :title="tailInsertTitle"
          data-drop-zone="container"
          :data-drop-target="node.id"
          type="button"
          @dragenter.prevent="isTailOver = true"
          @dragleave.prevent="isTailOver = false"
          @dragover.prevent
          @drop.prevent="dropOnContainer"
        >
          <v-icon icon="mdi-plus" size="16" />
        </button>
      </div>
    </div>

    <div v-else-if="node.type === 'array'" class="schema-tree-children schema-tree-children-array">
      <SchemaNodeCard
        v-if="node.item"
        :active-node-id="activeNodeId"
        :node="node.item"
        :parent-id="node.id"
        :parent-type="node.type"
        :scope="scope"
        @drop-container="emit('dropContainer', $event)"
        @drop-row="emit('dropRow', $event)"
        @drop-value="emit('dropValue', $event)"
        @select="emit('select', $event)"
        @start-drag="forwardStartDrag"
      />

      <div class="schema-insert-anchor-slot schema-insert-anchor-slot-bottom">
        <button
          class="schema-insert-anchor schema-insert-anchor-key"
          :class="{ 'schema-insert-anchor-active': isTailOver }"
          :aria-label="tailInsertTitle"
          :title="tailInsertTitle"
          data-drop-zone="container"
          :data-drop-target="node.id"
          type="button"
          @dragenter.prevent="isTailOver = true"
          @dragleave.prevent="isTailOver = false"
          @dragover.prevent
          @drop.prevent="dropOnContainer"
        >
          <v-icon icon="mdi-plus" size="16" />
        </button>
      </div>
    </div>
  </div>
</template>
