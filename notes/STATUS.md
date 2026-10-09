# Status

Updated: 2026-10-09T15:49:45Z

Current milestone: **M4 — On-device model export**, in progress. NEXT_ACTION:
CONTINUE. M0–M3 gates exist (PASS WITH CHANGES); no M4 gate, app or APK.
Every task model/result remains **PLACEHOLDER**, synthetic-only under ADR-002.
All failed baseline exports remain rejected; diagnostic copies are never bundles.

## M4 acceptance status

- **Quantised ONNX Runtime Mobile export: BUILT, ACCEPTANCE INCOMPLETE.** Two
  retained INT8 QDQ graphs (53 quantised Conv/one Gemm each) fail parity; their
  calibration used all/only 152 training components. No new quantisation fit or
  scope selection this iteration. ADR-012's labelled toy diagnostic workaround
  remains in force; Android operator/ABI support is unverified.
- **Exported/Python parity: FAIL, budgets unchanged.** New complete promoted BN
  graph fails training raw/probability budgets: maxima 0.000189304/0.00000240022
  versus fixed 0.0001/0.000001, zero flips. Preserved control reproduces previous
  failure 0.000240326/0.00000279320. No new frozen test/held-out/stress inference,
  reference/fit/budget change or deployment selection. Earlier failures retained.
- **Size ≤20 MB / preprocessing written and tested: BUILT.** New float32/float64
  BN diagnostic 6,255,113 bytes (runtime 6,156,135), original retained float
  6,095,579, preserved 6,188,494 and INT8 1,730,515/1,861,702. RGB letterbox and
  float32 1×3×224×224 → raw_logit [1] unchanged. No accepted deployment metadata
  package or Android decoding/preprocessing.

## This iteration's evidence

- Predeclared and committed ADR-017, queued for humans. New
  numbra_ml.export_promoted_bn validates all saved BN parameters/epsilon and
  replaces all 34 nodes with existing promoted rsqrt-affine arithmetic. Saved
  float32 coefficients, double Mul/Add and one float32 output boundary cast.
  Every other serialized node/initializer/interface remains intact. Original
  Conv/head/activation/reference retained; source/model state unchanged.
- ml/reports/PLACEHOLDER-m4-promoted-bn1.json: all 152 training components only.
  New maxima decrease, but mean raw/probability errors slightly increase; raw
  violations decrease 26→23, probability violations increase 29→32. Both graphs
  FAIL. Max feature drift increases 0.0000141859→0.0000162125; induced Python-head
  max error decreases 0.000228882→0.000188351. No causal or deployment claim.
- Actual disabled CPU/sequential/two intra-op/one inter-op runtime audits verify
  all 204 expression nodes/136 casts/coefficient bits/float32 boundaries and
  unchanged 53 Conv/one Gemm counts. ORT removes unused BN initializers and
  expands HardSwish even at disabled optimisation; other runtime nodes are not
  asserted byte-identical. Original/tapped logit differences remain zero.
- Separate audit passes: aggregate/private equality, recomputed parity, ordered
  training IDs, saved model/source/dependency/preparation provenance and nine
  graph records. Graphs/weights/private details stay ignored. Updated export
  documentation, ML README, DEV-SETUP, ADR follow-through and HUMAN-QUEUE.

## Observed verification

- Initial new subset: 11 PASS, 1 FAIL in 6.17s. Extra BN was rejected by saved
  parameter matching before the declared node-count check. Moved production
  count validation ahead of matching; unchanged test then passes. Corrected
  subset: 12 PASS in 6.15s, 28 exporter warnings. No test weakened/skipped/deleted.
- Diagnostic CLI exit 0: DIAGNOSTIC ONLY; M4 incomplete. Independent audit PASS.
- bash scripts/check.sh exit 0: 345 ML tests PASS in 52.62s, 86 exporter
  deprecation warnings; Android SKIPPED, RESULT PASS. No APK claim.
- Final root repository-contract check: 6 PASS in 0.077s after documentation/
  record updates. git diff --check clean; NEXT_ACTION exactly CONTINUE.
- No toolchain/dependency/checkpoint/dataset acquisition, protected edits,
  review.sh run, REVIEW/CHECK/GATE writes, publication/push or messages.

## Open blockers and limits

Selected-baseline float and INT8 parity remains the implementation blocker.
Complete BN substitution reduces maximum errors but does not meet acceptance.
Every failed export remains rejected. M4 is not ready for HANDOFF/review.
Float64 Android support/performance, unseen-input parity, clinical data approval,
clinical/ethics/legal/native-language validation and weight-notice approval absent.

## Next concrete step

Predeclare a joint training-only graph combining ADR-016's promoted stem Conv
patch/MatMul with all ADR-017 promoted BN expressions, retaining all other
Conv/head nodes and original float32 boundaries. Compare complete raw/probability/
decision parity to preserved and BN-only controls, audit actual runtime and retain
all failures. Local stem promotion did not lower its maximum native-Python error,
so success is uncertain. Explicitly declare selective static QDQ scope from
training results before any new frozen evaluation; resolve float64 mobile support
before bundling. Request REVIEW M4 only when every acceptance item is met.
