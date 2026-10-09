# M4 export contract — PLACEHOLDER, in progress

No exported or quantised model exists yet. M3 has passed its gate; this iteration
establishes the saved Python reference and testable parity contract for ADR-005's
ONNX Runtime Mobile route. [ADR-011](../decisions/ADR-011-export-parity-contract.md)
fixes budgets before export experiments. No M4 acceptance or on-device claim.

## Python reference

From repository root in the existing locked environment:

```bash
ml/.venv/bin/python -m numbra_ml.verify
```

This verifies the model/prediction/preparation hashes, strictly reloads the full
bundled backbone/scaling/head, checks component metadata and rescores using the
original feature batch size. The pretrained checkpoint is not needed. Baseline
and reproduction: 768 components each, max raw/probability error 0, decision flips
0. Default fallback: 384 components, also exact. Tolerance is 1e-5 raw logit and
zero frozen-threshold flips; these are saved Python comparisons, not ONNX parity.
The full training-to-save-to-reload toy-fixture path runs in tests of record.

## Preprocessing and planned graph interface

`numbra_ml.preprocessing.SPEC` version 1.0.0 is the executable authority; the
preprocessor and its colour/geometry/rounding/bounds tests already exist. Decoder
supplies oriented uint8 HWC RGB with 1..4096 pixels per dimension. Float32 graph
input is one contiguous NCHW tensor, planned shape 1×3×224×224. No EXIF decoder,
alpha conversion or Android preprocessing implementation is claimed yet.

1. Scale by `min(224/width,224/height)`; round resized dimensions half-up and
   clamp to 1..224.
2. Resize with bilinear half-pixel coordinates, clamped edges, no antialias.
   Interpolate in float64, round half-up and clamp to uint8 before normalisation.
3. Centre in a 224×224 RGB-128 canvas; odd extra padding goes right/bottom.
4. Divide uint8 channels by 255 in float32, subtract RGB mean
   `[0.485,0.456,0.406]`, divide by `[0.229,0.224,0.225]`; transpose HWC to CHW
   and add the external batch dimension. No fitted pixel transform.

The model emits one uncalibrated binary logit. Apply full-precision saved
temperature/sigmoid once outside the graph; compare inclusively with the saved
full-precision threshold. No disease label/absence may be inferred from it.
The letterbox differs from publisher pretraining geometry; no superiority claim.

## Parity requirements

`numbra_ml.parity.parity_report` compares matched ordered raw logits using the
same frozen temperature/threshold. Both numerical bounds and zero threshold
flips must pass independently. It reports all failure cases, max/mean errors,
crossings in each direction and separate conservative-margin referrals.

| Budget | Raw absolute error | Probability absolute error | Allowed frozen-threshold flips |
| --- | ---: | ---: | ---: |
| Float | ≤0.0001 | ≤0.000001 | 0 |
| Quantised | ≤0.1 | ≤0.001 | 0 |

The quantised conservative margin is 0.001 below the frozen threshold. Record
added referrals and any lost reference referral; recovering a referral via the
margin does not make an original-threshold flip pass. Tests prove that tiny errors
at high temperature can flip actions, large raw errors can disappear in sigmoid
saturation, inclusive equality is retained, and mismatched/nonfinite/duplicate
inputs fail; logits must be float32-representable to match the planned graph.
Individual failure cases belong only under ignored data/; tracked
reports contain aggregates and checksums. All reports must say PLACEHOLDER.

## Remaining M4 work

Verify/pin/hash-lock ONNX conversion and runtime dependencies; export and check a
float graph, then static INT8 QDQ using training-only synthetic calibration.
Compare against Python on all frozen test/held-out components and independent
generated colour/exposure/aspect/pattern stress inputs, with no calibration/test
overlap. Report exported held-out evaluation and inspect remaining float operators.
Measure bytes ≤20 MB and retain provenance/metadata/notices. No widening parity
budgets to make a failed conversion pass. Actual Android runtime/ABI/decode and
performance checks follow in M5–M8.

## Open questions

- Will the real frozen-feature graph meet strict quantised raw/decision parity?
- What runtime/operator/ABI, footprint and latency will the actual export measure?
- Do humans approve pending weight notices/rights and the engineering budgets?

## Confidence

Verified saved-reference and parity arithmetic on synthetic inputs only. ONNX
conversion, quantisation, mobile execution and clinical validation are pending.
