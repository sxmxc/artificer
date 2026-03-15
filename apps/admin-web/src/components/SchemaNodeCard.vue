<script setup lang="ts">
import { computed, ref } from "vue";
import { canAcceptChildren, nodeLabel, type BuilderNodeType, type BuilderScope, type SchemaBuilderNode } from "../schemaBuilder";

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
  select: [nodeId: string];
  startDrag: [nodeId: string];
}>();

const isContainerOver = ref(false);
const isRowOver = ref(false);

const isSelected = computed(() => props.activeNodeId === props.node.id);
const isContainer = computed(() => canAcceptChildren(props.node));

function startDrag(): void {
  if (!props.root) {
    emit("startDrag", props.node.id);
  }
}

function dropOnContainer(): void {
  isContainerOver.value = false;
  emit("dropContainer", props.node.id);
}

function dropOnRow(): void {
  isRowOver.value = false;
  emit("dropRow", props.node.id);
}
</script>

<template>
  <div class="schema-node-stack">
    <div
      v-if="!root && parentType === 'object'"
      class="schema-drop-zone"
      :class="{ 'schema-drop-zone-active': isRowOver }"
      @dragenter.prevent="isRowOver = true"
      @dragleave.prevent="isRowOver = false"
      @dragover.prevent
      @drop.prevent="dropOnRow"
    >
      Drop here to reorder
    </div>

    <v-card
      class="schema-node-card"
      :class="{ 'schema-node-card-active': isSelected }"
      :data-node-id="node.id"
      :draggable="!root"
      @click.stop="emit('select', node.id)"
      @dragstart="startDrag"
    >
      <v-card-text class="d-flex flex-column ga-3">
        <div class="d-flex align-start justify-space-between ga-3">
          <div class="d-flex align-start ga-3">
            <v-avatar :color="root ? 'secondary' : 'primary'" size="40" variant="tonal">
              <v-icon :icon="root ? 'mdi-pound' : 'mdi-drag-horizontal-variant'" />
            </v-avatar>
            <div>
              <div class="text-subtitle-1 font-weight-bold">
                {{ nodeLabel(node, Boolean(root)) }}
              </div>
              <div class="text-body-2 text-medium-emphasis">
                {{ node.description || (root ? "Root schema shape" : `${node.type} field`) }}
              </div>
            </div>
          </div>

          <div class="d-flex flex-wrap justify-end ga-2">
            <v-chip label size="small" variant="tonal">{{ node.type }}</v-chip>
            <v-chip v-if="scope === 'response'" color="secondary" label size="small" variant="tonal">
              {{ node.mode }}
            </v-chip>
            <v-chip v-if="!root && node.required" color="accent" label size="small" variant="tonal">
              required
            </v-chip>
          </div>
        </div>

        <div
          v-if="isContainer"
          class="schema-drop-zone"
          :class="{ 'schema-drop-zone-active': isContainerOver }"
          @dragenter.prevent="isContainerOver = true"
          @dragleave.prevent="isContainerOver = false"
          @dragover.prevent
          @drop.prevent="dropOnContainer"
        >
          {{ node.type === "array" ? "Drop the item shape here" : "Drop a field into this container" }}
        </div>

        <div v-if="node.type === 'object'" class="d-flex flex-column ga-3">
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
            @select="emit('select', $event)"
            @start-drag="emit('startDrag', $event)"
          />
        </div>

        <div v-else-if="node.type === 'array' && node.item" class="d-flex flex-column ga-3">
          <SchemaNodeCard
            :active-node-id="activeNodeId"
            :node="node.item"
            :parent-id="node.id"
            :parent-type="node.type"
            :scope="scope"
            @drop-container="emit('dropContainer', $event)"
            @drop-row="emit('dropRow', $event)"
            @select="emit('select', $event)"
            @start-drag="emit('startDrag', $event)"
          />
        </div>
      </v-card-text>
    </v-card>
  </div>
</template>
