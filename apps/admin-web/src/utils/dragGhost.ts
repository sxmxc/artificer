export type DragGhostTone = "mode" | "node" | "value";

export function setPillDragImage(
  event: DragEvent | undefined,
  options: {
    eyebrow?: string;
    label: string;
    tone: DragGhostTone;
  },
): void {
  if (!event?.dataTransfer || typeof document === "undefined") {
    return;
  }

  const ghost = document.createElement("div");
  ghost.className = `schema-drag-ghost schema-drag-ghost-${options.tone}`;

  if (options.eyebrow) {
    const eyebrow = document.createElement("span");
    eyebrow.className = "schema-drag-ghost-eyebrow";
    eyebrow.textContent = options.eyebrow;
    ghost.append(eyebrow);
  }

  const label = document.createElement("span");
  label.className = "schema-drag-ghost-label";
  label.textContent = options.label;
  ghost.append(label);

  document.body.append(ghost);
  event.dataTransfer.setDragImage(ghost, 18, Math.max(18, Math.round(ghost.offsetHeight / 2)));

  window.requestAnimationFrame(() => {
    window.setTimeout(() => {
      ghost.remove();
    }, 0);
  });
}
