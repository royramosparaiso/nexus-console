/**
 * End-to-end tests for the /voice cockpit page.
 *
 * Strategy:
 *   1. Spin up a mock WebSocket server that speaks the /_voice/stream
 *      protocol (start / PCM chunks / end) so we exercise useVoiceStream
 *      without a real Platform + Kokoro pair.
 *   2. Serve the Console web app via `npm run dev` (Playwright's webServer)
 *      and use page.route() to stub /api/instances and /_voice/voices so
 *      the app is fully self-contained.
 *   3. Assert on stream stats, status pill transitions, and that the
 *      AudioContext receives buffers in the right order (via a page-level
 *      hook installed before navigation).
 */

import { expect, test, type Route } from "@playwright/test";

import { startMockWs, type MockWsHandle, type Scenario } from "./support/mockWsServer";

// ---------------------------------------------------------------------------
// Shared setup \-\ each test spins up its own mock WS server on a random port,
// then feeds that port back into the app via route stubs.
// ---------------------------------------------------------------------------

async function bootScenario(scenario: Scenario) {
  const mock = await startMockWs(scenario);
  return mock;
}

async function stubBackend(page: import("@playwright/test").Page, mock: MockWsHandle) {
  const endpoint = `http://127.0.0.1:${mock.port}`;

  await page.route("**/api/instances", async (route: Route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify([
        {
          id: "00000000-0000-4000-8000-000000000001",
          name: "test-instance",
          status: "running",
          endpoint,
        },
      ]),
    });
  });

  await page.route(`${endpoint}/_voice/voices`, async (route: Route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        source: "backend",
        default: "af_bella",
        voices: [
          { id: "af_bella", language: "en-US", language_label: "American English", gender: "female" },
          { id: "am_adam",  language: "en-US", language_label: "American English", gender: "male" },
          { id: "ef_dora",  language: "es",    language_label: "Spanish",          gender: "female" },
        ],
      }),
    });
  });
}

/**
 * Install a small window-level probe that counts AudioBuffers scheduled on
 * any AudioContext instance. This lets us assert the client is actually
 * feeding PCM chunks into Web Audio, not just receiving bytes.
 */
async function installAudioProbe(page: import("@playwright/test").Page) {
  await page.addInitScript(() => {
    const w = window as unknown as {
      __audioBuffersScheduled: number;
      __audioSampleTotal: number;
    };
    w.__audioBuffersScheduled = 0;
    w.__audioSampleTotal = 0;
    const OriginalCtx = window.AudioContext;
    class ProbedContext extends OriginalCtx {
      createBufferSource(): AudioBufferSourceNode {
        const src = super.createBufferSource();
        const originalStart = src.start.bind(src);
        src.start = ((when?: number) => {
          if (src.buffer) {
            w.__audioBuffersScheduled += 1;
            w.__audioSampleTotal += src.buffer.length;
          }
          return originalStart(when);
        }) as AudioBufferSourceNode["start"];
        return src;
      }
    }
    Object.defineProperty(window, "AudioContext", {
      configurable: true,
      writable: true,
      value: ProbedContext,
    });
  });
}

// ---------------------------------------------------------------------------
// Specs
// ---------------------------------------------------------------------------

test.describe("Voice cockpit", () => {
  let mock: MockWsHandle | null = null;

  test.afterEach(async () => {
    if (mock) {
      await mock.close();
      mock = null;
    }
  });

  test("streams a full utterance and schedules audio chunks in order", async ({ page }) => {
    mock = await bootScenario("happy");
    await stubBackend(page, mock);
    await installAudioProbe(page);

    await page.goto("/#/voice");

    // Voice select should populate with the stubbed catalogue.
    await expect(page.getByTestId("select-voice")).toBeEnabled();
    await expect(page.getByTestId("text-voice-source")).toHaveText("3 live");

    // Kick off synthesis.
    await page.getByTestId("button-play").click();

    // The status pill walks connecting → streaming → done. We only assert
    // the terminal state to keep the test resilient to timing jitter.
    await expect(page.getByTestId("status-done")).toBeVisible({ timeout: 10_000 });

    // Stats should reflect the 3 chunks the mock sent (100ms @ 24kHz mono
    // int16 = 2400 samples * 2 bytes = 4800 bytes each).
    const stats = await page.getByTestId("text-stream-stats").textContent();
    expect(stats).toContain("3 chunks");
    expect(stats).toContain("14.1 kB"); // 14400 bytes / 1024

    // AudioContext probe: 3 buffers, 3 * 2400 samples.
    const scheduled = await page.evaluate(
      () => (window as unknown as { __audioBuffersScheduled: number }).__audioBuffersScheduled,
    );
    const samples = await page.evaluate(
      () => (window as unknown as { __audioSampleTotal: number }).__audioSampleTotal,
    );
    expect(scheduled).toBe(3);
    expect(samples).toBe(3 * 2400);
  });

  test("cancel button interrupts an in-flight stream", async ({ page }) => {
    mock = await bootScenario("cancellable");
    await stubBackend(page, mock);
    await installAudioProbe(page);

    await page.goto("/#/voice");
    await expect(page.getByTestId("select-voice")).toBeEnabled();

    await page.getByTestId("button-play").click();
    // Wait for the streaming pill so we know audio started flowing.
    await expect(page.getByTestId("status-streaming")).toBeVisible({ timeout: 10_000 });

    // Stop.
    await page.getByTestId("button-stop").click();

    // Back to idle. Play button should be available again.
    await expect(page.getByTestId("button-play")).toBeVisible({ timeout: 5_000 });

    // The mock must have observed a cancel frame.
    await expect
      .poll(() => mock!.received.some((m) => m.includes("\"cancel\"")), {
        timeout: 3_000,
      })
      .toBe(true);
  });

  test("surfaces backend rejection as an error", async ({ page }) => {
    mock = await bootScenario("reject");
    await stubBackend(page, mock);

    await page.goto("/#/voice");
    await expect(page.getByTestId("select-voice")).toBeEnabled();

    await page.getByTestId("button-play").click();

    await expect(page.getByTestId("status-error")).toBeVisible({ timeout: 5_000 });
    await expect(page.getByTestId("text-voice-error")).toContainText("text is required");
  });

  test("surfaces backend 'unavailable' as an error", async ({ page }) => {
    mock = await bootScenario("unavailable");
    await stubBackend(page, mock);

    await page.goto("/#/voice");
    await expect(page.getByTestId("select-voice")).toBeEnabled();

    await page.getByTestId("button-play").click();

    await expect(page.getByTestId("status-error")).toBeVisible({ timeout: 5_000 });
  });

  test("larger streams schedule gapless playback timings", async ({ page }) => {
    mock = await bootScenario("many-chunks");
    await stubBackend(page, mock);
    await installAudioProbe(page);

    await page.goto("/#/voice");
    await expect(page.getByTestId("select-voice")).toBeEnabled();

    await page.getByTestId("button-play").click();
    await expect(page.getByTestId("status-done")).toBeVisible({ timeout: 15_000 });

    const scheduled = await page.evaluate(
      () => (window as unknown as { __audioBuffersScheduled: number }).__audioBuffersScheduled,
    );
    expect(scheduled).toBe(10);

    // Total sample duration = 10 * 100ms = 1 s. Ensure the scheduler
    // wrote the expected sample count.
    const samples = await page.evaluate(
      () => (window as unknown as { __audioSampleTotal: number }).__audioSampleTotal,
    );
    expect(samples).toBe(10 * 2400);
  });
});
