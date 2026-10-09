# M4 export contract — PLACEHOLDER, in progress

Two float/static INT8 ONNX experiments now exist under ignored data/. **Both
failed the fixed parity budgets and are rejected for app bundling.** M4 remains
incomplete. [ADR-011](../decisions/ADR-011-export-parity-contract.md) fixes budgets;
[ADR-012](../decisions/ADR-012-export-diagnostic-workaround.md) records the labelled
toy-model pipeline workaround after two failures. No on-device/clinical claim.

## Python reference

From repository root in the existing locked environment:

```bash
ml/.venv/bin/python -m numbra_ml.verify
```

This verifies the model/prediction/preparation hashes, strictly reloads the full
bundled backbone/scaling/head, checks component metadata and rescores using the
original feature batch size. The pretrained checkpoint is not needed. Baseline
and reproduction: 768 components each, max raw/probability error 0, decision flips
0. Default fallback: 384 components, also exact. Tolerance is 1e-5 raw logit and
zero frozen-threshold flips; these are saved Python comparisons, not ONNX parity.
The full training-to-save-to-reload toy-fixture path runs in tests of record.

## Preprocessing and observed graph interface

`numbra_ml.preprocessing.SPEC` version 1.0.0 is the executable authority; the
preprocessor and its colour/geometry/rounding/bounds tests already exist. Decoder
supplies oriented uint8 HWC RGB with 1..4096 pixels per dimension. Float32 graph
input is one contiguous NCHW tensor named `rgb`, shape 1×3×224×224. Output is
float32 `raw_logit`, shape [1]. These names/types/shapes are runtime-validated.
Android EXIF/alpha conversion and preprocessing are still pending.

1. Scale by `min(224/width,224/height)`; round resized dimensions half-up and
   clamp to 1..224.
2. Resize with bilinear half-pixel coordinates, clamped edges, no antialias.
   Interpolate in float64, round half-up and clamp to uint8 before normalisation.
3. Centre in a 224×224 RGB-128 canvas; odd extra padding goes right/bottom.
4. Divide uint8 channels by 255 in float32, subtract RGB mean
   `[0.485,0.456,0.406]`, divide by `[0.229,0.224,0.225]`; transpose HWC to CHW
   and add the external batch dimension. No fitted pixel transform.

The model emits one uncalibrated binary logit. Apply full-precision saved
temperature/sigmoid once outside the graph; compare inclusively with the saved
full-precision threshold. No disease label/absence may be inferred from it.
The letterbox differs from publisher pretraining geometry; no superiority claim.

## Parity requirements

`numbra_ml.parity.parity_report` compares matched ordered raw logits using the
same frozen temperature/threshold. Both numerical bounds and zero threshold
flips must pass independently. It reports all failure cases, max/mean errors,
crossings in each direction and separate conservative-margin referrals.

| Budget | Raw absolute error | Probability absolute error | Allowed frozen-threshold flips |
| --- | ---: | ---: | ---: |
| Float | ≤0.0001 | ≤0.000001 | 0 |
| Quantised | ≤0.1 | ≤0.001 | 0 |

The quantised conservative margin is 0.001 below the frozen threshold. Record
added referrals and any lost reference referral; recovering a referral via the
margin does not make an original-threshold flip pass. Tests prove that tiny errors
at high temperature can flip actions, large raw errors can disappear in sigmoid
saturation, inclusive equality is retained, and mismatched/nonfinite/duplicate
inputs fail; logits must be float32-representable to match the planned graph.
Individual failure cases belong only under ignored data/; tracked
reports contain aggregates and checksums. All reports must say PLACEHOLDER.

## Reproduce the experiments

Install the [hash-locked environment](DEV-SETUP.md). Original selected M3 baseline
and prepared selection fixture must already exist. Supply new output directories;
overwriting existing experiments is refused. Both observed commands returned 1
because numerical/decision acceptance failed, although export/runtime succeeded:

```bash
ml/.venv/bin/python -m numbra_ml.export --output data/exports/PLACEHOLDER-m4-attempt1 --attempt minmax-per-tensor
ml/.venv/bin/python -m numbra_ml.export --output data/exports/PLACEHOLDER-m4-attempt2 --attempt minmax-per-channel
```

PyTorch 2.8 legacy exporter, opset 17, fixed batch 1, embedded weights; no
checkpoint/network access. Shape inference precedes quantisation without graph
optimisation. Static signed INT8 QDQ covers Conv/Gemm/MatMul; only 152 training
index images calibrate MinMax ranges. The predeclared attempts differ only in
per-channel weight quantisation. Original weights/temperature/threshold, inputs,
stress suite and budgets are preserved. Desktop CPU runtime uses two intra-op
threads, sequential execution and default graph optimisations.

All 768 component index images, the 308 test/held-out subset and 14 independent
generated stress images are compared against single-image saved Python execution.
Stress suite version 1.0.0: seed 741902; black/grey/white, three channel extremes,
noise at 1×1, 1×4096, 4096×1, 7×113, 113×7, 225×319, checker and gradient patterns.
Stress/calibration inputs are generated independently; no stress/test calibration.
Full failure cases/ordered logits stay in `PLACEHOLDER-parity-details.json` under
ignored data/. Frozen evaluation reports per-source/colour metrics without
refitting temperature/threshold; small cells retain M3 suppression rules.

Aggregate reports are generated from verified artifact hashes and ordered logits:

```bash
ml/.venv/bin/python -m numbra_ml.export --summarise --output data/exports/PLACEHOLDER-m4-attempt1
ml/.venv/bin/python -m numbra_ml.export --summarise --output data/exports/PLACEHOLDER-m4-attempt2
```

These write a new `ml/reports/<output-directory-name>.json`, refuse overwrite and
also return 1 for rejected experiments. Reporting revision 1.0.1 corrects the
first prototype's source/colour grouping, retains original experiment source and
lock hashes, and adds the saved-batch diagnostic; no new inference or refitting.

## Observed rejected results — 2026-10-09 UTC

Evidence: [attempt 1](../ml/reports/PLACEHOLDER-m4-attempt1.json),
[attempt 2](../ml/reports/PLACEHOLDER-m4-attempt2.json). The float graph is identical
across both attempts. Max errors below are on the 308 frozen test/held-out inputs:

| Artifact | Bytes | Max raw error | Max probability error | Threshold flips | Result |
| --- | ---: | ---: | ---: | ---: | --- |
| Float | 6,095,579 | 0.000272334 | 0.00000355427 | 0 | FAIL |
| INT8 per tensor | 1,730,515 | 50.784990 | 0.506519 | 26 | FAIL |
| INT8 per channel | 1,861,702 | 62.403598 | 0.612635 | 28 | FAIL |

Across all components float max raw/probability errors are 0.000323296/0.00000411753;
stress maxima 0.000507355/0.00000439209. Every float cohort exceeds both budgets.
INT8 all-component flips: 107/117; stress flips: 2/1. Margins are separately counted
in the reports and cannot rescue these failures. Source-C per-channel sensitivity
1.0 comes with specificity 0.0; it is **not** evidence of improved screening.
Float source-C sensitivity/specificity remain 0.914063/0.078125.

Both INT8 graphs have 53 Conv and one Gemm with INT8 weights through QDQ. Remaining
HardSwish, HardSigmoid, pooling, Add/Mul/Div/Sub and structural operators are listed
in each graph report. This is mixed float/INT8, not all-integer execution. All
graphs meet the decimal 20,000,000-byte limit, which alone does not establish M4.

Saved Python verification in the original training batch size remains exact.
Single-image Python vs saved batched logits has max raw difference 0.000383378,
zero threshold flips. Export budgets compare **the same single-image tensor**;
the batching difference is independently disclosed, never subtracted from error.

## Training-only drift diagnostics

[ADR-013](../decisions/ADR-013-training-only-export-diagnostics.md) declares the
diagnostic comparison before execution. Reproduce with a new output directory:

```bash
ml/.venv/bin/python -m numbra_ml.export_diagnostics --output data/exports/PLACEHOLDER-m4-diagnostics1
```

The command checks retained graph/report/saved-model/preparation provenance and
the pinned export environment. It runs only all training component index images
at ORT disabled/basic/extended/all optimisation levels, preserving two intra-op
threads, one inter-op thread and sequential CPU execution. Identical float graphs
are deduplicated; both source-report hashes remain recorded. Non-training pixels
and the stress suite are not opened. Original weights, fits and budgets remain
unchanged. Tests corrupt every non-training image to demonstrate isolation.

A separate diagnostic copy exposes the feature tensor entering the head. Its
features are compared to saved Python backbone execution, and the saved Python
head runs on those features to measure induced head error. A float64 affine
coefficient-weighted bound is reported alongside the actual float32 head error
and remaining runtime/head discrepancy. Instrumentation can affect optimisation:
both graphs run independently and any original/instrumented logit difference is
reported. Instrumented graphs have an extra output and fail the strict deployment
interface; they carry a **PLACEHOLDER diagnostic, never bundle** metadata notice.

Aggregate JSON is written to ignored output and a new `ml/reports/` target;
per-component diagnostics and graph copies stay ignored. Command exit 0 means
diagnostic evidence was generated, not parity acceptance. The top-level status
is always **DIAGNOSTIC ONLY**; original-graph training parity keeps all failures.

### Observed diagnostic results — 2026-10-09 UTC

[Aggregate evidence](../ml/reports/PLACEHOLDER-m4-diagnostics1.json): 152 original
training components, three distinct original graphs × four runtime profiles.
The frozen evaluation images/stress inputs were not used. Every profile fails.

| Original graph / profile | Max raw error | Max probability error | Threshold flips |
| --- | ---: | ---: | ---: |
| Float / all | 0.000323296 | 0.00000411753 | 0 |
| Float / disabled, basic, extended (each) | 0.000365257 | 0.00000465196 | 0 |
| INT8 per tensor / all four (each) | 59.860615 | 0.644490 | 32 |
| INT8 per channel / all four (each) | 82.789173 | 0.787463 | 36 |

The affine head has 1,024 features, minimum scale 0.0047290567, maximum effective
absolute coefficient 59.6626235 and coefficient L1 sum 1,362.464654. Float/all
maximum feature error 0.0000212193 induces maximum saved-Python-head error
0.000322342; the remaining runtime/head discrepancy is at most 0.0000114441.
These maxima can belong to different components and must not be added as an
exact decomposition of the worst case. The evidence points mainly to feature
drift amplified by the head; it does not identify which backbone operator causes
it. Across all profiles/graphs, original/instrumented logit difference is exactly
zero on these inputs; instrumentation equivalence beyond them remains unverified.

Per-tensor/channel maximum feature errors are 4.693677/4.346828. Running the
saved Python head on those features produces maximum errors 159.276985/132.302427;
remaining runtime/head discrepancies reach 104.171941/57.480897. Both feature
and head paths need attention; optimisation settings alone do not solve INT8 drift.
No new quantisation fit, export acceptance or deployment selection was made.

## BatchNorm-preserving training experiment

[ADR-014](../decisions/ADR-014-batchnorm-preserving-export.md) predeclares this
graph experiment. In the existing pinned environment, run to a new output:

```bash
ml/.venv/bin/python -m numbra_ml.export_batchnorm --output data/exports/PLACEHOLDER-m4-batchnorm2
```

This uses the same selected saved baseline, original fits/interface/preprocessing
and ADR-011 budgets. The legacy opset-17 exporter disables constant folding and
uses PRESERVE while every module is eval. All 34 inference-only BatchNormalization
nodes survive export. At disabled ORT optimisation, both original and head-tapped
serialized runtime graphs retain all 34. At all optimisation, both have zero.
Serialized optimized graphs are **PLACEHOLDER diagnostic, never bundle** copies;
ORT warns that the all profile's NCHWc graph may depend on the current hardware.
The folded control before diagnostic marking is byte-identical to the original
retained float export. Full saved model state hashes before/after are identical.
There is no quantisation fit or frozen evaluation/stress inference.

[Corrected aggregate evidence](../ml/reports/PLACEHOLDER-m4-batchnorm2.json):
all 152 training index images, the folded/preserved graphs at both profiles.
Every original-graph comparison still fails both numeric budgets, with zero
threshold flips. Head instrumentation logit changes are zero on these inputs.

| Training-only graph / ORT profile | Max raw error | Max probability error | Raw/probability violations | Flips |
| --- | ---: | ---: | ---: | ---: |
| Folded / disabled | 0.000365257 | 0.00000465196 | 40 / 50 | 0 |
| Preserved / disabled | 0.000240326 | 0.00000279320 | 26 / 29 | 0 |
| Folded or preserved / all (each) | 0.000323296 | 0.00000411753 | 36 / 44 | 0 |

The preserved diagnostic graph is 6,188,494 bytes; the marked folded control is
6,095,644 bytes (original before marking: 6,095,579). Both are float graphs, not
quantised deployment candidates. Preserved/disabled maximum feature drift is
0.0000141859, induced saved-Python-head error 0.000228882, and remaining runtime
head discrepancy 0.0000152588. Maxima may occur on different components; they do
not form an exact decomposition of the worst logit error. Keeping BN separate
reduces the observed maxima but does not solve the original parity contract.

The corrected run also taps all **53 Conv and 34 BatchNormalization** boundaries
at disabled optimisation, matched by saved weight names. Ordinary module-output
hooks match Conv/plain BN; timm BatchNormAct2d instead requires a pre-hook at its
`drop` input, after normalization and before activation. Copies are taken before
in-place activation; all hooks are removed even on exceptions. Tests cover both
ReLU and HardSwish on deliberately negative activations. Every matched boundary
appears in the aggregate; no favourable layer subset is selected.

| Example boundary (training only) | Max absolute local output difference |
| --- | ---: |
| Stem convolution | 0.000000476837 |
| Stem BatchNormalization, before activation | 0.00000667572 |
| First depthwise convolution | 0.000000953674 |
| Its BatchNormalization, before activation | 0.0000457764 |
| Final feature-head convolution | 0.0000176430 |

These compare accumulated outputs from independently executed graphs. They do
not separate propagated upstream error from operator-local arithmetic. Boundary
instrumentation changes original logits by zero on all training inputs, but
equivalence on unseen inputs is unverified. Same-input operator replay is the
next diagnostic step before attributing causation or choosing precision changes.

**Withdrawn boundary evidence:** the
[first aggregate](../ml/reports/PLACEHOLDER-m4-batchnorm1.json) explicitly marks its
boundary attribution INVALID. Initial Python hooks captured BatchNormAct2d
outputs after activation against ONNX values before activation, yielding false
large differences. Original ignored report/details are retained; the tracked
copy adds a reporting erratum and original-report hash. Its original-graph
parity and head-feature diagnostics remain valid and match the corrected run.
No budget, model, fit or input was changed for the corrected rerun.

## Same-input operator replay — 2026-10-09 UTC

[ADR-015](../decisions/ADR-015-same-input-operator-replay.md) predeclares first
stem/first depthwise Conv and immediately following saved BN pairs, selected by
module order/connectivity rather than observed error. Reproduce with a new output:

```bash
ml/.venv/bin/python -m numbra_ml.export_replay --output data/exports/PLACEHOLDER-m4-replay1
```

The command exits 0 for **DIAGNOSTIC ONLY**, not accepted parity. Its
[aggregate evidence](../ml/reports/PLACEHOLDER-m4-replay1.json) covers all and only
152 existing training index images. Original saved model/fits/budgets, retained
experiments and corrected preserved graph/report/details hashes are checked
before inference. No test/held-out/stress inference, quantisation fit or
deployment selection. Generated fixtures exercise both combined BN activations,
depthwise selection, extraction, hook cleanup, training-only pixel isolation and
rejection of stale fits, graph bytes, details and invalid boundary evidence.

Each operator is extracted with its original parameters/attributes and run at
disabled ORT optimisation, with actual serialized runtime graphs audited. Hooks
copy Python inputs and raw pre-activation outputs; a separate ONNX graph taps
the equivalent inputs/outputs. Both exact input origins are replayed through
native Python and ONNX. Python replay, ONNX replay vs tapped whole graph,
instrumented vs original logits and signed telescoping residual are all exactly
zero on these training inputs. This supports the local comparison on these
fixtures; it does not prove equivalence on unseen inputs or mobile runtimes.

| Operator | Same Python input: local kernel max | Same ONNX input: local kernel max | Propagated input effect max | Whole graph boundary max |
| --- | ---: | ---: | ---: | ---: |
| Stem Conv | 0.000000476837 | 0.000000476837 | 0 | 0.000000476837 |
| Stem BN | 0.000000953674 | 0.000000953674 | 0.00000667572 | 0.00000667572 |
| First depthwise Conv | 0.000000119209 | 0.000000119209 | 0.000000953674 | 0.000000953674 |
| First depthwise BN | 0.00000762939 | 0.00000762939 | 0.0000457764 | 0.0000457764 |

Propagation is native Python on the ONNX input minus captured Python output;
kernel drift is isolated ONNX minus native Python on the same ONNX input;
extraction effect is whole ONNX output minus isolated ONNX on that input. Their
**signed elementwise** sum equals the accumulated whole-graph difference.
Separate absolute maxima may occur at different elements/components and cannot
be added as an exact decomposition. At these early pairs, propagation reaches
larger maxima than local arithmetic; this is not a full-backbone causal account.

Three predeclared float32 BN alternatives use the exact saved buffers:
subtract/divide/scale/add, precomputed affine coefficients via rsqrt, and
precomputed affine coefficients via division by sqrt. At both BN layers and
both input origins, each primitive ONNX graph exactly matches its corresponding
Python formula. **None exactly matches native Python BN**: maxima remain
0.000000953674 at the stem and 0.00000762939 at the first depthwise BN. The
rounded float64 mathematical formula also has these nonzero maxima. The rsqrt
affine graph matches the local native-ORT error aggregates; this does not prove
implementation identity or that replacing BN fixes baseline parity. No new
complete-model parity run or numerical improvement claim is made.

Every full/tapped/extracted/formula/runtime graph is labelled **PLACEHOLDER
diagnostic, never bundle** and stays under ignored data/. Ordered component
details are private; tracked evidence contains only aggregates and hashes.

## Promoted operator arithmetic — ADR-016

**PLACEHOLDER diagnostic, never bundle.** Run from the repository root with a
new output directory:

```bash
ml/.venv/bin/python -m numbra_ml.export_precision --output data/exports/PLACEHOLDER-m4-precision1
```

This extends the guarded ADR-015 replay, retaining all 152 training components,
both exact input origins, pre-activation outputs and original graph/replay
comparisons. It never opens frozen test/held-out images or generated stress
inputs. Source/preparation/model/report provenance and ignored output guards
are unchanged. The selected saved model, fits and state hashes stay fixed.

The first stem Conv uses explicit Pad/Slice/Unsqueeze/Concat patch extraction,
Reshape/Transpose and float64 MatMul, followed by one float32 output cast. Its
saved float32 weight bits are serialized and promoted at runtime. Tests check
non-square kernels, stride, dilation, border zeros, channel ordering and bias
against an independent direct convolution; grouped/nonzero-mode padding is
rejected. Only this first Conv is promoted, never the depthwise Conv.

Both selected BN nodes use the two existing float32 affine coefficient recipes,
promoted multiply/add, and one float32 output cast. The expressions do not round
the product to float32 before adding beta. A cancellation fixture asserts the
distinction from ordinary float32 multiply/add. This is arithmetic emulation,
not proof of native CPU FMA implementation or general hardware identity.

[Aggregate evidence](../ml/reports/PLACEHOLDER-m4-precision1.json) has status
DIAGNOSTIC ONLY. Maximum same-input errors against native Python are:

| Operator / promoted arithmetic | Python-origin input | ORT-origin input |
| --- | ---: | ---: |
| Stem Conv / float64 patch MatMul | 0.000000476837 | 0.000000476837 |
| Stem BN / promoted affine rsqrt | 0.0000000596046 | 0.0000000596046 |
| Stem BN / promoted affine divide | 0.000000178814 | 0.000000178814 |
| First depthwise BN / promoted affine rsqrt | 0.00000381470 | 0.00000762939 |
| First depthwise BN / promoted affine divide | 0.00000381470 | 0.00000762939 |

Every promoted ONNX expression exactly matches its corresponding Python
promoted implementation on these inputs. That implementation is distinct from
the native saved float32 operator. Stem BN improves locally relative to native
ORT's 0.000000953674 maximum on both origins. Promoted stem Conv still differs
from native Python and has the same maximum as native ORT; higher precision
does not recover native float32 rounding. First depthwise BN improves its
Python-origin maximum but retains the prior ORT-origin maximum. No formula is
an exact native-Python replacement. These are local comparisons on identical
inputs, not propagated/full-model improvements.

Original/tapped logits, Python/ONNX replay-fidelity errors and signed telescoping
residuals are zero. The saved-state hashes match before/after; hooks clean up on
failure. Actual disabled-optimisation runtime graphs retain the promoted MatMul
or Mul/Add and their casts. Separate checksum audit verified the tracked/private
aggregate equality, source/dependency/preparation/saved-model provenance,
private details and 33 original/tapped/operator/formula/runtime graph records.
All graphs, weights, tensors and ordered component details remain ignored.
Float64 operator support/performance on Android remains unverified; these copies
have no deployment authority.

## Complete promoted BatchNorm graph — ADR-017

**PLACEHOLDER diagnostic, never bundle.** Run from the repository root with a
new output directory:

```bash
ml/.venv/bin/python -m numbra_ml.export_promoted_bn --output data/exports/PLACEHOLDER-m4-promoted-bn1
```

This validates and replaces every saved BN node in the verified preserved
graph, using ADR-016's promoted rsqrt-affine expression and retaining each
original float32 output boundary. Saved weight/bias/mean/variance and epsilon
are checked before coefficient computation. All 34 replacements use rounded
float32 alpha/beta bits, float64 multiply/add, and a float32 output cast. Every
original non-BN node, initializer and graph input/output remains intact in the
serialized diagnostic. Conv, activation and head arithmetic are unchanged there.

Both the preserved control and complete substitute run on all 152 training
inputs only, with disabled optimisation and the original CPU/thread settings.
No frozen test/held-out/stress pixels or quantisation calibration are used.
Original graph parity is measured separately from feature-tapped copies.
The actual original/tapped runtime graphs pass all 204 expression-node,
coefficient-bit, float32-boundary and 53 Conv/one Gemm count audits. ORT removes
unused BN initializers and expands HardSwish even at disabled optimisation;
the runtime audit does not assert byte identity of every other node.

[Aggregate evidence](../ml/reports/PLACEHOLDER-m4-promoted-bn1.json) records:

| Training comparison | Preserved control | Complete promoted BN |
| --- | ---: | ---: |
| Maximum raw-logit absolute error | 0.000240326 | 0.000189304 |
| Mean raw-logit absolute error | 0.0000558684 | 0.0000575436 |
| Maximum calibrated-probability absolute error | 0.00000279320 | 0.00000240022 |
| Mean calibrated-probability absolute error | 0.000000653101 | 0.000000667205 |
| Raw / probability budget violations | 26 / 29 | 23 / 32 |
| Frozen-threshold flips | 0 | 0 |
| Original / instrumented logit difference | 0 | 0 |
| Parity status | FAIL | FAIL |

The control reproduces previous evidence. Substitution lowers the maximum
errors while slightly increasing mean errors and probability violation count;
it still fails both fixed budgets. Feature maximum error also increases from
0.0000141859 to 0.0000162125, while induced Python-head maximum error decreases
from 0.000228882 to 0.000188351. These are diagnostic measurements, not causal
attribution or successful deployment. Saved state hashes match before/after.
The candidate is 6,255,113 bytes (runtime copy 6,156,135); it has no INT8 weights.

Separate audit verifies aggregate/private equality, recomputed parity, ordered
training IDs, source/model/dependency/preparation provenance and nine graph
records. All graphs, weights and ordered results stay ignored under data/.
Tests cover the complete arithmetic sequence including in-place timm
activations, unchanged graph connections, source/state preservation, runtime
audit corruption, invalid source parameters, training-only image isolation,
private output handling and stale provenance rejection. Float64 mobile support
and performance remain unverified. Exit 0 means DIAGNOSTIC ONLY; M4 stays open.

## Joint promoted stem/BatchNorm graph — ADR-018

**PLACEHOLDER diagnostic, never bundle.** Run to a new ignored output:

```bash
ml/.venv/bin/python -m numbra_ml.export_joint --output data/exports/PLACEHOLDER-m4-joint1
```

[ADR-018](../decisions/ADR-018-joint-promoted-stem-batchnorm.md) was committed
before the experiment. The command uses the same guarded training-only pipeline
as ADR-017, comparing preserved, BN-only and joint controls. It validates the
first saved stem Conv's parameters, geometry and graph-input connection, embeds
ADR-016's double patch/MatMul expression, and retains the float32 stem output.
All 34 BN substitutions and every remaining serialized node, original initializer
and graph interface are preserved. BN matching now validates only BN boundaries,
so it can compose with the independently validated stem substitution.

[Aggregate evidence](../ml/reports/PLACEHOLDER-m4-joint1.json): all 152 existing
training components, no frozen test/held-out/stress inference or quantisation fit.
Preserved and BN-only controls reproduce prior graph hashes and diagnostic
aggregates exactly. All comparisons FAIL the unchanged budgets.

| Training comparison | Preserved | BN-only | Joint stem/BN |
| --- | ---: | ---: | ---: |
| Max raw-logit absolute error | 0.000240326 | 0.000189304 | 0.000200748 |
| Mean raw-logit absolute error | 0.0000558684 | 0.0000575436 | 0.0000554888 |
| Max probability absolute error | 0.00000279320 | 0.00000240022 | 0.00000256741 |
| Mean probability absolute error | 0.000000653101 | 0.000000667205 | 0.000000648783 |
| Raw / probability violations | 26 / 29 | 23 / 32 | 25 / 32 |
| Frozen-threshold flips | 0 | 0 | 0 |

The joint graph has worse maxima than BN-only despite lower means. No statistic
changes the fixed acceptance result. Joint feature maximum drift 0.0000152588
and induced Python-head maximum error 0.000206947 are separate diagnostics;
maxima can occur on different inputs and cannot be added as causal accounting.
All original/tapped logit differences are zero; saved state hashes match.

Serialized joint size is 6,265,822 bytes; runtime copy 6,165,050. It is float32/
float64, with 52 Conv, one promoted MatMul and one Gemm, **no INT8 weights**.
Actual original/tapped runtime graphs pass exact BN/stem node, constant-bit and
float32-boundary audits. ORT adds default Reshape allowzero=0 even at disabled
optimisation; the composed expression declares it explicitly to retain exact
node-byte auditing. Unused original initializers are removed and HardSwish is
expanded at runtime; identity of every other runtime node is not claimed.

Separate audit checks report/private equality, recomputed parity, ordered
training IDs, source/model/dependency/preparation provenance, both retained
controls and 14 graph records. All graphs, weights and ordered details remain
ignored. Tests cover multi-pixel border/channel arithmetic through both timm
in-place activations, scope/parameter/geometry/cast/constant corruption, training
pixel isolation and stale provenance rejection. Exit 0 is DIAGNOSTIC ONLY.

## Complete same-input Conv/BatchNorm replay — ADR-019

**PLACEHOLDER diagnostic, never bundle.** Run to a new ignored output:

```bash
ml/.venv/bin/python -m numbra_ml.export_complete_replay --output data/exports/PLACEHOLDER-m4-complete-replay1
```

[ADR-019](../decisions/ADR-019-complete-same-input-replay.md) was committed
before execution. Selection follows saved module order and requires a one-to-one
match with every native Conv/BN graph node, including Conv without a following
BN. Exact saved parameter bits (including signed zero), Conv geometry, BN epsilon
and inference mode are validated, resolving only initializer/Identity aliases.
Both Python and preserved-ORT input origins are replayed for every operator.
All BNs retain three primitive expressions and the rounded float64 diagnostic,
plus both promoted affine coefficient recipes. No Conv is promoted in this run.

Isolated serialized and actual disabled-runtime native graphs must retain saved
parameters, geometry and float32 interfaces. Both promoted BN runtime expressions
must retain the declared double Cast/Mul/Add sequence, float32 coefficient bits
and single float32 output boundary. All graph checksums and complete aggregate
reconstruction are audited before the report is written. Exit 0 means diagnostic
evidence was generated; it cannot establish whole-model parity or close M4.

For each element, four signed float64 terms telescope to total boundary drift:
Python replay fidelity, propagation through the Python operator, same-input ORT
kernel difference, and extracted-versus-whole-graph execution difference. The
complete report records minima, maxima and means across component statistics,
including each term's signed extrema/mean and absolute extrema/mean. These are
per-boundary measurements; summing layer or component maxima is not causal
whole-model accounting. Individual component IDs, logits and rows stay ignored.

[Complete aggregate evidence](../ml/reports/PLACEHOLDER-m4-complete-replay1.json):
all 152 training components, 53 Conv and 34 BN nodes, 517 serialized/runtime graph
records. Python and ORT replay-fidelity errors, original/tapped logit changes and
both signed-accounting residuals are zero at every layer. Saved state hashes are
unchanged. The independent audit passes aggregate reconstruction, graph checksums,
ordered training IDs, saved-model/preparation/source/dependency provenance,
recomputed runtime audits and exact preserved-control ordered-logit/parity
reproduction. Audit performs no additional inference.

| Maximum across complete training replay | Conv (53 layers) | BN (34 layers) |
| --- | ---: | ---: |
| Native local kernel error, Python input | 0.00000190735 | 0.00000762939 |
| Native local kernel error, ORT input | 0.00000154972 | 0.00000762939 |
| Propagated input effect | 0.0000308752 | 0.000339508 |
| Whole-graph boundary drift | 0.0000309944 | 0.000339508 |
| Layers with nonzero local kernel maxima | 48 | 34 |
| Python / ORT replay fidelity | 0 / 0 | 0 / 0 |

The largest Conv local difference is at blocks.5.0.conv; largest propagated Conv
difference is at blocks.4.0.conv_dw. Largest native BN local difference is at
blocks.0.0.bn1, while largest propagated BN difference is at blocks.2.2.bn2.
Separate maxima can occur on different elements/inputs/layers. They cannot be
added as whole-model worst-case causal accounting or used to select a favourable
layer subset. Complete per-layer aggregates remain in the linked report.

| Promoted BN recipe / input origin | Max local error versus native Python | Layers with lower / equal / higher maxima than native ORT |
| --- | ---: | ---: |
| affine_rsqrt / Python | 0.00000381470 | 22 / 12 / 0 |
| affine_rsqrt / ORT | 0.00000762939 | 23 / 11 / 0 |
| affine_divide / Python | 0.00000762939 | 9 / 14 / 11 |
| affine_divide / ORT | 0.00000762939 | 9 / 18 / 7 |

Both promoted recipes agree exactly with their matching Python expressions at
all 34 BNs on both origins. Neither matches native Python across every tested
input at any BN layer. Counts compare maxima only; means and full-graph behavior
can differ. Original preserved parity is unchanged: FAIL, maximum raw/probability
error 0.000240326/0.00000279320, 26/29 violations, zero threshold flips. This
experiment creates no whole-model replacement or INT8 candidate, fits nothing
and never reads frozen test/held-out/stress inputs.

## Complete BN coefficient-rounding replay (ADR-020)

**PLACEHOLDER diagnostic only, never bundle.** The command
`python -m numbra_ml.export_bn_rounding --output data/exports/PLACEHOLDER-<new-name>`
retains ADR-019's complete native/operator/control audits, and evaluates all 32
predeclared coefficient/output recipes at every saved BN on both native-Python
and preserved-ORT inputs. It fits nothing and builds no replacement graph.

The five binary choices separately specify epsilon-sum, square-root/reciprocal,
alpha, beta and output rounding boundaries. Independent NumPy and eager PyTorch
implementations retain both engines' coefficient-bit records and native-relative
output errors; equality between library square roots is not presumed. Saved
float32 parameters and Python epsilon bits remain unchanged. The rounded-double
output is a mathematical diagnostic, not a hardware float32-FMA implementation.
Complete recipe/origin/layer scope, serialized/runtime graph audits, ordered
training inputs, coefficient reconstruction and aggregate reconstruction are
checked. Dictionary order is irrelevant; the explicit saved selection list
carries module order through JSON serialization. See
[the protocol](../decisions/ADR-020-batchnorm-rounding-replay.md).

[Complete aggregate evidence](../ml/reports/PLACEHOLDER-m4-bn-rounding2.json):
152 ordered training components, all 34 BNs and 32 recipes, both origins and
engines. Independent no-inference audit passes 517 graph records, coefficient
bits/reconstruction, aggregates, saved-state/model/preparation/source/dependency/
retained provenance, exact prior ADR-019 control logits/operator metrics and
preserved fixed-budget parity. No replacement graph or frozen inference.

| Declared recipes (all alpha choices included) | Count | Native-exact layers, Python / ORT origins | Max native error, Python / ORT origins |
| --- | ---: | ---: | ---: |
| e32-r32-a{32,64}-b64-o64 | 2 | 34 / 34 | 0 / 0 |
| e64-r32-a{32,64}-b64-o64 | 2 | 23 / 23 | 0.000000953674 / 0.00000143051 |
| Every remaining declared recipe | 28 | 0 / 0 | Up to 0.0000152588 / 0.0000152588 |

Exact means all tested inputs at that layer; this is finite training evidence,
not the native kernel's documented implementation or a mobile/unseen-input
claim. Both engines' outputs agree at every layer/origin for all 32 recipes.
Float64 reciprocal bits still disagree at 23 e32/r64 or 19 e64/r64 BNs, recorded
without changing the observed rounded float32 output. Complete individual recipe
and layer aggregates remain in the linked report. Preserved control remains FAIL:
raw/probability maxima 0.000240326/0.00000279320, 26/29 violations, zero flips.

## Complete rounded-affine BN candidate — ADR-021

The predeclared `e32-r32-a32-b64-o64` recipe replaces all 34 saved BNs in one
complete **PLACEHOLDER diagnostic** candidate. Each BN keeps original float32
input/output boundaries and float32 alpha/beta coefficients, with double Mul/Add.
Every other serialized node, initializer and connection remains intact. Independent
NumPy/eager-PyTorch coefficient bits must agree; missing layers, altered saved bits,
recipe/order changes and runtime expression corruption are rejected.

Command (repository root, existing environment and retained inputs):

```bash
ml/.venv/bin/python -m numbra_ml.export_rounded_bn --output data/exports/PLACEHOLDER-m4-rounded-bn2
```

[Aggregate evidence](../ml/reports/PLACEHOLDER-m4-rounded-bn2.json) covers all 152
ordered training component index images, preserved control and candidate only.
No test/held-out/stress inference or new quantisation fit. Model, calibration,
threshold and ADR-011 budgets remain unchanged. Separate feature taps produce
zero logit changes; original-graph parity is checked independently.

| Graph | Max raw error | Max probability error | Raw / probability violations | Flips | Bytes |
| --- | ---: | ---: | ---: | ---: | ---: |
| Preserved control | 0.000240326 | 0.00000279320 | 26 / 29 | 0 | 6,188,494 |
| Complete rounded BN | 0.000143051 | 0.00000183769 | 13 / 21 | 0 | 6,255,113 |

Both **FAIL** fixed raw/probability budgets 0.0001/0.000001. Candidate mean raw/
probability errors are 0.0000415946/0.000000485651. Better errors and zero flips
do not cancel numerical failures. Feature error max is 0.0000121593; induced
Python-head max error is 0.000142574. Remaining differences are not attributed
solely to Conv: activations, pooling/head and propagation also remain unchanged.

Coefficient audits PASS for all 34 saved BNs; serialized/runtime audits PASS for
204 declared arithmetic nodes, 136 Casts, 53 retained Conv and one Gemm. The
independent no-inference audit rechecks eight graph records, complete ordered
input scope, parity/failure/feature aggregates, tap accounting and saved-model/
preparation/source/retained/dependency/source-code provenance. Native Python and
preserved-control ordered logits reproduce ADR-020 exactly. Private audit:
`data/exports/PLACEHOLDER-m4-rounded-bn2/PLACEHOLDER-independent-audit.json`, SHA-256
`1388700ac2588a7a4334f4145303f5f59e99650fbb65ba4ae3e23bcd80c3b825`.

The first complete run remains retained in
[its aggregate report](../ml/reports/PLACEHOLDER-m4-rounded-bn1.json). A subsequent
prior-control audit failed because it assumed ADR-020's protocol had temperature/
threshold fields. Corrected the audit to bind fits via the exact saved-run hash,
with a regression matching the actual schema; regenerated the second run with
current source hashes. Both runs' graphs, details and artifact aggregates match
exactly. This fix changes no inference arithmetic or acceptance budget.

## Fixed training-only runtime profiles (ADR-022)

The new `numbra_ml.export_runtime_profiles` command reuses the unchanged ADR-021
rounded-affine graph and preserved control. It verifies prior complete evidence
before opening training images, runs every disabled/basic/extended/all profile,
and retains original and separate feature-tapped runtime graphs. No quantisation
fit or test/held-out/stress inference occurs. All results remain **PLACEHOLDER
diagnostic only, never bundle**.

```bash
ml/.venv/bin/python -m numbra_ml.export_runtime_profiles --output data/exports/PLACEHOLDER-m4-runtime-profiles1
```

[Aggregate evidence](../ml/reports/PLACEHOLDER-m4-runtime-profiles1.json) covers
all eight artifact/profile comparisons on all 152 ordered training index images.
Every comparison **FAILS** fixed raw/probability budgets 0.0001/0.000001;
every comparison has zero frozen-threshold flips and zero feature-tap changes.

| Graph | Profile | Max raw error | Max probability error | Raw / probability violations |
| --- | --- | ---: | ---: | ---: |
| Preserved control | disabled | 0.000240326 | 0.00000279320 | 26 / 29 |
| Preserved control | basic | 0.000365257 | 0.00000465196 | 40 / 50 |
| Preserved control | extended | 0.000365257 | 0.00000465196 | 40 / 50 |
| Preserved control | all | 0.000323296 | 0.00000411753 | 36 / 44 |
| Rounded BN | disabled | 0.000143051 | 0.00000183769 | 13 / 21 |
| Rounded BN | basic | 0.000143051 | 0.00000183769 | 13 / 21 |
| Rounded BN | extended | 0.000143051 | 0.00000183769 | 13 / 21 |
| Rounded BN | all | 0.000310421 | 0.00000394886 | 11 / 15 |

BN-expression semantic audits PASS for all original and tapped candidate runtime
graphs. Disabled retains all 204 expression nodes and 68 coefficient Casts;
basic/extended/all fold those 68 Casts into exact float32-to-double coefficient
bits and retain 136 expression nodes. Every double input/Mul/Add/float32 output
boundary remains audited. Extended changes 18 candidate Conv nodes to FusedConv;
all retains 53 Conv and adds 43 ReorderInput / 44 ReorderOutput operators. Basic
folds control BNs into Conv, extended has 23 FusedConv, and all adds layout reorder
operators. These are observed graph inventories; arithmetic equivalence outside
BN and Android support remain **UNVERIFIED**. No profile is selected for deployment.

Independent no-inference audit PASS: 20 graph records (four serialized artifact/
tap records and sixteen runtime records), all profile/input/reference scope,
fixed-budget parity/failure reconstruction, feature aggregates/tap accounting,
saved parameter/epsilon/coefficient bits, current code/dependency provenance and
saved-model/preparation/retained/source/prior hashes. Disabled details reproduce
ADR-021 exactly for both graphs. The private audit is
`data/exports/PLACEHOLDER-m4-runtime-profiles1/PLACEHOLDER-independent-audit.json`,
SHA-256 `ecde48f2f7b89dd3107b5b3908b2470102671983b6f45e634896b8b3bfbe351f`.

Generated regression tests also compare every tapped runtime BN output exactly
to an independent NumPy expression on its **actual runtime input** under every
profile, including a cancellation fixture. An initial version incorrectly used
native Python inputs across upstream hard-swish rounding differences and failed
four assertions. Corrected input isolation retains exact output equality and
unchanged production arithmetic/budgets. Corrupted constant bits/types, Casts,
Mul order, alias cycles, omitted layers/profiles, stale prior evidence and
rehashed ordered details must still fail. Original evidence remains unchanged.

## ADR-023 remaining-operator preflight (no baseline inference)

[ADR-023](../decisions/ADR-023-remaining-operator-replay.md) declares two stages:
complete static scope and tested isolated primitives, followed by complete native/
tapped training replay. The first stage is implemented in
`numbra_ml.export_remaining`; **the second stage is still unimplemented**.

```bash
ml/.venv/bin/python -m numbra_ml.export_remaining \
  --output data/exports/PLACEHOLDER-m4-remaining-preflight2
```

The command refuses an existing output or aggregate report. Use a new
PLACEHOLDER name for a fresh reconstruction. No image decoding, model forward
call or baseline ONNX runtime session occurs. Observed execution additionally
blocked all three paths with raising guards. Saved weights/fits, prior graphs,
preparation/ordered training scope and dependency/code provenance are verified.

[Preflight evidence](../ml/reports/PLACEHOLDER-m4-remaining-preflight2.json)
accounts for every 160 serialized preserved-graph node: 87 saved Conv/BN controls,
72 remaining operators and one Constant. All 212 initializers are checked against
the unchanged rounded graph. The complete remaining scope is 19 HardSwish,
14 Relu, nine each HardSigmoid/ReduceMean/Mul, six Add, and one each
GlobalAveragePool/Flatten/Sub/Div/Gemm/Squeeze. Every remaining/control node is
byte-identical across the two graphs; saved head constants are checked against
native saved bits, including signed zero. Ordered positions, connectivity,
static dtype/shapes, attributes and hashes are explicit. Independent complete
no-inference reconstruction PASS means **static preflight only**, not parity.

Generated-fixture tests exercise every isolated remaining primitive, both binary
operands, broadcasting, repeated operands, negative squeeze axes, and exact
serialized/runtime expressions. Disabled ORT adds unused domain imports and
expands HardSwish into HardSigmoid/Mul even with optimisation disabled. Audits
allow only that precise declared expression with alpha=float32(1/6), beta=0.5,
unchanged connections and float32 boundaries; other rewrites fail. Native eager
hard-swish rounding drift is retained as measured signed errors. Independent
recipes are explicitly **not captured native model outputs**.

Initial new tests exposed Identity-alias fixtures and unused imports; the next
run isolated the HardSwish function expansion. These tooling errors were fixed
in code and fixture constant resolution, with corruption regressions. Existing
tests and ADR-011 budgets remain unchanged. Reports contain no baseline replay
results or clinical claim; every failed export remains rejected.

The original preflight remains retained. A post-commit audit exposed that its
auditor compared historical git commit/dirty fields with the current checkout.
The corrected auditor validates that the recorded commit exists and the dirty
flag is boolean, preserves both as historical context, and still reconstructs
all other fields exactly, including current code/dependency hashes. New
regressions cover changed current checkout context and invalid recorded metadata.
The second report regenerates provenance after the fix; complete plan, graphs,
scope, saved-model/preparation/prior records reproduce the first report exactly.
There is no inference-expression change or additional baseline inference.

## ADR-023 native capture primitives — 2026-10-09 UTC

[Native mapping evidence](../ml/reports/PLACEHOLDER-m4-native-mapping1.json)
binds all 159 computational nodes (87 Conv/BN controls and 72 remaining operators)
to exact saved module owners and native types. The one Constant remains explicit
in the original static inventory. Complete scope, saved model/preparation/prior
provenance, graph hashes and all tap specifications reconstruct independently
without image decoding, module forward calls or ORT sessions; raising guards
blocked all three during saved-baseline mapping. This PASS means **static mapping
only**, with no new saved-baseline arithmetic/parity result.

`export_remaining_native.native_plan` validates exact exporter scope, owner type,
geometry, saved constants and the complete ordered computational scope before
inference. `capture_native` observes actual native calls under their owning
modules with `TorchFunctionMode`. It copies every operand before execution and
every output immediately afterwards, including pre-activation BN values and
both residual/SE operands. It verifies each operand against its declared graph
producer or exact constant, and rejects extra, missing or reordered calls,
unsupported settings, shared owners, foreign hooks, changed state or boundaries.
It calls the original saved forward; eager recipes are separate comparisons.
Hooks and interception are removed after success or exceptions.

`native_fidelity` reports unsuppressed signed differences and bit equality for
every remaining recipe versus its captured output. Generated-only tests use both
a small residual/SE fixture and the full mobile architecture with new random
weights, no checkpoint download or saved M3 artifact. On the full generated
fixture, capture covers all 159 operations and every one of the 72 remaining
recipes reproduces the captured native result bit-for-bit; captured/untapped
native whole logits also match exactly. This is **generated-fixture evidence**,
not saved-baseline or export parity evidence.

`tap_complete_graph` adds every original operand/output, including constants and
int64 axes, to both declared graphs without changing computation or initializer
bytes. It checks original graph binding, full original boundary order (including
all replaced BN boundaries), and shape/dtype. Internal double BN values are not
original boundaries. Generated disabled-ORT original/tapped logits agree exactly
on both graphs. Actual runtime expression audits and per-origin isolated replay
on the saved training inputs are still unimplemented in this runner.

The new suite has 39 PASS, including failure cleanup/reuse, altered native
operands/settings, signed-zero preservation, unsuppressed drift, partial/reordered
mapping rejection, invalid inputs and explicit no-inference mapping guards.
Initial runs exposed missing Tensor-method metadata, binary dispatch aliases,
rounded-graph double intermediates and a fixture without its asserted ReLU.
Fixed capture/tap code and added ReLU to the fixture; exact assertions and all
existing parity budgets remain. The original preflight reports remain historical:
current-code audits intentionally change when source changes. The new mapping
report records this implementation's complete source/dependency provenance.

## ADR-023 complete runtime foundation — 2026-10-09 UTC

`export_remaining_runtime.CompleteRuntime` constructs separate original and
fully tapped disabled-optimisation CPU sessions using the fixed two intra-op/one
inter-op thread configuration. It audits their serialized and actual runtime
graphs before running any caller-supplied tensor; it has no saved-baseline or
dataset CLI. All runtime expressions, constants and static boundaries are
accounted for, including internal rounded-BN double arithmetic. Audit PASS means
the declared expressions remain intact, never numerical agreement with Python.

Generated fixtures show the pinned runtime reschedules independent nodes,
lowers tensor Constant to an identical initializer, reorders attribute records
and materializes specific operator defaults. The auditor binds every original
node by output and exact name/operator/ordered operands, validates topological
execution, and permits only the bounded default attributes, bit-identical
Constant lowering and the previously declared HardSwish function expansion.
Every runtime node is checked exactly once. It records runtime node order,
operator inventory and graph hashes; changed weights, aliases, coefficients,
casts, operands, domains, attributes, interfaces or extra boundaries fail closed.

Each supplied input produces separately measured original/tapped logits and
the complete original operand/output tuples. All taps must have the declared
shape/dtype; input and constant bits must match exactly. Instrumentation changes
are reported as signed metrics without a numerical suppression threshold.
Both feed dictionaries remain alive until output copies are complete because
ORT pass-through taps can alias input memory. Returned arrays are independent of
subsequent runs and the caller's input. Signed four-term accounting now supports
head/flatten output ranks as well as NCHW, retaining finite nonempty float32,
same-shape and exact telescoping checks; Conv/BN input validation is unchanged.

The combined generated-fixture suite has 129 PASS. Both complete random mobile
graphs account for all 159 original computational nodes and 373 original tap
boundaries; every runtime expression passes the audit and original/tapped
logits agree bit-for-bit on the fixed generated input. Corruption tests cover
HardSwish ordering/attributes, all rounded-BN expression stages, exact constant
bits including signed zero, alias connections, extra nodes/boundaries and invalid
interfaces. Initial runs exposed independent scheduling and input-buffer lifetime
bugs; corrected both, retaining exact assertions. Fixture errors in test-only
protobuf access and the promoted-node prefix were also corrected.

This iteration runs no saved model forward, training image decoding, baseline
ORT inference, quantisation fit or frozen evaluation. Earlier static report
source hashes remain historical; no new saved-baseline reconstruction or parity
PASS is claimed. Complete training replay and ordered-detail auditing remain
unfinished, and all earlier failed deployment exports remain rejected.

## Complete supplied-tensor replay integration — ADR-023

`export_remaining_replay.CompleteReplay` combines the native capture and
complete runtime foundations on one supplied diagnostic tensor. It has no
saved-model or dataset entry point. Before the first forward call it builds
both original/tapped whole-runtime pairs and all isolated expressions, audits
every runtime node/constant/boundary, and independently rebuilds the rounded-BN
serialized graph from the saved coefficients and fixed ADR-021 recipe. This
last check protects against changed serialized coefficients that a runtime
audit against the same supplied graph would not detect.

Every original computational node has an explicit isolated graph. All operands
remain inputs, including binary operands, saved weights and squeeze axes; their
order, shape, dtype and repeated-operand bits are checked. Rounded BN uses the
actual rounded expression as its isolated candidate, with the preserved native
ONNX operator retained as a control. Run both exact native and runtime operand
tuples on both unchanged graphs. Keep all three BN primitive formulas, both
promoted affine formulas, float64 reference expression, all 32 rounding recipes
on both independent engines, and every saved Conv control. Record both local
kernel origins and full four-term signed accounting at every output rank.
Separate original/captured native logits and original/tapped runtime logits
retain all instrumentation changes; no discrepancies are suppressed.

`reconstruct_row` rebuilds every signed metric from retained arrays without
running a model, eager recipe or runtime. It validates complete ordered operator,
graph, operand, origin and control scope; source graph/plan binding; all tensor
specifications; exact constant/axis bits; and exact native/runtime producer
lineage through the final logits. All controls retain both differences from
native eager results and paired recipe/engine differences. The arrays are
observations: this audit does not independently recalculate their inference
results or authenticate their historical origin. The future complete runner
must bind persisted ordered rows and reconstructed aggregates to selected
saved/source/preparation evidence and independently verified ADR-022 reports.

Generated-only integration tests cover the complete random MobileNet
architecture (159 computations: 53 Conv, 34 BN and 72 remaining nodes), both
graphs and both origins. They also cover input/state/mode/hook rejection before
inference, missing or altered scope, saved constants, axes, boundary lineage,
nonzero native replay/instrumentation drift, exact serialized rounded expression
and coefficient corruption, and unconditional capture cleanup on failure.
Weights and input tensors are generated anew; no saved M3 forward or existing
training image is used. Observed test outcomes are recorded in JOURNAL.

## Complete ordered evidence persistence — generated fixtures only

`export_remaining_evidence` persists supplied replay observations only below
ignored `data/` in fresh `PLACEHOLDER-*` directories. Every nonempty finite
float32/int64 array is stored losslessly and addressed by its dtype, shape
and exact C-order bytes. Identical arrays share a file, including repeated saved
parameters and identical control outputs. This removes redundant storage without
dropping an operator, origin, graph, control or bit. Explicit ordered dictionary
trees preserve scope order even when JSON serializers sort object keys. Files
and decoded bits have separate checksums; decoding forbids pickle and symlinks.

The writer accepts one declared ordered component at a time. It reconstructs
its complete row metrics and requires original native/runtime logit bits to
match the supplied ADR-022 disabled observations before writing that row. An
incomplete run has no completed index. Original/captured and original/tapped
instrumentation differences remain recorded and unsuppressed. Fits and ADR-011
budgets remain unchanged; no quantisation or deployment decision is made.

`audit_ordered` streams the retained rows without image decoding, eager recipes,
model forward or runtime session creation. It validates exact component order,
complete file/array/row scope, each checksum/specification, all existing
operator/operand/constant/lineage checks, every row metric, every numeric/boolean
aggregate leaf and both original-graph parity reports. It repeats exact prior
original-logit checks, including signed-zero bits. The aggregate contains no
component IDs, logits or individual failure observations; these stay ignored.

This API does **not** reconstruct saved-model/preparation/source/dependency or
ADR-022 report provenance. Its caller must independently verify those artifacts
before supplying the prior details and scope. Generated tests use two newly
generated tensors and a new random miniature architecture containing Conv/BN,
activation, residual, SE, pooling and head arithmetic. Their prior observations
come from that same fixture, rather than the saved M3 model. The tests establish
persistence/checking mechanics, never selected-baseline numerical parity or
historical inference authentication. During that foundation iteration, no existing
ordered training image or saved M3 forward was opened. Observed test results are
in JOURNAL; the later selected full replay is described below.

## Remaining M4 work

The first complete selected runner attempt stopped before image decoding when
disabled ORT removed 136 directly unused original BN initializers from the
rounded graph. The runtime audit now records and permits only original
initializers without any node consumer or graph input/output role to disappear.
Identity aliases, tapped parameters and lowered Constant outputs remain
mandatory. Every retained constant keeps its exact bits/type/shape; extra
constants and unexplained missing boundaries still fail. Generated nondefault
BN fixtures exercise both the removal and the tapped retention paths; corruption
regressions preserve live/alias/input/output/Constant and signed-zero checks.
The failed directory remains incomplete and cannot produce accepted evidence.

**PLACEHOLDER storage workaround:** the second full attempt was deliberately
interrupted after 25 ordered rows, without a completed index/report. Its roughly
28 seconds/input rate plus complete audits risked the documented default
90-minute iteration limit. New files use lossless uncompressed NPZ, preserving
all content-addressed tensor bits/dtypes/shapes, exact file checksums, ordered
scope and full reconstruction. Previous compressed evidence is never rewritten;
the reader accepts either archive format with independent bit/file verification.
Actual ZIP_STORED and both-format bit regressions pass. One retained row's storage
benchmark is 2.336s, 457,326,160 archive bytes vs 412,322,311 compressed bytes;
this is resource evidence only, not complete-run parity or provenance acceptance.
All earlier partial runs remain diagnostic and incomplete.

[Complete selected training evidence](../ml/reports/PLACEHOLDER-m4-remaining-training3.json)
now covers all 152 ordered training components, 159 computational nodes (53
Conv, 34 BN, 72 remaining), both unchanged preserved/rounded graphs and both
input origins. All Conv/BN primitive/promoted/32-recipe/two-engine controls
remain. Actual setup reconstructs 904 serialized/runtime graphs before image
decoding; final runner reconstruction PASS precedes report publication. All
original native and original runtime logits exactly reproduce the ADR-022
prior bits. Model state/fits/preprocessing/profile/budgets are unchanged.
[Separate guarded audit](../ml/reports/PLACEHOLDER-m4-remaining-training3-audit.json)
PASS: complete saved/preparation/retained/source/dependency/prior context,
904 setup graphs, every ordered array/metric/lineage, original parity and exact
prior-logit bits reconstructed with image decode, native module calls, ORT
sessions, eager recipes and evidence writes blocked. It runs no inference and
does not authenticate historical execution. Audit/summary/ignored and tracked
report fingerprints agree exactly. Current runner source snapshot
`50f7c65e7b6a6168a17d498be4d663c89b11742f` independently matches all 33 Python
source hashes and the full tree; live dependency pins remain exact.

[Readable aggregate summary](../ml/reports/PLACEHOLDER-m4-remaining-training3-summary.json)
is derived from the complete report and checksum-bound index, never additional
inference. All 159 native replay fidelities and uncaptured/captured native logits
are exact; both whole original/tapped logits are exact; every four-term signed
telescoping residual is zero. Isolated-versus-whole execution is exact at 158
nodes; Gemm alone differs (max 0.0000152588 preserved / 0.0000114441 rounded).
Isolated head operands include explicit parameters; whole-graph parameters are
constants. A constant-preserving head isolation check should examine this
execution-context difference. A kernel-packing explanation is **UNVERIFIED**.

Same-native-input maxima across every declared layer and all 152 inputs:

| Operator | Layers | Preserved max error | Rounded max error |
| --- | ---: | ---: | ---: |
| Conv | 53 | 0.00000190735 | 0.00000190735 |
| BatchNormalization | 34 | 0.00000762939 | 0 |
| HardSwish | 19 | 0.00000381470 | 0.00000381470 |
| Relu | 14 | 0 | 0 |
| ReduceMean | 9 | 0.00000572205 | 0.00000572205 |
| HardSigmoid | 9 | 0.0000000596046 | 0.0000000596046 |
| Mul | 9 | 0 | 0 |
| Add | 6 | 0 | 0 |
| GlobalAveragePool | 1 | 0.00000286102 | 0.00000286102 |
| Flatten / Sub / Div / Squeeze | 1 each | 0 | 0 |
| Gemm | 1 | 0.00000381470 | 0.00000381470 |

All 34 rounded BNs match native exactly on both origins. Every HardSwish,
HardSigmoid, ReduceMean, final pool and Gemm has nonzero same-input drift;
48/53 Conv also do. Relu/Mul/Add/Flatten/Sub/Div/Squeeze are exact on both
origins. These finite local measurements do not establish a whole-model fix.
Head four-term propagation maxima are 0.000228882 preserved / 0.000142574
rounded, with separate same-runtime-input kernel maxima 0.00000381470 /
0.00000762939 and extraction maxima above. **Do not add these separate maxima**
as an exact worst-case accounting; full signed per-component decomposition is
retained under ignored data/.

Original graph parity still **FAILS**: preserved max raw/probability
0.000240326/0.00000279320 (26/29 violations); rounded
0.000143051/0.00000183769 (13/21 violations). Zero threshold flips for both.
Native reference, full-precision temperature/threshold and ADR-011 budgets
remain unchanged. No new selected quantisation fit or frozen evaluation.

The completed index retains 481,293 unique arrays: 68,554,263,856 archive bytes
and 68,427,202,504 decoded array bytes. Arrays, private observations, graphs,
weights and setup records remain ignored. Only aggregate reports are tracked.
Historical ADR-022 source still binds to
`808cc3393ccf1cce95c2feeef91e5a8608b481e4`; current runner source/dependencies/
hardware remain exact. Local reconstruction never authenticates past inference.

[ADR-024](../decisions/ADR-024-bounded-remaining-arithmetic.md) now predeclares
bounded complete activation/reduction recipes and constant-preserved head
isolation. The supplied-graph primitives in `export_remaining_arithmetic`
are built and generated-only tests pass. **Guarded retained training replay
is still unimplemented**; there is no new selected-baseline parity result.

Each HardSigmoid uses float32 `clamp(x+3,0,6)` followed by either division by
six or multiplication by the rounded float32 reciprocal. Each HardSwish first
multiplies that clamp by x, then applies the same two fixed alternatives. Every
operation retains its own float32 boundary. ReduceMean/GlobalAveragePool use
either float32 ReduceSum/divide or double ReduceMean with one final float32
cast. These recipes are diagnostic hypotheses, never native reference replacements.
Gemm retains its exact original initializer/Constant/Identity dependency closure,
only the activation as an input, and its original node/attributes. Existing
all-input isolation remains a separate control.

`complete_arithmetic_scope` first runs existing complete saved/control/head
validation and returns every target in original order. A full random mobile
fixture has 39 target nodes and 77 recipe graphs, identical across its preserved
and rounded contexts, with all 87 Conv/BN controls still validated. Static scope
construction blocks decode, model forward and runtime session construction in
tests. Serialized audits independently rebuild complete recipe bits/interfaces;
actual disabled-runtime audits reuse ADR-023's unchanged complete auditor.
Generated fixtures check clamp/signed-zero boundaries, distinct division and
reciprocal arithmetic, double-reduction cancellation, original head/alias bits,
invalid operands/overflow, and serialized/runtime corruption rejection.

The generated constant-head fixture has nonzero ORT/eager linear drift;
`expression_metrics` retains signed/max/mean discrepancies with no suppression
or equivalence assertion. Exact isolated-versus-original constant-context ONNX
equality is verified for that fixture. This does not resolve the selected head's
extraction discrepancy or establish kernel-packing causality.

Next integrate these primitives with complete verified ADR-023 retained
observations, including an explicit exact historical source snapshot after code
changes. Keep every existing Conv/BN/remaining control and all ordered training
inputs on both graph/input origins. Resolve float arithmetic before choosing a
selective QDQ scope, fitting or using frozen acceptance inputs.

An explicit selective static QDQ scope must still be declared from training
evidence before a new quantisation fit or frozen evaluation. Float64 mobile
compatibility/performance remains unresolved. ADR-012's labelled toy workaround
is diagnostic only. No accepted export, deployment-metadata package or M4 review
request exists; Android ABI/decode/device work remains M5–M8.

## Open questions

- Will the real frozen-feature graph meet strict quantised raw/decision parity?
- What runtime/operator/ABI, footprint and latency will the actual export measure?
- Do humans approve pending weight notices/rights and the engineering budgets?

## Confidence

High for observed desktop conversion/quantisation, size, aggregate arithmetic and
rejection of failed parity. No accepted baseline export, mobile execution or
clinical validation evidence.
