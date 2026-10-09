# M4 export contract — PLACEHOLDER, in progress

Two float/static INT8 ONNX experiments now exist under ignored data/. **Both
failed the fixed parity budgets and are rejected for app bundling.** M4 remains
incomplete. [ADR-011](../decisions/ADR-011-export-parity-contract.md) fixes budgets;
[ADR-012](../decisions/ADR-012-export-diagnostic-workaround.md) records the labelled
toy-model pipeline workaround after two failures. No on-device/clinical claim.

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

## Preprocessing and observed graph interface

`numbra_ml.preprocessing.SPEC` version 1.0.0 is the executable authority; the
preprocessor and its colour/geometry/rounding/bounds tests already exist. Decoder
supplies oriented uint8 HWC RGB with 1..4096 pixels per dimension. Float32 graph
input is one contiguous NCHW tensor named `rgb`, shape 1×3×224×224. Output is
float32 `raw_logit`, shape [1]. These names/types/shapes are runtime-validated.
Android EXIF/alpha conversion and preprocessing are still pending.

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

## Reproduce the experiments

Install the [hash-locked environment](DEV-SETUP.md). Original selected M3 baseline
and prepared selection fixture must already exist. Supply new output directories;
overwriting existing experiments is refused. Both observed commands returned 1
because numerical/decision acceptance failed, although export/runtime succeeded:

```bash
ml/.venv/bin/python -m numbra_ml.export --output data/exports/PLACEHOLDER-m4-attempt1 --attempt minmax-per-tensor
ml/.venv/bin/python -m numbra_ml.export --output data/exports/PLACEHOLDER-m4-attempt2 --attempt minmax-per-channel
```

PyTorch 2.8 legacy exporter, opset 17, fixed batch 1, embedded weights; no
checkpoint/network access. Shape inference precedes quantisation without graph
optimisation. Static signed INT8 QDQ covers Conv/Gemm/MatMul; only 152 training
index images calibrate MinMax ranges. The predeclared attempts differ only in
per-channel weight quantisation. Original weights/temperature/threshold, inputs,
stress suite and budgets are preserved. Desktop CPU runtime uses two intra-op
threads, sequential execution and default graph optimisations.

All 768 component index images, the 308 test/held-out subset and 14 independent
generated stress images are compared against single-image saved Python execution.
Stress suite version 1.0.0: seed 741902; black/grey/white, three channel extremes,
noise at 1×1, 1×4096, 4096×1, 7×113, 113×7, 225×319, checker and gradient patterns.
Stress/calibration inputs are generated independently; no stress/test calibration.
Full failure cases/ordered logits stay in `PLACEHOLDER-parity-details.json` under
ignored data/. Frozen evaluation reports per-source/colour metrics without
refitting temperature/threshold; small cells retain M3 suppression rules.

Aggregate reports are generated from verified artifact hashes and ordered logits:

```bash
ml/.venv/bin/python -m numbra_ml.export --summarise --output data/exports/PLACEHOLDER-m4-attempt1
ml/.venv/bin/python -m numbra_ml.export --summarise --output data/exports/PLACEHOLDER-m4-attempt2
```

These write a new `ml/reports/<output-directory-name>.json`, refuse overwrite and
also return 1 for rejected experiments. Reporting revision 1.0.1 corrects the
first prototype's source/colour grouping, retains original experiment source and
lock hashes, and adds the saved-batch diagnostic; no new inference or refitting.

## Observed rejected results — 2026-10-09 UTC

Evidence: [attempt 1](../ml/reports/PLACEHOLDER-m4-attempt1.json),
[attempt 2](../ml/reports/PLACEHOLDER-m4-attempt2.json). The float graph is identical
across both attempts. Max errors below are on the 308 frozen test/held-out inputs:

| Artifact | Bytes | Max raw error | Max probability error | Threshold flips | Result |
| --- | ---: | ---: | ---: | ---: | --- |
| Float | 6,095,579 | 0.000272334 | 0.00000355427 | 0 | FAIL |
| INT8 per tensor | 1,730,515 | 50.784990 | 0.506519 | 26 | FAIL |
| INT8 per channel | 1,861,702 | 62.403598 | 0.612635 | 28 | FAIL |

Across all components float max raw/probability errors are 0.000323296/0.00000411753;
stress maxima 0.000507355/0.00000439209. Every float cohort exceeds both budgets.
INT8 all-component flips: 107/117; stress flips: 2/1. Margins are separately counted
in the reports and cannot rescue these failures. Source-C per-channel sensitivity
1.0 comes with specificity 0.0; it is **not** evidence of improved screening.
Float source-C sensitivity/specificity remain 0.914063/0.078125.

Both INT8 graphs have 53 Conv and one Gemm with INT8 weights through QDQ. Remaining
HardSwish, HardSigmoid, pooling, Add/Mul/Div/Sub and structural operators are listed
in each graph report. This is mixed float/INT8, not all-integer execution. All
graphs meet the decimal 20,000,000-byte limit, which alone does not establish M4.

Saved Python verification in the original training batch size remains exact.
Single-image Python vs saved batched logits has max raw difference 0.000383378,
zero threshold flips. Export budgets compare **the same single-image tensor**;
the batching difference is independently disclosed, never subtracted from error.

## Remaining M4 work

Diagnose float graph/runtime rounding and INT8 activation/weight drift using
training-only operator diagnostics. Record graph/runtime changes before running
them; retain every failure and fixed budgets. A generated toy model exercises the
export/runtime path in tests; it cannot substitute for the selected baseline's
acceptance. No passing deployable model, runtime-metadata package or M4 review
request yet. Android runtime/ABI/decode and device performance remain M5–M8 work.

## Open questions

- Will the real frozen-feature graph meet strict quantised raw/decision parity?
- What runtime/operator/ABI, footprint and latency will the actual export measure?
- Do humans approve pending weight notices/rights and the engineering budgets?

## Confidence

High for observed desktop conversion/quantisation, size, aggregate arithmetic and
rejection of failed parity. No accepted baseline export, mobile execution or
clinical validation evidence.
