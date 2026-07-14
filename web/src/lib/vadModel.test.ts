/**
 * Integrity test for the committed Silero VAD LiteRT model. This runs in the
 * vitest (node) environment and guards the actual binary at
 * web/public/models/silero-vad/silero_vad.tflite: its SHA256 and size must
 * match the pins in vadBenchmark.ts (and fetch-vad-model.mjs). If the model is
 * ever regenerated, this fails until the pins are updated in lock-step.
 */
import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { describe, expect, it } from "vitest";

import { SILERO_VAD } from "./vadBenchmark";

const here = dirname(fileURLToPath(import.meta.url));
const modelPath = resolve(here, "..", "..", "public", "models", "silero-vad", "silero_vad.tflite");

describe("committed silero_vad.tflite", () => {
  it("matches the pinned SHA256 and size", () => {
    const bytes = readFileSync(modelPath);
    expect(bytes.length).toBe(1248472);
    const digest = createHash("sha256").update(bytes).digest("hex");
    expect(digest).toBe(SILERO_VAD.sha256);
  });

  it("is a valid TFLite flatbuffer (TFL3 magic at offset 4)", () => {
    const bytes = readFileSync(modelPath);
    // TFLite files carry the file identifier "TFL3" at bytes 4..8.
    expect(bytes.subarray(4, 8).toString("ascii")).toBe("TFL3");
  });
});
