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

## Open questions

- Does the declared complete graph meet the unchanged training-only budgets?
- Which fixed selective QDQ scope can preserve whole-model parity?
- Can the eventual mobile runtime execute the required arithmetic reliably?

## Confidence

High for the predeclared finite protocol; whole-model parity, mobile execution
and clinical validity remain unverified before the experiment.
