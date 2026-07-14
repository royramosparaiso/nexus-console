/**
 * vadBenchmark.ts — Silero VAD proof-of-concept benchmark for the Voice
 * cockpit. Runs the real, committed silero_vad.tflite through LiteRT.js and
 * measures runtime init, model compile, and per-frame inference latency on
 * *this device/session only*, plus honest capability diagnostics.
 *
 * Model provenance: Silero VAD is MIT-licensed (github.com/snakers4/silero-vad).
 * Upstream ships ONNX/JIT, not .tflite, so we convert the verified v5.1 ONNX
 * ourselves (see tools/vad-conversion/) and commit the parity-checked result at
 * web/public/models/silero-vad/silero_vad.tflite. scripts/fetch-vad-model.mjs
 * re-verifies its SHA256 on setup.
 *
 * Stateful contract (16 kHz, 512-sample frames):
 *   inputs : input f32 [1,512]  (one frame)
 *            state f32 [2,128]  (LSTM h;c, zeros at stream start)
 *   outputs: prob  f32 [1,1]    (speech probability)
 *            state f32 [2,128]  (fed into the next frame's state)
 * We init state to zeros and carry the output state across frames — the real
 * recurrent lifecycle, not a per-frame reset.
 *
 * Deterministic E2E path: if `window.__NEXUS_VAD_MOCK__` is set, the benchmark
 * returns that mocked result (source:"mock") without loading any WASM, so CI
 * can drive every UI state with no hardware. Mocked numbers are never presented
 * as hardware numbers.
 */

import type { Tensor, TensorDetails } from "@litertjs/core";

import {
  Backend,
  DeviceCapabilities,
  TimingSummary,
  collectCapabilities,
  ensureRuntime,
  loadModel,
  selectBackend,
  summarize,
} from "./literert";

export type { Backend } from "./literert";

/** LSTM hidden size — the recurrent state is [2, HIDDEN] (row 0 = h, 1 = c). */
const HIDDEN = 128;

export const SILERO_VAD = {
  /** Committed, integrity-checked model served from web/public/models/. */
  url: "/models/silero-vad/silero_vad.tflite",
  license: "MIT",
  source: "github.com/snakers4/silero-vad",
  version: "v5.1",
  /** SHA256 of the committed .tflite (see fetch-vad-model.mjs / README). */
  sha256: "99e2ca568d436f781a98f669b71bb83db248452c367144f51704a8feae4996a7",
  /** Silero VAD v5.1 operates on 16 kHz audio in 512-sample frames. */
  sampleRate: 16000,
  frameSize: 512,
  stateShape: [2, HIDDEN] as const,
} as const;

export type BenchmarkStatus = "ok" | "fallback" | "error" | "model-unavailable";

export interface VadModelInfo {
  url: string;
  license: string;
  source: string;
  version: string;
  sha256: string;
}

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
  /** Frames actually pushed through the model (measured runs). */
  framesProcessed: number | null;
  /** Max speech probability observed over the measured frames (real output). */
  maxSpeechProb: number | null;
  model: VadModelInfo;
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

function tensorSize(d: TensorDetails): number {
  return Array.from(d.shape).reduce((a, b) => a * b, 1);
}

/**
 * A deterministic pseudo-audio frame at time-offset `start` (in samples): a
 * fixed mixture of sine tones so every run/device processes byte-identical
 * input. Values in [-1, 1]. Consecutive frames use contiguous offsets to form
 * a coherent stream for the stateful model.
 */
export function makeDeterministicFrame(n: number, start = 0): Float32Array {
  const out = new Float32Array(n);
  for (let i = 0; i < n; i++) {
    const t = start + i;
    out[i] =
      0.6 * Math.sin((2 * Math.PI * 220 * t) / SILERO_VAD.sampleRate) +
      0.3 * Math.sin((2 * Math.PI * 440 * t) / SILERO_VAD.sampleRate) +
      0.1 * Math.sin((2 * Math.PI * 880 * t) / SILERO_VAD.sampleRate);
  }
  return out;
}

/** A contiguous sequence of `count` deterministic frames of `frameSize`. */
export function makeDeterministicFrames(count: number, frameSize: number): Float32Array[] {
  const frames: Float32Array[] = [];
  for (let f = 0; f < count; f++) frames.push(makeDeterministicFrame(frameSize, f * frameSize));
  return frames;
}

/** Slice a flat PCM buffer into `count` frames of `frameSize`, tiling if short. */
function sliceIntoFrames(buf: Float32Array, count: number, frameSize: number): Float32Array[] {
  const frames: Float32Array[] = [];
  for (let f = 0; f < count; f++) {
    const frame = new Float32Array(frameSize);
    for (let i = 0; i < frameSize; i++) {
      const src = f * frameSize + i;
      frame[i] = buf.length ? buf[src % buf.length] : 0;
    }
    frames.push(frame);
  }
  return frames;
}

function nextPow2(n: number): number {
  let p = 1;
  while (p < n) p <<= 1;
  return p;
}

async function captureMicFrames(count: number, frameSize: number): Promise<Float32Array[]> {
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  try {
    const AudioCtx =
      window.AudioContext ||
      (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
    const ctx = new AudioCtx({ sampleRate: SILERO_VAD.sampleRate });
    try {
      const source = ctx.createMediaStreamSource(stream);
      const analyser = ctx.createAnalyser();
      const need = count * frameSize;
      analyser.fftSize = Math.min(32768, Math.max(2048, nextPow2(need)));
      source.connect(analyser);
      await new Promise((r) => setTimeout(r, 200)); // let some audio arrive
      const buf = new Float32Array(analyser.fftSize);
      analyser.getFloatTimeDomainData(buf);
      return sliceIntoFrames(buf, count, frameSize);
    } finally {
      await ctx.close();
    }
  } finally {
    for (const t of stream.getTracks()) t.stop();
  }
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

interface SequenceRun {
  timing: TimingSummary;
  framesProcessed: number;
  maxSpeechProb: number;
}

/**
 * Run the VAD model over a frame sequence with the real recurrent-state
 * lifecycle: state starts at zeros [2,128] and each frame's output state is
 * carried into the next frame. Warmup frames prime the state + JIT and are not
 * timed; measured frames are timed with performance.now(). All tensors are
 * freed each frame to keep WASM memory bounded.
 */
async function runVadSequence(
  core: Awaited<ReturnType<typeof ensureRuntime>>["core"],
  model: Awaited<ReturnType<typeof loadModel>>["model"],
  frames: Float32Array[],
  opts: { warmupRuns: number; measuredRuns: number },
): Promise<SequenceRun> {
  const inD = model.getInputDetails();
  const outD = model.getOutputDetails();
  // Identify the recurrent-state input (size 2*HIDDEN) vs the audio input.
  const stateInIdx = inD.findIndex((d) => tensorSize(d) === 2 * HIDDEN);
  const audioInIdx = inD.findIndex((_, i) => i !== stateInIdx);
  if (stateInIdx < 0 || audioInIdx < 0) {
    throw new Error(
      `unexpected VAD input signature: ${inD.map((d) => `${d.name}${JSON.stringify(Array.from(d.shape))}`).join(", ")}`,
    );
  }

  // Annotated so `state` and the copied `nextState` share the (augmented)
  // Float32Array type; the @litertjs/core global augmentation would otherwise
  // make the two disagree on the backing-buffer type parameter.
  let state: Float32Array = new Float32Array(2 * HIDDEN); // zeros at stream start

  const runFrame = async (frame: Float32Array): Promise<{ dt: number; prob: number }> => {
    const inputs: Tensor[] = inD.map((d, i) => {
      if (i === stateInIdx) return new core.Tensor(state, [2, HIDDEN]);
      const arr = new Float32Array(tensorSize(d));
      arr.set(frame.subarray(0, arr.length));
      return new core.Tensor(arr, Array.from(d.shape));
    });
    const t0 = performance.now();
    const outputs = (await model.run(inputs)) as Tensor[];
    const dt = performance.now() - t0;

    let prob = NaN;
    let nextState: Float32Array | null = null;
    for (let k = 0; k < outputs.length; k++) {
      const size = tensorSize(outD[k]);
      const data = await outputs[k].data();
      if (size === 1) prob = data[0];
      else if (size === 2 * HIDDEN) {
        // Copy out of WASM memory. Construct via numeric length + set (not
        // new Float32Array(data)) to keep the ArrayBuffer-backed type — the
        // @litertjs/core global augmentation otherwise weakens Float32Array.
        const copy = new Float32Array(size);
        copy.set(data as ArrayLike<number>);
        nextState = copy;
      }
    }
    for (const o of outputs) o.delete();
    for (const t of inputs) t.delete();
    if (nextState) state = nextState;
    return { dt, prob };
  };

  const n = frames.length;
  let fi = 0;
  for (let i = 0; i < opts.warmupRuns; i++) await runFrame(frames[fi++ % n]);

  const latencies: number[] = [];
  let maxProb = 0;
  for (let i = 0; i < opts.measuredRuns; i++) {
    const { dt, prob } = await runFrame(frames[fi++ % n]);
    latencies.push(dt);
    if (Number.isFinite(prob)) maxProb = Math.max(maxProb, prob);
  }
  return {
    timing: summarize(latencies, opts.warmupRuns),
    framesProcessed: opts.measuredRuns,
    maxSpeechProb: maxProb,
  };
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

  const modelInfo: VadModelInfo = {
    url: SILERO_VAD.url,
    license: SILERO_VAD.license,
    source: SILERO_VAD.source,
    version: SILERO_VAD.version,
    sha256: SILERO_VAD.sha256,
  };

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
    framesProcessed: null,
    maxSpeechProb: null,
    model: modelInfo,
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
      model: { ...modelInfo, ...(mock.model ?? {}) },
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
        "Run `node scripts/fetch-vad-model.mjs` to verify/provision it (MIT).",
    };
  }

  let runtimeInitMs: number | null = null;
  try {
    const { core } = await ensureRuntime();
    runtimeInitMs = (await ensureRuntime()).initMs;

    const selected: Backend =
      requestedBackend === "wasm" ? "wasm" : await selectBackend();

    const loaded = await loadModel(SILERO_VAD.url, selected);

    const warmupRuns = opts.warmupRuns ?? 3;
    const measuredRuns = opts.measuredRuns ?? 30;
    const frameSize = SILERO_VAD.frameSize;

    let frames: Float32Array[];
    let usedMic = false;
    const needed = warmupRuns + measuredRuns;
    if (opts.useMicrophone && typeof navigator !== "undefined" && navigator.mediaDevices) {
      try {
        frames = await captureMicFrames(needed, frameSize);
        usedMic = true;
      } catch {
        frames = makeDeterministicFrames(needed, frameSize);
      }
    } else {
      frames = makeDeterministicFrames(needed, frameSize);
    }

    const seq = await runVadSequence(core, loaded.model, frames, {
      warmupRuns,
      measuredRuns,
    });

    const budget = frameBudgetMs(frameSize, SILERO_VAD.sampleRate);
    return {
      ...base,
      status: loaded.fallbackUsed ? "fallback" : "ok",
      selectedBackend: loaded.backend,
      fallbackUsed: loaded.fallbackUsed,
      runtimeInitMs,
      modelCompileMs: loaded.compileMs,
      timing: seq.timing,
      frameSize,
      frameBudgetMs: budget,
      realTimeFactor: seq.timing.medianMs / budget,
      framesProcessed: seq.framesProcessed,
      maxSpeechProb: seq.maxSpeechProb,
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
