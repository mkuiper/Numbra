# Status

Updated: 2026-10-09T15:18:10Z

Current milestone: **M4 — On-device model export**, in progress. NEXT_ACTION:
CONTINUE. M0–M3 gates exist (PASS WITH CHANGES); no M4 gate, app or APK.
Every task model/result remains **PLACEHOLDER**, synthetic-only under ADR-002.
Retained baseline exports remain rejected; new graph copies are diagnostic only.

## M4 acceptance status

- **Quantised ONNX Runtime Mobile export: BUILT, ACCEPTANCE INCOMPLETE.** The two
  retained static INT8 QDQ graphs have 53 quantised Conv/one Gemm each, but both
  fail parity. All/only 152 training components calibrated them. No new
  quantisation fit in this iteration; Android/ABI compatibility unverified.
- **Exported/Python parity: FAIL, budgets unchanged.** New BatchNorm-preserved
  float/disabled training max raw/probability errors 0.000240326/0.00000279320
  exceed fixed 0.0001/0.000001 budgets, with zero flips. Other new profiles also
  fail. Original frozen test/held-out/stress failures retained unchanged; no
  new frozen evaluation inference or selection. Saved model/inputs/fits unchanged.
- **Size ≤20 MB / preprocessing written and tested: BUILT.** New preserved float
  diagnostic 6,188,494 bytes; original float 6,095,579 and INT8 1,730,515/1,861,702.
  RGB letterbox/normalisation and float32 1×3×224×224 → raw_logit [1] unchanged.
  No accepted deployment metadata package or Android decoding/preprocessing.

## This iteration's evidence

- ADR-014 predeclares BatchNorm preservation, disabled/all runtime audits and
  complete Conv/BN boundary taps if still failing; queued for humans.
- New numbra_ml.export_batchnorm uses legacy opset 17, folding disabled and
  PRESERVE with every module eval. Export/disabled-runtime graphs retain all 34
  inference-only BN nodes; all optimisation removes all 34. Both original and
  feature-tapped sessions' actual serialized runtime graphs are audited.
- Fresh folded control before diagnostic marking is byte-identical to retained
  original float graph. Saved model state hashes before/after match. Aggregate
  source/model/run/graph/detail hashes separately checked against current files.
- Corrected ml/reports/PLACEHOLDER-m4-batchnorm2.json: all 152 training inputs.
  Folded/disabled raw/probability maxima 0.000365257/0.00000465196, 40/50 numeric
  violations; preserved/disabled 0.000240326/0.00000279320, 26/29; folded/preserved
  all profiles each 0.000323296/0.00000411753, 36/44. Every profile FAILS; zero
  flips throughout. Head instrumentation has zero logit changes on these inputs.
- Preserved/disabled max feature drift 0.0000141859, induced Python-head error
  0.000228882, remaining head/runtime error 0.0000152588. Maxima can occur on
  different components and cannot be added as an exact decomposition.
- Corrected 53 Conv + 34 BN boundary taps report every matched boundary. Stem
  Conv drift 0.000000476837, stem pre-activation BN 0.00000667572, first depthwise
  Conv 0.000000953674 and its BN 0.0000457764. Boundary instrumentation logit
  changes are zero. These are accumulated output differences, not isolated
  operator-local error or causal evidence.
- First report's boundary attribution explicitly INVALID: initial hooks compared
  timm combined BN/activation outputs after activation to ONNX before activation.
  Tracked aggregate adds an erratum/original-report hash; ignored originals stay
  unchanged. Original-graph parity/head-feature results remain valid. Corrected
  pre-hooks at drop input copy before in-place activation, with ReLU/HardSwish
  negative-input regressions. Corrected rerun uses the same complete training set.
- No new frozen/stress inference, weights/fit/input/budget change, quantisation
  fit or deployment selection. ADR-012 toy diagnostic workaround remains in force.
  All runtime/tapped copies have PLACEHOLDER diagnostic/never-bundle notices;
  ORT's all-profile optimized graphs may be hardware-specific.

## Observed verification

- Initial new suite: **4 PASS in 5.69s**. Corrected/expanded suite: **6 PASS in
  5.85s**, 16 warnings. Isolation test corrupts every non-training index image;
  original artifact hashes preserved; provenance tampering rejected; BN runtime
  counts, correct fused-activation taps and hook cleanup on exceptions checked.
- Both diagnostic CLIs exit 0: DIAGNOSTIC ONLY, every original-graph profile fails.
- bash scripts/check.sh: exit 0, **318 ML tests PASS in 39.53s**, 34 exporter
  deprecation warnings; Android SKIPPED, RESULT PASS. No APK claim.
- Root contract suite: **6 PASS in 0.064s**. No existing test weakened/skipped.
  No toolchain/dependency/model/dataset acquisition, protected edits, publish/push
  or outbound messages. Existing 42-package export lock retained.

## Open blockers and limits

Selected-baseline float and INT8 parity remains the implementation blocker.
Preserving BN improves the training-only maximum but does not meet acceptance.
All existing baseline exports remain rejected; no M4 HANDOFF/review request.
Real clinical data approval, clinical/ethics/legal/native-language validation and
weight-notice approval remain absent. Finite desktop diagnostics establish
neither unseen-input parity nor mobile/clinical safety or performance.

## Next concrete step

Predeclare same-input Conv/BN operator replay at the stem and first depthwise
block: use training-only taps to distinguish propagated error from local kernel
arithmetic, then choose arithmetic/precision and explicit quantised scope using
training evidence. Keep the selected saved baseline, original interface/fits and
ADR-011 budgets. Freeze the next graph strategy before any new test/held-out/
stress evaluation. Request REVIEW M4 only when every acceptance item is met.
