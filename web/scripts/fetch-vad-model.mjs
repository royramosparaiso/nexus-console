#!/usr/bin/env node
/**
 * fetch-vad-model.mjs — provision + integrity-check the Silero VAD model for
 * the Voice cockpit benchmark, with pinned provenance that refuses to proceed
 * on any mismatch.
 *
 * Provenance (MIT — github.com/snakers4/silero-vad):
 *   Upstream distributes ONNX and TorchScript (.jit), NOT .tflite. LiteRT.js
 *   consumes .tflite only, so we convert the verified v5.1 ONNX ourselves with
 *   the deterministic, parity-gated pipeline in tools/vad-conversion/. The
 *   resulting silero_vad.tflite is COMMITTED (it is the one binary under
 *   web/public/models/ tracked by git), so the benchmark works out of the box.
 *
 * What this script does:
 *   1. Verifies the committed silero_vad.tflite against its pinned SHA256/size;
 *      refuses (exit 1) on mismatch. This is the model the app actually loads.
 *   2. Optionally (--with-onnx) downloads the pinned source ONNX and verifies
 *      it too, writing it next to the .tflite (gitignored) for anyone
 *      reproducing the conversion via tools/vad-conversion/convert.py.
 *
 * Deterministic: same tag -> same bytes; same commit -> same .tflite.
 */
import { createHash } from "node:crypto";
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

// The committed, verified LiteRT model the app loads at runtime.
const TFLITE = {
  sha256: "99e2ca568d436f781a98f669b71bb83db248452c367144f51704a8feae4996a7",
  sizeBytes: 1248472,
  license: "MIT",
};

// The upstream source ONNX (source of truth for the conversion, not a runtime
// artifact). Pinned to the v5.1 release tag so the digest is stable over time.
const ONNX_SOURCE = {
  url: "https://github.com/snakers4/silero-vad/raw/v5.1/src/silero_vad/data/silero_vad.onnx",
  sha256: "2623a2953f6ff3d2c1e61740c6cdb7168133479b267dfef114a4a3cc5bdd788f",
  sizeBytes: 2327524,
  license: "MIT",
};

const here = dirname(fileURLToPath(import.meta.url));
const outDir = resolve(here, "..", "public", "models", "silero-vad");
const tflitePath = resolve(outDir, "silero_vad.tflite");
const onnxPath = resolve(outDir, "silero_vad.onnx");

function sha256(bytes) {
  return createHash("sha256").update(bytes).digest("hex");
}

function verifyTflite() {
  if (!existsSync(tflitePath)) {
    throw new Error(
      `committed model missing: ${tflitePath}\n` +
        "It should be tracked in git. Re-run the conversion (tools/vad-conversion/) if needed.",
    );
  }
  const bytes = readFileSync(tflitePath);
  if (bytes.length !== TFLITE.sizeBytes) {
    throw new Error(
      `tflite size mismatch: got ${bytes.length}, expected ${TFLITE.sizeBytes}. Refusing.`,
    );
  }
  const digest = sha256(bytes);
  if (digest !== TFLITE.sha256) {
    throw new Error(
      `tflite SHA256 mismatch:\n  got      ${digest}\n  expected ${TFLITE.sha256}\nRefusing.`,
    );
  }
  console.log(
    `fetch-vad-model: verified committed ${TFLITE.license} tflite ` +
      `(${bytes.length} bytes, sha256 ok) -> ${tflitePath}`,
  );
}

async function fetchOnnx() {
  console.log(`fetch-vad-model: downloading source ONNX ${ONNX_SOURCE.url}`);
  const res = await fetch(ONNX_SOURCE.url);
  if (!res.ok) {
    throw new Error(`download failed: HTTP ${res.status} ${res.statusText}`);
  }
  const bytes = Buffer.from(await res.arrayBuffer());
  if (bytes.length !== ONNX_SOURCE.sizeBytes) {
    throw new Error(
      `ONNX size mismatch: got ${bytes.length}, expected ${ONNX_SOURCE.sizeBytes}. Refusing.`,
    );
  }
  const digest = sha256(bytes);
  if (digest !== ONNX_SOURCE.sha256) {
    throw new Error(
      `ONNX SHA256 mismatch:\n  got      ${digest}\n  expected ${ONNX_SOURCE.sha256}\nRefusing.`,
    );
  }
  mkdirSync(outDir, { recursive: true });
  writeFileSync(onnxPath, bytes);
  console.log(
    `fetch-vad-model: verified ${ONNX_SOURCE.license} source ONNX ` +
      `(${bytes.length} bytes, sha256 ok) -> ${onnxPath} (gitignored)`,
  );
}

async function main() {
  verifyTflite();
  if (process.argv.includes("--with-onnx")) {
    await fetchOnnx();
    console.log(
      "\nSource ONNX provisioned. Reproduce the .tflite with:\n" +
        "  cd tools/vad-conversion && pip install -r requirements.txt\n" +
        "  python3 convert.py --src ../../web/public/models/silero-vad/silero_vad.onnx \\\n" +
        "    --out ../../web/public/models/silero-vad/silero_vad.tflite",
    );
  } else {
    console.log(
      "fetch-vad-model: model ready. (Pass --with-onnx to also fetch the " +
        "source ONNX for reproducing the conversion.)",
    );
  }
}

main().catch((err) => {
  console.error(`fetch-vad-model: ${err.message}`);
  process.exit(1);
});
