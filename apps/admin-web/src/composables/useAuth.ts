import { computed, reactive } from "vue";
import {
  AdminApiError,
  clearStoredCredentials,
  hasCredentials,
  listEndpoints,
  loadStoredCredentials,
  persistCredentials,
} from "../api/admin";
import type { AdminCredentials } from "../types/endpoints";

type AuthStatus = "restoring" | "logged_out" | "authenticating" | "authenticated";

interface LoginOptions {
  rememberMe: boolean;
}

interface LoginResult {
  ok: boolean;
  error?: string;
}

function normalizeAuthError(error: unknown, fallbackMessage: string): string {
  if (error instanceof AdminApiError && error.status === 401) {
    return "Those credentials were rejected. Check the admin username and password from the backend environment.";
  }

  return error instanceof Error ? error.message : fallbackMessage;
}

const state = reactive<{
  credentials: AdminCredentials | null;
  sessionMessage: string | null;
  status: AuthStatus;
}>({
  credentials: null,
  sessionMessage: null,
  status: "restoring",
});

let bootPromise: Promise<void> | null = null;

export const authUsername = computed(() => state.credentials?.username ?? null);
export const isAuthenticated = computed(() => state.status === "authenticated" && hasCredentials(state.credentials));

export async function ensureAuthBooted(): Promise<void> {
  if (bootPromise) {
    return bootPromise;
  }

  bootPromise = (async () => {
    const bootCredentials = loadStoredCredentials();

    if (!hasCredentials(bootCredentials)) {
      state.credentials = null;
      state.status = "logged_out";
      return;
    }

    state.status = "restoring";

    try {
      await listEndpoints(bootCredentials);
      state.credentials = bootCredentials;
      state.status = "authenticated";
    } catch (error) {
      clearStoredCredentials();
      state.credentials = null;
      state.status = "logged_out";
      state.sessionMessage = normalizeAuthError(error, "Your saved admin session could not be restored.");
    }
  })();

  try {
    await bootPromise;
  } finally {
    bootPromise = null;
  }
}

export async function login(nextCredentials: AdminCredentials, options: LoginOptions): Promise<LoginResult> {
  if (!hasCredentials(nextCredentials)) {
    return { ok: false, error: "Enter both username and password." };
  }

  state.status = "authenticating";
  state.sessionMessage = null;

  try {
    await listEndpoints(nextCredentials);
    state.credentials = nextCredentials;
    persistCredentials(nextCredentials, options.rememberMe);
    state.status = "authenticated";
    return { ok: true };
  } catch (error) {
    clearStoredCredentials();
    state.credentials = null;
    state.status = "logged_out";
    return { ok: false, error: normalizeAuthError(error, "We could not sign you in.") };
  }
}

export function logout(message?: string): void {
  clearStoredCredentials();
  state.credentials = null;
  state.status = "logged_out";
  state.sessionMessage = message ?? null;
}

export function clearSessionMessage(): void {
  state.sessionMessage = null;
}

export function useAuth() {
  return {
    state,
    status: computed(() => state.status),
    credentials: computed(() => state.credentials),
    sessionMessage: computed(() => state.sessionMessage),
    username: authUsername,
    isAuthenticated,
    clearSessionMessage,
    login,
    logout,
    ensureBooted: ensureAuthBooted,
  };
}
