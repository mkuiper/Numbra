# ADR-017 — Training-only complete promoted BatchNorm PLACEHOLDER graph

Date: 2026-10-10

Status: Accepted (autopilot) — pending human review

## Context

ADR-016 finds local improvement from promoted rsqrt-affine arithmetic at the
stem BN, while differences from native Python remain. Local measurements do
not establish complete-model improvement. The retained preserved graph contains
34 saved BN nodes; the selected baseline and every earlier failure remain fixed.
ADR-012's labelled toy diagnostic workaround remains in force.

## Decision — declared before execution

Replace **every** inference-only BatchNormalization node in the verified
ADR-014 preserved graph with ADR-016's promoted `affine_rsqrt` expression.
Match all saved BN modules by weight name and validate the source node's saved
weight, bias, mean, variance and epsilon. Reject missing/extra/ambiguous nodes,
training mode, unsupported modules, non-finite coefficients and name collisions.
Compute alpha/beta once from the saved float32 buffers using the existing
rsqrt recipe; serialize their float32 bits, cast inputs/coefficients to float64,
multiply/add, and cast once to float32 at each original BN output. Keep every
other graph node, original initializer, connection and graph interface intact,
including original Conv, head, activation and float32 stage boundaries.

Use all and only the existing ordered training component index images. Verify
model/preparation/retained exports/preserved report, graphs and private details
before inference; record source, dependency and state hashes. Compare both the
unmodified preserved control and the complete substituted graph to the native
saved Python reference at disabled ORT optimisation, sequential CPU execution,
two intra-op/one inter-op threads. Measure original-graph raw/probability/decision
parity against unchanged ADR-011 budgets; retain every failed case privately.
Also expose the head features on separate copies and report instrumentation
changes and head attribution. Audit actual runtime graphs for all declared
promoted expressions, coefficients, casts and unchanged Conv/head counts.

No quantisation fitting, frozen test/held-out/stress input inference, retraining,
reference/fit/interface/budget change or deployment selection. Graph copies,
ordered component outputs and details stay ignored under data/; tracked reports
contain aggregates and hashes only. All copies are **PLACEHOLDER diagnostic,
never bundle**. Exit 0 means evidence was written, regardless of parity status;
M4 remains incomplete even if this training-only comparison passes.

## Consequences

This tests propagation through the whole graph without tuning on frozen inputs.
Double arithmetic is diagnostic until mobile compatibility is resolved. A
separate explicit selective static QDQ scope and runtime strategy must be
declared from training evidence before quantisation or new frozen evaluation.
Training parity cannot establish unseen-input, mobile or clinical performance.

## Open questions

- Does complete substitution improve native-reference logit parity on training inputs?
- Which arithmetic/runtime and quantised scope can meet the fixed contract?
- Do humans accept this diagnostic protocol and unresolved mobile support?

## Confidence

High for the declared finite training-only protocol; complete-model results,
deployment compatibility and clinical validity remain unverified.
