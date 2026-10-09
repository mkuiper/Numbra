# ADR-023 — Complete remaining PLACEHOLDER operator replay

Date: 2026-10-10

Status: Accepted (autopilot) — pending human review

## Context

ADR-022's four fixed runtime profiles all fail ADR-011. Exact rounded BN
expressions alone do not resolve whole-model error. Conv/BN replay already has
complete controls; remaining activation, pooling, residual, squeeze/excitation
and head arithmetic must not be omitted or assumed equivalent. Every previous
failed export remains rejected; ADR-012's toy diagnostic workaround remains.

## Decision — declared before implementation or execution

Implement in two reviewable stages. First build a **no-inference preflight**
and generated-fixture isolated replay primitives. Preflight verifies the saved
model and prior preserved/rounded evidence, inventories every original graph
node in topological order, partitions Conv/BN controls from the complete
remaining scope, checks every saved head constant bit and operator attribute,
and verifies each remaining node is byte-identical in the rounded graph.
Reject missing/extra/ambiguous nodes, unsupported arithmetic, disconnected nodes,
changed head parameters, dynamic boundaries or incomplete reports. Initializers,
Constant and Identity aliases are explicit scope records, never silent exclusions.
No image decoding, model forward call or baseline runtime inference in this stage.

The fixed remaining scope includes every Relu, HardSwish, HardSigmoid,
ReduceMean, GlobalAveragePool, Mul, Add, Flatten, Sub, Div, Gemm and Squeeze,
not a favourable module/error subset. Isolated graphs preserve operand order,
attributes, exact constants, shapes and float32 boundaries (int64 squeeze axes).
Audit both serialized and disabled-optimisation runtime graphs. Independent
eager PyTorch recipes use native hard-swish/hard-sigmoid, native reduction/pool,
float32 elementwise operations and native linear head arithmetic. These recipes
are diagnostic expressions; they must not be described as captured saved-model
outputs. Report signed discrepancies without tolerance-based suppression.

Second, in a subsequent implementation step, complete the runner before opening
the existing ordered training index images. Capture actual saved native inputs
and outputs for mapped modules and functional residual/SE/head boundaries,
copying before in-place mutation; validate mapping and native replay fidelity.
Replay on both exact native and tapped runtime input tuples, preserving all
operands for binary operators. Measure original/tapped whole logits separately
on both unchanged preserved and rounded graphs. Keep complete Conv/BN controls,
four-term signed telescoping accounting and all instrumentation differences.
Reconstruct every ordered component/operator/origin/graph/metric and exact prior
disabled-profile logits independently without additional inference.

All real diagnostic inference remains all and only the existing 152 ordered
training components; sequential CPU, two intra-op/one inter-op threads, disabled
optimisation. Keep the selected native saved Python reference, state, fits,
preprocessing, temperature, threshold and ADR-011 budgets. No frozen
test/held-out/stress inference, new quantisation fit, adaptive formula/profile,
retraining, deployment selection or mobile claim. Generated unit fixtures are
separate and cannot establish selected-baseline parity.

All outputs are **PLACEHOLDER diagnostic only, never bundle**. Preflight PASS
means complete static scope/provenance checks passed, not arithmetic equivalence
or M4 acceptance. Track aggregate evidence only; graphs/details remain ignored
under data/. A separate static QDQ scope decision and mobile compatibility work
are still required before acceptance evaluation and bundling.

## Consequences

The first stage provides a tested fail-closed foundation and actionable complete
scope without another model experiment. Remaining native boundary mapping and
full training replay are explicit incomplete work. This decision cannot close
M4, accept any failed graph or authorise M5.

## Tooling observation and bounded audit rule — before baseline preflight

Generated fixtures expose two exporter/runtime details: equal saved constants
may be Identity aliases, and disabled ORT adds unused domain imports and expands
HardSwish into its HardSigmoid/Mul function. Keep exact serialized-node audits.
For actual isolated runtime HardSwish allow only the two-node ordered expression
`HardSigmoid(x, alpha=float32(1/6), beta=0.5)` followed by `Mul(x, gate)` with
the original float32 input/output and same-shape float32 gate. Audit every
connection/attribute and reject all other rewrites. Inventory unused imports;
they cannot authorise a custom-domain computation. This is a runtime expression
audit, not an arithmetic-equivalence claim against native PyTorch. Preserve all
measured rounding differences. No baseline inference has occurred.

## Observed first stage — 2026-10-10 UTC

[Static preflight](../ml/reports/PLACEHOLDER-m4-remaining-preflight2.json) accounts
for all 160 preserved-graph nodes: 87 Conv/BN controls, 72 remaining replay nodes
and one Constant; all 212 initializer records. Remaining/control serialized
nodes and original constants are unchanged in the rounded graph. Saved head
bits, shapes/dtypes, attributes, connectivity, complete ordered training scope
and saved/prior/source/dependency provenance pass independent reconstruction.
Actual execution blocked image decoding, model forward and baseline ORT sessions
with raising guards. No baseline inference or new parity result occurred.

All 69 generated-fixture tests pass, including full artifact/preparation/prior
reconstruction with unreadable images and inference blocked. Native HardSwish
versus its ORT function expansion has nonzero measured local drift on the fixed
generated fixture; no baseline extrapolation or equivalence claim. Stage two's
native capture and complete training replay remain unimplemented. M4 remains
incomplete and all failed graphs remain rejected.

The first report is retained. Its post-commit audit exposed an incorrect
comparison of historical git context with current HEAD/dirty state. The corrected
auditor validates the recorded commit exists and dirty flag is boolean; every
other field, including live code/dependency hashes, is still reconstructed
exactly. Added commit-context regressions and regenerated the second report;
complete scope/plan/graph/saved/preparation/prior evidence is identical. No
inference-expression or parity-budget change.

## Observed native capture foundation — 2026-10-09 UTC

Stage two's native mapping, actual-call pre-mutation capture, complete multi-operand
static taps and eager-fidelity primitives are implemented. Generated-only tests
exercise residual/SE/head arithmetic and the complete mobile architecture with
new random weights. Capture and untapped native logits agree exactly; every one
of the 72 remaining recipes reproduces captured outputs on that generated full
fixture. These are generated fixtures, never the selected saved M3 baseline.

[Saved native mapping](../ml/reports/PLACEHOLDER-m4-native-mapping1.json) covers all
159 computational nodes and complete original boundaries on both unchanged
graphs. Independent static reconstruction of saved/prior/preparation/graph/source
provenance and the full mapping/taps PASS with decode, forward and ORT session
creation blocked. No saved-baseline inference, quantisation fit, frozen evaluation,
deployment selection or accepted export occurred. Actual runtime graph audits,
original/tapped saved logits, full training replay, signed accounting and complete
ordered-row/prior-logit reconstruction remain unimplemented. Stage two is incomplete.

## Observed complete runtime foundation — 2026-10-09 UTC

Added `export_remaining_runtime` primitives for original and fully tapped
disabled sessions of both declared graphs. Before any input is run, independently
audit every actual runtime operator, ordered operand connection, constant bit and
static boundary, including every internal double BN Cast/Mul/Add/coefficient.
This does not invoke the saved baseline or establish numerical equivalence.

Generated fixtures reveal bounded serialization changes: disabled ORT lowers
tensor Constant into an identical initializer, reorders attribute records and
materializes Conv auto_pad=NOTSET, HardSigmoid beta=0.5 and Gemm transA=0 defaults.
It also reschedules independent nodes, particularly constant Identity aliases.
The auditor allows only those defaults, exact Constant lowering and the already
declared HardSwish expansion. Every original node remains independently bound
by its output, exact name/type and connections; every runtime expression must
be accounted for once. The runtime node order and graph hashes are recorded;
topological validity and exact operand order remain required. Identity parameter
aliases cannot change bits or connectivity. This bounded fixture observation
does not select a new arithmetic expression, runtime profile or deployable graph.

Original and tapped whole logits are measured separately; all original input,
constant and computational taps are checked for exact scope, shape and dtype.
Instrumentation drift is reported without suppression. ORT pass-through input
taps may alias the feed buffer, so both feed dictionaries stay alive until
all outputs are copied. Generated regressions retain corruption/invalid-input
failures, output independence and the exact tapped input bits. Four-term signed
accounting now supports head/flatten ranks while Conv/BN inputs remain NCHW.
Shape, float32, finite/nonempty and exact telescoping checks remain enforced.

Combined generated-only verification: 129 tests PASS, including all 159 original
computational nodes/373 original boundaries on both full random mobile graphs,
all runtime expressions and constants, and exact original/tapped logits on the
fixed generated input. These weights and inputs are generated anew, never saved
M3 artifacts or ordered training images. Full guarded training replay,
both-origin isolated runtime integration, ordered-detail/prior-logit audit,
selective QDQ and mobile execution remain incomplete. All earlier failed exports
remain rejected; M4 stays open and this does not authorise M5.

## Observed supplied-tensor replay integration — 2026-10-09 UTC

`export_remaining_replay` now integrates complete native capture, separate
uncaptured/captured native logits, both original/tapped whole runtime pairs,
all isolated remaining and Conv/BN expressions on both exact input origins,
and rank-general four-term signed accounting. All three BN primitive formulas,
both promoted affine controls, float64 formula and 32 two-engine rounding
controls remain, on both graph origins. No expression/profile/model is selected.

Setup statically rebuilds the complete rounded graph from independently agreed
saved coefficients and the fixed recipe, then audits every original/tapped and
isolated runtime before a supplied input can run. Ordered operands remain
explicit inputs, including parameters/axes; rounded BN isolates its actual
expression with native ONNX retained as a separate control. Invalid inputs,
stale saved state/settings/mode/hooks and changed serialized rounded coefficient
bits/expressions fail before inference. All drift is recorded without suppression.

Retained arrays permit a separate no-inference reconstruction of every metric,
complete operator/graph/origin/control scope, exact saved constant bits and
native/runtime boundary lineage. This checks recorded observations, not their
numerical truth against recomputed inference. Full ordered-component persistence,
aggregate/source/saved/prior audit and exact ADR-022 disabled-logit reconstruction
remain separate unfinished work. No baseline dataset is opened by this module.

Generated-only integration covers both full random mobile graphs and all 159
computational nodes (53 Conv, 34 BN, 72 remaining), including head ranks and
both binary operands. Tests retain nonzero local HardSwish drift and deliberate
native/instrumentation discrepancies. These random weights/generated tensors
cannot establish selected-baseline parity. No new saved M3 inference,
quantisation fit, frozen evaluation, mobile result or accepted export occurred;
M4 remains incomplete. The complete runner must finish before ordered training
images are opened. Test outcomes are recorded in JOURNAL.

## Open questions

- Can complete remaining arithmetic replay isolate an actionable parity strategy?
- Which selective QDQ scope and mobile runtime can meet the unchanged contract?
- Do humans accept the staged protocol and continued export blocker?

## Confidence

High for the bounded protocol; arithmetic outcomes, accepted export, mobile
execution and clinical validity remain unverified.
