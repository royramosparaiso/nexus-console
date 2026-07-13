/**
 * Minimal mock WebSocket server that speaks the Platform /_voice/stream
 * protocol. Used by Playwright tests to exercise useVoiceStream without
 * needing a real Kokoro backend.
 *
 * Wire protocol (must match app/api/voice.py in nexus-platform):
 *   → recv   { text, voice?, speed?, format? }         (JSON)
 *   ← send   { event: "start", voice, format }         (JSON)
 *   ← send   Buffer (raw PCM 16-bit LE @ 24kHz mono)   (repeated)
 *   ← send   { event: "end", chunks, bytes }           (JSON)
 *
 * Errors: { event: "error"|"rejected"|"unavailable", detail }.
 * Client can cancel with { event: "cancel" }.
 */

import type { AddressInfo } from "node:net";
import { WebSocketServer, type WebSocket } from "ws";

export type Scenario =
  | "happy"          // start + 3 chunks + end
  | "many-chunks"    // start + 10 chunks + end (larger duration)
  | "reject"         // { event: "rejected" } immediately
  | "unavailable"    // start + { event: "unavailable" }
  | "cancellable";   // long stream, expects client cancel

export interface MockWsHandle {
  url: string;
  port: number;
  close: () => Promise<void>;
  /** Frames observed on the socket, useful for assertions. */
  received: string[];
}

/** Deterministic PCM sine tone \-\ two 24kHz mono int16 frames. */
export function makePcmChunk(sampleCount: number, freqHz = 440): Buffer {
  const buf = Buffer.alloc(sampleCount * 2);
  for (let i = 0; i < sampleCount; i++) {
    const s = Math.round(Math.sin((2 * Math.PI * freqHz * i) / 24_000) * 8_000);
    buf.writeInt16LE(s, i * 2);
  }
  return buf;
}

export async function startMockWs(scenario: Scenario): Promise<MockWsHandle> {
  const wss = new WebSocketServer({ port: 0, host: "127.0.0.1" });

  const received: string[] = [];

  const runHappy = async (ws: WebSocket, chunkCount: number) => {
    ws.send(JSON.stringify({ event: "start", voice: "af_bella", format: "pcm" }));
    let totalBytes = 0;
    for (let i = 0; i < chunkCount; i++) {
      const chunk = makePcmChunk(2400); // 100 ms @ 24kHz
      ws.send(chunk);
      totalBytes += chunk.byteLength;
      // Small delay so the client actually observes streaming.
      await new Promise((r) => setTimeout(r, 15));
    }
    ws.send(
      JSON.stringify({ event: "end", chunks: chunkCount, bytes: totalBytes }),
    );
    ws.close(1000);
  };

  wss.on("connection", (ws) => {
    ws.on("message", async (raw) => {
      const asString = raw.toString();
      received.push(asString);
      let payload: Record<string, unknown> = {};
      try {
        payload = JSON.parse(asString);
      } catch {
        return;
      }

      if (payload.event === "cancel") {
        // Client-initiated cancel: just close.
        try {
          ws.close(1000);
        } catch {
          // ignore
        }
        return;
      }

      switch (scenario) {
        case "reject":
          ws.send(JSON.stringify({ event: "rejected", detail: "text is required" }));
          ws.close(1003);
          return;
        case "unavailable":
          ws.send(JSON.stringify({ event: "start", voice: "af_bella", format: "pcm" }));
          ws.send(JSON.stringify({ event: "unavailable" }));
          ws.close(1011);
          return;
        case "happy":
          await runHappy(ws, 3);
          return;
        case "many-chunks":
          await runHappy(ws, 10);
          return;
        case "cancellable":
          // Send start, then keep sending chunks slowly until cancelled or closed.
          ws.send(
            JSON.stringify({ event: "start", voice: "af_bella", format: "pcm" }),
          );
          let seq = 0;
          const timer = setInterval(() => {
            if (ws.readyState !== ws.OPEN) {
              clearInterval(timer);
              return;
            }
            ws.send(makePcmChunk(2400));
            seq += 1;
            if (seq > 200) clearInterval(timer);
          }, 30);
          ws.on("close", () => clearInterval(timer));
          return;
      }
    });
  });

  await new Promise<void>((resolve) => wss.on("listening", () => resolve()));
  const addr = wss.address() as AddressInfo;
  const port = addr.port;

  return {
    url: `ws://127.0.0.1:${port}`,
    port,
    received,
    close: () =>
      new Promise((resolve) => {
        for (const c of wss.clients) {
          try {
            c.terminate();
          } catch {
            // ignore
          }
        }
        wss.close(() => resolve());
      }),
  };
}
