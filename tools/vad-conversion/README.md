# Silero VAD — deterministic ONNX → LiteRT/TFLite conversion

This directory holds the reproducible pipeline that produced the committed
LiteRT model at `web/public/models/silero-vad/silero_vad.tflite`.

Upstream Silero VAD ships **ONNX/JIT only — no official `.tflite`**. LiteRT.js
consumes `.tflite`, so we convert the pinned v5.1 ONNX ourselves, and gate the
output on numerical parity vs ONNX Runtime. The script refuses to emit a model
if the source hash is wrong or if parity exceeds tolerance.

## Provenance

| | value |
| --- | --- |
| Source | Silero VAD v5.1 — `github.com/snakers4/silero-vad` (MIT) |
| Source file | `src/silero_vad/data/silero_vad.onnx` @ tag `v5.1` |
| Source SHA256 | `2623a2953f6ff3d2c1e61740c6cdb7168133479b267dfef114a4a3cc5bdd788f` |
| Source size | 2,327,524 bytes |
| Output SHA256 | `99e2ca568d436f781a98f669b71bb83db248452c367144f51704a8feae4996a7` |
| Output size | 1,248,472 bytes |
| Output license | MIT (unchanged from source) |

## Toolchain

Python 3.12 with the pins in `requirements.txt`. Key converters:
`onnx==1.17.0`, `onnxslim==0.1.94`, `onnx2tf==1.28.0`, `tensorflow==2.20.0`,
`tf-keras==2.20.1`, `onnxruntime==1.27.0` (parity reference),
`ai-edge-litert==2.1.6` (parity interpreter).

## Reproduce

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Provision the verified source ONNX (also used by the web app):
node ../../web/scripts/fetch-vad-model.mjs
#   -> web/public/models/silero-vad/silero_vad.onnx (gitignored)

python3 convert.py \
  --src ../../web/public/models/silero-vad/silero_vad.onnx \
  --out ../../web/public/models/silero-vad/silero_vad.tflite \
  --workdir /tmp/silero_convert
```

The script prints per-fixture parity and the output SHA256, and exits non-zero
if the source hash or parity gate fails.

## Pipeline (`convert.py`)

1. **Verify** source ONNX SHA256 == the pinned v5.1 hash.
2. **Static 16 kHz**: pin `sr = 16000` as a constant and fix input shapes.
3. **Constant-fold** (`onnxslim`) to eliminate the now-dead `sr`-keyed `If`.
4. **Decoder in rank-2**: decompose the single-timestep LSTM into explicit cell
   math (Gemm/Sigmoid/Tanh/Mul) carrying a 2D `[2,128]` state. onnx2tf's
   NCHW→NWC pass never transposes rank-2 tensors, so the decoder survives
   conversion intact.
5. **Split STFT conv**: the 258-channel STFT `Conv` is split into two convs
   (129 real + 129 imag) to remove the channel-axis `Slice` that onnx2tf cannot
   translate through its transpose.
6. **onnx2tf** → float32 TFLite (`-b 1`, fixed batch).
7. **Parity**: frame-by-frame vs ONNX Runtime on deterministic fixtures.

## TFLite I/O contract (static, 16 kHz only)

| dir | name | dtype | shape | meaning |
| --- | --- | --- | --- | --- |
| in | `input` | f32 | `[1, 512]` | one 512-sample frame |
| in | `state` | f32 | `[2, 128]` | LSTM state (h;c), zeros at start |
| out | `Identity` | f32 | `[1, 1]` | speech probability |
| out | `Identity_1` | f32 | `[2, 128]` | next state (feed back next frame) |

The external state is 2D `[2,128]` (row 0 = h, row 1 = c); the browser runtime
initialises it to zeros and carries `Identity_1` into the next frame's `state`.

## Parity (committed model vs ONNX Runtime)

Tolerances (conversion FAILS if exceeded): `max|Δprob| ≤ 1e-3`,
`max|Δstate| ≤ 1e-2`, decision disagreements at threshold 0.5 must be `0`.

| fixture | max\|Δprob\| |
| --- | --- |
| silence | 6.3e-8 |
| impulse | 6.3e-8 |
| sine 440 Hz | 2.5e-6 |
| seeded noise | 6.3e-8 |
| synthetic speech | 6.6e-7 |

Overall: `max|Δprob| = 2.5e-6`, `max|Δstate| = 8.3e-5`,
**0 / 80 decision disagreements**.
