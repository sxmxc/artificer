module.exports = {
  root: true,
  env: {
    browser: true,
    es2021: true,
    node: true,
  },
  extends: ["eslint:recommended", "plugin:vue/vue3-recommended", "plugin:@typescript-eslint/recommended"],
  parser: "vue-eslint-parser",
  parserOptions: {
    parser: "@typescript-eslint/parser",
    ecmaVersion: "latest",
    extraFileExtensions: [".vue"],
    sourceType: "module",
  },
  plugins: ["vue", "@typescript-eslint"],
  globals: {
    beforeEach: "readonly",
    describe: "readonly",
    expect: "readonly",
    it: "readonly",
    vi: "readonly",
  },
  rules: {
    "no-unused-vars": "off",
    "@typescript-eslint/no-unused-vars": [
      "error",
      {
        argsIgnorePattern: "^_",
      },
    ],
    "vue/max-attributes-per-line": "off",
    "vue/multi-word-component-names": "off",
    "vue/singleline-html-element-content-newline": "off",
  },
};
