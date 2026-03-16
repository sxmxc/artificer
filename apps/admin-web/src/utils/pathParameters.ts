export function extractPathParameters(path: string): string[] {
  const matches = path.matchAll(/\{([^}]+)\}/g);
  const seen = new Set<string>();
  const parameters: string[] = [];

  for (const match of matches) {
    const name = match[1]?.trim();
    if (!name || seen.has(name)) {
      continue;
    }

    seen.add(name);
    parameters.push(name);
  }

  return parameters;
}

export function buildDefaultPathParameters(path: string): Record<string, string> {
  return extractPathParameters(path).reduce<Record<string, string>>((accumulator, key) => {
    accumulator[key] = `sample-${key}`;
    return accumulator;
  }, {});
}

export function resolvePathParameters(path: string, parameters: Record<string, string>): string {
  return path.replace(/\{([^}]+)\}/g, (_, key: string) => encodeURIComponent(parameters[key] || `sample-${key}`));
}
