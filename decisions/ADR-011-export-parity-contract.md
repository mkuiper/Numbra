# ADR-011 — PLACEHOLDER export parity and frozen-decision contract

Date: 2026-10-09

Status: Accepted (autopilot) — pending human review

## Context

M3 gate closed PASS WITH CHANGES. REVIEW-1 issue 4 correctly identifies that the
M0 proposed quantised probability tolerance 0.02 alone can hide threshold flips.
The original saved PLACEHOLDER baseline has temperature 19.150006 and threshold
0.40079881738785716, held-out sensitivity below target, and a strongly overfit head.
None of those fits or synthetic inputs will be changed to improve export parity.
ADR-005 selects ONNX Runtime Mobile; this decision fixes test requirements, not
an export success or clinical/device performance claim.

## Decision

Use the original selected M3 PLACEHOLDER baseline as a software-test artifact.
Retain the explicit unselected refer-all model as separate fallback evidence;
never silently swap artifacts to obtain a passing parity report. Publisher-rights
and whether to carry the selected model into future clinical work remain human
questions; no clinical use is authorised.

Before any conversion/quantisation experiment, fix these absolute budgets:

| Artifact comparison to saved Python reference | Raw logit max error | Calibrated probability max error | Frozen-threshold flips allowed |
| --- | ---: | ---: | ---: |
| Float ONNX | 0.0001 | 0.000001 | 0 |
| Quantised ONNX | 0.1 | 0.001 | 0 |

Both numerical budgets and zero flips must pass independently on the same ordered
preprocessed tensors. Temperature/sigmoid are applied once outside the graph.
Report max/mean errors, all violating cases, and both directions of threshold
crossing. Record every failure; never widen a budget after seeing a failing run.
These are engineering acceptance budgets, not clinical validation thresholds.

Separately measure conservative referral at `score >= max(0, threshold-0.001)`
for the quantised artifact. Count added referrals and any lost Python-reference
referrals. This margin cannot erase failures at the original threshold or cancel
symptom/contact/concern/quality/missingness rules in M6. Future clinical margins
need independent calibration/threshold validation. Preserve full-precision
threshold/temperature in runtime metadata; displayed rounded values are not inputs.

First verify the saved model with `numbra_ml.verify` (raw tolerance 1e-5, zero
decision flips); load bundled backbone/scaling/head without a hub/checkpoint fetch.
Export raw-logit NCHW float32 graph, planned fixed single-image 1×3×224×224 input.
Use ADR-005 static INT8 QDQ with training-only calibration inputs; leave test and
held-out components out of quantisation fitting. Inspect quantised and remaining
float operators and measure actual file bytes (≤20 MB). Unsupported graphs or
unmet parity need two genuine documented attempts before a labelled workaround
and amended ADR; the runtime/export milestone remains incomplete until accepted.

Use frozen test and held-out components plus independent generated stress tensors
for parity. Generated stress inputs cover extreme RGB/exposure, aspect ratios and
nonuniform patterns; derive them independently of quantisation calibration, never
choose a subset after errors. Check per-input numerical/decision parity, not just
mean error. Aggregate evidence is tracked; individual failures/predictions and
model weights stay under ignored data/. Exported held-out evaluation must also be
reported rather than assuming quantisation preserves synthetic metrics.

## Consequences

The small probability budget alone still cannot guarantee threshold stability;
the explicit flip requirement protects the tested fixtures. Testing is finite,
so unseen-input parity remains unverified. Desktop Python/ONNX results do not
establish Android decode/orientation, ABI/operator compatibility, memory, latency
or device reliability. M6 must compare Android preprocessing against the written
RGB letterbox spec and M8 must test the complete synthetic flow.

No ONNX graph or quantised artifact has been produced in this iteration. Exact
export/runtime dependency pins, operator support and Android compatibility must
be verified in the next export step. All artifacts/UI/results remain PLACEHOLDER.

## Open questions

- Do humans accept these stricter budgets and finite-fixture zero-flip requirement?
- What independent clinical/device protocol and margin can replace this software test?
- Should future app testing favour the selected PLACEHOLDER or refer-all artifact?

## Confidence

High for tested parity arithmetic and saved Python reference; export/quantisation
and mobile/clinical performance remain unverified.
