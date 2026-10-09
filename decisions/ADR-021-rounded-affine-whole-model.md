# ADR-021 — Training-only complete rounded-affine PLACEHOLDER BN graph

Date: 2026-10-10

Status: Accepted (autopilot) — pending human review

## Context

ADR-020's complete local replay found `e32-r32-a32-b64-o64` matched native
BatchNorm on every saved BN, both input origins and all 152 training inputs.
That finite local observation does not establish whole-model parity. Original
Conv kernel drift remains and every previous export remains rejected. ADR-012's
labelled toy diagnostic workaround remains in force.

## Decision — declared before execution

Build one complete candidate from the unchanged verified preserved graph:
replace all 34 saved BNs with `e32-r32-a32-b64-o64`. Compute epsilon sum,
square root/reciprocal and alpha in float32; compute beta in float64 and round
to float32. Serialize float32 alpha/beta, cast input and coefficients to double,
Mul/Add in double, then cast once to the original float32 output boundary.
Use independent NumPy and eager-PyTorch coefficient expressions and reject any
bit disagreement. Preserve every other serialized node, initializer, input and
output, including Conv, activations, head and original float32 boundaries.
Match every saved BN in module order and audit saved parameter/epsilon bits,
the complete coefficient recipe and actual runtime Cast/Mul/Add expression.

Compare only this candidate and the unmodified preserved control on all and only
the ordered training components with disabled ORT optimisation, sequential CPU
execution, two intra-op/one inter-op threads. Retain the native saved Python
reference, model, fits, temperature, threshold and ADR-011 budgets. Independently
reconstruct original-graph parity from ignored ordered details and verify the
control against ADR-020 ordered logits; reject missing/extra/reordered scope.
Feature taps remain separate copies with measured instrumentation changes.

No favourable layer subset, new quantisation fit, frozen test/held-out/stress
inference, reference/budget change, deployment selection or mobile claim.
All graphs/details remain ignored under data/ and labelled **PLACEHOLDER
diagnostic only, never bundle**. Exit 0 means diagnostic evidence was written;
training-only PASS, if observed, still cannot close M4. Quantisation and mobile
double operator compatibility require separate declared work before acceptance.

## Consequences

This bounded experiment tests propagation of the locally matching BN expression
without tuning against frozen inputs. Conv arithmetic may still defeat parity;
double output arithmetic is not a claim of hardware float32 FMA. It does not
authorise bundling or change the roadmap order.

## Observed follow-through — 2026-10-09 UTC

[Complete aggregate evidence](../ml/reports/PLACEHOLDER-m4-rounded-bn2.json):
all 34 BNs replaced; all 152 ordered training inputs; unchanged control/model/
fits/budgets. Independent engines agree on every coefficient bit, and all
serialized/runtime expressions pass audits. Candidate max raw/probability
errors 0.000143051/0.00000183769 **FAIL** budgets 0.0001/0.000001, with 13/21
violations and zero flips. Preserved control reproduces maxima
0.000240326/0.00000279320 and 26/29 violations. Every failed graph stays rejected.

Independent no-inference audit PASS: eight graph records, ordered input scope,
coefficient bits and runtime arithmetic, fixed-budget parity/failure aggregates,
features/tap accounting, saved-model/preparation/source/retained/dependency/code
provenance, and exact ADR-020 Python/control ordered logits. Zero feature-tap
changes. Candidate 6,255,113 bytes; size does not cancel failed parity.

The first run remains retained. Its subsequent prior-control audit assumed
temperature/threshold fields in ADR-020's replay protocol and raised KeyError.
Corrected it to bind the fits through the identical saved-run hash and added an
actual-schema regression. Regenerated evidence after the source change: graph,
detail and artifact aggregates reproduce exactly. No inference expression changed.
The diagnostic exit status still does not imply acceptance.

Next predeclare complete training-only fixed ORT optimisation profiles on the
rounded-affine graph and preserved control, auditing any folded constants and
operator semantics. Quantisation scope and mobile double support remain separate
blockers; no frozen inference or deployment selection occurred.

## Open questions

- Does the declared complete graph meet the unchanged training-only budgets?
- Which fixed selective QDQ scope can preserve whole-model parity?
- Can the eventual mobile runtime execute the required arithmetic reliably?

## Confidence

High for the finite training-only protocol and observed failed whole-model parity.
Unseen-input/mobile execution and clinical validity remain unverified.
