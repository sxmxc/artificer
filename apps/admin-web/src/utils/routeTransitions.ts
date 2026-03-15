interface TransitionRouteLike {
  meta: Record<string, unknown>;
  name?: string | symbol | null;
  path: string;
}

export function getPageTransitionKey(route: TransitionRouteLike): string {
  const transitionShell = route.meta.transitionShell;
  if (typeof transitionShell === "string" && transitionShell.trim()) {
    return transitionShell;
  }

  return typeof route.name === "string" ? route.name : route.path;
}
