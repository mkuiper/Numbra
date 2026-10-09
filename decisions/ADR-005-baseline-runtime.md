# ADR-005 — Small transfer baseline with ONNX Runtime Mobile on CPU

Date: 2026-10-09

Status: Accepted (autopilot) — pending human review

## Context and evidence

The roadmap needs CPU transfer training, a quantised artifact ≤20 MB, parity and
offline Android inference. The timm publisher's
[MobileNetV3Small card](https://huggingface.co/timm/mobilenetv3_small_100.lamb_in1k/raw/main/README.md)
declares Apache-2.0 for the ImageNet-pretrained checkpoint. Binary anonymous access
is not yet verified. [ONNX Runtime mobile documentation](https://onnxruntime.ai/docs/tutorials/mobile/)
supports Android Java APIs and CPU execution;
[quantisation guidance](https://onnxruntime.ai/docs/performance/model-optimizations/quantization.html)
recommends static quantisation for CNNs. Sources accessed 2026-10-09. None of these
establish leprosy performance or Numbra conversion success.

## Options

- Keras/LiteRT: viable alternative, but switching framework solely for export adds
  uncertainty while weight-specific permissions have not been verified here.
- PyTorch/timm → ONNX Runtime Mobile: selected; use one export representation for
  Python parity and Android CPU execution.
- Derm Foundation: excluded for account/terms gating; mobile deployment unverified.

## Decision

After M0 gate, use `mobilenetv3_small_100.lamb_in1k`, frozen features and a trained
binary head on generated synthetic data. Before acquiring weights, verify
anonymous access without registration/extra agreement, retain licence evidence,
pin revision and checksum, prefer safetensors and keep all weights under ignored
`data/pretrained/` (with a file-extension ignore as defence in depth). No real
task data or ImageNet images are approved by this decision.

Export to **ONNX Runtime Mobile**, the roadmap's permitted alternative. Start
static INT8 QDQ quantisation of supported convolution/linear operators using
training-only synthetic calibration inputs. Document remaining float operators;
do not claim all-integer execution unless graph inspection supports it. Use CPU
first; accelerator performance is a later measured choice. Bundle runtime and
PLACEHOLDER artifact locally; no model or runtime download during screening.
Exact dependency pins, Android minSdk and ABI support must be verified when built.

M4 must pass preprocessing and probability parity tests under the
[deployment proposal](../research/05-deployment-constraints.md), including threshold
crossings, and measure artifact size. The POC remains **PLACEHOLDER** even with
ImageNet pretraining because the clinical task head is synthetic.

## Consequences and revisit trigger

ONNX runtime adds native library/APK size; conversion and low-end-device latency
are untested. If checkpoint acquisition fails after two genuine attempts, use
**labelled workaround: synthetic pretraining then transfer** on a small mobile
backbone: pretrain on a separate generated shape task using training groups only,
freeze it and train the screening fixture head. Record that it has no ImageNet or
clinical pretraining; this is real transfer between artificial tasks, not random
weights described as transfer learning. Queue the workaround and retain
PLACEHOLDER everywhere. Conversion failure similarly needs two documented attempts
and an amended ADR before changing runtime; never relax parity tests silently.

Revisit architecture/runtime for unsupported operators, failed parity, measured
device budgets or weight-rights concerns. Preserve licences/notices before any
future distribution. The [ONNX Runtime code licence](https://raw.githubusercontent.com/microsoft/onnxruntime/main/LICENSE)
is MIT; notices of transitive components still need audit.

## Open questions

- Will the exact frozen-feature graph quantise with acceptable threshold stability?
- Which device OS/ABI mix must later Android support, and what is the measured APK footprint?
- Do humans accept publisher-declared pretrained-weight permission for future distribution?

## Confidence

Medium: primary documentation supports the proposed architecture and runtime, but
conversion, binary access, parity and device performance have not been tested.
