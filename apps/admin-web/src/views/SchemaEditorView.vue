<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { AdminApiError, getEndpoint, updateEndpoint } from "../api/admin";
import SchemaEditorWorkspace from "../components/SchemaEditorWorkspace.vue";
import { useAuth } from "../composables/useAuth";
import { schemaToTree, validateTree } from "../schemaBuilder";
import type { BuilderScope } from "../schemaBuilder";
import type { Endpoint, JsonObject } from "../types/endpoints";
import { describeAdminError, endpointToPayload } from "../utils/endpointDrafts";
import { extractPathParameters } from "../utils/pathParameters";

const route = useRoute();
const router = useRouter();
const auth = useAuth();

const endpoint = ref<Endpoint | null>(null);
const requestSchema = ref<JsonObject>({});
const responseSchema = ref<JsonObject>({});
const seedKey = ref("");
const tab = ref<BuilderScope>(route.query.tab === "request" ? "request" : "response");
const isLoading = ref(true);
const isSaving = ref(false);
const loadError = ref<string | null>(null);
const pageError = ref<string | null>(null);
const pageSuccess = ref<string | null>(null);

const endpointId = computed(() => {
  const rawId = route.params.endpointId;
  return typeof rawId === "string" ? Number(rawId) : null;
});

const isDirty = computed(() => {
  if (!endpoint.value) {
    return false;
  }

  return (
    JSON.stringify(requestSchema.value) !== JSON.stringify(endpoint.value.request_schema ?? {}) ||
    JSON.stringify(responseSchema.value) !== JSON.stringify(endpoint.value.response_schema ?? {}) ||
    seedKey.value !== (endpoint.value.seed_key ?? "")
  );
});
const pathParameters = computed(() => endpoint.value ? extractPathParameters(endpoint.value.path) : []);

watch(
  () => route.query.tab,
  (value) => {
    tab.value = value === "request" ? "request" : "response";
  },
  { immediate: true },
);

watch(tab, (value) => {
  if (route.query.tab === value) {
    return;
  }

  void router.replace({
    query: {
      ...route.query,
      tab: value,
    },
  });
});

watch(
  endpointId,
  () => {
    void loadEndpoint();
  },
  { immediate: true },
);

async function loadEndpoint(): Promise<void> {
  if (!endpointId.value || !auth.session.value) {
    isLoading.value = false;
    loadError.value = "Missing endpoint id.";
    return;
  }

  isLoading.value = true;
  loadError.value = null;
  pageError.value = null;

  try {
    const loadedEndpoint = await getEndpoint(endpointId.value, auth.session.value);
    endpoint.value = loadedEndpoint;
    requestSchema.value = loadedEndpoint.request_schema ?? {};
    responseSchema.value = loadedEndpoint.response_schema ?? {};
    seedKey.value = loadedEndpoint.seed_key ?? "";
  } catch (error) {
    if (error instanceof AdminApiError && error.status === 401) {
      void auth.logout("Your admin session expired. Sign in again before editing schemas.");
      void router.push({ name: "login" });
      return;
    }

    loadError.value = describeAdminError(error, "Unable to load the endpoint schema.");
  } finally {
    isLoading.value = false;
  }
}

function resetToSavedState(): void {
  if (!endpoint.value) {
    return;
  }

  requestSchema.value = endpoint.value.request_schema ?? {};
  responseSchema.value = endpoint.value.response_schema ?? {};
  seedKey.value = endpoint.value.seed_key ?? "";
  pageError.value = null;
  pageSuccess.value = null;
}

async function saveSchemas(): Promise<void> {
  if (!endpoint.value || !auth.session.value) {
    return;
  }

  pageError.value = null;
  pageSuccess.value = null;

  const requestError = validateTree(schemaToTree(requestSchema.value, "request"));
  if (requestError) {
    pageError.value = requestError;
    tab.value = "request";
    return;
  }

  const responseError = validateTree(schemaToTree(responseSchema.value, "response"));
  if (responseError) {
    pageError.value = responseError;
    tab.value = "response";
    return;
  }

  isSaving.value = true;

  try {
    const updatedEndpoint = await updateEndpoint(
      endpoint.value.id,
      endpointToPayload(endpoint.value, {
        request_schema: requestSchema.value,
        response_schema: responseSchema.value,
        seed_key: seedKey.value.trim() ? seedKey.value.trim() : null,
      }),
      auth.session.value,
    );

    endpoint.value = updatedEndpoint;
    requestSchema.value = updatedEndpoint.request_schema ?? {};
    responseSchema.value = updatedEndpoint.response_schema ?? {};
    seedKey.value = updatedEndpoint.seed_key ?? "";
    pageSuccess.value = `Saved schema changes for ${updatedEndpoint.name}.`;
  } catch (error) {
    if (error instanceof AdminApiError && error.status === 401) {
      void auth.logout("Your admin session expired. Sign in again before saving schema changes.");
      void router.push({ name: "login" });
      return;
    }

    pageError.value = describeAdminError(error, "Unable to save schema changes.");
  } finally {
    isSaving.value = false;
  }
}
</script>

<template>
  <div class="schema-editor-page d-flex flex-column ga-4">
    <div class="d-flex flex-column flex-lg-row justify-space-between ga-4">
      <div>
        <div class="text-h3 font-weight-bold">
          {{ endpoint?.name || "Loading schema" }}
        </div>
        <div v-if="endpoint?.summary" class="text-body-1 text-medium-emphasis mt-3">
          {{ endpoint.summary }}
        </div>
      </div>

      <div class="d-flex flex-wrap align-start justify-end ga-2">
        <v-btn
          prepend-icon="mdi-arrow-left"
          variant="text"
          @click="router.push({ name: endpoint ? 'endpoints-edit' : 'endpoints-browse', params: endpoint ? { endpointId: endpoint.id } : undefined })"
        >
          Back to settings
        </v-btn>
        <v-btn
          v-if="endpoint"
          prepend-icon="mdi-flask-outline"
          variant="text"
          @click="router.push({ name: 'endpoint-preview', params: { endpointId: endpoint.id } })"
        >
          Test route
        </v-btn>
        <v-chip v-if="isDirty" color="warning" label variant="tonal">
          Unsaved changes
        </v-chip>
        <v-btn v-if="isDirty" prepend-icon="mdi-restore" variant="text" @click="resetToSavedState">
          Reset
        </v-btn>
        <v-btn color="primary" :loading="isSaving" prepend-icon="mdi-content-save-outline" @click="saveSchemas">
          Save schema
        </v-btn>
      </div>
    </div>

    <v-alert v-if="pageSuccess" border="start" color="success" variant="tonal">
      {{ pageSuccess }}
    </v-alert>

    <v-alert v-if="pageError" border="start" color="error" variant="tonal">
      {{ pageError }}
    </v-alert>

    <v-skeleton-loader
      v-if="isLoading"
      class="workspace-card"
      type="heading, paragraph, paragraph, table-heading, table-row-divider, table-row-divider, paragraph"
    />

    <v-card v-else-if="!endpoint" class="workspace-card">
      <v-card-text class="pa-8">
        <div class="text-overline text-error">Schema unavailable</div>
        <div class="text-h4 font-weight-bold mt-2">We could not load that endpoint.</div>
        <div class="text-body-1 text-medium-emphasis mt-4">
          {{ loadError ?? "The endpoint is missing or your session changed while loading the schema editor." }}
        </div>
      </v-card-text>
    </v-card>

    <template v-else>
      <v-card class="workspace-card">
        <v-card-text class="d-flex flex-column flex-xl-row justify-space-between ga-4">
          <div class="d-flex flex-wrap ga-2">
            <v-chip color="primary" label size="small" variant="tonal">{{ endpoint.method }}</v-chip>
            <v-chip :color="endpoint.enabled ? 'accent' : 'error'" label size="small" variant="tonal">
              {{ endpoint.enabled ? "Live" : "Disabled" }}
            </v-chip>
            <v-chip v-if="endpoint.category" color="secondary" label size="small" variant="tonal">
              {{ endpoint.category }}
            </v-chip>
            <v-chip label size="small" variant="outlined">{{ endpoint.path }}</v-chip>
          </div>

          <div class="schema-tab-shell">
            <v-tabs
              v-model="tab"
              align-tabs="start"
              color="secondary"
              density="compact"
            >
              <v-tab value="request">Request schema</v-tab>
              <v-tab value="response">Response schema</v-tab>
            </v-tabs>
          </div>
        </v-card-text>
      </v-card>

      <div class="schema-workspace-shell">
        <SchemaEditorWorkspace
          v-if="tab === 'request'"
          :schema="requestSchema"
          scope="request"
          @update:schema="requestSchema = $event"
        />

        <SchemaEditorWorkspace
          v-else
          v-model:seed-key="seedKey"
          :path-parameters="pathParameters"
          :schema="responseSchema"
          scope="response"
          @update:schema="responseSchema = $event"
        />
      </div>
    </template>
  </div>
</template>

<style scoped>
.schema-editor-page {
  min-height: 100%;
}

.schema-workspace-shell {
  min-height: 0;
}
</style>
