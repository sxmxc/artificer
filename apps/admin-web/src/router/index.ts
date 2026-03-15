import { createRouter, createWebHistory } from "vue-router";
import EndpointsView from "../views/EndpointsView.vue";
import EndpointPreviewView from "../views/EndpointPreviewView.vue";
import LoginView from "../views/LoginView.vue";
import SchemaEditorView from "../views/SchemaEditorView.vue";
import { ensureAuthBooted, isAuthenticated } from "../composables/useAuth";

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      redirect: "/endpoints",
    },
    {
      path: "/login",
      name: "login",
      component: LoginView,
      meta: {
        title: "Sign in",
      },
    },
    {
      path: "/endpoints",
      name: "endpoints-browse",
      component: EndpointsView,
      props: {
        mode: "browse",
      },
      meta: {
        requiresAuth: true,
        title: "Endpoint catalog",
      },
    },
    {
      path: "/endpoints/new",
      name: "endpoints-create",
      component: EndpointsView,
      props: {
        mode: "create",
      },
      meta: {
        requiresAuth: true,
        title: "Create endpoint",
      },
    },
    {
      path: "/endpoints/:endpointId",
      name: "endpoints-edit",
      component: EndpointsView,
      props: {
        mode: "edit",
      },
      meta: {
        requiresAuth: true,
        title: "Endpoint settings",
      },
    },
    {
      path: "/endpoints/:endpointId/schema",
      name: "schema-editor",
      component: SchemaEditorView,
      meta: {
        requiresAuth: true,
        title: "Schema studio",
      },
    },
    {
      path: "/endpoints/:endpointId/preview",
      name: "endpoint-preview",
      component: EndpointPreviewView,
      meta: {
        requiresAuth: true,
        title: "Route preview",
      },
    },
  ],
});

router.beforeEach(async (to) => {
  await ensureAuthBooted();

  if (to.meta.requiresAuth && !isAuthenticated.value) {
    return {
      name: "login",
      query: {
        redirect: to.fullPath,
      },
    };
  }

  if (to.name === "login" && isAuthenticated.value) {
    return {
      name: "endpoints-browse",
    };
  }

  return true;
});

router.afterEach((to) => {
  if (typeof document !== "undefined") {
    const pageTitle = typeof to.meta.title === "string" ? to.meta.title : "Mockingbird Studio";
    document.title = `Mockingbird Admin | ${pageTitle}`;
  }
});
