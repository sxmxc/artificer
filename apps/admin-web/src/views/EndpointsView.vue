<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import {
  AdminApiError,
  createEndpoint,
  deleteEndpoint,
  listEndpoints,
  updateEndpoint,
} from "../api/admin";
import EndpointCatalog from "../components/EndpointCatalog.vue";
import EndpointSettingsForm from "../components/EndpointSettingsForm.vue";
import { useAuth } from "../composables/useAuth";
import type { Endpoint, EndpointDraft } from "../types/endpoints";
import { buildPayload, createEmptyDraft, describeAdminError, draftFromEndpoint } from "../utils/endpointDrafts";

const props = defineProps<{
  mode: "browse" | "create" | "edit";
}>();

const route = useRoute();
const router = useRouter();
const auth = useAuth();

const endpoints = ref<Endpoint[]>([]);
const draft = ref<EndpointDraft>(createEmptyDraft());
const fieldErrors = ref<Record<string, string>>({});
const isLoading = ref(false);
const isSaving = ref(false);
const catalogError = ref<string | null>(null);
const pageError = ref<string | null>(null);
const pageSuccess = ref<string | null>(null);

const endpointId = computed(() => {
  const rawId = route.params.endpointId;
  return typeof rawId === "string" ? Number(rawId) : null;
});

const selectedEndpoint = computed(() =>
  endpointId.value ? endpoints.value.find((endpoint) => endpoint.id === endpointId.value) ?? null : null,
);

const isInitialCatalogLoad = computed(() => isLoading.value && endpoints.value.length === 0);
const recordTransitionKey = computed(() =>
  props.mode === "create" ? "create" : selectedEndpoint.value ? `endpoint-${selectedEndpoint.value.id}` : "empty",
);

async function fetchEndpoints(): Promise<void> {
  if (!auth.credentials.value) {
    endpoints.value = [];
    return;
  }

  isLoading.value = true;
  catalogError.value = null;

  try {
    endpoints.value = await listEndpoints(auth.credentials.value);
  } catch (error) {
    if (error instanceof AdminApiError && error.status === 401) {
      auth.logout("Your admin session expired. Sign in again to keep editing.");
      void router.push({ name: "login" });
      return;
    }

    endpoints.value = [];
    catalogError.value = describeAdminError(error, "Unable to load endpoints.");
  } finally {
    isLoading.value = false;
  }
}

watch(
  () => auth.credentials.value,
  () => {
    void fetchEndpoints();
  },
  { immediate: true },
);

watch(
  [() => props.mode, selectedEndpoint],
  () => {
    fieldErrors.value = {};
    pageError.value = null;

    if (props.mode === "create") {
      draft.value = createEmptyDraft();
      return;
    }

    if (props.mode === "edit" && selectedEndpoint.value) {
      draft.value = draftFromEndpoint(selectedEndpoint.value);
    }
  },
  { immediate: true },
);

onMounted(() => {
  if (route.query.saved === "1") {
    pageSuccess.value = "Saved endpoint settings.";
  }
});

function applyDraftPatch(patch: Partial<EndpointDraft>): void {
  draft.value = {
    ...draft.value,
    ...patch,
  };
}

async function handleSave(): Promise<void> {
  if (!auth.credentials.value) {
    pageError.value = "Sign in again before saving endpoints.";
    return;
  }

  pageError.value = null;
  pageSuccess.value = null;

  const { errors, payload } = buildPayload(draft.value);
  fieldErrors.value = errors;

  if (!payload || Object.keys(errors).length > 0) {
    return;
  }

  isSaving.value = true;

  try {
    if (props.mode === "create") {
      const createdEndpoint = await createEndpoint(payload, auth.credentials.value);
      endpoints.value = [createdEndpoint, ...endpoints.value];
      void router.push({ name: "endpoints-edit", params: { endpointId: createdEndpoint.id }, query: { saved: "1" } });
      return;
    }

    if (!selectedEndpoint.value) {
      pageError.value = "Select an endpoint before saving.";
      return;
    }

    const updatedEndpoint = await updateEndpoint(selectedEndpoint.value.id, payload, auth.credentials.value);
    endpoints.value = endpoints.value.map((endpoint) => (endpoint.id === updatedEndpoint.id ? updatedEndpoint : endpoint));
    pageSuccess.value = `Saved ${updatedEndpoint.name}.`;
  } catch (error) {
    if (error instanceof AdminApiError && error.status === 401) {
      auth.logout("Your admin session expired. Sign in again before saving more changes.");
      void router.push({ name: "login" });
      return;
    }

    pageError.value = describeAdminError(error, "Unable to save the endpoint.");
  } finally {
    isSaving.value = false;
  }
}

async function handleDelete(): Promise<void> {
  if (!selectedEndpoint.value || !auth.credentials.value) {
    return;
  }

  const shouldDelete = window.confirm(`Delete "${selectedEndpoint.value.name}" from the catalog?`);
  if (!shouldDelete) {
    return;
  }

  isSaving.value = true;
  pageError.value = null;
  pageSuccess.value = null;

  try {
    await deleteEndpoint(selectedEndpoint.value.id, auth.credentials.value);
    endpoints.value = endpoints.value.filter((endpoint) => endpoint.id !== selectedEndpoint.value?.id);
    void router.push({ name: "endpoints-browse" });
  } catch (error) {
    if (error instanceof AdminApiError && error.status === 401) {
      auth.logout("Your admin session expired. Sign in again before deleting endpoints.");
      void router.push({ name: "login" });
      return;
    }

    pageError.value = describeAdminError(error, "Unable to delete the endpoint.");
  } finally {
    isSaving.value = false;
  }
}

function openSchemaStudio(): void {
  if (!selectedEndpoint.value) {
    return;
  }

  void router.push({ name: "schema-editor", params: { endpointId: selectedEndpoint.value.id } });
}

function openPreview(): void {
  if (!selectedEndpoint.value) {
    return;
  }

  void router.push({ name: "endpoint-preview", params: { endpointId: selectedEndpoint.value.id } });
}

const activeTitle = computed(() => {
  if (props.mode === "create") {
    return "Start a new route";
  }

  if (!selectedEndpoint.value) {
    return "Choose a route";
  }

  return selectedEndpoint.value.name;
});
</script>

<template>
  <v-row class="workspace-grid">
    <v-col cols="12" xl="3" lg="4">
      <div class="d-flex flex-column ga-4">
        <v-card class="workspace-card">
          <v-card-item>
            <template #prepend>
              <v-avatar color="accent" variant="tonal">
                <v-icon icon="mdi-waveform" />
              </v-avatar>
            </template>

            <v-card-title>Workspace ready</v-card-title>
            <v-card-subtitle>The backend database is still the source of truth for runtime and OpenAPI.</v-card-subtitle>
          </v-card-item>
          <v-card-text class="text-body-2 text-medium-emphasis">
            Signed in as <strong>{{ auth.username.value }}</strong>. Use this surface for endpoint settings, then jump
            into the dedicated schema editor when you need full builder focus.
          </v-card-text>
        </v-card>

        <EndpointCatalog
          :active-endpoint-id="selectedEndpoint?.id"
          :endpoints="endpoints"
          :error="catalogError"
          :loading="isLoading"
          @create="router.push({ name: 'endpoints-create' })"
          @refresh="fetchEndpoints"
          @select="(id) => router.push({ name: 'endpoints-edit', params: { endpointId: id } })"
        />
      </div>
    </v-col>

    <v-col cols="12" xl="9" lg="8">
      <div class="d-flex flex-column ga-4">
        <v-alert v-if="pageSuccess" border="start" color="success" variant="tonal">
          {{ pageSuccess }}
        </v-alert>

        <v-alert v-if="pageError" border="start" color="error" variant="tonal">
          {{ pageError }}
        </v-alert>

        <v-skeleton-loader
          v-if="isInitialCatalogLoad"
          class="workspace-card"
          type="heading, paragraph, paragraph, paragraph, table-heading, table-row-divider, table-row-divider"
        />

        <v-card v-else-if="props.mode === 'browse'" class="workspace-card browse-card">
          <v-card-text class="pa-8">
            <div class="text-overline text-secondary">Endpoint studio</div>
            <div class="text-h3 font-weight-bold mt-2">Pick a route from the catalog or start a new one.</div>
            <div class="text-body-1 text-medium-emphasis mt-4">
              Settings stay here. Schema design now gets its own full-page workspace so the builder is no longer
              competing with general form controls.
            </div>
            <div class="d-flex flex-wrap ga-3 mt-6">
              <v-btn color="primary" prepend-icon="mdi-plus" @click="router.push({ name: 'endpoints-create' })">
                Create endpoint
              </v-btn>
              <v-btn prepend-icon="mdi-refresh" variant="text" @click="fetchEndpoints">
                Refresh catalog
              </v-btn>
            </div>
          </v-card-text>
        </v-card>

        <v-card
          v-else-if="props.mode === 'edit' && !selectedEndpoint"
          class="workspace-card browse-card"
        >
          <v-card-text class="pa-8">
            <div class="text-overline text-error">Missing endpoint</div>
            <div class="text-h4 font-weight-bold mt-2">That route is no longer in the catalog.</div>
            <div class="text-body-1 text-medium-emphasis mt-4">
              Refresh the list, pick another record, or create a fresh endpoint shell.
            </div>
          </v-card-text>
        </v-card>

        <template v-else>
          <v-slide-y-transition mode="out-in">
            <div :key="recordTransitionKey" class="d-flex flex-column ga-4">
              <v-card class="workspace-card record-hero">
                <v-card-text class="d-flex flex-column flex-md-row justify-space-between ga-4">
                  <div>
                    <div class="text-overline text-secondary">
                      {{ props.mode === "create" ? "New route shell" : "Active record" }}
                    </div>
                    <div class="text-h4 font-weight-bold mt-2">{{ activeTitle }}</div>
                    <div class="text-body-1 text-medium-emphasis mt-3">
                      {{
                        props.mode === "create"
                          ? "Start with identity and behavior. Once the endpoint exists, the schema studio opens on its own page."
                          : selectedEndpoint?.path
                      }}
                    </div>
                  </div>

                  <div class="d-flex flex-wrap align-start justify-end ga-2">
                    <v-chip v-if="selectedEndpoint" color="primary" label variant="tonal">
                      {{ selectedEndpoint.method }}
                    </v-chip>
                    <v-chip v-if="selectedEndpoint" :color="selectedEndpoint.enabled ? 'accent' : 'surface-variant'" label variant="tonal">
                      {{ selectedEndpoint.enabled ? "Live" : "Disabled" }}
                    </v-chip>
                    <v-chip v-if="selectedEndpoint?.category" color="secondary" label variant="tonal">
                      {{ selectedEndpoint.category }}
                    </v-chip>
                  </div>
                </v-card-text>
              </v-card>

              <EndpointSettingsForm
                :created-at="selectedEndpoint?.created_at"
                :draft="draft"
                :endpoint-id="selectedEndpoint?.id"
                :errors="fieldErrors"
                :is-creating="props.mode === 'create'"
                :is-saving="isSaving"
                :updated-at="selectedEndpoint?.updated_at"
                @change="applyDraftPatch"
                @delete="handleDelete"
                @open-schema="openSchemaStudio"
                @preview="openPreview"
                @submit="handleSave"
              />
            </div>
          </v-slide-y-transition>
        </template>
      </div>
    </v-col>
  </v-row>
</template>
