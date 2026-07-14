---
id: local_inference
name: local_inference
artifact_type: skill
lifecycle: ops
category: operations
phase: null
step: null
domain: operations
rollout_stage: 1-foundation
autonomy: human-assisted
maturity: 1
verticals: [any]
role: null
mode: null
depends_on: []
produces: structured_json
tools: [litertjs_runtime]
tags: [inference, webgpu, litertjs, vad, browser, skill]
gate: false
optional: false
---

# local_inference

## Identity

```yaml
skills:
  - name: local_inference
    kind: skill
    produces: structured_json
    domain: operations
```

## Purpose

Reusable capability: run small `.tflite` models **inside the browser** via
LiteRT.js (`@litertjs/core`) instead of round-tripping to a remote endpoint.
Backed by `web/src/lib/literert.ts`. First concrete use is a Silero VAD PoC in
the Voice cockpit (voice-activity detection before streaming audio to STT);
the same runtime also fits wake-word, denoising, and local embeddings.

## Tools

| Tool | Backing | Provider | Key? |
| --- | --- | --- | --- |
| `litertjs_runtime` | LiteRT.js WASM (`@litertjs/core`) | google-ai-edge | no |

## Inputs

A registered model reference (`agent_local_model`: `model_url` + `sha256` +
`license`) plus a typed input tensor (e.g. an audio frame as `Float32Array`).

## Outputs

Model output tensor(s) as `structured_json`, alongside inference metadata:
selected backend (`webgpu` | `wasm`), runtime init / compile timings, and
median / p95 latency measured with `performance.now()`.

## Wiring

Callable by any agent whose deployed instance has `local_inference=true`. Not
runnable on its own. Model access is gated by the `agent_local_model` registry
so an agent can only load `.tflite` URLs explicitly whitelisted for it.

## Safety limits

- Backends: WebGPU when `navigator.gpu` is present and the adapter/device can
  be acquired; deterministic fallback to the WASM (CPU/XNNPACK) backend.
- The sandbox iframe forbids `localStorage` / `sessionStorage` / `indexedDB` /
  cookies — nothing is persisted client-side. WASM + `.tflite` are re-fetched
  per session and rely on the HTTP cache (`Cache-Control: immutable`) only.
- Every model carries provenance (`sha256`, `license`) and is verified before
  it is served.
- No LLMs in-browser yet — `@litertjs/lm` is not published. Scope is limited to
  small perception models (VAD, wake-word, embeddings, light vision).

## Extension notes

- Prefer models `< 10 MB gzip`; larger models are impractical without client
  persistence.
- Report the selected backend + timings back to the operator so a device that
  silently degrades from WebGPU to CPU is visible, not hidden.
