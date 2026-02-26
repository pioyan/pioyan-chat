/**
 * Tests for JWT auth utility (lib/auth.ts)
 * Red phase: testing before implementation
 */
import { describe, it, expect, beforeEach } from "vitest";

// Storage mock
const localStorageMock = (() => {
  let store: Record<string, string> = {};
  return {
    getItem: (key: string) => store[key] ?? null,
    setItem: (key: string, value: string) => {
      store[key] = value;
    },
    removeItem: (key: string) => {
      delete store[key];
    },
    clear: () => {
      store = {};
    },
  };
})();

Object.defineProperty(globalThis, "localStorage", { value: localStorageMock });

describe("auth utils", () => {
  beforeEach(() => {
    localStorageMock.clear();
  });

  it("saves and retrieves token", async () => {
    const { saveToken, getToken } = await import("@/lib/auth");
    saveToken("test-token-123");
    expect(getToken()).toBe("test-token-123");
  });

  it("removes token", async () => {
    const { saveToken, getToken, removeToken } = await import("@/lib/auth");
    saveToken("test-token");
    removeToken();
    expect(getToken()).toBeNull();
  });

  it("returns null when no token stored", async () => {
    const { getToken } = await import("@/lib/auth");
    expect(getToken()).toBeNull();
  });

  it("isAuthenticated returns true when token exists", async () => {
    const { saveToken, isAuthenticated } = await import("@/lib/auth");
    saveToken("some-token");
    expect(isAuthenticated()).toBe(true);
  });

  it("isAuthenticated returns false when no token", async () => {
    const { isAuthenticated } = await import("@/lib/auth");
    expect(isAuthenticated()).toBe(false);
  });
});
