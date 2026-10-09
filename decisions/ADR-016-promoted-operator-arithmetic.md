# ADR-016 — Training-only PLACEHOLDER promoted operator arithmetic

Date: 2026-10-09

Status: Accepted (autopilot) — pending human review

## Context

ADR-015 local same-input replay finds small stem Conv and BN kernel differences
and larger propagated differences. Its three unfused BN formulas do not match
native Python exactly. Higher precision may differ from native float32 arithmetic;
this is a hypothesis test, not a promised fix. Existing exports stay rejected.

## Decision — declared before execution

Retain ADR-015 selection, provenance guards, all existing training component
inputs, both Python and preserved-ORT input origins, saved float32 parameter
bits and native Python pre-activation outputs. Reuse its unmodified replay and
telescoping measurements. Keep ADR-011 budgets, model, fits and preprocessing.

For the first stem Conv only, explicitly form the fixed-shape image patches
using zero Pad, strided Slice, Unsqueeze, Concat, Reshape and Transpose. Promote
inputs and exact float32 weights to float64 for MatMul (and bias addition when
present), then cast once to float32 at the original Conv output boundary. Retain
saved stride, zero padding and dilation. Reject groups other than one and
unsupported padding modes instead of silently approximating them. Compare to
a Python float64 unfold/MatMul implementation and to native Python Conv on
identical inputs. This arithmetic reference is diagnostic only; it does not
establish mobile float64 support or reproduce native accumulation order.

For both selected BNs, precompute the same float32 affine_rsqrt and affine_divide
coefficients as ADR-015, preserving their rounded bits. Promote input and those
coefficients to float64, multiply/add without an intermediate float32 rounding,
then cast once to float32. Compare to the matching Python promoted expression
and native Python BN on both input origins. This emulates a single float32
rounding of the affine expression for these finite inputs; it is not proof of
the native kernel's implementation or general hardware FMA identity.

Audit serialized operator graphs and actual disabled-optimisation ORT graphs.
Use the existing sequential CPU/two intra-op/one inter-op settings. Check model
state and hook cleanup. Keep graphs, tensors and component details ignored under
data/; track only aggregate evidence and hashes. Everything remains PLACEHOLDER
diagnostic, never bundle. No whole-model replacement, quantisation fitting,
test/held-out/stress inference, selection or acceptance claim in this experiment.

## Consequences

M4 remains incomplete and ADR-012's labelled toy diagnostic workaround stays in
force. A complete graph arithmetic strategy and explicit quantised scope must
still be declared from training evidence before any new frozen evaluation.
Local improvement, if observed, does not establish complete-model parity,
unseen-input behavior, device execution or clinical performance.

## Observed follow-through — 2026-10-09 UTC

[Aggregate evidence](../ml/reports/PLACEHOLDER-m4-precision1.json) retains all
152 training inputs and unchanged state hashes. Promoted ONNX/Python expressions
agree exactly on both origins. Stem Conv still differs from native Python by
up to 0.000000476837; it does not reduce native ORT's maximum. Promoted affine
rsqrt reduces stem BN maximum to 0.0000000596046 on both origins, but still
differs. First depthwise BN maximum is 0.00000381470 on Python-origin inputs
and 0.00000762939 on ORT-origin inputs with either recipe. Local native
differences remain; no complete-model parity or improved logit claim is made.

Tap/original logits, replay-fidelity errors and signed accounting residuals
are zero. Serialized runtime graph audits retain the declared double arithmetic
and float32 casts. Separate report/source/graph/detail/provenance checksum audit
passes. No frozen evaluation, quantisation fit, deployment selection or M4
closure. Next declare complete-graph BN substitution on training inputs before
any selective quantisation or new frozen evaluation. See
[export documentation](../docs/ML-EXPORT.md) for arithmetic and mobile limits.

## Open questions

- Does promoted arithmetic match native Python more closely on these training inputs?
- Which complete-graph and quantised strategy can meet the unchanged budgets?
- Do humans accept this diagnostic protocol and the remaining M4 blocker?

## Confidence

High for tested isolation, graph construction and observed local arithmetic.
Complete-model parity, deployment compatibility and clinical validity remain
unverified; promoted precision does not exactly recover native float32 outputs.
