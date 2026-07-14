#!/usr/bin/env python3
"""Deterministic Silero VAD v5.1 ONNX -> LiteRT/TFLite conversion.

Pipeline (all numerics verified against ONNX Runtime at the end; the script
exits non-zero if parity exceeds the tolerances below):

  1. Verify the source ONNX SHA256 == the pinned Silero v5.1 hash.
  2. Pin `sr` = 16000 as a constant and fix input shapes -> static 16 kHz graph.
  3. onnxslim constant-fold to eliminate the sr-keyed `If` control flow.
  4. Rewrite the decoder in rank-2 tensors: decompose the single-timestep LSTM
     into explicit cell math (Gemm/Sigmoid/Tanh/Mul) and carry a 2D [2,128]
     state. onnx2tf's NCHW->NWC pass never transposes rank-2 tensors, so the
     decoder survives conversion intact.
  5. Split the 258-channel STFT Conv into two convs (129 real + 129 imag) to
     remove the channel-axis Slice that onnx2tf cannot translate.
  6. onnx2tf -> float32 TFLite.
  7. Frame-by-frame parity vs ONNX Runtime on deterministic fixtures.

TFLite I/O contract (static, 16 kHz only):
  inputs : input  f32 [1, 512]   (one 512-sample frame)
           state  f32 [2, 128]   (recurrent LSTM state h;c, zeros at start)
  outputs: Identity   f32 [1, 1]   speech probability
           Identity_1 f32 [2, 128] next state
"""
import argparse
import hashlib
import subprocess
import sys
from pathlib import Path

import numpy as np
import onnx
import onnxruntime as ort
from onnx import helper, numpy_helper

PINNED_SHA256 = "2623a2953f6ff3d2c1e61740c6cdb7168133479b267dfef114a4a3cc5bdd788f"
SAMPLE_RATE = 16000
FRAME = 512
HIDDEN = 128
# Parity gates (max over all fixtures/frames). Conversion FAILS if exceeded.
TOL_PROB = 1e-3
TOL_STATE = 1e-2


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def set_shape(vi, dims):
    del vi.type.tensor_type.shape.dim[:]
    for d in dims:
        vi.type.tensor_type.shape.dim.add().dim_value = d


def topo_sort(graph):
    avail = {i.name for i in graph.initializer} | {i.name for i in graph.input} | {""}
    pending = list(graph.node)
    ordered = []
    while pending:
        rest = []
        progressed = False
        for n in pending:
            if all(i in avail for i in n.input):
                ordered.append(n)
                avail.update(n.output)
                progressed = True
            else:
                rest.append(n)
        pending = rest
        if not progressed:
            raise RuntimeError(f"cycle/unresolved inputs near {[x.name for x in pending][:3]}")
    del graph.node[:]
    graph.node.extend(ordered)


def step_static(src: Path, out: Path):
    m = onnx.load(str(src))
    g = m.graph
    sr = [i for i in g.input if i.name == "sr"]
    if sr:
        g.input.remove(sr[0])
        g.initializer.append(numpy_helper.from_array(np.array(SAMPLE_RATE, dtype=np.int64), name="sr"))
    for vi in g.input:
        if vi.name == "input":
            set_shape(vi, [1, FRAME])
        elif vi.name == "state":
            set_shape(vi, [2, 1, HIDDEN])
    onnx.save(m, str(out))


def step_fold(src: Path, out: Path):
    # onnxslim eliminates the (now-constant) sr-keyed If control flow.
    subprocess.run(["onnxslim", str(src), str(out)], check=True, capture_output=True)


def step_decoder_2d(src: Path, out: Path):
    m = onnx.load(str(src))
    g = m.graph
    inits = {i.name: i for i in g.initializer}
    prod = {o: n for n in g.node for o in n.output}
    cons = {}
    for n in g.node:
        for i in n.input:
            cons.setdefault(i, []).append(n)

    lstm = [n for n in g.node if n.op_type == "LSTM"][0]
    enc2d = prod[lstm.input[0]].input[0]                 # [1,128] native Squeeze output = Xt
    W = numpy_helper.to_array(inits[lstm.input[1]])[0]   # [512,128]
    R = numpy_helper.to_array(inits[lstm.input[2]])[0]   # [512,128]
    B = numpy_helper.to_array(inits[lstm.input[3]])       # [1,1024]
    sq_h = cons[lstm.output[1]][0]
    Th = sq_h.output[0]                                   # classifier consumes Th (= Ht)
    sq_c = cons[lstm.output[2]][0]
    old_concat = prod["stateN"]
    uns_h = prod[old_concat.input[0]]
    uns_c = prod[old_concat.input[1]]
    uns_h0 = prod[lstm.input[5]]
    uns_c0 = prod[lstm.input[6]]
    gathers = [n for n in g.node if n.op_type == "Gather" and "state" in n.input]

    WT = W.T.copy().astype(np.float32)   # [128,512]
    RT = R.T.copy().astype(np.float32)
    bias = (B[0][:512] + B[0][512:1024]).astype(np.float32)

    P = "cell/"
    g.initializer.extend([
        numpy_helper.from_array(WT, P + "WT"),
        numpy_helper.from_array(RT, P + "RT"),
        numpy_helper.from_array(bias, P + "bias"),
        numpy_helper.from_array(np.array([HIDDEN] * 4, dtype=np.int64), P + "split4"),
        numpy_helper.from_array(np.array([0], dtype=np.int64), P + "s0"),
        numpy_helper.from_array(np.array([1], dtype=np.int64), P + "s1"),
        numpy_helper.from_array(np.array([2], dtype=np.int64), P + "s2"),
        numpy_helper.from_array(np.array([0], dtype=np.int64), P + "axst"),
    ])
    new_nodes = []

    def nd(op, ins, outs, **kw):
        new_nodes.append(helper.make_node(op, ins, outs, name=P + outs[0].split("/")[-1], **kw))

    nd("Slice", ["state", P + "s0", P + "s1", P + "axst"], [P + "H0"])
    nd("Slice", ["state", P + "s1", P + "s2", P + "axst"], [P + "C0"])
    nd("Gemm", [enc2d, P + "WT", P + "bias"], [P + "gx"])
    nd("Gemm", [P + "H0", P + "RT"], [P + "gh"])
    nd("Add", [P + "gx", P + "gh"], [P + "gates"])
    nd("Split", [P + "gates", P + "split4"], [P + "gi", P + "go", P + "gf", P + "gc"], axis=1)
    nd("Sigmoid", [P + "gi"], [P + "it"])
    nd("Sigmoid", [P + "go"], [P + "ot"])
    nd("Sigmoid", [P + "gf"], [P + "ft"])
    nd("Tanh", [P + "gc"], [P + "cg"])
    nd("Mul", [P + "ft", P + "C0"], [P + "fC"])
    nd("Mul", [P + "it", P + "cg"], [P + "ic"])
    nd("Add", [P + "fC", P + "ic"], [P + "Ct"])
    nd("Tanh", [P + "Ct"], [P + "thC"])
    nd("Mul", [P + "ot", P + "thC"], [Th])          # Ht -> Th (classifier input)
    nd("Concat", [Th, P + "Ct"], ["stateN"], axis=0)  # [2,128]

    remove = {id(x) for x in [lstm, sq_h, sq_c, uns_h, uns_c, uns_h0, uns_c0, old_concat] + gathers}
    keep = [n for n in g.node if id(n) not in remove]
    del g.node[:]
    g.node.extend(keep + new_nodes)
    topo_sort(g)
    for vi in g.input:
        if vi.name == "state":
            set_shape(vi, [2, HIDDEN])
    for vo in g.output:
        if vo.name == "stateN":
            set_shape(vo, [2, HIDDEN])
    onnx.checker.check_model(m)
    onnx.save(m, str(out))


def step_split_stft(src: Path, out: Path):
    m = onnx.load(str(src))
    g = m.graph
    inits = {i.name: i for i in g.initializer}
    cons = {}
    for n in g.node:
        for i in n.input:
            cons.setdefault(i, []).append(n)
    stft = [n for n in g.node if n.op_type == "Conv"
            and numpy_helper.to_array(inits[n.input[1]]).shape == (258, 1, 256)][0]
    W = numpy_helper.to_array(inits[stft.input[1]])   # [258,1,256]
    slc = cons[stft.output[0]]
    assert all(s.op_type == "Slice" for s in slc)

    def start_ch(s):
        return int(numpy_helper.to_array(inits[s.input[1]])[1])

    real_s = next(s for s in slc if start_ch(s) == 0)
    imag_s = next(s for s in slc if start_ch(s) == 129)
    g.initializer.extend([
        numpy_helper.from_array(W[:129].copy(), "stft/Wr"),
        numpy_helper.from_array(W[129:].copy(), "stft/Wi"),
    ])
    a = {aa.name: onnx.helper.get_attribute_value(aa) for aa in stft.attribute}

    def conv(name, w, o):
        return helper.make_node("Conv", [stft.input[0], w], [o], name=name,
                                dilations=a.get("dilations", [1]), group=a.get("group", 1),
                                kernel_shape=a["kernel_shape"], pads=a["pads"], strides=a["strides"])

    new_nodes = [conv("stft/conv_real", "stft/Wr", real_s.output[0]),
                 conv("stft/conv_imag", "stft/Wi", imag_s.output[0])]
    remove = {id(stft), id(real_s), id(imag_s)}
    keep = [n for n in g.node if id(n) not in remove]
    del g.node[:]
    g.node.extend(keep + new_nodes)
    topo_sort(g)
    onnx.checker.check_model(m)
    onnx.save(m, str(out))


def step_onnx2tf(src: Path, workdir: Path) -> Path:
    subprocess.run(["onnx2tf", "-i", str(src), "-o", str(workdir / "saved_model"), "-b", "1"],
                   check=True, capture_output=True)
    tfl = workdir / "saved_model" / (src.stem + "_float32.tflite")
    return tfl


def make_fixtures():
    rng = np.random.default_rng(1234)
    n = 16
    fx = {}
    fx["silence"] = np.zeros((n, FRAME), np.float32)
    imp = np.zeros((n, FRAME), np.float32)
    imp[:, 0] = 1.0
    fx["impulse"] = imp
    t = np.arange(n * FRAME) / SAMPLE_RATE
    fx["sine"] = (0.5 * np.sin(2 * np.pi * 440 * t)).astype(np.float32).reshape(n, FRAME)
    fx["noise"] = rng.standard_normal((n, FRAME)).astype(np.float32) * 0.1
    # Synthetic voiced signal: summed formants, 120 Hz pitch, 3 Hz syllabic AM.
    f0, formants = 120.0, [700.0, 1220.0, 2600.0]
    sig = np.zeros(n * FRAME, np.float32)
    for k in range(1, 25):
        sig += (0.6 / k) * np.sin(2 * np.pi * f0 * k * t)
    for fmt in formants:
        sig += 0.3 * np.sin(2 * np.pi * fmt * t)
    sig *= (0.5 + 0.5 * np.sin(2 * np.pi * 3.0 * t))
    sig = (sig / np.max(np.abs(sig)) * 0.8).astype(np.float32)
    fx["speech"] = sig.reshape(n, FRAME)
    return fx


def ort_ref(onnx_path: Path, fx):
    so = ort.SessionOptions()
    so.intra_op_num_threads = 1
    so.inter_op_num_threads = 1
    s = ort.InferenceSession(str(onnx_path), so, providers=["CPUExecutionProvider"])
    has_sr = "sr" in [i.name for i in s.get_inputs()]
    onames = [o.name for o in s.get_outputs()]
    ref = {}
    for name, frames in fx.items():
        st = np.zeros((2, 1, HIDDEN), np.float32)
        probs = []
        for fr in frames:
            feed = {"input": fr.reshape(1, FRAME).astype(np.float32), "state": st}
            if has_sr:
                feed["sr"] = np.array(SAMPLE_RATE, dtype=np.int64)
            d = dict(zip(onames, s.run(None, feed)))
            probs.append(float(d["output"].reshape(-1)[0]))
            st = d["stateN"].astype(np.float32)
        ref[name] = (np.array(probs), st.reshape(2, HIDDEN))
    return ref


def validate(tflite_path: Path, ref, fx):
    from ai_edge_litert.interpreter import Interpreter
    it = Interpreter(model_path=str(tflite_path))
    it.allocate_tensors()
    ind = {d["name"]: d for d in it.get_input_details()}
    outd = it.get_output_details()

    def run(x, st):
        it.set_tensor(ind["input"]["index"], x.astype(np.float32))
        it.set_tensor(ind["state"]["index"], st.astype(np.float32))
        it.invoke()
        vals = [it.get_tensor(d["index"]) for d in outd]
        prob = next(v for v in vals if v.size == 1).reshape(-1)[0]
        state = next(v for v in vals if v.size == 2 * HIDDEN).reshape(2, HIDDEN)
        return float(prob), state.astype(np.float32)

    max_p = max_s = 0.0
    disagree = frames_total = 0
    per = {}
    for name, frames in fx.items():
        st = np.zeros((2, HIDDEN), np.float32)
        dp = 0.0
        rp = ref[name][0]
        for i, fr in enumerate(frames):
            p, st = run(fr.reshape(1, FRAME), st)
            dp = max(dp, abs(p - rp[i]))
            disagree += int((p >= 0.5) != (rp[i] >= 0.5))
            frames_total += 1
        ds = np.abs(st - ref[name][1]).max()
        per[name] = (dp, ds)
        max_p = max(max_p, dp)
        max_s = max(max_s, ds)
    return max_p, max_s, disagree, frames_total, per


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True, help="pinned silero_vad.onnx (v5.1)")
    ap.add_argument("--out", required=True, help="output silero_vad.tflite")
    ap.add_argument("--workdir", default="/tmp/silero_convert")
    args = ap.parse_args()
    src = Path(args.src)
    work = Path(args.workdir)
    work.mkdir(parents=True, exist_ok=True)

    digest = sha256(src)
    print(f"source sha256: {digest}")
    if digest != PINNED_SHA256:
        sys.exit(f"FATAL: source ONNX sha256 mismatch (expected pinned {PINNED_SHA256})")

    step_static(src, work / "s1_static.onnx")
    step_fold(work / "s1_static.onnx", work / "s2_folded.onnx")
    step_decoder_2d(work / "s2_folded.onnx", work / "s3_decoder2d.onnx")
    step_split_stft(work / "s3_decoder2d.onnx", work / "s4_final.onnx")
    tfl = step_onnx2tf(work / "s4_final.onnx", work)

    fx = make_fixtures()
    ref = ort_ref(src, fx)
    max_p, max_s, disagree, total, per = validate(tfl, ref, fx)
    print("Per-fixture parity (TFLite vs ONNX Runtime):")
    for name, (dp, ds) in per.items():
        print(f"  {name:8s} max|dprob|={dp:.3e} max|dstate|={ds:.3e}")
    print(f"OVERALL max|dprob|={max_p:.3e} (tol {TOL_PROB}) "
          f"max|dstate|={max_s:.3e} (tol {TOL_STATE}) "
          f"decision_disagreements={disagree}/{total}")
    if max_p > TOL_PROB or max_s > TOL_STATE or disagree > 0:
        sys.exit("FATAL: parity exceeds tolerance — refusing to emit model")

    Path(args.out).write_bytes(tfl.read_bytes())
    print(f"WROTE {args.out}  sha256={sha256(Path(args.out))}  bytes={Path(args.out).stat().st_size}")


if __name__ == "__main__":
    main()
