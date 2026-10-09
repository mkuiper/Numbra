# ADR-013 — Training-only PLACEHOLDER export diagnostics

Date: 2026-10-09

Status: Accepted (autopilot) — pending human review

## Context

Both retained M4 baseline exports fail ADR-011. ADR-012 provides a diagnostic
toy-model workaround and requires a declared strategy before more experiments.
Local inspection of the saved selected head finds 1,024 features, minimum scale
0.0047290567 and maximum absolute effective coefficient 59.662624. These suggest
amplification but do not establish the cause of the observed failures.

## Decision — declared before execution

Use only all training component index images, in their existing order, to diagnose
the original float and both rejected INT8 graphs. Compare the four pinned ORT CPU
optimisation levels (disabled, basic, extended, all), with the same two intra-op
threads, one inter-op thread and sequential execution. Do not change Python,
weights, graph arithmetic, quantisation calibration, fits or budgets. Record
original graph/report/model/preparation/lock/source hashes. This is a diagnostic
comparison, not a passing export or a new deployment selection.

For each graph, add a second output at the features entering the head Sub node
on an ignored diagnostic copy. Run both original and instrumented graphs for each
profile, reporting any logit change caused by instrumentation. Compare these
features to the saved Python backbone and run the saved Python head on the ONNX
features to separate feature drift from head/runtime drift. Report maximum and
mean feature error, maximum induced head error, remaining head discrepancy and
the linear coefficient-weighted feature-error bound. Bounds describe the affine
head in real arithmetic; float rounding and diagnostic graph effects are reported
separately. No intermediate patient/image data or per-component outputs in git.

Keep full diagnostic outputs under ignored data/, track aggregate evidence only.
Tests must show non-training image bytes are never opened, inputs and output
paths are checked, graph provenance is checked, and diagnostic instrumentation
does not masquerade as original-graph parity. A successful diagnostic command
means evidence was generated, **not** that M4 passes. Retain all failures.

Any next conversion or mixed-precision strategy will be declared separately,
based on these training-only diagnostics, before touching frozen evaluation
inputs. This iteration does not choose a favourable test/stress subset or widen
ADR-011. M4 stays incomplete until the selected baseline meets its contract.

## Consequences

This bounds an engineering investigation without repeatedly tuning against the
frozen test/held-out/stress fixtures. Numerical differences on generated training
pixels are not clinical, mobile or unseen-input evidence. No app bundle is
approved; every model, report and surface remains **PLACEHOLDER**.

## Observed follow-through — 2026-10-09 UTC

[Diagnostic evidence](../ml/reports/PLACEHOLDER-m4-diagnostics1.json) retains all
152 training components and three original graphs across four profiles. Every
profile fails training parity. Float/all maximum raw/probability errors are
0.000323296/0.00000411753; disabled/basic/extended each reach
0.000365257/0.00000465196, with zero flips. Both INT8 graphs' maximum raw errors
and flips are unchanged across profiles: 59.860615/32 per tensor,
82.789173/36 per channel. Instrumentation logit changes are zero on these inputs.

Float/all feature error reaches 0.0000212193, induced Python-head error
0.000322342 and remaining head/runtime discrepancy 0.0000114441. The evidence
points mainly to backbone feature drift amplified by scaling/head; the underlying
operator cause is still unknown. INT8 also has large head-path discrepancies.
See [export documentation](../docs/ML-EXPORT.md) for complete interpretation.
No profile selected for deployment and no frozen evaluation used. Local saved
Python has 34 BatchNorm2d modules; the retained float ONNX graph has none. A future
declared BatchNorm-preserving graph experiment will test folding as a hypothesis.

## Open questions

- Which stage dominates baseline drift and can a declared precision strategy fix it?
- Do humans accept these diagnostics and the fixed deployment parity requirements?

## Confidence

High for inspected saved-head values, observed training-only profile differences
and tested diagnostic isolation/provenance. Operator causation and unseen/mobile
parity remain unverified; no clinical validity is established.
