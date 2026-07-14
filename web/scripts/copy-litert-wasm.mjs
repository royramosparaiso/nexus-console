#!/usr/bin/env node
/**
 * Copy the LiteRT.js WASM runtime artifacts out of the installed
 * @litertjs/core package into web/public/wasm/litertjs/ so Vite serves them
 * from a stable public URL (/wasm/litertjs/).
 *
 * literert.ts calls loadLiteRt('/wasm/litertjs/'); the loader then feature-
 * detects the browser and fetches the matching *_internal.js + .wasm pair, so
 * all four variants (default / compat / threaded / jspi) must be present.
 *
 * Deterministic: same inputs -> same bytes. Committed artifacts are refreshed
 * by re-running `npm run copy:litert-wasm` after bumping @litertjs/core.
 */
import { cpSync, mkdirSync, readdirSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const src = resolve(here, "..", "node_modules", "@litertjs", "core", "wasm");
const dst = resolve(here, "..", "public", "wasm", "litertjs");

try {
  const files = readdirSync(src);
  mkdirSync(dst, { recursive: true });
  for (const f of files) {
    cpSync(resolve(src, f), resolve(dst, f));
  }
  console.log(`copied ${files.length} LiteRT WASM artifacts -> public/wasm/litertjs/`);
} catch (err) {
  // Don't hard-fail install if the package isn't present yet (e.g. CI that
  // never installs @litertjs/core). The committed artifacts remain in place.
  console.warn(`copy-litert-wasm: skipped (${err.message})`);
}
