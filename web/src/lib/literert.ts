/// <reference types="@webgpu/types" />
/**
 * literert.ts — lazy, reusable loader for the LiteRT.js browser runtime.
 *
 * Design constraints (see console/agent_templates/skills/local_inference.md):
 *  - The heavy @litertjs/core runtime (~9 MB WASM) is loaded via a dynamic
 *    import() so it never inflates the initial Voice/Console bundle. Nothing
 *    here is imported at module top-level except *types* (erased at build).
 *  - WASM is served from the stable public URL /wasm/litertjs/ (artifacts
 *    copied there by scripts/copy-litert-wasm.mjs). loadLiteRt() feature-
 *    detects the browser and picks the matching *_internal.js + .wasm pair.
 *  - Backend selection: prefer WebGPU when navigator.gpu is present AND an
 *    adapter can actually be acquired; otherwise fall back deterministically
 *    to the WASM (CPU/XNNPACK) backend.
 *  - Timings use performance.now(); we distinguish warmup runs from measured
 *    runs and report median / p95.
 *  - No localStorage / sessionStorage / indexedDB / cookies — the sandbox
 *    iframe forbids them. State lives in module-level promises only, which
 *    also guarantees the runtime + each model initialise at most once across
 *    React re-renders.
 */

import type {
  Accelerator,
  CompiledModel,
  LiteRt,
  Tensor,
} from "@litertjs/core";

type CoreModule = typeof import("@litertjs/core");

export type Backend = Accelerator; // 'webgpu' | 'wasm'

/** Public URL of the directory holding the LiteRT WASM artifacts. */
export const WASM_DIR = "/wasm/litertjs/";

// ---------------------------------------------------------------------------
// Test seam — lets unit tests inject a mocked @litertjs/core without a real
// WASM download. Production always uses the dynamic import.
// ---------------------------------------------------------------------------

let coreImporter: () => Promise<CoreModule> = () => import("@litertjs/core");

/** @internal test-only: override the runtime module loader. */
export function __setCoreImporterForTests(fn: () => Promise<CoreModule>): void {
  coreImporter = fn;
}

/** @internal test-only: reset all cached state + the module loader. */
export function __resetForTests(): void {
  coreImporter = () => import("@litertjs/core");
  runtimePromise = null;
  modelCache.clear();
}

// ---------------------------------------------------------------------------
// Capability diagnostics — capability of *this* device/session, not global
// statistics. Everything is guarded so it is safe under SSR / node / tests.
// ---------------------------------------------------------------------------

export interface DeviceCapabilities {
  /** navigator.gpu exists (the WebGPU API surface is present). */
  webgpuApiPresent: boolean;
  /** requestAdapter() returned a usable adapter. undefined until probed. */
  adapterAcquired?: boolean;
  /** Best-effort adapter identity where the browser exposes it. */
  adapterInfo?: {
    vendor?: string;
    architecture?: string;
    device?: string;
    description?: string;
  };
  /** crossOriginIsolated — required for threaded WASM; informational here. */
  crossOriginIsolated: boolean;
  userAgent: string;
  platform: string;
}

export function isWebGpuApiPresent(): boolean {
  return typeof navigator !== "undefined" && !!navigator.gpu;
}

/**
 * Probe the WebGPU adapter for this session. Never throws — a browser without
 * WebGPU, or one that refuses an adapter, resolves to adapterAcquired=false.
 */
export async function probeWebGpuAdapter(): Promise<{
  acquired: boolean;
  info?: DeviceCapabilities["adapterInfo"];
}> {
  if (!isWebGpuApiPresent()) return { acquired: false };
  try {
    const adapter = await navigator.gpu!.requestAdapter();
    if (!adapter) return { acquired: false };
    // adapter.info is not universally available; read defensively.
    const info = (adapter as unknown as { info?: GPUAdapterInfo }).info;
    return {
      acquired: true,
      info: info
        ? {
            vendor: info.vendor,
            architecture: info.architecture,
            device: info.device,
            description: info.description,
          }
        : undefined,
    };
  } catch {
    return { acquired: false };
  }
}

export async function collectCapabilities(): Promise<DeviceCapabilities> {
  const nav = typeof navigator !== "undefined" ? navigator : undefined;
  const base: DeviceCapabilities = {
    webgpuApiPresent: isWebGpuApiPresent(),
    crossOriginIsolated:
      typeof globalThis !== "undefined" &&
      (globalThis as { crossOriginIsolated?: boolean }).crossOriginIsolated === true,
    userAgent: nav?.userAgent ?? "unknown",
    platform:
      (nav as unknown as { platform?: string })?.platform ?? "unknown",
  };
  const probe = await probeWebGpuAdapter();
  base.adapterAcquired = probe.acquired;
  base.adapterInfo = probe.info;
  return base;
}

/**
 * Decide which backend to *request*. WebGPU only when the API is present and
 * an adapter is actually acquirable; otherwise WASM. Deterministic given the
 * same device state.
 */
export async function selectBackend(): Promise<Backend> {
  const probe = await probeWebGpuAdapter();
  return probe.acquired ? "webgpu" : "wasm";
}

// ---------------------------------------------------------------------------
// Runtime — single shared initialization.
// ---------------------------------------------------------------------------

export interface RuntimeHandle {
  core: CoreModule;
  runtime: LiteRt;
  /** Wall-clock ms to import the module + loadLiteRt(). */
  initMs: number;
}

let runtimePromise: Promise<RuntimeHandle> | null = null;

export class LiteRtError extends Error {
  constructor(message: string, readonly cause?: unknown) {
    super(message);
    this.name = "LiteRtError";
  }
}

/**
 * Load the WASM runtime exactly once. Concurrent callers share one promise;
 * a failed load clears the cache so a later call can retry.
 */
export function ensureRuntime(): Promise<RuntimeHandle> {
  if (runtimePromise) return runtimePromise;
  runtimePromise = (async () => {
    const t0 = performance.now();
    let core: CoreModule;
    try {
      core = await coreImporter();
    } catch (err) {
      throw new LiteRtError(
        "Failed to import @litertjs/core. Is the runtime bundle available?",
        err,
      );
    }
    let runtime: LiteRt;
    try {
      runtime = await core.loadLiteRt(WASM_DIR);
    } catch (err) {
      throw new LiteRtError(
        `Failed to initialise LiteRT WASM from ${WASM_DIR}. ` +
          "Confirm the artifacts were copied (npm run copy:litert-wasm).",
        err,
      );
    }
    return { core, runtime, initMs: performance.now() - t0 };
  })();
  runtimePromise.catch(() => {
    runtimePromise = null;
  });
  return runtimePromise;
}

// ---------------------------------------------------------------------------
// Model loading — one compiled model per (url, backend), cached.
// ---------------------------------------------------------------------------

export interface LoadedModel {
  model: CompiledModel;
  /** Backend that was actually compiled. */
  backend: Backend;
  /** Backend that was requested before any fallback. */
  requestedBackend: Backend;
  /** ms to compile the model. */
  compileMs: number;
  /** True when a webgpu request was downgraded to wasm. */
  fallbackUsed: boolean;
}

const modelCache = new Map<string, Promise<LoadedModel>>();

/**
 * Load + compile a .tflite model. If webgpu is requested but compilation
 * fails, deterministically retries on wasm and reports fallbackUsed=true.
 */
export function loadModel(
  url: string,
  requestedBackend: Backend = "webgpu",
): Promise<LoadedModel> {
  const key = `${url}::${requestedBackend}`;
  const cached = modelCache.get(key);
  if (cached) return cached;

  const promise = (async (): Promise<LoadedModel> => {
    const { core } = await ensureRuntime();

    const compile = async (backend: Backend): Promise<{ model: CompiledModel; ms: number }> => {
      const t0 = performance.now();
      const model = await core.loadAndCompile(url, { accelerator: backend });
      return { model, ms: performance.now() - t0 };
    };

    if (requestedBackend === "wasm") {
      try {
        const { model, ms } = await compile("wasm");
        return { model, backend: "wasm", requestedBackend, compileMs: ms, fallbackUsed: false };
      } catch (err) {
        throw new LiteRtError(`Failed to compile model on wasm: ${url}`, err);
      }
    }

    // requestedBackend === 'webgpu'
    try {
      const { model, ms } = await compile("webgpu");
      return { model, backend: "webgpu", requestedBackend, compileMs: ms, fallbackUsed: false };
    } catch (webgpuErr) {
      // Deterministic fallback to CPU.
      try {
        const { model, ms } = await compile("wasm");
        return { model, backend: "wasm", requestedBackend, compileMs: ms, fallbackUsed: true };
      } catch (wasmErr) {
        throw new LiteRtError(
          `Failed to compile model on webgpu (${(webgpuErr as Error)?.message ?? webgpuErr}) ` +
            `and on wasm fallback: ${url}`,
          wasmErr,
        );
      }
    }
  })();

  modelCache.set(key, promise);
  promise.catch(() => modelCache.delete(key));
  return promise;
}

// ---------------------------------------------------------------------------
// Inference timing.
// ---------------------------------------------------------------------------

export interface TimingSummary {
  runs: number;
  warmupRuns: number;
  latenciesMs: number[];
  medianMs: number;
  p95Ms: number;
  minMs: number;
  maxMs: number;
  meanMs: number;
}

export function summarize(latenciesMs: number[], warmupRuns: number): TimingSummary {
  const sorted = [...latenciesMs].sort((a, b) => a - b);
  const n = sorted.length;
  const pct = (p: number) => {
    if (n === 0) return 0;
    const idx = Math.min(n - 1, Math.ceil((p / 100) * n) - 1);
    return sorted[Math.max(0, idx)];
  };
  const sum = sorted.reduce((a, b) => a + b, 0);
  return {
    runs: n,
    warmupRuns,
    latenciesMs,
    medianMs: pct(50),
    p95Ms: pct(95),
    minMs: n ? sorted[0] : 0,
    maxMs: n ? sorted[n - 1] : 0,
    meanMs: n ? sum / n : 0,
  };
}

/**
 * Run a compiled model `measuredRuns` times (after `warmupRuns` discarded
 * warmups) against a factory that yields fresh input tensors, timing each
 * measured run with performance.now(). Output tensors are deleted between
 * runs to avoid leaking WASM buffers.
 */
export async function timeInference(
  model: CompiledModel,
  makeInput: () => Tensor | Tensor[],
  opts: { warmupRuns?: number; measuredRuns?: number } = {},
): Promise<TimingSummary> {
  const warmupRuns = opts.warmupRuns ?? 2;
  const measuredRuns = opts.measuredRuns ?? 20;

  const runOnce = async (): Promise<number> => {
    const input = makeInput();
    const t0 = performance.now();
    const outputs = await model.run(input as Tensor | Tensor[]);
    const dt = performance.now() - t0;
    // Free outputs + inputs to keep WASM memory bounded across runs.
    for (const o of Array.isArray(outputs) ? outputs : Object.values(outputs)) {
      try {
        (o as Tensor).delete();
      } catch {
        /* ignore */
      }
    }
    for (const i of Array.isArray(input) ? input : [input]) {
      try {
        i.delete();
      } catch {
        /* ignore */
      }
    }
    return dt;
  };

  for (let i = 0; i < warmupRuns; i++) await runOnce();
  const latencies: number[] = [];
  for (let i = 0; i < measuredRuns; i++) latencies.push(await runOnce());
  return summarize(latencies, warmupRuns);
}
