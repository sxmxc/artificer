import "@mdi/font/css/materialdesignicons.css";
import "vuetify/styles";
import { createVuetify } from "vuetify";
import * as directives from "vuetify/directives";
import * as components from "vuetify/components";
import { aliases, mdi } from "vuetify/iconsets/mdi";

const studioLight = {
  dark: false,
  colors: {
    background: "#f6f2ea",
    surface: "#fffdfa",
    "surface-variant": "#ebe3d3",
    primary: "#245a7d",
    secondary: "#c67b42",
    accent: "#2b8c7f",
    info: "#2f86b0",
    success: "#2f8b57",
    warning: "#cb8d26",
    error: "#bf4f44",
  },
};

const studioDark = {
  dark: true,
  colors: {
    background: "#10141c",
    surface: "#171d28",
    "surface-variant": "#202938",
    primary: "#82cafc",
    secondary: "#f1aa6b",
    accent: "#7fe0c9",
    info: "#88d7ff",
    success: "#7dd8a2",
    warning: "#f4c66a",
    error: "#ff9d91",
  },
};

export const vuetify = createVuetify({
  components,
  directives,
  icons: {
    defaultSet: "mdi",
    aliases,
    sets: {
      mdi,
    },
  },
  theme: {
    defaultTheme: "studioLight",
    themes: {
      studioLight,
      studioDark,
    },
  },
  defaults: {
    VCard: {
      elevation: 0,
      rounded: "xl",
    },
    VBtn: {
      rounded: "pill",
    },
    VTextField: {
      density: "comfortable",
      variant: "outlined",
    },
    VTextarea: {
      density: "comfortable",
      variant: "outlined",
    },
    VSelect: {
      density: "comfortable",
      variant: "outlined",
    },
  },
});
