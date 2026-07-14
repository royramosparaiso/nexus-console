/**
 * vadBenchmark.ts — Silero VAD proof-of-concept benchmark for the Voice
 * cockpit. Measures LiteRT.js runtime init, model compile, and inference
 * latency on *this device/session only*, and reports honest capability
 * diagnostics.
 *
 * Model provenance: Silero VAD is MIT-licensed (github.com/snakers4/silero-vad).
 * Upstream distributes ONNX/JIT, not .tflite — so the .tflite must be
 * provisioned locally (see scripts/fetch-vad-model.mjs, which pins the source
 * URL + SHA256 and refuses on mismatch). When the model is absent we report
 * `model-unavailable` and never fabricate inference numbers.
 *
 * Deterministic E2E path: if `window.__NEXUS_VAD_MOCK__` is set, the benchmark
 * returns that mocked result (clearly labelled source:"mock") without loading
 * any WASM. This lets CI exercise the UI's success/fallback/error states with
 * no hardware WebGPU. Mocked numbers are never presented as hardware numbers.
 */

import type { TensorDetails, Tensor } from "@litertjs/core";

import {
  Backend,
  DeviceCapabilities,
  TimingSummary,
  collectCapabilities,
  ensureRuntime,
  loadModel,
  selectBackend,
  timeInference,
} from "./literert";

export type { Backend } from "./literert";

export const SILERO_VAD = {
  /** Local path served from web/public/models/silero-vad/ (gitignored). */
  url: "/models/silero-vad/silero_vad.tflite",
  license: "MIT",
  source: "github.com/snakers4/silero-vad",
  /** Silero VAD v5 operates on 16 kHz audio in 512-sample frames. */
  sampleRate: 16000,
  frameSize: 512,
} as const;

export type BenchmarkStatus = "ok" | "fallback" | "error" | "model-unavailable";

export interface VadBenchmarkResult {
  status: BenchmarkStatus;
  /** "hardware" = real LiteRT execution; "mock" = injected deterministic E2E. */
  source: "hardware" | "mock";
  capabilities: DeviceCapabilities;
  requestedBackend: Backend;
  selectedBackend: Backend | null;
  fallbackUsed: boolean;
  runtimeInitMs: number | null;
  modelCompileMs: number | null;
  timing: TimingSummary | null;
  sampleRate: number;
  frameSize: number;
  /** Wall-clock budget for one frame of audio, ms. */
  frameBudgetMs: number;
  /** medianMs / frameBudgetMs — <1 means faster than real time. */
  realTimeFactor: number | null;
  model: { url: string; license: string; source: string };
  usedMicrophone: boolean;
  error?: string;
}

export interface BenchmarkOptions {
  requestedBackend?: Backend;
  warmupRuns?: number;
  measuredRuns?: number;
  useMicrophone?: boolean;
}

interface VadMock extends Partial<VadBenchmarkResult> {
  /** Optional artificial delay so the UI can show its "running" state. */
  delayMs?: number;
}

function readMock(): VadMock | undefined {
  if (typeof window === "undefined") return undefined;
  return (window as unknown as { __NEXUS_VAD_MOCK__?: VadMock }).__NEXUS_VAD_MOCK__;
}

const DTYPE_CTOR = {
  float32: Float32Array,
  int32: Int32Array,
  uint8: Uint8Array,
} as const;

/**
 * A deterministic pseudo-audio frame: a fixed mixture of sine tones so every
 * run/device processes byte-identical input. Values in [-1, 1].
 */
export function makeDeterministicFrame(n: number): Float32Array {
  const out = new Float32Array(n);
  for (let i = 0; i < n; i++) {
    out[i] =
      0.6 * Math.sin((2 * Math.PI * 220 * i) / SILERO_VAD.sampleRate) +
      0.3 * Math.sin((2 * Math.PI * 440 * i) / SILERO_VAD.sampleRate) +
      0.1 * Math.sin((2 * Math.PI * 880 * i) / SILERO_VAD.sampleRate);
  }
  return out;
}

async function captureMicFrame(n: number): Promise<Float32Array> {
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  try {
    const AudioCtx =
      window.AudioContext ||
      (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
    const ctx = new AudioCtx({ sampleRate: SILERO_VAD.sampleRate });
    try {
      const source = ctx.createMediaStreamSource(stream);
      const analyser = ctx.createAnalyser();
      analyser.fftSize = Math.max(2048, nextPow2(n));
      source.connect(analyser);
      await new Promise((r) => setTimeout(r, 120)); // let a little audio arrive
      const buf = new Float32Array(analyser.fftSize);
      analyser.getFloatTimeDomainData(buf);
      return buf.slice(0, n);
    } finally {
      await ctx.close();
    }
  } finally {
    for (const t of stream.getTracks()) t.stop();
  }
}

function nextPow2(n: number): number {
  let p = 1;
  while (p < n) p <<= 1;
  return p;
}

/**
 * Build one fresh set of positional input tensors matching the model's
 * declared input signature. The largest float32 input receives the audio
 * fixture (tiled/truncated to fit); all other inputs (state, sample-rate) are
 * zero-initialised. Robust to Silero's multi-input signature without
 * hardcoding tensor names.
 */
function makeInputsFactory(
  core: Awaited<ReturnType<typeof ensureRuntime>>["core"],
  details: readonly TensorDetails[],
  audio: Float32Array,
): () => Tensor[] {
  return () =>
    details.map((d) => {
      const shape = Array.from(d.shape);
      const size = shape.reduce((a, b) => a * b, 1);
      const Ctor = DTYPE_CTOR[d.dtype as keyof typeof DTYPE_CTOR] ?? Float32Array;
      const arr = new Ctor(size);
      if (d.dtype === "float32") {
        for (let i = 0; i < size; i++) arr[i] = audio[i % audio.length];
      }
      return new core.Tensor(arr as never, shape);
    });
}

/** Choose the audio-carrying input's frame size (largest float32 input). */
function inferFrameSize(details: readonly TensorDetails[]): number {
  let best: number = SILERO_VAD.frameSize;
  let bestSize = -1;
  for (const d of details) {
    if (d.dtype !== "float32") continue;
    const shape = Array.from(d.shape);
    const size = shape.reduce((a, b) => a * b, 1);
    if (size > bestSize) {
      bestSize = size;
      best = shape[shape.length - 1] || size;
    }
  }
  return best;
}

async function modelAvailable(url: string): Promise<boolean> {
  if (typeof fetch === "undefined") return false;
  try {
    const res = await fetch(url, { method: "HEAD" });
    if (res.ok) return true;
    // Some static servers don't support HEAD — try a ranged GET.
    const res2 = await fetch(url, { headers: { Range: "bytes=0-0" } });
    return res2.ok || res2.status === 206;
  } catch {
    return false;
  }
}

function frameBudgetMs(frameSize: number, sampleRate: number): number {
  return (frameSize / sampleRate) * 1000;
}

/**
 * Run the VAD benchmark. Never throws — failures are captured in the returned
 * result's `status`/`error` so the UI can render them.
 */
export async function runVadBenchmark(
  opts: BenchmarkOptions = {},
): Promise<VadBenchmarkResult> {
  const requestedBackend = opts.requestedBackend ?? "webgpu";
  const capabilities = await collectCapabilities();

  const base: VadBenchmarkResult = {
    status: "error",
    source: "hardware",
    capabilities,
    requestedBackend,
    selectedBackend: null,
    fallbackUsed: false,
    runtimeInitMs: null,
    modelCompileMs: null,
    timing: null,
    sampleRate: SILERO_VAD.sampleRate,
    frameSize: SILERO_VAD.frameSize,
    frameBudgetMs: frameBudgetMs(SILERO_VAD.frameSize, SILERO_VAD.sampleRate),
    realTimeFactor: null,
    model: { url: SILERO_VAD.url, license: SILERO_VAD.license, source: SILERO_VAD.source },
    usedMicrophone: false,
  };

  // Deterministic E2E path.
  const mock = readMock();
  if (mock) {
    if (mock.delayMs) await new Promise((r) => setTimeout(r, mock.delayMs));
    const merged: VadBenchmarkResult = {
      ...base,
      ...mock,
      source: "mock",
      capabilities: { ...capabilities, ...(mock.capabilities ?? {}) },
    };
    if (merged.timing && merged.frameBudgetMs) {
      merged.realTimeFactor = merged.timing.medianMs / merged.frameBudgetMs;
    }
    return merged;
  }

  // Real hardware path.
  if (!(await modelAvailable(SILERO_VAD.url))) {
    return {
      ...base,
      status: "model-unavailable",
      error:
        `Silero VAD model not found at ${SILERO_VAD.url}. ` +
        "Run `node scripts/fetch-vad-model.mjs` to provision it (MIT).",
    };
  }

  let runtimeInitMs: number | null = null;
  try {
    const { core } = await ensureRuntime();
    runtimeInitMs = (await ensureRuntime()).initMs;

    const selected: Backend =
      requestedBackend === "wasm" ? "wasm" : await selectBackend();

    const loaded = await loadModel(SILERO_VAD.url, selected);

    let audio: Float32Array;
    let usedMic = false;
    const details = loaded.model.getInputDetails();
    const frameSize = inferFrameSize(details);
    if (opts.useMicrophone && typeof navigator !== "undefined" && navigator.mediaDevices) {
      try {
        audio = await captureMicFrame(frameSize);
        usedMic = true;
      } catch {
        audio = makeDeterministicFrame(frameSize);
      }
    } else {
      audio = makeDeterministicFrame(frameSize);
    }

    const timing = await timeInference(
      loaded.model,
      makeInputsFactory(core, details, audio),
      { warmupRuns: opts.warmupRuns ?? 3, measuredRuns: opts.measuredRuns ?? 30 },
    );

    const budget = frameBudgetMs(frameSize, SILERO_VAD.sampleRate);
    return {
      ...base,
      status: loaded.fallbackUsed ? "fallback" : "ok",
      selectedBackend: loaded.backend,
      fallbackUsed: loaded.fallbackUsed,
      runtimeInitMs,
      modelCompileMs: loaded.compileMs,
      timing,
      frameSize,
      frameBudgetMs: budget,
      realTimeFactor: timing.medianMs / budget,
      usedMicrophone: usedMic,
    };
  } catch (err) {
    return {
      ...base,
      status: "error",
      runtimeInitMs,
      error: err instanceof Error ? `${err.name}: ${err.message}` : String(err),
    };
  }
}
