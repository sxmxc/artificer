import { afterEach, describe, expect, it, vi } from "vitest";

import { copyText } from "./clipboard";

describe("copyText", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("uses the async clipboard api when available", async () => {
    const writeText = vi.fn().mockResolvedValue(undefined);

    Object.defineProperty(navigator, "clipboard", {
      configurable: true,
      value: { writeText },
    });

    await expect(copyText("schema")).resolves.toBe(true);
    expect(writeText).toHaveBeenCalledWith("schema");
  });

  it("falls back to document.execCommand when navigator.clipboard is unavailable", async () => {
    Object.defineProperty(navigator, "clipboard", {
      configurable: true,
      value: undefined,
    });

    const execCommand = vi.fn().mockReturnValue(true);
    Object.defineProperty(document, "execCommand", {
      configurable: true,
      value: execCommand,
    });

    await expect(copyText("preview")).resolves.toBe(true);
    expect(execCommand).toHaveBeenCalledWith("copy");
  });
});
