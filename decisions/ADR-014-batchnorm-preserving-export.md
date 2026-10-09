# ADR-014 — Training-only BatchNorm-preserving PLACEHOLDER export

Date: 2026-10-09

Status: Accepted (autopilot) — pending human review

## Context and local evidence

ADR-013's training-only diagnostics identify amplified backbone drift, without
isolating its cause. The saved Python backbone has 34 eval-mode BatchNorm2d
modules; both retained float exports have no BatchNormalization nodes. In the
installed, pinned torch 2.8.0 exporter, `torch/onnx/utils.py` gates its eval
peephole/constant-fold pass on `do_constant_folding`. This is inspected local
implementation evidence, not a promise that disabling folding fixes parity.

## Decision — declared before execution

Export the same saved selected baseline with legacy opset 17, fixed float32
1×3×224×224 input and raw-logit [1] output, `do_constant_folding=False` and
`TrainingMode.PRESERVE` while every module remains in eval mode. Verify all saved
state hashes before/after export, and require the exported BatchNormalization
count to equal the saved module count, with inference-only attributes. No model,
fit, preprocessing, tensor interface or ADR-011 budget changes.

Use only all existing training component index images. Compare the preserved
graph at ORT disabled and all optimisation levels, with the existing sequential
CPU/two intra-op/one inter-op settings. Serialize each session's actual optimized
graph under ignored data/ and inspect its operators. The disabled profile must
retain every BatchNormalization node; the all profile is a deliberate fusion
control, not a silently selected deployment configuration. Compare a fresh
default folded export at the same profiles to separate exporter-setting changes
from the previously retained experiment. Verify its identity with the retained
float graph where bytes match; report differences honestly otherwise.

Expose the saved head's input on separate diagnostic copies and measure the
same feature/head attribution as ADR-013. Audit both original and instrumented
runtime graphs; report instrumentation logit changes. If preserving BatchNorm
still fails, locate divergence at all saved Conv2d/BatchNorm2d boundaries in the
preserved graph, matching nodes through their saved weight names and comparing
to temporary Python hooks. Record per-boundary maximum/mean absolute drift,
with every matched boundary included rather than a favourable subset. Hooks
must be removed even on failure; instrumented logits are compared to original
execution. These taps explain local drift only, not downstream causal effects.

Verify saved model/prediction/preparation and retained experiment provenance,
environment/source/lock hashes before inference. Do not open non-training
images or generated stress tensors. Keep models, optimized/tapped graphs and
per-component diagnostics ignored; track aggregate reports only. Every copy
and report is **PLACEHOLDER diagnostic, never bundle**. Exit 0 means diagnostic
evidence was written; top-level status remains DIAGNOSTIC ONLY even if a profile
passes training budgets. No quantisation fit or frozen evaluation in this step.

## Consequences

M4 remains incomplete, ADR-012's labelled toy diagnostic workaround remains in
force, and existing rejected exports remain rejected. A subsequent precision
and quantised-operator strategy must be declared before frozen evaluation.
Training-only numerical comparisons do not establish unseen-input, Android,
device or clinical performance. No change to the runtime selection or roadmap.

## Implementation correction — before corrected rerun

The first run's boundary taps incorrectly compared timm BatchNormAct2d module
outputs (after activation) with ONNX BatchNormalization outputs (before it).
Its boundary attribution is **INVALID** and explicitly withdrawn in
[the first aggregate](../ml/reports/PLACEHOLDER-m4-batchnorm1.json); original-graph
parity and saved-head feature comparisons are unaffected. Original ignored
report/details are retained unchanged. This is a diagnostic implementation error,
not evidence of large BatchNorm arithmetic drift.

Corrected taps use a temporary pre-hook at BatchNormAct2d's `drop` input, directly
after normalization and before drop/activation, copying before any in-place
activation. Ordinary Conv2d/BatchNorm2d retain output hooks; unsupported BatchNorm
subclasses are rejected. ReLU/HardSwish negative-input regression fixtures check
this exact distinction. The same complete training set and unchanged strategy
will be rerun to a new output; there is no selection from the frozen evaluation.

## Observed follow-through — 2026-10-09 UTC

[Corrected aggregate](../ml/reports/PLACEHOLDER-m4-batchnorm2.json): all 152
training inputs only; model state hashes before/after match. The pre-marking
folded control is byte-identical to the retained float graph. Export and
disabled-runtime graphs retain all 34 BN nodes; all-runtime graphs retain none.
Folded/disabled maximum raw/probability errors 0.000365257/0.00000465196;
preserved/disabled 0.000240326/0.00000279320; both all profiles
0.000323296/0.00000411753. Every profile FAILS both budgets, with zero flips.

All 87 corrected boundaries are reported (53 Conv, 34 BN), with zero original/
instrumented logit difference. Stem Conv drift reaches 0.000000476837, stem
pre-activation BN 0.00000667572, first depthwise Conv 0.000000953674 and its
pre-activation BN 0.0000457764. These are accumulated graph differences, not
operator-local causation. Preserved float diagnostic size is 6,188,494 bytes.
No quantisation fit, frozen evaluation or deployment selection. See
[export documentation](../docs/ML-EXPORT.md) for interpretation and next work.

## Open questions

- Which operator-local arithmetic changes can reduce the remaining drift?
- Can a declared quantised strategy meet the unchanged baseline budgets?
- Do humans accept the diagnostic protocol and corrected implementation?

## Confidence

High for inspected local exporter/state facts and corrected training-only
measurements. Preserving BN alone demonstrably fails these fixed budgets;
operator causation, unseen/mobile parity and clinical validity are unverified.
