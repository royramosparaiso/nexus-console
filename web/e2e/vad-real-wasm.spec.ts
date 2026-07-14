/**
 * Real-model browser smoke test: no mock injected, so this drives the actual
 * LiteRT.js WASM runtime against the committed silero_vad.tflite. It proves the
 * model loads + compiles on the WASM (CPU) backend in a real browser and
 * produces genuine, non-fabricated inference numbers.
 *
 * WebGPU is not asserted here — headless Chromium in CI exposes no adapter, so
 * we request the WASM backend explicitly (deterministic, no GPU needed). The
 * ~9 MB WASM download + compile is slow, hence the extended timeout.
 */
import { expect, test, type Route } from "@playwright/test";

test.describe("VAD real WASM inference", () => {
  test.slow(); // triple the timeout: real WASM load + compile.

  test("loads + compiles the committed model and reports real latency", async ({ page }) => {
    await page.route("**/api/instances", async (route: Route) => {
      await route.fulfill({ status: 200, contentType: "application/json", body: "[]" });
    });

    await page.goto("/#/voice");
    await expect(page.getByTestId("vad-panel")).toBeVisible();

    // Force the WASM/CPU backend so the test is deterministic without a GPU.
    await page.getByTestId("select-vad-backend").selectOption("wasm");
    await page.getByTestId("button-run-vad").click();

    // Real load+compile can take a while; wait generously for the result.
    await expect(page.getByTestId("vad-result")).toBeVisible({ timeout: 90_000 });

    // Real hardware execution, not a mock.
    await expect(page.getByTestId("vad-source")).toHaveText("hardware");
    await expect(page.getByTestId("vad-status")).toHaveText("Pass");
    await expect(page.getByTestId("vad-backend")).toHaveText("wasm → wasm");

    // Genuine, non-placeholder latency (format "<n> ms", never the em-dash).
    const median = await page.getByTestId("vad-median").textContent();
    expect(median).toMatch(/^\d+(\.\d+)?\s*ms$/);

    // A real speech probability in [0, 1] was produced by the model.
    const prob = await page.getByTestId("vad-max-prob").textContent();
    expect(prob).toMatch(/^\d\.\d{3}$/);
    expect(Number(prob)).toBeGreaterThanOrEqual(0);
    expect(Number(prob)).toBeLessThanOrEqual(1);

    // Provenance is surfaced.
    await expect(page.getByTestId("vad-model-sha")).toContainText(
      "99e2ca568d436f781a98f669b71bb83db248452c367144f51704a8feae4996a7",
    );
  });
});
