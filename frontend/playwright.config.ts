import { defineConfig, devices } from "@playwright/test";

/**
 * Playwright 設定ファイル
 * DM 機能などの E2E 検証用
 * @see https://playwright.dev/docs/test-configuration
 */
export default defineConfig({
  testDir: "./src/e2e",
  testMatch: "**/*.spec.ts",
  /* テストが失敗した場合の再試行回数 */
  retries: 1,
  /* 並列実行数 */
  workers: 1,
  /* レポーター設定 */
  reporter: [["html", { open: "never" }], ["list"]],

  use: {
    /* ベース URL — pnpm dev が localhost:3000 で起動している前提 */
    baseURL: "http://localhost:3000",
    /* フルページスクリーンショットをエラー時に撮影 */
    screenshot: "only-on-failure",
    /* ヘッドレスで動作 */
    headless: true,
    /* ナビゲーション待機タイムアウト */
    navigationTimeout: 15000,
    actionTimeout: 8000,
  },

  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
});
