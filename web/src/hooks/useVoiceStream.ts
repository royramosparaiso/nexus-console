/**
 * useVoiceStream — WebSocket client for Platform /_voice/stream.
 *
 * The server streams raw PCM audio (24kHz mono int16 by default). We
 * decode each binary frame to Float32 samples and schedule them on a
 * shared AudioContext so playback is gapless while chunks keep arriving.
 *
 * Wire protocol (matches app/api/voice.py in nexus-platform):
 *   → send    { text, voice?, speed?, format? }
 *   ← recv    { event: "start" }               (JSON)
 *   ← recv    Blob (binary PCM chunk)          (repeated N times)
 *   ← recv    { event: "end", chunks, bytes }  (JSON)
 *
 * Errors on the server side arrive as:
 *   ← recv    { event: "error" | "rejected" | "unavailable", detail }
 *
 * The client can cancel mid-stream by sending { event: "cancel" }.
 */

import { useCallback, useEffect, useRef, useState } from "react";

// Kokoro-FastAPI defaults, exposed for future overrides.
const SAMPLE_RATE = 24_000;
const CHANNELS = 1;

export type VoiceStatus =
  | "idle"
  | "connecting"
  | "streaming"
  | "playing"
  | "done"
  | "error";

export interface UseVoiceStreamOptions {
  /** Full WS URL to /_voice/stream on the target Platform. */
  endpoint: string;
}

export interface SynthesizeRequest {
  text: string;
  voice?: string;
  speed?: number;
  format?: string;
}

export interface VoiceStreamState {
  status: VoiceStatus;
  bytesReceived: number;
  chunksReceived: number;
  error: string | null;
}

const INITIAL_STATE: VoiceStreamState = {
  status: "idle",
  bytesReceived: 0,
  chunksReceived: 0,
  error: null,
};

/** Convert int16 little-endian bytes into Float32 samples in [-1, 1]. */
function pcm16ToFloat32(bytes: ArrayBuffer): Float32Array<ArrayBuffer> {
  const view = new DataView(bytes);
  const sampleCount = bytes.byteLength / 2;
  const out = new Float32Array(sampleCount);
  for (let i = 0; i < sampleCount; i++) {
    const s = view.getInt16(i * 2, true);
    out[i] = s < 0 ? s / 0x8000 : s / 0x7fff;
  }
  return out;
}

export function useVoiceStream({ endpoint }: UseVoiceStreamOptions) {
  const [state, setState] = useState<VoiceStreamState>(INITIAL_STATE);
  const wsRef = useRef<WebSocket | null>(null);
  const ctxRef = useRef<AudioContext | null>(null);
  // Next scheduled start time inside the AudioContext clock.
  const nextStartRef = useRef<number>(0);

  const cleanup = useCallback((closeWs: boolean) => {
    if (closeWs && wsRef.current) {
      try {
        wsRef.current.close();
      } catch {
        // ignore
      }
    }
    wsRef.current = null;
    nextStartRef.current = 0;
  }, []);

  useEffect(() => {
    return () => {
      cleanup(true);
      if (ctxRef.current) {
        void ctxRef.current.close();
        ctxRef.current = null;
      }
    };
  }, [cleanup]);

  const ensureAudioContext = useCallback((): AudioContext => {
    if (!ctxRef.current || ctxRef.current.state === "closed") {
      const Ctor: typeof AudioContext =
        window.AudioContext ??
        (window as unknown as { webkitAudioContext: typeof AudioContext })
          .webkitAudioContext;
      ctxRef.current = new Ctor({ sampleRate: SAMPLE_RATE });
      nextStartRef.current = 0;
    }
    // Resume — required in Chromium after user gesture.
    if (ctxRef.current.state === "suspended") {
      void ctxRef.current.resume();
    }
    return ctxRef.current;
  }, []);

  const scheduleChunk = useCallback((bytes: ArrayBuffer) => {
    const ctx = ensureAudioContext();
    const samples = pcm16ToFloat32(bytes);
    if (samples.length === 0) return;

    const buffer = ctx.createBuffer(CHANNELS, samples.length, SAMPLE_RATE);
    buffer.copyToChannel(samples, 0);

    const source = ctx.createBufferSource();
    source.buffer = buffer;
    source.connect(ctx.destination);

    const startAt = Math.max(ctx.currentTime, nextStartRef.current);
    source.start(startAt);
    nextStartRef.current = startAt + buffer.duration;
  }, [ensureAudioContext]);

  const synthesize = useCallback(
    (req: SynthesizeRequest) => {
      cleanup(true);
      setState({ ...INITIAL_STATE, status: "connecting" });
      // Prime the AudioContext synchronously to survive Chromium's autoplay
      // policy — this call must happen inside a user gesture.
      ensureAudioContext();

      const ws = new WebSocket(endpoint);
      ws.binaryType = "arraybuffer";
      wsRef.current = ws;

      ws.addEventListener("open", () => {
        ws.send(JSON.stringify(req));
      });

      ws.addEventListener("message", (evt) => {
        if (typeof evt.data === "string") {
          let payload: { event?: string; detail?: string };
          try {
            payload = JSON.parse(evt.data);
          } catch {
            return;
          }
          if (payload.event === "start") {
            setState((s) => ({ ...s, status: "streaming" }));
          } else if (payload.event === "end") {
            setState((s) => ({ ...s, status: "playing" }));
            // Playback keeps running for scheduled chunks; flip to `done`
            // once the last scheduled chunk has finished.
            const ctx = ctxRef.current;
            const untilDone = ctx
              ? Math.max(0, nextStartRef.current - ctx.currentTime)
              : 0;
            window.setTimeout(() => {
              setState((s) => ({ ...s, status: "done" }));
            }, Math.ceil(untilDone * 1000) + 50);
          } else if (
            payload.event === "error" ||
            payload.event === "rejected" ||
            payload.event === "unavailable"
          ) {
            setState((s) => ({
              ...s,
              status: "error",
              error: payload.detail || payload.event || "unknown error",
            }));
          }
          return;
        }

        // Binary chunk
        const buf = evt.data as ArrayBuffer;
        scheduleChunk(buf);
        setState((s) => ({
          ...s,
          bytesReceived: s.bytesReceived + buf.byteLength,
          chunksReceived: s.chunksReceived + 1,
        }));
      });

      ws.addEventListener("error", () => {
        setState((s) =>
          s.status === "error"
            ? s
            : { ...s, status: "error", error: "websocket transport error" },
        );
      });

      ws.addEventListener("close", (evt) => {
        setState((s) => {
          if (s.status === "streaming" || s.status === "connecting") {
            return {
              ...s,
              status: "error",
              error: `connection closed (${evt.code})`,
            };
          }
          return s;
        });
      });
    },
    [cleanup, endpoint, ensureAudioContext, scheduleChunk],
  );

  const cancel = useCallback(() => {
    const ws = wsRef.current;
    if (ws && ws.readyState === WebSocket.OPEN) {
      try {
        ws.send(JSON.stringify({ event: "cancel" }));
      } catch {
        // ignore
      }
    }
    cleanup(true);
    setState((s) => ({ ...s, status: "idle" }));
  }, [cleanup]);

  return { state, synthesize, cancel };
}
