/**
 * Voice — cockpit for exercising Platform's /_voice/stream endpoint.
 *
 * Lets the operator pick an instance, type text, choose a voice, and hear
 * the streamed audio in the browser. Meant for QA / demo of the voice
 * layer that Jarvis will consume programmatically.
 */

import { useEffect, useMemo, useState } from "react";
import { AlertCircle, Mic, Square } from "lucide-react";

import { apiFetch } from "../lib/api";
import {
  useVoiceStream,
  type SynthesizeRequest,
} from "../hooks/useVoiceStream";

interface Instance {
  id: string;
  name: string;
  status: string;
  endpoint: string | null;
}

// Kokoro-FastAPI ships with several English + multilingual voices. We
// surface a small curated set; the endpoint accepts any Kokoro voice id.
const VOICE_OPTIONS: { value: string; label: string }[] = [
  { value: "af_bella", label: "Bella (English, warm)" },
  { value: "af_heart", label: "Heart (English, calm)" },
  { value: "af_sky", label: "Sky (English, bright)" },
  { value: "am_adam", label: "Adam (English, male)" },
  { value: "em_alex", label: "Alex (Spanish)" },
];

function endpointToWebSocketUrl(endpoint: string): string {
  // Platform endpoint is http://host:port — /_voice/stream is a WS route.
  const wsBase = endpoint.replace(/^http/i, "ws").replace(/\/$/, "");
  return `${wsBase}/_voice/stream`;
}

export default function Voice() {
  const [instances, setInstances] = useState<Instance[]>([]);
  const [selected, setSelected] = useState<string>("");
  const [text, setText] = useState<string>(
    "Nexus voice layer is streaming this response in real time.",
  );
  const [voice, setVoice] = useState<string>("af_bella");
  const [speed, setSpeed] = useState<number>(1.0);
  const [listError, setListError] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const rows = await apiFetch<Instance[]>("/instances");
        const running = rows.filter(
          (r) => r.status === "running" && r.endpoint,
        );
        setInstances(running);
        if (running.length && !selected) setSelected(running[0].id);
      } catch (e) {
        setListError(e instanceof Error ? e.message : "failed to load");
      }
    })();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const selectedInstance = useMemo(
    () => instances.find((i) => i.id === selected),
    [instances, selected],
  );

  const wsUrl = selectedInstance?.endpoint
    ? endpointToWebSocketUrl(selectedInstance.endpoint)
    : "";

  const { state, synthesize, cancel } = useVoiceStream({ endpoint: wsUrl });

  const canSynthesize =
    !!wsUrl &&
    text.trim().length > 0 &&
    state.status !== "connecting" &&
    state.status !== "streaming";

  const onPlay = () => {
    const req: SynthesizeRequest = { text: text.trim(), voice, speed };
    synthesize(req);
  };

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <header className="mb-8">
        <h1
          className="text-xl font-semibold text-text"
          data-testid="text-page-title"
        >
          Voice cockpit
        </h1>
        <p className="text-sm text-text-muted mt-1">
          Stream text-to-speech from a running Platform instance via
          <span className="mx-1 font-mono">/_voice/stream</span>.
        </p>
      </header>

      {listError && (
        <div
          className="mb-6 rounded-md border border-error/40 bg-error/10 p-3 text-sm text-error flex items-start gap-2"
          data-testid="error-instance-list"
        >
          <AlertCircle className="w-4 h-4 mt-0.5 shrink-0" />
          <span>Failed to load instances: {listError}</span>
        </div>
      )}

      {!listError && instances.length === 0 && (
        <div
          className="mb-6 rounded-md border border-dashed border-border p-6 text-center text-sm text-text-muted"
          data-testid="empty-instances"
        >
          No running instance with a voice endpoint yet. Complete a wizard
          bootstrap first — voice becomes available once Platform is up.
        </div>
      )}

      {instances.length > 0 && (
        <section className="space-y-5 rounded-lg border border-border bg-surface p-6">
          <label className="block">
            <span className="block text-xs font-medium text-text-muted mb-1.5">
              Instance
            </span>
            <select
              value={selected}
              onChange={(e) => setSelected(e.target.value)}
              data-testid="select-instance"
              className="w-full rounded-md border border-border bg-bg px-3 py-2 text-sm text-text"
            >
              {instances.map((inst) => (
                <option key={inst.id} value={inst.id}>
                  {inst.name} — {inst.endpoint}
                </option>
              ))}
            </select>
          </label>

          <div className="grid grid-cols-2 gap-4">
            <label className="block">
              <span className="block text-xs font-medium text-text-muted mb-1.5">
                Voice
              </span>
              <select
                value={voice}
                onChange={(e) => setVoice(e.target.value)}
                data-testid="select-voice"
                className="w-full rounded-md border border-border bg-bg px-3 py-2 text-sm text-text"
              >
                {VOICE_OPTIONS.map((v) => (
                  <option key={v.value} value={v.value}>
                    {v.label}
                  </option>
                ))}
              </select>
            </label>

            <label className="block">
              <span className="block text-xs font-medium text-text-muted mb-1.5">
                Speed ({speed.toFixed(2)}×)
              </span>
              <input
                type="range"
                min={0.5}
                max={1.5}
                step={0.05}
                value={speed}
                onChange={(e) => setSpeed(parseFloat(e.target.value))}
                data-testid="input-speed"
                className="w-full mt-2"
              />
            </label>
          </div>

          <label className="block">
            <span className="block text-xs font-medium text-text-muted mb-1.5">
              Text
            </span>
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              rows={5}
              maxLength={4000}
              data-testid="input-text"
              className="w-full rounded-md border border-border bg-bg px-3 py-2 text-sm text-text font-mono resize-none"
            />
            <span className="mt-1 block text-[11px] text-text-faint">
              {text.length}/4000 characters
            </span>
          </label>

          <div className="flex items-center gap-3">
            {state.status === "streaming" || state.status === "connecting" ? (
              <button
                onClick={cancel}
                data-testid="button-stop"
                className="inline-flex items-center gap-2 rounded-md bg-error px-4 py-2 text-sm font-medium text-white hover:opacity-90 transition"
              >
                <Square className="w-4 h-4" />
                Stop
              </button>
            ) : (
              <button
                onClick={onPlay}
                disabled={!canSynthesize}
                data-testid="button-play"
                className="inline-flex items-center gap-2 rounded-md bg-primary px-4 py-2 text-sm font-medium text-white hover:bg-primary-hover transition disabled:opacity-40 disabled:cursor-not-allowed"
              >
                <Mic className="w-4 h-4" />
                Synthesize
              </button>
            )}

            <StatusPill state={state.status} />

            <div
              className="ml-auto text-[11px] font-mono text-text-faint"
              data-testid="text-stream-stats"
            >
              {state.chunksReceived} chunks · {(state.bytesReceived / 1024).toFixed(1)} kB
            </div>
          </div>

          {state.error && (
            <div
              className="rounded-md border border-error/40 bg-error/10 p-3 text-sm text-error flex items-start gap-2"
              data-testid="text-voice-error"
            >
              <AlertCircle className="w-4 h-4 mt-0.5 shrink-0" />
              <span>{state.error}</span>
            </div>
          )}
        </section>
      )}
    </div>
  );
}

function StatusPill({ state }: { state: string }) {
  const labels: Record<string, string> = {
    idle: "Idle",
    connecting: "Connecting…",
    streaming: "Streaming",
    playing: "Playing",
    done: "Done",
    error: "Error",
  };
  const colors: Record<string, string> = {
    idle: "bg-surface-alt text-text-muted",
    connecting: "bg-primary/15 text-primary",
    streaming: "bg-primary/15 text-primary animate-pulse",
    playing: "bg-primary/15 text-primary",
    done: "bg-success/15 text-success",
    error: "bg-error/15 text-error",
  };
  return (
    <span
      data-testid={`status-${state}`}
      className={`text-[11px] font-medium uppercase tracking-wider rounded-full px-2.5 py-1 ${colors[state] ?? colors.idle}`}
    >
      {labels[state] ?? state}
    </span>
  );
}
