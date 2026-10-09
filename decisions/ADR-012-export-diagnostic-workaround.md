# ADR-012 — PLACEHOLDER export toolchain and diagnostic-only workaround

Date: 2026-10-09

Status: Accepted (autopilot) — pending human review

## Context and sources

ADR-005 selects ONNX Runtime Mobile; ADR-011 fixes budgets before experiments.
[PyTorch 2.8 ONNX documentation](https://docs.pytorch.org/docs/2.8/onnx.html)
documents the legacy exporter option.
[ONNX Runtime quantisation documentation](https://onnxruntime.ai/docs/performance/model-optimizations/quantization.html)
describes static calibration, QDQ and per-channel options; quantisation can lose
accuracy. [Mobile documentation](https://onnxruntime.ai/docs/tutorials/mobile/)
supports the mobile route, but does not establish compatibility of this graph.
Accessed 2026-10-09 using the documented web-tool fallback after Firecrawl again
reported zero credits and rejected the scrape. No account/credential changes.

Seven new packages installed in ml/.venv include onnx 1.19.1, onnxruntime 1.23.2
and their transitive dependencies in requirements-export.lock; existing
35-package CPU lock remains unchanged. Final combined lock has 42 unique packages,
CPython 3.12 Linux x86_64 only. Legacy opset 17 export avoids an additional dynamo
toolchain and was actually executed; future PyTorch exporter migration is separate.

## Two genuine attempts and evidence

Both use the original selected PLACEHOLDER baseline, its bundled saved weights,
frozen temperature/threshold, identical fixed input/preprocessing and ADR-011
budgets. No retraining, checkpoint fetch, threshold or tolerance adjustment.
MinMax static signed INT8 QDQ Conv/Gemm/MatMul calibration uses all and only 152
training components. Attempt 1 is per-tensor weights; attempt 2 is per-channel
weights, predeclared in the command interface before experiment 1.

[Attempt 1 aggregate evidence](../ml/reports/PLACEHOLDER-m4-attempt1.json):
test/held-out INT8 max raw/probability errors 50.784990/0.506519, 26 threshold flips.
[Attempt 2](../ml/reports/PLACEHOLDER-m4-attempt2.json):
62.403598/0.612635, 28 flips. Both INT8 graphs have 53 quantised Conv/one Gemm and
remain mixed precision. Sizes 1,730,515/1,861,702 bytes pass the 20 MB limit.

Identical float graph in both attempts: 6,095,579 bytes, max test/held-out raw
error 0.000272334 and probability error 0.00000355427, zero flips. It **fails**
both numeric budgets. Stress and all-component comparisons also fail. Observed
single-image Python vs original saved-batch differences are separately reported.
All per-component outputs, graphs and intermediate weights remain ignored data/.

## Decision: labelled workaround

**PLACEHOLDER labelled workaround — generated toy-model export for diagnostic
pipeline testing only.** Continue testing conversion/QDQ/CPU inference/reporting
using generated RGB and a separately labelled toy backbone in the tests of
record. This keeps the pipeline usable after two baseline parity failures. A
known passing centre-pixel toy tests the strict float interface; an average-pool
toy additionally asserts that actual runtime rounding failures remain failures.
The complete synthetic preparation→toy training→saved verification→export→runtime
path tests provenance, quantised operators and preservation of failed reports.

Reject all current baseline exports for app bundling. Retain original selected
baseline as the M4 reference: toy evidence cannot replace it, widen budgets or
close acceptance. NEXT_ACTION stays CONTINUE; no M4 review request yet. Proceed
to training-only operator/activation diagnostics and precision/runtime work,
rather than repeating failed settings. Document the next graph strategy before
execution. Any future mixed-precision workaround must identify every remaining
float operator and pass the original budgets/zero flips before requesting review.

## Consequences

M4 remains incomplete; roadmap order prevents starting M5. Runtime/interface/
reporting code is tested, but no deployment package is authorised by this ADR.
No Android execution, ABI, latency, clinical or field-safety claim. The per-channel
source-C result has sensitivity 1 with specificity 0 and demonstrates drift;
it is not a replacement model or a clinical improvement. Future real data and
weight-rights approval remain blocked under existing decisions.

## Open questions

- Which graph/runtime precision strategy can meet the unchanged selected-baseline budgets?
- Do humans accept the diagnostic workaround and exporter/runtime version pins?
- Which independent clinical/device protocol replaces these finite synthetic tests?

## Confidence

High for observed failed desktop experiments and tested diagnostic pipeline;
no confidence in deployable baseline parity or clinical validity.
