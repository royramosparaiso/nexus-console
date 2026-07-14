/**
 * Unit tests for literert.ts — the LiteRT.js loader. The heavy @litertjs/core
 * runtime is never downloaded here; we inject a fake module via the test seam
 * (__setCoreImporterForTests) so backend selection, the deterministic
 * webgpu→wasm fallback, runtime/model caching, and timing math are all
 * exercised without WASM or WebGPU.
 */
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import {
  __resetForTests,
  __setCoreImporterForTests,
  collectCapabilities,
  ensureRuntime,
  isWebGpuApiPresent,
  loadModel,
  selectBackend,
  summarize,
  timeInference,
} from "./literert";

// --- Fake @litertjs/core -------------------------------------------------

class FakeTensor {
  deleted = false;
  constructor(
    public data: unknown,
    public shape: number[],
  ) {}
  delete() {
    this.deleted = true;
  }
}

interface FakeModelOpts {
  runMs?: number;
}

function makeFakeModel(opts: FakeModelOpts = {}) {
  return {
    run: vi.fn(async (_input: unknown) => {
      if (opts.runMs) {
        const end = performance.now() + opts.runMs;
        while (performance.now() < end) {
          /* busy-wait to produce a measurable latency */
        }
      }
      return [new FakeTensor(new Float32Array([1]), [1])];
    }),
    getInputDetails: () => [
      { name: "in", index: 0, dtype: "float32", shape: [1, 512], supportedBufferTypes: [] },
    ],
  };
}

/**
 * Build a fake core module. `webgpuFails` makes loadAndCompile throw whenever
 * webgpu is requested so the deterministic CPU fallback can be observed.
 */
function makeFakeCore(opts: { webgpuFails?: boolean; runMs?: number } = {}) {
  const loadAndCompile = vi.fn(
    async (_url: string, cfg: { accelerator: string }) => {
      if (opts.webgpuFails && cfg.accelerator === "webgpu") {
        throw new Error("no webgpu adapter");
      }
      return makeFakeModel({ runMs: opts.runMs });
    },
  );
  const loadLiteRt = vi.fn(async (_dir: string) => ({ runtime: true }));
  return {
    module: {
      loadLiteRt,
      loadAndCompile,
      Tensor: FakeTensor,
    } as never,
    loadAndCompile,
    loadLiteRt,
  };
}

beforeEach(() => {
  __resetForTests();
});

afterEach(() => {
  vi.unstubAllGlobals();
  __resetForTests();
});

describe("summarize", () => {
  it("computes median/p95/min/max/mean over the latency set", () => {
    const s = summarize([10, 20, 30, 40, 50], 3);
    expect(s.runs).toBe(5);
    expect(s.warmupRuns).toBe(3);
    expect(s.minMs).toBe(10);
    expect(s.maxMs).toBe(50);
    expect(s.meanMs).toBe(30);
    expect(s.medianMs).toBe(30);
    expect(s.p95Ms).toBe(50);
  });

  it("is order-independent and handles the empty set", () => {
    expect(summarize([30, 10, 20], 0).medianMs).toBe(20);
    const empty = summarize([], 0);
    expect(empty.runs).toBe(0);
    expect(empty.medianMs).toBe(0);
    expect(empty.p95Ms).toBe(0);
  });
});

describe("capability detection", () => {
  it("reports WebGPU absent when navigator.gpu is missing", async () => {
    vi.stubGlobal("navigator", { userAgent: "test-ua", platform: "test" });
    expect(isWebGpuApiPresent()).toBe(false);
    const caps = await collectCapabilities();
    expect(caps.webgpuApiPresent).toBe(false);
    expect(caps.adapterAcquired).toBe(false);
    expect(caps.userAgent).toBe("test-ua");
  });

  it("selects wasm when no adapter can be acquired", async () => {
    vi.stubGlobal("navigator", { userAgent: "test-ua" });
    await expect(selectBackend()).resolves.toBe("wasm");
  });

  it("selects webgpu and records adapter info when an adapter is acquired", async () => {
    vi.stubGlobal("navigator", {
      userAgent: "gpu-ua",
      gpu: {
        requestAdapter: async () => ({ info: { vendor: "acme", architecture: "rdna" } }),
      },
    });
    expect(isWebGpuApiPresent()).toBe(true);
    await expect(selectBackend()).resolves.toBe("webgpu");
    const caps = await collectCapabilities();
    expect(caps.adapterAcquired).toBe(true);
    expect(caps.adapterInfo?.vendor).toBe("acme");
  });
});

describe("ensureRuntime", () => {
  it("initialises once and shares the promise across callers", async () => {
    const core = makeFakeCore();
    __setCoreImporterForTests(async () => core.module);
    const [a, b] = await Promise.all([ensureRuntime(), ensureRuntime()]);
    expect(a).toBe(b);
    expect(core.loadLiteRt).toHaveBeenCalledTimes(1);
    expect(typeof a.initMs).toBe("number");
    expect(a.initMs).toBeGreaterThanOrEqual(0);
  });
});

describe("loadModel", () => {
  it("compiles on webgpu when it works", async () => {
    const core = makeFakeCore();
    __setCoreImporterForTests(async () => core.module);
    const loaded = await loadModel("/m.tflite", "webgpu");
    expect(loaded.backend).toBe("webgpu");
    expect(loaded.fallbackUsed).toBe(false);
    expect(loaded.compileMs).toBeGreaterThanOrEqual(0);
  });

  it("falls back deterministically to wasm when webgpu compile fails", async () => {
    const core = makeFakeCore({ webgpuFails: true });
    __setCoreImporterForTests(async () => core.module);
    const loaded = await loadModel("/m.tflite", "webgpu");
    expect(loaded.backend).toBe("wasm");
    expect(loaded.fallbackUsed).toBe(true);
    // webgpu attempted, then wasm.
    expect(core.loadAndCompile).toHaveBeenCalledTimes(2);
  });

  it("does not fall back when wasm is explicitly requested", async () => {
    const core = makeFakeCore();
    __setCoreImporterForTests(async () => core.module);
    const loaded = await loadModel("/m.tflite", "wasm");
    expect(loaded.backend).toBe("wasm");
    expect(loaded.fallbackUsed).toBe(false);
    expect(core.loadAndCompile).toHaveBeenCalledTimes(1);
  });

  it("caches one compiled model per (url, backend)", async () => {
    const core = makeFakeCore();
    __setCoreImporterForTests(async () => core.module);
    const a = await loadModel("/m.tflite", "wasm");
    const b = await loadModel("/m.tflite", "wasm");
    expect(a).toBe(b);
    expect(core.loadAndCompile).toHaveBeenCalledTimes(1);
  });
});

describe("timeInference", () => {
  it("runs warmups + measured runs and frees tensors each run", async () => {
    const core = makeFakeCore();
    __setCoreImporterForTests(async () => core.module);
    const { core: coreMod } = await ensureRuntime();
    const loaded = await loadModel("/m.tflite", "wasm");
    const made: FakeTensor[] = [];
    const summary = await timeInference(
      loaded.model,
      () => {
        const t = new coreMod.Tensor(new Float32Array([1]), [1]) as unknown as FakeTensor;
        made.push(t);
        return t as never;
      },
      { warmupRuns: 2, measuredRuns: 5 },
    );
    expect(summary.runs).toBe(5);
    expect(summary.warmupRuns).toBe(2);
    // 2 warmup + 5 measured = 7 total runs.
    expect((loaded.model.run as ReturnType<typeof vi.fn>)).toHaveBeenCalledTimes(7);
    // Every input tensor we handed in was deleted.
    expect(made.every((t) => t.deleted)).toBe(true);
  });
});
