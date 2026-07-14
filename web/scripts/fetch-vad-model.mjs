#!/usr/bin/env node
/**
 * fetch-vad-model.mjs — provision the Silero VAD model for the Voice cockpit
 * benchmark, with pinned provenance and an integrity check that refuses to
 * install a mismatched file.
 *
 * Provenance (MIT — github.com/snakers4/silero-vad):
 *   The upstream project distributes ONNX and TorchScript (.jit) artifacts.
 *   It does NOT ship an official .tflite. LiteRT.js consumes .tflite only, so
 *   the ONNX we verify here is provenance/source-of-truth, not a drop-in
 *   runtime model. Until a *verified* .tflite conversion is committed, the
 *   benchmark UI honestly reports "model unavailable" rather than fabricating
 *   inference numbers (see web/src/lib/vadBenchmark.ts).
 *
 * What this script does:
 *   1. Downloads the pinned ONNX from a pinned tag URL.
 *   2. Verifies its SHA256 against the pinned digest; refuses on mismatch.
 *   3. Writes it to web/public/models/silero-vad/silero_vad.onnx (gitignored).
 *   4. Prints the conversion guidance needed to produce silero_vad.tflite.
 *
 * Re-run after bumping the pin. Deterministic: same tag -> same bytes.
 */
import { createHash } from "node:crypto";
import { mkdirSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const SOURCE = {
  // Pinned to the v5.1 release tag so the digest is stable over time.
  url: "https://github.com/snakers4/silero-vad/raw/v5.1/src/silero_vad/data/silero_vad.onnx",
  sha256: "2623a2953f6ff3d2c1e61740c6cdb7168133479b267dfef114a4a3cc5bdd788f",
  sizeBytes: 2327524,
  license: "MIT",
};

const here = dirname(fileURLToPath(import.meta.url));
const outDir = resolve(here, "..", "public", "models", "silero-vad");
const onnxPath = resolve(outDir, "silero_vad.onnx");

async function main() {
  console.log(`fetch-vad-model: downloading ${SOURCE.url}`);
  const res = await fetch(SOURCE.url);
  if (!res.ok) {
    throw new Error(`download failed: HTTP ${res.status} ${res.statusText}`);
  }
  const bytes = Buffer.from(await res.arrayBuffer());

  if (bytes.length !== SOURCE.sizeBytes) {
    throw new Error(
      `size mismatch: got ${bytes.length} bytes, expected ${SOURCE.sizeBytes}. Refusing to install.`,
    );
  }

  const digest = createHash("sha256").update(bytes).digest("hex");
  if (digest !== SOURCE.sha256) {
    throw new Error(
      `SHA256 mismatch:\n  got      ${digest}\n  expected ${SOURCE.sha256}\nRefusing to install a model that does not match the pinned digest.`,
    );
  }

  mkdirSync(outDir, { recursive: true });
  writeFileSync(onnxPath, bytes);
  console.log(
    `fetch-vad-model: verified ${SOURCE.license} ONNX (${bytes.length} bytes, sha256 ok) -> ${onnxPath}`,
  );
  console.log(
    "\nNOTE: LiteRT.js requires a .tflite model. Upstream Silero VAD ships no\n" +
      "official .tflite, so the benchmark will report 'model unavailable' until a\n" +
      "verified silero_vad.tflite is provisioned alongside this ONNX. Convert the\n" +
      "verified ONNX with a trusted onnx2tf/ai-edge-torch pipeline, then commit the\n" +
      "resulting .tflite + its own pinned SHA256 to this script.",
  );
}

main().catch((err) => {
  console.error(`fetch-vad-model: ${err.message}`);
  process.exit(1);
});
