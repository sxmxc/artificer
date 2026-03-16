function escapeHtml(value: string): string {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

export function highlightJson(value: unknown): string {
  const json = typeof value === "string" ? value : JSON.stringify(value ?? null, null, 2);
  const safeJson = escapeHtml(json);

  return safeJson.replace(
    /("(\\u[\da-fA-F]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?\b|\btrue\b|\bfalse\b|\bnull\b)/g,
    (token) => {
      let tokenClass = "json-token--number";

      if (token.startsWith("\"")) {
        tokenClass = token.endsWith(":") ? "json-token--key" : "json-token--string";
      } else if (token === "true" || token === "false") {
        tokenClass = "json-token--boolean";
      } else if (token === "null") {
        tokenClass = "json-token--null";
      }

      return `<span class="json-token ${tokenClass}">${token}</span>`;
    },
  );
}
