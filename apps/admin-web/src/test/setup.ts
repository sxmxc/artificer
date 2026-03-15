import "@testing-library/jest-dom/vitest";

class ResizeObserverMock {
  observe() {}

  unobserve() {}

  disconnect() {}
}

vi.stubGlobal("ResizeObserver", ResizeObserverMock);

const originalConsoleError = console.error;

vi.spyOn(console, "error").mockImplementation((...args: unknown[]) => {
  if (args.some((value) => typeof value === "string" && value.includes("Could not parse CSS stylesheet"))) {
    return;
  }

  originalConsoleError(...args);
});
