# ADR-018 — Training-only joint promoted stem/BatchNorm PLACEHOLDER graph

Date: 2026-10-10

Status: Accepted (autopilot) — pending human review

## Context

ADR-017's complete promoted BN graph still fails both ADR-011 numerical budgets.
ADR-016's promoted stem Conv does not reduce its maximum local native-Python
error. Combining the two is an uncertain propagation experiment, not an assumed
fix. All previous failed exports remain rejected; ADR-012's labelled toy
diagnostic workaround remains in force.

## Decision — declared before execution

Use the verified ADR-014 preserved graph and unchanged saved model. Replace only
the first saved stem Conv with ADR-016's fixed-shape zero-padded patch extraction,
float64 MatMul and single float32 output cast. Validate its saved float32 weight/
bias bits, geometry, ungrouped zero padding and connection to the graph input.
Replace all saved BN nodes with ADR-017's float32 rsqrt-affine coefficients,
float64 Mul/Add and single float32 boundary casts. Retain every other serialized
node, original initializer and interface. Audit every promoted expression and
constant in the serialized and actual disabled-optimisation runtime graphs;
require exactly one fewer Conv and one additional MatMul with unchanged Gemm.

Compare the preserved control, newly generated BN-only control, and joint graph
to the native saved Python reference on all and only the existing ordered
training component index images. Use sequential CPU execution, two intra-op and
one inter-op threads. Apply unchanged ADR-011 raw/probability/zero-flip budgets.
Measure original graphs separately from feature taps, record instrumentation
effects, head diagnostics, source/dependency/preparation/state hashes and all
failures. No frozen test/held-out/stress inference, quantisation fit, retraining,
reference/fit/budget change or deployment selection. Models, detailed outputs and
runtime graphs remain ignored under data/; aggregate evidence alone is tracked.

Everything is **PLACEHOLDER diagnostic, never bundle**. Exit 0 means evidence
was generated. M4 remains incomplete even if training parity passes. No static
QDQ scope is selected by this ADR; a separate decision must declare that scope
from training evidence before quantisation or any new frozen evaluation.

## Consequences

The controls allow comparison with retained evidence without adapting the frozen
evaluation. Float64 mobile compatibility, performance, quantisation and unseen
input parity remain unresolved. After this experiment, assess whether more
arithmetic diagnostics have a plausible route to the contract before continuing.

## Open questions

- Does the joint substitution reduce complete-model drift on training inputs?
- Which runtime/arithmetic and explicit quantised scope can meet fixed budgets?
- Do humans accept the diagnostic strategy and unresolved mobile requirements?

## Confidence

High for the previously tested component expressions; joint-model improvement,
mobile execution and clinical validity remain unverified.
