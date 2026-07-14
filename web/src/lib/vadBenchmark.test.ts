/**
 * Unit tests for vadBenchmark.ts. The real @litertjs/core WASM is never loaded;
 * we inject a fake core via literert's test seam so we can assert the
 * recurrent-state lifecycle (zeros init, state carried frame-to-frame), output
 * mapping (prob vs next-state by size), tensor freeing, the deterministic
 * fixture generators, and the mocked-E2E path — all without a browser.
 */
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { __resetForTests, __setCoreImporterForTests } from "./literert";
import {
  SILERO_VAD,
  makeDeterministicFrame,
  makeDeterministicFrames,
  runVadBenchmark,
} from "./vadBenchmark";

const HIDDEN = 128;

interface FakeRunRecord {
  statesSeen: Float32Array[];
  freed: { deleted: boolean }[];
}

function makeFakeCore(rec: FakeRunRecord) {
  class T {
    deleted = false;
    _arr: Float32Array;
    constructor(
      public arr: Float32Array,
      public shape: number[],
    ) {
      this._arr = arr;
    }
    async data() {
      return this._arr;
    }
    delete() {
      this.deleted = true;
      rec.freed.push(this);
    }
  }

  let step = 0;
  const model = {
    getInputDetails: () => [
      { name: "input", index: 0, dtype: "float32", shape: [1, 512], supportedBufferTypes: [] },
      { name: "state", index: 1, dtype: "float32", shape: [2, HIDDEN], supportedBufferTypes: [] },
    ],
    getOutputDetails: () => [
      { name: "Identity", index: 0, dtype: "float32", shape: [1, 1], supportedBufferTypes: [] },
      { name: "Identity_1", index: 1, dtype: "float32", shape: [2, HIDDEN], supportedBufferTypes: [] },
    ],
    run: vi.fn(async (inputs: T[]) => {
      // input[1] is the recurrent state; record what the model actually saw.
      rec.statesSeen.push(new Float32Array(inputs[1]._arr));
      // Produce a monotonically increasing next-state so the carry is testable.
      const next = new Float32Array(2 * HIDDEN);
      for (let i = 0; i < next.length; i++) next[i] = inputs[1]._arr[i] + 1;
      const prob = new Float32Array([Math.min(1, 0.1 * ++step)]);
      return [new T(prob, [1, 1]), new T(next, [2, HIDDEN])];
    }),
  };

  const loadAndCompile = vi.fn(async () => model);
  const loadLiteRt = vi.fn(async () => ({ runtime: true }));
  return {
    module: { loadLiteRt, loadAndCompile, Tensor: T } as never,
    model,
  };
}

beforeEach(() => {
  __resetForTests();
  // modelAvailable() does a HEAD fetch — say yes.
  vi.stubGlobal("fetch", vi.fn(async () => ({ ok: true, status: 200 }) as unknown as Response));
});

afterEach(() => {
  vi.unstubAllGlobals();
  __resetForTests();
  delete (globalThis as { __NEXUS_VAD_MOCK__?: unknown }).__NEXUS_VAD_MOCK__;
});

describe("deterministic fixtures", () => {
  it("makeDeterministicFrame is byte-identical for the same offset", () => {
    const a = makeDeterministicFrame(512, 0);
    const b = makeDeterministicFrame(512, 0);
    expect(Array.from(a)).toEqual(Array.from(b));
    expect(a.length).toBe(512);
    expect(a.every((v) => v >= -1.1 && v <= 1.1)).toBe(true);
  });

  it("makeDeterministicFrames produces distinct, contiguous frames", () => {
    const frames = makeDeterministicFrames(4, 512);
    expect(frames).toHaveLength(4);
    // Different offsets => different content.
    expect(Array.from(frames[0])).not.toEqual(Array.from(frames[1]));
    // Frame f starts at f*512, so frame 1 sample 0 == a fresh frame at offset 512.
    expect(frames[1][0]).toBeCloseTo(makeDeterministicFrame(512, 512)[0], 12);
  });
});

describe("runVadBenchmark real path (fake core)", () => {
  it("carries recurrent state frame-to-frame starting from zeros", async () => {
    const rec: FakeRunRecord = { statesSeen: [], freed: [] };
    const core = makeFakeCore(rec);
    __setCoreImporterForTests(async () => core.module);

    const res = await runVadBenchmark({
      requestedBackend: "wasm",
      warmupRuns: 1,
      measuredRuns: 3,
    });

    expect(res.source).toBe("hardware");
    expect(res.status).toBe("ok");
    expect(res.selectedBackend).toBe("wasm");
    expect(res.framesProcessed).toBe(3);
    expect(res.timing?.runs).toBe(3);

    // 1 warmup + 3 measured = 4 runs.
    expect(core.model.run).toHaveBeenCalledTimes(4);
    // First state seen is all zeros; each subsequent state is the prior + 1.
    expect(Array.from(rec.statesSeen[0])).toEqual(new Array(2 * HIDDEN).fill(0));
    expect(rec.statesSeen[1][0]).toBe(1);
    expect(rec.statesSeen[2][0]).toBe(2);
    expect(rec.statesSeen[3][0]).toBe(3);
    // Real output surfaced (prob grows to 0.4 by the 4th run).
    expect(res.maxSpeechProb).toBeGreaterThan(0);
    // Every tensor created (2 inputs + 2 outputs per run) was freed.
    expect(rec.freed.length).toBe(4 * 4);
    expect(rec.freed.every((t) => t.deleted)).toBe(true);
  });

  it("reports model-unavailable when the fetch check fails", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => ({ ok: false, status: 404 }) as unknown as Response));
    const core = makeFakeCore({ statesSeen: [], freed: [] });
    __setCoreImporterForTests(async () => core.module);
    const res = await runVadBenchmark({ requestedBackend: "wasm" });
    expect(res.status).toBe("model-unavailable");
    expect(res.timing).toBeNull();
    expect(res.maxSpeechProb).toBeNull();
  });

  it("includes pinned model provenance (sha256 + version)", async () => {
    const core = makeFakeCore({ statesSeen: [], freed: [] });
    __setCoreImporterForTests(async () => core.module);
    const res = await runVadBenchmark({ requestedBackend: "wasm", warmupRuns: 0, measuredRuns: 1 });
    expect(res.model.sha256).toBe(SILERO_VAD.sha256);
    expect(res.model.version).toBe("v5.1");
    expect(res.model.license).toBe("MIT");
  });
});

describe("mocked E2E path", () => {
  it("returns source=mock and recomputes real-time factor without WASM", async () => {
    vi.stubGlobal("window", {
      __NEXUS_VAD_MOCK__: {
        status: "ok",
        selectedBackend: "webgpu",
        timing: {
          runs: 30,
          warmupRuns: 3,
          latenciesMs: [],
          medianMs: 3.2,
          p95Ms: 5,
          minMs: 3,
          maxMs: 6,
          meanMs: 3.5,
        },
      },
    });
    const res = await runVadBenchmark({ requestedBackend: "webgpu" });
    expect(res.source).toBe("mock");
    expect(res.status).toBe("ok");
    // frameBudget = 512/16000*1000 = 32ms; RTF = 3.2/32 = 0.1.
    expect(res.realTimeFactor).toBeCloseTo(0.1, 6);
    // Provenance still filled from defaults.
    expect(res.model.sha256).toBe(SILERO_VAD.sha256);
  });
});
