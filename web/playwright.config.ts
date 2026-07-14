import { defineConfig, devices } from "@playwright/test";

/**
 * Playwright config for the voice cockpit smoke tests.
 *
 * The Vite dev server is spawned automatically \-\ tests hit it at
 * http://127.0.0.1:5173. Each spec spins up its own mock WebSocket server
 * (see support/mockWsServer.ts) so we never rely on a real Kokoro/Platform.
 */
export default defineConfig({
  testDir: "./e2e",
  testMatch: /.*\.spec\.ts/,
  fullyParallel: false,
  workers: 1,
  reporter: [["list"]],
  timeout: 30_000,
  use: {
    baseURL: "http://127.0.0.1:5173",
    trace: "off",
    // Chromium's autoplay policy would otherwise refuse AudioContext.resume()
    // outside a user gesture \-\ we click a button before playing so it's fine.
    launchOptions: {
      args: ["--autoplay-policy=no-user-gesture-required"],
    },
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
    {
      name: "mobile",
      use: { ...devices["Pixel 5"] },
    },
  ],
  webServer: {
    command: "npm run dev -- --host 127.0.0.1 --port 5173",
    url: "http://127.0.0.1:5173",
    reuseExistingServer: !process.env.CI,
    timeout: 60_000,
  },
});
