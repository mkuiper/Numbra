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

## Remaining M4 work

BatchNorm preservation and complete promoted BN substitution both fail parity.
Next predeclare a joint training-only graph combining the already declared
promoted stem Conv patch/MatMul expression with complete promoted BN, retaining
all other Conv/head nodes and float32 stage boundaries. Compare to the preserved
and BN-only controls before choosing quantised scope. ADR-016's local promoted
stem Conv did not lower its native-Python maximum, so improvement is uncertain;
do not assume higher precision fixes the contract. A selective static QDQ scope
must be explicitly declared and justified from training evidence before any
new frozen evaluation; float64 mobile compatibility also needs resolution.
Keep every failure, original reference, fits/inputs and ADR-011 budgets. The toy
model stays diagnostic only.
No passing deployment artifact, runtime-metadata package or M4 review request
exists. Android runtime/ABI/decode and device performance remain M5–M8 work.

## Open questions

- Will the real frozen-feature graph meet strict quantised raw/decision parity?
- What runtime/operator/ABI, footprint and latency will the actual export measure?
- Do humans approve pending weight notices/rights and the engineering budgets?

## Confidence

High for observed desktop conversion/quantisation, size, aggregate arithmetic and
rejection of failed parity. No accepted baseline export, mobile execution or
clinical validation evidence.
