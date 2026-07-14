# Silero VAD — committed LiteRT/TFLite model

`silero_vad.tflite` is a numerically-verified conversion of the upstream
Silero VAD v5.1 ONNX. It is the only binary under `web/public/models/` that is
committed to git (see the repo `.gitignore`); everything else here is
provisioned at setup time by `web/scripts/fetch-vad-model.mjs`.

## Provenance

| | value |
| --- | --- |
| Model | Silero VAD v5.1 |
| Upstream | `github.com/snakers4/silero-vad` |
| License | **MIT** (unchanged from upstream) |
| Source ONNX SHA256 | `2623a2953f6ff3d2c1e61740c6cdb7168133479b267dfef114a4a3cc5bdd788f` (2,327,524 bytes) |
| This file SHA256 | `99e2ca568d436f781a98f669b71bb83db248452c367144f51704a8feae4996a7` |
| This file size | 1,248,472 bytes |
| Converted by | `tools/vad-conversion/convert.py` (onnx 1.17.0 · onnxslim 0.1.94 · onnx2tf 1.28.0 · tensorflow 2.20.0) |

The exact reproduction steps, toolchain pins, and parity report live in
[`tools/vad-conversion/README.md`](../../../../tools/vad-conversion/README.md).
`web/scripts/fetch-vad-model.mjs` re-verifies this file's SHA256 on setup and
refuses to proceed on mismatch.

## I/O contract (static, 16 kHz only)

| dir | name | dtype | shape | meaning |
| --- | --- | --- | --- | --- |
| in | `input` | f32 | `[1, 512]` | one 512-sample frame |
| in | `state` | f32 | `[2, 128]` | LSTM state (h;c), zeros at start |
| out | `Identity` | f32 | `[1, 1]` | speech probability |
| out | `Identity_1` | f32 | `[2, 128]` | next state (feed into next frame) |

State is 2D `[2,128]` (row 0 = h, row 1 = c). Initialise to zeros; carry
`Identity_1` into the next frame's `state`. Sequential frames share state — do
not reset between frames of the same stream.

## Registering with the backend

The Platform gates which `.tflite` an agent may fetch via the
`agent_local_model` registry (`console/app/models/db.py`). There is **no**
startup seed — the table is intentionally empty until a row is inserted, so no
surprising DB side effects occur on migration. Register this model by inserting
one row (soft-referencing the `voice_vad` catalogue card):

```python
from app.models.db import AgentLocalModelRow

session.add(AgentLocalModelRow(
    template_id="voice_vad",
    model_url="/models/silero-vad/silero_vad.tflite",
    sha256="99e2ca568d436f781a98f669b71bb83db248452c367144f51704a8feae4996a7",
    size_bytes=1248472,
    license="MIT",
))
```

The `(template_id, model_url)` pair is unique; `sha256` must be 64 hex chars and
`size_bytes` non-negative (enforced by table constraints).

## Parity vs ONNX Runtime

`max|Δprob| = 2.5e-6`, `max|Δstate| = 8.3e-5`, **0 / 80 decision
disagreements** at threshold 0.5 across silence / impulse / sine / seeded
noise / synthetic-speech fixtures. Gates: `Δprob ≤ 1e-3`, `Δstate ≤ 1e-2`,
`0` disagreements.
