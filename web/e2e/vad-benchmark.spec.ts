/**
 * End-to-end tests for the Silero VAD benchmark panel on /voice.
 *
 * The panel is device-local, so it renders even with zero instances. We never
 * touch real WASM/WebGPU here: window.__NEXUS_VAD_MOCK__ is injected before
 * navigation (see web/src/lib/vadBenchmark.ts), which makes runVadBenchmark
 * return a deterministic, clearly-labelled "mock" result. This lets us drive
 * every UI state — pass, CPU fallback, error, model-unavailable — and both
 * WebGPU-present and WebGPU-absent device-coverage readouts, with no hardware.
 */
import { expect, test, type Route } from "@playwright/test";

async function stubNoInstances(page: import("@playwright/test").Page) {
  await page.route("**/api/instances", async (route: Route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: "[]",
    });
  });
}

// Inject a mocked benchmark result before any app code runs.
async function injectMock(
  page: import("@playwright/test").Page,
  mock: Record<string, unknown>,
) {
  await page.addInitScript((m) => {
    (window as unknown as { __NEXUS_VAD_MOCK__: unknown }).__NEXUS_VAD_MOCK__ = m;
  }, mock);
}

const TIMING = {
  runs: 30,
  warmupRuns: 3,
  latenciesMs: [],
  medianMs: 4.2,
  p95Ms: 6.1,
  minMs: 3.8,
  maxMs: 7.0,
  meanMs: 4.5,
};

test.describe("VAD benchmark panel", () => {
  test("renders and is visible even with no instances", async ({ page }) => {
    await stubNoInstances(page);
    await page.goto("/#/voice");
    await expect(page.getByTestId("vad-panel")).toBeVisible();
    await expect(page.getByTestId("button-run-vad")).toBeVisible();
    await expect(page.getByTestId("vad-ui-state")).toHaveText("idle");
  });

  test("pass state on WebGPU with real-time factor + adapter coverage", async ({ page }) => {
    await stubNoInstances(page);
    await injectMock(page, {
      status: "ok",
      selectedBackend: "webgpu",
      requestedBackend: "webgpu",
      fallbackUsed: false,
      runtimeInitMs: 120,
      modelCompileMs: 40,
      timing: TIMING,
      frameSize: 512,
      sampleRate: 16000,
      capabilities: {
        webgpuApiPresent: true,
        adapterAcquired: true,
        crossOriginIsolated: true,
        adapterInfo: { vendor: "acme", architecture: "rdna3" },
        userAgent: "e2e-agent",
        platform: "e2e",
      },
    });
    await page.goto("/#/voice");
    await page.getByTestId("button-run-vad").click();

    await expect(page.getByTestId("vad-result")).toBeVisible({ timeout: 10_000 });
    await expect(page.getByTestId("vad-status")).toHaveText("Pass");
    await expect(page.getByTestId("vad-source")).toHaveText("mocked (E2E)");
    await expect(page.getByTestId("vad-median")).toHaveText("4.2 ms");
    await expect(page.getByTestId("vad-p95")).toHaveText("6.1 ms");
    await expect(page.getByTestId("vad-backend")).toHaveText("webgpu → webgpu");
    await expect(page.getByTestId("vad-webgpu-present")).toHaveText("yes");
    await expect(page.getByTestId("vad-adapter-acquired")).toHaveText("yes");
    await expect(page.getByTestId("vad-adapter-info")).toContainText("acme");
    // frameBudget = 512/16000*1000 = 32ms; RTF = 4.2/32 = 0.131.
    await expect(page.getByTestId("vad-rtf")).toHaveText("0.131×");
    await expect(page.getByTestId("vad-frame-budget")).toHaveText("32.0 ms");
    // Fallback badge must NOT be present on a clean webgpu pass.
    await expect(page.getByTestId("vad-fallback-used")).toHaveCount(0);
  });

  test("CPU fallback state when WebGPU is absent", async ({ page }) => {
    await stubNoInstances(page);
    await injectMock(page, {
      status: "fallback",
      selectedBackend: "wasm",
      requestedBackend: "webgpu",
      fallbackUsed: true,
      runtimeInitMs: 200,
      modelCompileMs: 90,
      timing: TIMING,
      frameSize: 512,
      sampleRate: 16000,
      capabilities: {
        webgpuApiPresent: false,
        adapterAcquired: false,
        crossOriginIsolated: false,
        userAgent: "e2e-agent-nogpu",
        platform: "e2e",
      },
    });
    await page.goto("/#/voice");
    await page.getByTestId("button-run-vad").click();

    await expect(page.getByTestId("vad-status")).toHaveText("Pass (CPU fallback)");
    await expect(page.getByTestId("vad-fallback-used")).toBeVisible();
    await expect(page.getByTestId("vad-backend")).toHaveText("webgpu → wasm");
    await expect(page.getByTestId("vad-webgpu-present")).toHaveText("no");
    await expect(page.getByTestId("vad-adapter-acquired")).toHaveText("no");
  });

  test("error state surfaces the failure message", async ({ page }) => {
    await stubNoInstances(page);
    await injectMock(page, {
      status: "error",
      error: "LiteRtError: compile blew up",
      capabilities: {
        webgpuApiPresent: true,
        adapterAcquired: false,
        crossOriginIsolated: true,
        userAgent: "e2e-agent",
        platform: "e2e",
      },
    });
    await page.goto("/#/voice");
    await page.getByTestId("button-run-vad").click();

    await expect(page.getByTestId("vad-status")).toHaveText("Error");
    await expect(page.getByTestId("vad-error")).toContainText("compile blew up");
  });

  test("model-unavailable state is explicit and never fakes numbers", async ({ page }) => {
    await stubNoInstances(page);
    await injectMock(page, {
      status: "model-unavailable",
      error: "Silero VAD model not found. Run node scripts/fetch-vad-model.mjs.",
      capabilities: {
        webgpuApiPresent: true,
        adapterAcquired: true,
        crossOriginIsolated: true,
        userAgent: "e2e-agent",
        platform: "e2e",
      },
    });
    await page.goto("/#/voice");
    await page.getByTestId("button-run-vad").click();

    await expect(page.getByTestId("vad-status")).toHaveText("Model unavailable");
    await expect(page.getByTestId("vad-model-unavailable")).toContainText("not found");
    // No fabricated latency — median stays the em-dash placeholder.
    await expect(page.getByTestId("vad-median")).toHaveText("—");
  });

  test("reset returns the panel to idle", async ({ page }) => {
    await stubNoInstances(page);
    await injectMock(page, {
      status: "ok",
      selectedBackend: "wasm",
      requestedBackend: "wasm",
      timing: TIMING,
      capabilities: {
        webgpuApiPresent: false,
        adapterAcquired: false,
        crossOriginIsolated: false,
        userAgent: "e2e-agent",
        platform: "e2e",
      },
    });
    await page.goto("/#/voice");
    await page.getByTestId("button-run-vad").click();
    await expect(page.getByTestId("vad-result")).toBeVisible();

    await page.getByTestId("button-reset-vad").click();
    await expect(page.getByTestId("vad-ui-state")).toHaveText("idle");
    await expect(page.getByTestId("vad-result")).toHaveCount(0);
  });
});
