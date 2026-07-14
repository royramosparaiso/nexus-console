/**
 * VadBenchmarkPanel — Silero VAD proof-of-concept for the Voice cockpit.
 *
 * Runs a LiteRT.js benchmark against the current device and reports honest,
 * current-device-only metrics + capability diagnostics. It never fabricates
 * numbers: if the model is not provisioned it says so, and mocked E2E runs are
 * labelled as such. See web/src/lib/vadBenchmark.ts.
 */

import { useRef, useState } from "react";
import { AlertCircle, Cpu, Gauge, RotateCcw, Square, Zap } from "lucide-react";

import {
  type Backend,
  type BenchmarkStatus,
  type VadBenchmarkResult,
  runVadBenchmark,
} from "../lib/vadBenchmark";

type UiState = "idle" | "running" | "done";

const STATUS_LABEL: Record<BenchmarkStatus, string> = {
  ok: "Pass",
  fallback: "Pass (CPU fallback)",
  error: "Error",
  "model-unavailable": "Model unavailable",
};

const STATUS_CLASS: Record<BenchmarkStatus, string> = {
  ok: "bg-success/15 text-success",
  fallback: "bg-primary/15 text-primary",
  error: "bg-error/15 text-error",
  "model-unavailable": "bg-surface-alt text-text-muted",
};

function ms(v: number | null | undefined): string {
  return v == null ? "—" : `${v.toFixed(1)} ms`;
}

function yesNo(v: boolean | undefined): string {
  if (v === undefined) return "—";
  return v ? "yes" : "no";
}

function Metric({
  label,
  value,
  testid,
}: {
  label: string;
  value: string;
  testid: string;
}) {
  return (
    <div className="rounded-md border border-border bg-bg px-3 py-2">
      <div className="text-[10px] font-medium uppercase tracking-wider text-text-faint">
        {label}
      </div>
      <div className="mt-0.5 font-mono text-sm text-text" data-testid={testid}>
        {value}
      </div>
    </div>
  );
}

export default function VadBenchmarkPanel() {
  const [uiState, setUiState] = useState<UiState>("idle");
  const [result, setResult] = useState<VadBenchmarkResult | null>(null);
  const [backend, setBackend] = useState<Backend>("webgpu");
  const [useMic, setUseMic] = useState(false);
  const cancelledRef = useRef(false);
  const runningRef = useRef(false);

  const onRun = async () => {
    if (runningRef.current) return; // guard against double-invocation
    runningRef.current = true;
    cancelledRef.current = false;
    setResult(null);
    setUiState("running");
    try {
      const r = await runVadBenchmark({
        requestedBackend: backend,
        useMicrophone: useMic,
      });
      if (cancelledRef.current) return;
      setResult(r);
      setUiState("done");
    } finally {
      runningRef.current = false;
    }
  };

  const onCancel = () => {
    cancelledRef.current = true;
    runningRef.current = false;
    setUiState("idle");
  };

  const onReset = () => {
    cancelledRef.current = true;
    runningRef.current = false;
    setResult(null);
    setUiState("idle");
  };

  const cap = result?.capabilities;

  return (
    <section
      className="mt-6 space-y-5 rounded-lg border border-border bg-surface p-6"
      data-testid="vad-panel"
    >
      <div className="flex items-start gap-2">
        <Zap className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
        <div>
          <h2 className="text-sm font-semibold text-text" data-testid="text-vad-title">
            Silero VAD benchmark (LiteRT.js PoC)
          </h2>
          <p className="mt-1 text-xs text-text-muted">
            Runs voice-activity detection locally in your browser via LiteRT.js
            to measure inference latency and WebGPU coverage on{" "}
            <span className="font-medium">this device only</span>. Model:
            Silero VAD ({SILERO_VAD_LICENSE}).
          </p>
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <label className="flex items-center gap-2 text-xs text-text-muted">
          <span>Backend</span>
          <select
            value={backend}
            onChange={(e) => setBackend(e.target.value as Backend)}
            disabled={uiState === "running"}
            data-testid="select-vad-backend"
            className="rounded-md border border-border bg-bg px-2 py-1.5 text-sm text-text disabled:opacity-50"
          >
            <option value="webgpu">WebGPU (auto-fallback to CPU)</option>
            <option value="wasm">WASM / CPU</option>
          </select>
        </label>

        <label className="flex items-center gap-2 text-xs text-text-muted">
          <input
            type="checkbox"
            checked={useMic}
            onChange={(e) => setUseMic(e.target.checked)}
            disabled={uiState === "running"}
            data-testid="checkbox-vad-mic"
          />
          <span>Use microphone (else deterministic fixture)</span>
        </label>

        {uiState === "running" ? (
          <button
            onClick={onCancel}
            data-testid="button-stop-vad"
            className="inline-flex items-center gap-2 rounded-md bg-error px-4 py-2 text-sm font-medium text-white transition hover:opacity-90"
          >
            <Square className="h-4 w-4" />
            Cancel
          </button>
        ) : (
          <button
            onClick={onRun}
            data-testid="button-run-vad"
            className="inline-flex items-center gap-2 rounded-md bg-primary px-4 py-2 text-sm font-medium text-white transition hover:bg-primary-hover"
          >
            <Gauge className="h-4 w-4" />
            Run benchmark
          </button>
        )}

        {uiState === "done" && (
          <button
            onClick={onReset}
            data-testid="button-reset-vad"
            className="inline-flex items-center gap-2 rounded-md border border-border bg-bg px-3 py-2 text-sm text-text-muted transition hover:text-text"
          >
            <RotateCcw className="h-4 w-4" />
            Reset
          </button>
        )}

        <span
          className="ml-auto text-[11px] font-medium uppercase tracking-wider text-text-faint"
          data-testid="vad-ui-state"
          aria-live="polite"
        >
          {uiState}
        </span>
      </div>

      {uiState === "running" && (
        <div
          className="rounded-md border border-dashed border-border p-4 text-center text-sm text-text-muted"
          data-testid="vad-running"
          aria-busy="true"
        >
          Loading runtime and running inference…
        </div>
      )}

      {result && uiState === "done" && (
        <div className="space-y-4" data-testid="vad-result">
          <div className="flex flex-wrap items-center gap-2">
            <span
              className={`rounded-full px-2.5 py-1 text-[11px] font-medium uppercase tracking-wider ${STATUS_CLASS[result.status]}`}
              data-testid="vad-status"
            >
              {STATUS_LABEL[result.status]}
            </span>
            <span
              className="rounded-full bg-surface-alt px-2.5 py-1 text-[11px] font-medium uppercase tracking-wider text-text-muted"
              data-testid="vad-source"
            >
              {result.source === "mock" ? "mocked (E2E)" : "hardware"}
            </span>
            {result.fallbackUsed && (
              <span
                className="inline-flex items-center gap-1 rounded-full bg-primary/15 px-2.5 py-1 text-[11px] font-medium uppercase tracking-wider text-primary"
                data-testid="vad-fallback-used"
              >
                <Cpu className="h-3 w-3" /> CPU fallback
              </span>
            )}
          </div>

          {result.status === "model-unavailable" && (
            <div
              className="flex items-start gap-2 rounded-md border border-border bg-surface-alt p-3 text-sm text-text-muted"
              data-testid="vad-model-unavailable"
            >
              <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
              <span>{result.error}</span>
            </div>
          )}

          {result.status === "error" && result.error && (
            <div
              className="flex items-start gap-2 rounded-md border border-error/40 bg-error/10 p-3 text-sm text-error"
              data-testid="vad-error"
            >
              <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
              <span>{result.error}</span>
            </div>
          )}

          {/* Measurement — current device/session only. */}
          <div>
            <div className="mb-2 text-[10px] font-semibold uppercase tracking-wider text-text-faint">
              Measurement (this session)
            </div>
            <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
              <Metric label="Runtime init" value={ms(result.runtimeInitMs)} testid="vad-runtime-init" />
              <Metric label="Model compile" value={ms(result.modelCompileMs)} testid="vad-compile-ms" />
              <Metric
                label="Warmup runs"
                value={result.timing ? String(result.timing.warmupRuns) : "—"}
                testid="vad-warmup"
              />
              <Metric
                label="Median latency"
                value={result.timing ? ms(result.timing.medianMs) : "—"}
                testid="vad-median"
              />
              <Metric
                label="p95 latency"
                value={result.timing ? ms(result.timing.p95Ms) : "—"}
                testid="vad-p95"
              />
              <Metric
                label="Real-time factor"
                value={result.realTimeFactor != null ? `${result.realTimeFactor.toFixed(3)}×` : "—"}
                testid="vad-rtf"
              />
              <Metric
                label="Backend (req→sel)"
                value={`${result.requestedBackend} → ${result.selectedBackend ?? "—"}`}
                testid="vad-backend"
              />
              <Metric
                label="Frame / rate"
                value={`${result.frameSize} @ ${result.sampleRate} Hz`}
                testid="vad-frame"
              />
              <Metric
                label="Frame budget"
                value={ms(result.frameBudgetMs)}
                testid="vad-frame-budget"
              />
              <Metric
                label="Frames processed"
                value={result.framesProcessed != null ? String(result.framesProcessed) : "—"}
                testid="vad-frames"
              />
              <Metric
                label="Max speech prob"
                value={result.maxSpeechProb != null ? result.maxSpeechProb.toFixed(3) : "—"}
                testid="vad-max-prob"
              />
            </div>
          </div>

          {/* Capability diagnostics — current device coverage, not global stats. */}
          <div>
            <div className="mb-2 text-[10px] font-semibold uppercase tracking-wider text-text-faint">
              Device coverage (current device only)
            </div>
            <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
              <Metric
                label="WebGPU API"
                value={yesNo(cap?.webgpuApiPresent)}
                testid="vad-webgpu-present"
              />
              <Metric
                label="Adapter acquired"
                value={yesNo(cap?.adapterAcquired)}
                testid="vad-adapter-acquired"
              />
              <Metric
                label="crossOriginIsolated"
                value={yesNo(cap?.crossOriginIsolated)}
                testid="vad-coi"
              />
              <Metric
                label="Adapter"
                value={
                  cap?.adapterInfo
                    ? [cap.adapterInfo.vendor, cap.adapterInfo.architecture]
                        .filter(Boolean)
                        .join(" / ") || "(anonymous)"
                    : "—"
                }
                testid="vad-adapter-info"
              />
              <Metric label="Microphone" value={yesNo(result.usedMicrophone)} testid="vad-mic-used" />
              <Metric
                label="Model"
                value={`Silero VAD ${result.model.version} (${result.model.license})`}
                testid="vad-model-license"
              />
            </div>
            <p
              className="mt-2 break-all font-mono text-[10px] text-text-faint"
              data-testid="vad-model-sha"
            >
              sha256:{result.model.sha256}
            </p>
            <p
              className="mt-1 break-all text-[10px] text-text-faint"
              data-testid="vad-ua"
            >
              {cap?.userAgent}
            </p>
          </div>
        </div>
      )}
    </section>
  );
}

const SILERO_VAD_LICENSE = "MIT";
