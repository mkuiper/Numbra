# ADR-022 — Fixed training-only PLACEHOLDER runtime profiles

Date: 2026-10-10

Status: Accepted (autopilot) — pending human review

## Context

ADR-021's complete rounded-affine BN graph still fails the fixed ADR-011
budgets. Every previous failed export remains rejected; ADR-012's labelled
toy diagnostic workaround remains in force. Changing optimisation can change
arithmetic elsewhere in the graph and can fold the constant coefficient Casts.
The locally installed pinned runtime, not a presumed optimisation recipe,
defines the runtime graphs this experiment will inspect.

## Decision — declared before implementation or execution

Compare the unchanged ADR-021 rounded-affine graph and preserved control under
all four existing fixed profiles, in order: disabled, basic, extended, all.
Use all and only the ordered training component index images, unchanged saved
native Python reference/state/fits, preprocessing, temperature, threshold and
ADR-011 float budgets. Sequential CPU execution remains two intra-op and one
inter-op threads. No adaptive profiles, favourable input/layer subset, new
quantisation fit, frozen test/held-out/stress inference or deployment selection.

Verify prior saved-model/preparation/retained-export/source/rounded-graph evidence
before inference. Retain each original runtime graph and separate feature-tapped
runtime graph. For every rounded BN boundary, audit connectivity, input/output
Cast types, double Mul/Add order and original float32 output boundary. Accept
coefficient Casts either unchanged or folded into double constants only when
their bits exactly equal the saved float32 coefficients promoted to float64.
Resolve only initializers and Identity/Cast constant aliases, with cycle/type
checks. Reject unexpected BN-expression nodes, changed coefficient bits, fused
expressions or changed output boundaries; retain explicit semantic failures
without silently treating them as an accepted profile. Report every runtime
operator inventory and serialized/runtime graph hash, including optimisations
outside BN; do not presume their arithmetic is unchanged.

Independently reconstruct all original-graph parity, feature aggregates and tap
accounting from ignored ordered details; require identical Python logits across
all eight comparisons and exact disabled-profile control/candidate logits from
ADR-021. Audit complete profile/artifact/input scope, graph hashes, coefficient
bits, saved state/fits and current source/dependency provenance without inference.
Aggregate evidence alone is tracked. All graphs and ordered details stay ignored
under data/ and labelled **PLACEHOLDER diagnostic only, never bundle**. Exit 0
means complete evidence was written, including failures, not M4 acceptance.

## Consequences

A profile that passes training parity or changes runtime arithmetic still needs
separately predeclared quantisation scope, complete fixed acceptance evaluation
and mobile compatibility work. Hardware-specific optimisations and double
operator support/performance remain unverified on Android. This experiment does
not authorise bundling, change budgets or permit moving to M5 before M4 closes.

## Observed follow-through — 2026-10-09 UTC

[Complete aggregate evidence](../ml/reports/PLACEHOLDER-m4-runtime-profiles1.json)
contains both unchanged graphs × every four declared profiles × all 152 ordered
training inputs. All eight comparisons FAIL the fixed numerical budgets; all
have zero flips and zero feature-tap changes. Rounded BN disabled/basic/extended
max raw/probability errors remain 0.000143051/0.00000183769; all increases maxima
to 0.000310421/0.00000394886. Control disabled/basic/extended/all maxima are
0.000240326/0.00000279320, 0.000365257/0.00000465196,
0.000365257/0.00000465196 and 0.000323296/0.00000411753 respectively.
No profile selected; no failed export accepted.

All eight candidate runtime BN-expression audits PASS. Disabled retains 204
expression nodes with 68 coefficient Casts; other profiles fold 68 coefficients
exactly into double constants and retain 136 nodes. Every double Mul/Add and
float32 boundary remains intact. Extended introduces 18 candidate FusedConv;
all introduces layout reorder nodes. Control optimisations fold BN into Conv.
Arithmetic equivalence outside audited BN boundaries and mobile execution remain
UNVERIFIED, despite complete operator inventories and measured original parity.

Independent no-inference audit PASS for complete scope, 20 graph records,
fixed-budget parity/failure/feature/tap reconstruction, saved coefficient bits,
model/preparation/prior/retained/source/current-code/dependency provenance and
exact ADR-021 disabled details for both graphs. A new direct-boundary test first
failed because it assumed identical upstream native/ORT hard-swish inputs;
corrected it to use each actual runtime BN input, retaining exact equality and
production budgets. This changes no inference code or retained evidence.

Next predeclare complete same-input activation/pooling/head replay rather than
repeating failed profiles. Quantisation scope, float parity and mobile double
compatibility remain blockers. ADR-012's toy workaround remains diagnostic only;
M4 remains incomplete with no frozen inference, new fit or deployment selection.

## Open questions

- Which profiles preserve the declared BN expression and meet training parity?
- Which independent quantisation strategy and mobile runtime can meet the contract?
- Do humans accept the diagnostic protocol and continued M4 blocker?

## Confidence

High for the declared bounded software experiment; outcomes, deployable parity,
mobile performance and clinical validity remain unverified.
