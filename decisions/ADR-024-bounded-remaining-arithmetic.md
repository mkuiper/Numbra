# ADR-024 — Bounded PLACEHOLDER activation/reduction arithmetic and head context

Date: 2026-10-10

Status: Accepted (autopilot) — pending human review

## Context

ADR-023 retains all 152 ordered training observations and every computational
node on both unchanged graphs and input origins. All HardSwish, HardSigmoid,
ReduceMean, final GlobalAveragePool and Gemm boundaries have same-input drift.
Gemm extraction additionally differs between explicit parameter inputs and
whole-graph constant parameters. Kernel packing as its cause is **UNVERIFIED**.
The original and rounded-BN whole graphs still fail ADR-011; no failed artifact
is accepted and the labelled ADR-012 toy workaround remains diagnostic only.

## Decision — declared before implementation or execution

Implement supplied-graph primitives first, with generated-only runtime tests.
Cover every HardSwish, HardSigmoid, ReduceMean and GlobalAveragePool, in original
graph order, without an optional node subset. Declare exactly two recipes per
operator; do not add recipes after looking at selected training results:

- HardSigmoid: float32 `clamp(x + 3, 0, 6) / 6` and
  `clamp(x + 3, 0, 6) * float32(1/6)`.
- HardSwish: float32 `(x * clamp(x + 3, 0, 6)) / 6` and
  `(x * clamp(x + 3, 0, 6)) * float32(1/6)`.
- ReduceMean and GlobalAveragePool: float32 ReduceSum over axes 2,3 followed
  by division by the float32 spatial element count; or promote input to double,
  ReduceMean over axes 2,3 in double, and cast once to the float32 output.

Each float32 expression has a separate rounding boundary after every operation.
No fusion, reassociation, rounded reciprocal substitution in the division
recipe, adaptive precision or native-kernel equivalence is presumed. Use
independent eager PyTorch expressions to measure ONNX expression drift; these
are arithmetic controls, never replacement native references. Reject nonfinite,
nonpositive/dynamic geometry, unsupported attributes/types and count overflow.

For the unique Gemm, additionally isolate the original node with only its
activation operand as an input. Retain the exact original initializer,
Constant and Identity alias dependency closure for both weight and bias,
including signed zeros, node attributes and names. Do not fold aliases, make
parameters inputs, change saved head bits or declare context drift solved.
Keep the existing all-input Gemm isolation as a separate control.

Audit serialized recipes by rebuilding their complete expressions, constant
bits and static interfaces. Audit disabled-optimisation runtime graphs with
ADR-023's existing complete expression/constant/boundary auditor. Existing
control arithmetic/audits remain unchanged. Everything is **PLACEHOLDER
diagnostic only, never bundle**; generated primitive success cannot close M4.

A later guarded integration must first reconstruct the complete ADR-023
saved/preparation/prior/source evidence. Replay every declared recipe on all
and only its 152 ordered training components, both unchanged graph contexts
and both exact retained native/runtime input origins. Retain every Conv/BN and
remaining-operator control, native and original/tapped logits, signed accounting
and exact prior bits. Reuse verified retained inputs without decoding images or
running the saved model again where possible. Report all errors and all recipes;
no favourable node/input subset. The integration and its evidence persistence
are explicit unfinished work, not authorised by a primitive PASS alone.

Keep saved reference/state/fits/preprocessing/temperature/threshold and ADR-011
budgets. No complete-model substitution, quantisation fitting, frozen
test/held-out/stress inference, deployment selection or mobile support claim in
this experiment. Any subsequent whole-model candidate and QDQ scope need a
separate predeclared decision based on training evidence.

## Consequences

This bounded experiment tests arithmetic and parameter context without changing
acceptance or using frozen inputs. Reduction accumulation order may still
differ; double kernels remain unverified on mobile. Original Conv drift also
remains. Finite local success cannot establish whole-model parity or clinical
validity. M4 stays incomplete and M5 must wait for its gate.

## Observed primitive foundation — 2026-10-09 UTC

`export_remaining_arithmetic` builds all fixed expressions and the original
head's ordered constant/alias closure without inference. Complete scope on a
fresh random MobileNetV3 fixture covers 19 HardSwish, nine HardSigmoid, nine
ReduceMean, final GlobalAveragePool and one Gemm: 77 recipe graphs. Every
recipe's serialized bits also agree between the two generated graph contexts;
all 87 existing Conv/BN controls are validated before scope construction.
Runtime fixtures audit every expression, constant and boundary with the
unchanged ADR-023 auditor. Signed runtime/eager discrepancies remain explicit.

The first run found an invalid protobuf fixture insertion and a disputed test
assumption of exact ORT/eager Gemm equality (observed 0.0000019073486 drift).
Fixed insertion, and replaced the unjustified equivalence assertion with exact
original constant-context ONNX equality plus unsuppressed signed drift checks.
This is not a production reference/tolerance change; the rejected test and
observed failure are recorded in JOURNAL/HUMAN-QUEUE. Activation/reduction
fixture equality assertions and every existing parity test remain intact.

Generated-only focused verification: 56 PASS, four exporter deprecation warnings.
Required scripts/check.sh: 822 ML PASS, 568 warnings, 172.81s, exit 0;
Android SKIPPED, RESULT PASS. No APK claim.
No selected saved-model execution, retained-observation replay, whole candidate,
new fit, frozen inference or accepted export occurred. Complete guarded retained
training replay and its source-snapshot/evidence audits remain unfinished.

## Observed retained-reader foundation — 2026-10-09 UTC

The complete ADR-023 auditor now applies that decision's explicit historical
source rule to its own report: exact full commit/file map/tree hash, with live
dependencies/locks/hardware and complete artifact/scope/metric/prior checks.
ADR-022 remains separately bound. Old reports and numerical budgets stay intact.

`export_remaining_retained.training_rows` completes that original audit before
exposing any row, then rechecks accessed ordered rows and read-only arrays,
metrics, native/runtime lineage and exact prior bits. Every original control
remains available. Exhaustion checks full array use; partial consumption creates
no completed experiment. Generated tests reject source/dependency/hardware drift,
a corrupt final row before first yield, and index/row/tensor mutations after the
global audit. Decode, model calls, sessions, eager recipes and persistence are
blocked during generated reading. Focused runner/reader verification: 46 PASS;
required scripts/check.sh: 836 ML PASS, 574 warnings, 200.77s, exit 0; Android
SKIPPED, RESULT PASS. No APK claim or selected-model inference.

This is a provenance/reading foundation. Selected retained recipe execution,
new arithmetic persistence and complete independent reconstruction remain
unfinished. All previous parity failures and M4 blockers remain.

[Separate historical-source selected audit](../ml/reports/PLACEHOLDER-m4-remaining-training3-snapshot-audit.json)
PASS: all 152 retained rows, 159 operators, 904 setup graphs and complete
tensor/metric/lineage/parity/prior-bit reconstruction. All five actual
decode/native-call/session/eager/write guards remained active. Exact historical
snapshot matches all 33 source files/tree; dependencies remain live and exact.
Tracked and ignored original report fingerprints agree and remain unchanged.
No selected arithmetic experiment or new model inference occurred.

## Observed supplied retained-tensor integration — 2026-10-09 UTC

`export_arithmetic_replay.ArithmeticReplay` now builds every fixed recipe in
both unchanged graph contexts and independently reconstructs all serialized/
runtime expressions, constants, boundaries, records and files before any supplied
retained operands run. The generated full-mobile fixture covers every 39 target
node/77 fixed recipe, 154 sessions and 308 graph files. Original saved rounded
binding and all existing control/node scope checks precede recipe setup.

Each supplied retained row first passes complete original native/runtime lineage
and control reconstruction. All new recipes run on both exact origins without
decoding images, calling the native model, constructing whole-model sessions or
rerunning original controls. Original arrays remain shared and unmodified;
new eager/runtime arrays remain in memory. All signed native/eager/runtime/
isolated/tapped comparisons and complete four-term accounting are reconstructed
independently without inference. The final accounting term is explicitly the
difference against the original tapped boundary, never a claim of equivalent
replacement extraction. Recorded outputs are observations, not authenticated
historical inference or independently rerun numerical truth.

Initial generated-only suite: 32 PASS, 12 exporter deprecation warnings, 68.94s.
Coverage includes full random mobile arithmetic, complete guarded-reader fixture
exhaustion with new native calls/decode/original control recipes blocked, complete
file/runtime reconstruction, partial/corrupt evidence rejection, stale state/
graph/expression/hooks, and unsuppressed nonzero/signed-zero differences. Four
additional fresh-output rejection cases passed in the required full check:
872 ML PASS, 586 warnings, 263.96s, exit 0; Android SKIPPED, RESULT PASS.
All 36 new tests included; no APK claim. No failing test was weakened or skipped.

This completes the supplied-tensor primitive, not a selected training experiment.
Lossless arithmetic observation persistence, streaming complete audit and the
guarded selected runner remain unfinished. No retained selected recipe execution,
selected native inference, whole-model candidate, fit, frozen evaluation, mobile
compatibility result or accepted export occurred. M4 remains incomplete and
M5 must wait for its gate.

## Observed ordered arithmetic persistence — 2026-10-09 UTC

`export_arithmetic_evidence` persists complete supplied observations: every
original retained control/array and all fixed recipe outputs on both graph
contexts/input origins/engines. The ADR-024 protocol binds ordered target scope,
recipe order, original source/plan, fixed fits and ADR-011 budgets. Shared
ADR-023 lossless ordered storage keeps every tensor bit and file hash; the
original protocol/report format is unchanged. Partial runs have no completed
index. Complete row/metric/prior reconstruction precedes each append.

Independent streaming reconstruction checks complete file/array/ordered row
scope, every original control/lineage, all signed recipe comparisons/accounting,
every numeric/boolean aggregate, both original-graph parity reports and exact
prior bits. Generated tests also verify arrays are released between components.
No decode, native inference, sessions, eager recipe or evidence writes are
needed during reconstruction. Numerical truth of recipe outputs and historical
inference authentication are not claimed. The aggregate declares whole-model
recipe parity UNVERIFIED and deployment selection false.

Initial focused generated-only persistence suites: 72 PASS, four deprecation
warnings, 15.49s. Four additional protocol/acceptance-claim rejection cases are
included in the required full check; final results are recorded in JOURNAL and
STATUS. No test weakened or skipped. Complete generated two-component fixtures
include all original Conv/BN controls and recipe arrays, exact round-trips,
partial/ordered scope and corrupt/rehashed container rejection, signed-zero and
nonzero discrepancies, and unchanged fits/budgets/prior bits.

This is supplied-row software infrastructure, not a selected training experiment.
The guarded selected runner must still verify full original historical-source/
dependency/context evidence and every setup graph before any retained recipe
input, exhaust all 152 components, persist and independently reconstruct the
entire experiment before publishing a completed report. No selected recipe
execution, native baseline inference, new fit, frozen evaluation, whole-model
candidate, mobile compatibility or accepted export occurred. M4 stays incomplete.

Required scripts/check.sh observed exit 0: 909 ML PASS, 588 deprecation warnings,
273.91s; Android SKIPPED, RESULT PASS. All 37 new arithmetic persistence tests
included, with every historical audit/control/parity test intact. No APK claim.

## Open questions

- Which fixed recipes reduce native drift across the complete retained scope?
- Does constant-preserved Gemm isolation reproduce whole-graph outputs?
- Can a subsequent whole graph and quantised mobile runtime meet ADR-011?

## Confidence

High for bounded scope and unchanged acceptance safeguards. Arithmetic outcomes,
head-context causality, complete-model parity and mobile execution are unverified.
