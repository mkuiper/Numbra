# Status

Updated: 2026-10-09T15:30:37Z

Current milestone: **M4 — On-device model export**, in progress. NEXT_ACTION:
CONTINUE. M0–M3 gates exist (PASS WITH CHANGES); no M4 gate, app or APK.
Every task model/result remains **PLACEHOLDER**, synthetic-only under ADR-002.
Retained baseline exports remain rejected; graph copies are diagnostic only.

## M4 acceptance status

- **Quantised ONNX Runtime Mobile export: BUILT, ACCEPTANCE INCOMPLETE.** Two
  retained INT8 QDQ graphs (53 quantised Conv/one Gemm each) fail parity. All/only
  152 training components calibrated them. No new quantisation fitting this
  iteration; Android/ABI support unverified. Toy diagnostic workaround remains.
- **Exported/Python parity: FAIL, budgets unchanged.** Original float/INT8 and
  BatchNorm-preserved complete-model failures retained. Preserved/disabled
  training max raw/probability errors remain 0.000240326/0.00000279320, exceeding
  0.0001/0.000001. This iteration makes no new complete-model parity or frozen
  test/held-out/stress inference, saved-reference/fit/budget change or selection.
- **Size ≤20 MB / preprocessing written and tested: BUILT.** Retained float
  6,095,579 bytes, preserved diagnostic 6,188,494, INT8 1,730,515/1,861,702.
  RGB letterbox/normalisation and float32 1×3×224×224 → raw_logit [1] unchanged.
  No accepted deployment metadata package or Android decoding/preprocessing.

## This iteration's evidence

- ADR-015 predeclares same-input replay of first stem/first depthwise Conv and
  their immediately following saved BN nodes, selected by order/connectivity.
  Queued for humans. No clinical/deployment authority implied.
- New numbra_ml.export_replay verifies preparation, selected saved model/run,
  retained experiments and corrected preserved graph/report/details provenance
  before inference. Hooks capture exact inputs/raw pre-activation outputs and
  clean up on failure. Exact operators and three fixed BN primitive formulas
  are extracted/built, labelled never bundle, and audited after disabled ORT
  optimisation. Existing sequential/two intra-op/one inter-op settings retained.
- ml/reports/PLACEHOLDER-m4-replay1.json: all 152 training components only.
  Python and ONNX replay fidelity, tapped/original logit differences and signed
  telescoping residuals are zero on these inputs. Saved state hashes unchanged.
- Same-input local kernel maxima (both input origins): stem Conv 0.000000476837,
  stem BN 0.000000953674, first depthwise Conv 0.000000119209, its BN
  0.00000762939. Corresponding propagated input-effect maxima: 0, 0.00000667572,
  0.000000953674, 0.0000457764. Signed per-element accounting separates local
  arithmetic, propagation and extraction effects; separate maxima are not additive.
- Subtract/divide/scale/add, affine rsqrt and affine divide-by-sqrt BN formulas
  each have exact Python/primitive-ORT agreement on both input origins. None
  eliminates native-Python BN differences. Rounded float64 formula also differs.
  No claim of full-backbone causation, a precision fix, or improved model parity.
- Separate aggregate audit checks current source, graph/runtime/detail hashes
  and equality of tracked/private aggregate copies. Graphs, weights, component
  details and tensors stay ignored. Documentation and human queue updated.

## Observed verification

- First new suite: 5 PASS, 1 FAIL (5.59s). Guard incorrectly required boundary
  diagnostics on a passing toy export, which ADR-014 legitimately omits. Fixed
  code to allow absence only when every preserved profile passes and to reject
  invalid boundary evidence. No failing test deleted/skipped/weakened.
- Next subset: 6 PASS in 5.99s, 16 exporter warnings. Full suite includes added
  swapped-graph/invalid-boundary rejection cases and non-training pixel corruption.
- Replay CLI exit 0: DIAGNOSTIC ONLY, M4 incomplete.
- bash scripts/check.sh: exit 0, 324 ML tests PASS in 43.92s, 50 legacy exporter
  warnings; Android SKIPPED, RESULT PASS. No APK claim. Root contract suite:
  6 PASS in 0.065s after documentation/iteration records; diff whitespace clean.
- No toolchain/dependency/checkpoint/dataset acquisition, protected edits,
  review.sh run, review/check/gate files written, publish/push or messages.

## Open blockers and limits

Selected-baseline float and INT8 parity remains the implementation blocker.
BatchNorm preservation and the fixed local BN formulas do not solve it. Existing
exports remain rejected; no M4 HANDOFF/review request. Clinical data approval,
clinical/ethics/legal/native-language validation and weight-notice approval are
absent. Finite desktop training diagnostics do not establish unseen-input parity,
mobile compatibility or clinical performance.

## Next concrete step

Predeclare and test promoted-precision stem Conv accumulation (explicit
Pad/Slice/MatMul plus cast) and fused-affine BN emulation on the same training
inputs. Retain saved float32 weight bits, stage boundaries, native Python
reference and ADR-011 budgets; higher precision may still disagree with native
float32 rounding. Choose a complete graph arithmetic/precision and explicit
quantised scope using training evidence before new frozen evaluation. Request
REVIEW M4 only when every acceptance item is met.
