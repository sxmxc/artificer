<script setup lang="ts">
import { computed, ref } from "vue";
import type { Endpoint } from "../types/endpoints";

const props = defineProps<{
  activeEndpointId?: number | null;
  endpoints: Endpoint[];
  error: string | null;
  loading: boolean;
}>();

const emit = defineEmits<{
  create: [];
  refresh: [];
  select: [endpointId: number];
}>();

const search = ref("");
const statusFilter = ref<"all" | "live" | "disabled">("all");
const methodFilter = ref("all");

const methodOptions = computed(() => {
  const methods = new Set(props.endpoints.map((endpoint) => endpoint.method));
  return ["all", ...Array.from(methods).sort()];
});

const filteredEndpoints = computed(() =>
  props.endpoints.filter((endpoint) => {
    const matchesSearch =
      !search.value.trim() ||
      [endpoint.name, endpoint.path, endpoint.category ?? "", endpoint.method]
        .join(" ")
        .toLowerCase()
        .includes(search.value.trim().toLowerCase());

    const matchesStatus =
      statusFilter.value === "all" ||
      (statusFilter.value === "live" ? endpoint.enabled : !endpoint.enabled);

    const matchesMethod = methodFilter.value === "all" || endpoint.method === methodFilter.value;

    return matchesSearch && matchesStatus && matchesMethod;
  }),
);
</script>

<template>
  <v-card class="workspace-card">
    <v-card-item>
      <template #prepend>
        <v-avatar color="primary" variant="tonal">
          <v-icon icon="mdi-routes" />
        </v-avatar>
      </template>

      <v-card-title>Endpoint catalog</v-card-title>
      <v-card-subtitle>Search, filter, and jump between live mock routes.</v-card-subtitle>

      <template #append>
        <div class="d-flex ga-2">
          <v-btn
            :loading="loading && endpoints.length > 0"
            icon="mdi-refresh"
            variant="text"
            @click="emit('refresh')"
          />
          <v-btn color="primary" prepend-icon="mdi-plus" @click="emit('create')">
            New
          </v-btn>
        </div>
      </template>
    </v-card-item>

    <v-card-text class="d-flex flex-column ga-4">
      <v-text-field
        v-model="search"
        hide-details
        placeholder="Search by name, path, method, or category"
        prepend-inner-icon="mdi-magnify"
      />

      <div class="d-flex flex-wrap ga-3">
        <v-chip-group v-model="statusFilter" color="secondary" mandatory selected-class="text-secondary">
          <v-chip value="all" filter variant="outlined">All</v-chip>
          <v-chip value="live" filter variant="outlined">Live</v-chip>
          <v-chip value="disabled" filter variant="outlined">Disabled</v-chip>
        </v-chip-group>

        <v-chip-group v-model="methodFilter" color="primary" mandatory selected-class="text-primary">
          <v-chip
            v-for="method in methodOptions"
            :key="method"
            :value="method"
            filter
            variant="outlined"
          >
            {{ method === "all" ? "Any method" : method }}
          </v-chip>
        </v-chip-group>
      </div>

      <v-alert v-if="error" border="start" color="error" variant="tonal">
        {{ error }}
      </v-alert>

      <v-skeleton-loader
        v-if="loading && endpoints.length === 0 && !error"
        type="list-item-two-line, list-item-two-line, list-item-two-line, list-item-two-line"
      />

      <v-alert v-else-if="!filteredEndpoints.length" border="start" color="info" variant="tonal">
        No endpoints match the current filters.
      </v-alert>

      <v-list v-else class="catalog-list" lines="three" rounded="xl">
        <v-list-item
          v-for="endpoint in filteredEndpoints"
          :key="endpoint.id"
          :active="endpoint.id === activeEndpointId"
          class="catalog-item"
          rounded="xl"
          @click="emit('select', endpoint.id)"
        >
          <template #prepend>
            <v-avatar :color="endpoint.enabled ? 'accent' : 'surface-variant'" size="44" variant="tonal">
              <span class="text-caption font-weight-bold">{{ endpoint.method }}</span>
            </v-avatar>
          </template>

          <v-list-item-title class="font-weight-bold">{{ endpoint.name }}</v-list-item-title>
          <v-list-item-subtitle>{{ endpoint.path }}</v-list-item-subtitle>

          <template #append>
            <div class="d-flex flex-column align-end ga-2">
              <v-chip :color="endpoint.enabled ? 'accent' : 'surface-variant'" label size="small" variant="tonal">
                {{ endpoint.enabled ? "Live" : "Disabled" }}
              </v-chip>
              <span class="text-caption text-medium-emphasis">{{ endpoint.category || "uncategorized" }}</span>
            </div>
          </template>
        </v-list-item>
      </v-list>
    </v-card-text>
  </v-card>
</template>
