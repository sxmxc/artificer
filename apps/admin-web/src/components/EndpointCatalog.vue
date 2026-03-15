<script setup lang="ts">
import { computed, ref, watch } from "vue";
import type { Endpoint } from "../types/endpoints";

const ITEMS_PER_PAGE = 8;

const props = defineProps<{
  activeEndpointId?: number | null;
  endpoints: Endpoint[];
  error: string | null;
  loading: boolean;
}>();

const emit = defineEmits<{
  create: [];
  duplicate: [endpointId: number];
  refresh: [];
  select: [endpointId: number];
}>();

const search = ref("");
const statusFilter = ref<"all" | "live" | "disabled">("all");
const methodFilter = ref("all");
const currentPage = ref(1);

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

const totalPages = computed(() => Math.max(1, Math.ceil(filteredEndpoints.value.length / ITEMS_PER_PAGE)));
const paginatedEndpoints = computed(() => {
  const start = (currentPage.value - 1) * ITEMS_PER_PAGE;
  return filteredEndpoints.value.slice(start, start + ITEMS_PER_PAGE);
});
const pageSummary = computed(() => {
  if (!filteredEndpoints.value.length) {
    return "No endpoints in the current result set";
  }

  const start = (currentPage.value - 1) * ITEMS_PER_PAGE + 1;
  const end = Math.min(start + ITEMS_PER_PAGE - 1, filteredEndpoints.value.length);
  return `Showing ${start}-${end} of ${filteredEndpoints.value.length} endpoints`;
});

watch([search, statusFilter, methodFilter], () => {
  currentPage.value = 1;
});

watch(totalPages, (value) => {
  if (currentPage.value > value) {
    currentPage.value = value;
  }
});

watch(
  [() => props.activeEndpointId, filteredEndpoints],
  ([activeEndpointId, endpoints]) => {
    if (!activeEndpointId) {
      return;
    }

    const activeIndex = endpoints.findIndex((endpoint) => endpoint.id === activeEndpointId);
    if (activeIndex === -1) {
      return;
    }

    const pageForActiveEndpoint = Math.floor(activeIndex / ITEMS_PER_PAGE) + 1;
    if (pageForActiveEndpoint !== currentPage.value) {
      currentPage.value = pageForActiveEndpoint;
    }
  },
  { immediate: true },
);
</script>

<template>
  <v-card class="workspace-card catalog-card">
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

    <v-card-text class="catalog-card-body d-flex flex-column ga-4">
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

      <div class="d-flex align-center justify-space-between flex-wrap ga-3">
        <div class="text-caption text-medium-emphasis">{{ pageSummary }}</div>
        <v-chip label size="small" variant="outlined">
          Page {{ currentPage }} / {{ totalPages }}
        </v-chip>
      </div>

      <div class="catalog-scroll-region">
        <v-alert v-if="error" border="start" color="error" variant="tonal">
          {{ error }}
        </v-alert>

        <v-skeleton-loader
          v-else-if="loading && endpoints.length === 0"
          type="list-item-two-line, list-item-two-line, list-item-two-line, list-item-two-line"
        />

        <v-alert v-else-if="!filteredEndpoints.length" border="start" color="info" variant="tonal">
          No endpoints match the current filters.
        </v-alert>

        <v-list v-else class="catalog-list" lines="three" rounded="xl">
          <v-list-item
            v-for="endpoint in paginatedEndpoints"
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
                <v-btn
                  aria-label="Duplicate endpoint"
                  density="comfortable"
                  icon="mdi-content-copy"
                  size="small"
                  variant="text"
                  @click.stop="emit('duplicate', endpoint.id)"
                />
                <span class="text-caption text-medium-emphasis">{{ endpoint.category || "uncategorized" }}</span>
              </div>
            </template>
          </v-list-item>
        </v-list>
      </div>

      <v-pagination
        v-if="filteredEndpoints.length > ITEMS_PER_PAGE"
        v-model="currentPage"
        aria-label="Catalog pagination"
        class="align-self-center"
        :length="totalPages"
        rounded="circle"
        :total-visible="5"
      />
    </v-card-text>
  </v-card>
</template>

<style scoped>
.catalog-card {
  display: flex;
  flex-direction: column;
}

.catalog-card-body {
  flex: 1 1 auto;
  min-height: 0;
}

.catalog-scroll-region {
  min-height: 0;
}

@media (min-width: 1280px) {
  .catalog-card {
    height: clamp(32rem, 68vh, 46rem);
  }

  .catalog-scroll-region {
    flex: 1 1 auto;
    overflow-y: auto;
    padding-right: 0.35rem;
  }
}
</style>
