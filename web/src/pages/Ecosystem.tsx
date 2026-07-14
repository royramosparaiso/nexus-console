/**
 * Ecosystem — honest catalogue of the AI building blocks Nexus can plug into.
 *
 * Renders the /ecosystem registry grouped by category with explicit status
 * badges (available / configurable / experimental / planned). No fake grid of
 * logos: every card states what it is, where the integration lives, and what
 * an operator must do to make it work.
 *
 * Two categories are interactive because they ship real code:
 *  - Voicebox (external voice sidecar): live health check + consent notice.
 *  - LiteRT.js (native local inference): device capability probe.
 */

import { useEffect, useState } from "react";
import {
  AlertCircle,
  CheckCircle2,
  Cpu,
  ExternalLink,
  Mic,
  RefreshCw,
} from "lucide-react";

import { apiFetch } from "../lib/api";
import {
  INTEGRATION_LABEL,
  STATUS_ORDER,
  statusMeta,
  totalEntries,
  type EcosystemEntry,
  type EcosystemStatus,
  type EcosystemView,
} from "../lib/ecosystem";
import { collectCapabilities, type DeviceCapabilities } from "../lib/literert";

interface VoiceboxConfig {
  enabled: boolean;
  base_url: string | null;
  mcp_url: string | null;
  api_key_configured: boolean;
  voice_cloning_consent: boolean;
  configured: boolean;
}

interface VoiceboxStatus {
  state: string;
  detail: string | null;
  base_url: string | null;
  latency_ms: number | null;
  version: string | null;
}

interface CloningConsent {
  consent: boolean;
  notice: string;
}

function StatusBadge({ status }: { status: EcosystemStatus }) {
  const meta = statusMeta(status);
  return (
    <span
      title={meta.hint}
      data-testid={`badge-status-${status}`}
      className={`text-[10px] font-medium uppercase tracking-wider rounded-full px-2 py-0.5 ${meta.className}`}
    >
      {meta.label}
    </span>
  );
}

function EntryCard({ entry }: { entry: EcosystemEntry }) {
  return (
    <div
      className="border border-border bg-surface rounded-lg p-4 flex flex-col gap-2"
      data-testid={`card-ecosystem-${entry.id}`}
    >
      <div className="flex items-start justify-between gap-2">
        <span className="font-medium text-text text-sm">{entry.name}</span>
        <StatusBadge status={entry.status} />
      </div>
      <p className="text-xs text-text-muted leading-relaxed">{entry.summary}</p>
      <div className="flex items-center gap-2 flex-wrap mt-auto pt-1">
        <span className="text-[10px] uppercase tracking-wider text-text-faint">
          {INTEGRATION_LABEL[entry.integration]}
        </span>
        {entry.docs_url && (
          <a
            href={entry.docs_url}
            target="_blank"
            rel="noreferrer noopener"
            className="text-[11px] text-primary hover:underline inline-flex items-center gap-1"
            data-testid={`link-docs-${entry.id}`}
          >
            docs <ExternalLink className="w-3 h-3" />
          </a>
        )}
      </div>
      {entry.requires.length > 0 && entry.status !== "available" && (
        <ul className="text-[11px] text-text-faint list-disc list-inside space-y-0.5">
          {entry.requires.map((r) => (
            <li key={r}>{r}</li>
          ))}
        </ul>
      )}
    </div>
  );
}

function VoiceboxPanel() {
  const [config, setConfig] = useState<VoiceboxConfig | null>(null);
  const [consent, setConsent] = useState<CloningConsent | null>(null);
  const [status, setStatus] = useState<VoiceboxStatus | null>(null);
  const [checking, setChecking] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      apiFetch<VoiceboxConfig>("/voicebox/config"),
      apiFetch<CloningConsent>("/voicebox/cloning-consent"),
    ])
      .then(([c, cc]) => {
        setConfig(c);
        setConsent(cc);
      })
      .catch((e) => setError(String(e)));
  }, []);

  const check = async () => {
    setChecking(true);
    setError(null);
    try {
      setStatus(await apiFetch<VoiceboxStatus>("/voicebox/status"));
    } catch (e) {
      setError(String(e));
    } finally {
      setChecking(false);
    }
  };

  return (
    <section
      className="rounded-lg border border-border bg-surface p-6 space-y-4"
      data-testid="panel-voicebox"
    >
      <div className="flex items-center gap-2">
        <Mic className="w-4 h-4 text-primary" />
        <h2 className="font-semibold text-text">Voicebox — local voice sidecar</h2>
      </div>

      {!config?.enabled ? (
        <div
          className="rounded-md border border-dashed border-border p-4 text-sm text-text-muted"
          data-testid="voicebox-disabled"
        >
          Disabled. Run Voicebox locally, then set{" "}
          <code className="bg-surface-alt px-1 rounded text-xs">CONSOLE_VOICEBOX_ENABLED=true</code>{" "}
          and{" "}
          <code className="bg-surface-alt px-1 rounded text-xs">CONSOLE_VOICEBOX_BASE_URL</code>.
          Everything runs on your machine — no audio is sent anywhere.
        </div>
      ) : (
        <div className="space-y-3 text-sm">
          <dl className="grid grid-cols-[auto_1fr] gap-x-3 gap-y-1 text-xs">
            <dt className="text-text-faint">Base URL</dt>
            <dd className="font-mono text-text">{config.base_url ?? "—"}</dd>
            <dt className="text-text-faint">MCP URL</dt>
            <dd className="font-mono text-text">{config.mcp_url ?? "—"}</dd>
            <dt className="text-text-faint">API key</dt>
            <dd className="text-text">{config.api_key_configured ? "configured" : "none"}</dd>
          </dl>

          <div className="flex items-center gap-3">
            <button
              onClick={check}
              disabled={checking}
              data-testid="button-voicebox-check"
              className="inline-flex items-center gap-2 rounded-md bg-primary px-3 py-1.5 text-xs font-medium text-white hover:bg-primary-hover transition disabled:opacity-40"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${checking ? "animate-spin" : ""}`} />
              Check health
            </button>
            {status && (
              <span data-testid="voicebox-status" className="text-xs">
                <span
                  className={
                    status.state === "reachable"
                      ? "text-success"
                      : status.state === "disabled" || status.state === "unconfigured"
                        ? "text-text-muted"
                        : "text-error"
                  }
                >
                  {status.state}
                </span>
                {status.latency_ms != null && (
                  <span className="text-text-faint"> · {status.latency_ms} ms</span>
                )}
                {status.version && <span className="text-text-faint"> · v{status.version}</span>}
                {status.detail && <span className="text-text-faint"> · {status.detail}</span>}
              </span>
            )}
          </div>
        </div>
      )}

      {consent && (
        <div
          className="rounded-md border border-warning/40 bg-warning/10 p-3 text-xs text-text-muted flex items-start gap-2"
          data-testid="voicebox-consent"
        >
          <AlertCircle className="w-4 h-4 mt-0.5 shrink-0 text-warning" />
          <div>
            <span className="font-medium text-text">
              Voice cloning: {consent.consent ? "opted in" : "opt-in required"}
            </span>
            <p className="mt-0.5">{consent.notice}</p>
          </div>
        </div>
      )}

      {error && (
        <div className="text-error text-xs" data-testid="voicebox-error">
          {error}
        </div>
      )}
    </section>
  );
}

function LiteRtPanel() {
  const [caps, setCaps] = useState<DeviceCapabilities | null>(null);
  const [probing, setProbing] = useState(false);

  const probe = async () => {
    setProbing(true);
    try {
      setCaps(await collectCapabilities());
    } finally {
      setProbing(false);
    }
  };

  const backend = caps ? (caps.adapterAcquired ? "webgpu" : "wasm (CPU)") : null;

  return (
    <section
      className="rounded-lg border border-border bg-surface p-6 space-y-4"
      data-testid="panel-litert"
    >
      <div className="flex items-center gap-2">
        <Cpu className="w-4 h-4 text-primary" />
        <h2 className="font-semibold text-text">LiteRT.js — on-device inference</h2>
      </div>
      <p className="text-sm text-text-muted">
        Small <code className="bg-surface-alt px-1 rounded text-xs">.tflite</code> models run
        in-browser via WebGPU with a deterministic CPU/WASM fallback. Backs the Silero VAD slice in
        the{" "}
        <a href="#/voice" className="text-primary hover:underline">
          Voice cockpit
        </a>
        .
      </p>
      <div className="flex items-center gap-3">
        <button
          onClick={probe}
          disabled={probing}
          data-testid="button-litert-probe"
          className="inline-flex items-center gap-2 rounded-md bg-surface-alt px-3 py-1.5 text-xs font-medium text-text hover:bg-border transition disabled:opacity-40"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${probing ? "animate-spin" : ""}`} />
          Probe this device
        </button>
        {caps && (
          <span data-testid="litert-caps" className="text-xs flex items-center gap-1.5">
            {caps.adapterAcquired ? (
              <CheckCircle2 className="w-3.5 h-3.5 text-success" />
            ) : (
              <AlertCircle className="w-3.5 h-3.5 text-warning" />
            )}
            <span className="text-text">
              backend: <span className="font-mono">{backend}</span>
            </span>
            {caps.adapterInfo?.vendor && (
              <span className="text-text-faint">· {caps.adapterInfo.vendor}</span>
            )}
          </span>
        )}
      </div>
    </section>
  );
}

export default function Ecosystem() {
  const [view, setView] = useState<EcosystemView | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiFetch<EcosystemView>("/ecosystem")
      .then((data) => {
        setView(data);
        setError(null);
      })
      .catch((e) => setError(String(e)))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <header className="mb-8">
        <h1 className="text-xl font-semibold text-text" data-testid="text-page-title">
          Ecosystem
        </h1>
        <p className="text-sm text-text-muted mt-1">
          The AI building blocks Nexus can plug into. Statuses are honest: what works today, what
          needs configuring, what's experimental, and what's a discoverable plan.
        </p>
      </header>

      {loading && (
        <div className="text-text-muted text-sm" data-testid="text-loading">
          Loading…
        </div>
      )}
      {error && (
        <div className="text-error text-sm" data-testid="text-error">
          {error}
        </div>
      )}

      {view && (
        <>
          <div className="flex items-center gap-2 flex-wrap mb-6" data-testid="status-summary">
            {STATUS_ORDER.map((s) => (
              <span
                key={s}
                className={`text-xs rounded-full px-2.5 py-1 ${statusMeta(s).className}`}
              >
                {view.counts[s] ?? 0} {statusMeta(s).label.toLowerCase()}
              </span>
            ))}
            <span className="text-xs text-text-faint ml-auto">
              {totalEntries(view)} entries · registry v{view.version}
            </span>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-8">
            <LiteRtPanel />
            <VoiceboxPanel />
          </div>

          <div className="space-y-8">
            {view.groups.map((group) => (
              <section key={group.category} data-testid={`group-${group.category}`}>
                <h2 className="text-sm font-semibold text-text mb-3 flex items-center gap-2">
                  {group.label}
                  <span className="text-xs font-normal text-text-faint">
                    {group.entries.length}
                  </span>
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3">
                  {group.entries.map((entry) => (
                    <EntryCard key={entry.id} entry={entry} />
                  ))}
                </div>
              </section>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
