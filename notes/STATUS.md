# Status

Updated: 2026-10-09T15:40:15Z

Current milestone: **M4 — On-device model export**, in progress. NEXT_ACTION:
CONTINUE. M0–M3 gates exist (PASS WITH CHANGES); no M4 gate, app or APK.
Every task model/result remains **PLACEHOLDER**, synthetic-only under ADR-002.
Retained baseline exports remain rejected; diagnostic copies are never bundles.

## M4 acceptance status

- **Quantised ONNX Runtime Mobile export: BUILT, ACCEPTANCE INCOMPLETE.** Two
  retained INT8 QDQ graphs (53 quantised Conv/one Gemm each) fail parity. They
  used all/only 152 training components for calibration. No new quantisation
  fit or scope selection this iteration; Android/ABI support unverified.
  ADR-012's labelled toy diagnostic workaround remains in force.
- **Exported/Python parity: FAIL, budgets unchanged.** Original float/INT8 and
  complete BatchNorm-preserved failures remain. Preserved/disabled training max
  raw/probability errors remain 0.000240326/0.00000279320 versus the fixed
  0.0001/0.000001 budgets. This iteration measures only same-input arithmetic:
  no new whole-model parity, frozen test/held-out/stress inference, saved
  reference/fit/budget change or deployment selection.
- **Size ≤20 MB / preprocessing written and tested: BUILT.** Retained float
  6,095,579 bytes, preserved diagnostic 6,188,494, INT8 1,730,515/1,861,702.
  RGB letterbox/normalisation and float32 1×3×224×224 → raw_logit [1] unchanged.
  No accepted deployment metadata package or Android decoding/preprocessing.

## This iteration's evidence

- ADR-016 predeclares training-only promoted stem Conv patch/MatMul accumulation
  and two promoted affine BN expressions. Queued for humans. Saved float32
  weights/coefficient bits and float32 output boundaries retained; native Python
  stays the reference. Higher precision is a diagnostic hypothesis, not a fix.
- New numbra_ml.export_precision reuses verified saved-model/preparation/retained
  export/preserved-graph provenance and ADR-015 replay. Explicit Conv zero Pad,
  strided/dilated Slice, patch ordering and float64 MatMul; float64 BN multiply/
  add with one float32 cast. Unsupported Conv geometry rejected. Actual disabled
  ORT graphs audited with existing sequential/two intra-op/one inter-op settings.
- ml/reports/PLACEHOLDER-m4-precision1.json: all 152 training components only.
  Every promoted ONNX expression matches its Python promoted expression exactly
  on both input origins. Native-Python differences remain: stem Conv maximum
  0.000000476837, stem BN rsqrt-affine 0.0000000596046 (divide 0.000000178814),
  first depthwise BN 0.00000381470 on Python-origin / 0.00000762939 on ORT-origin
  inputs with either recipe. Stem BN improves locally; promoted stem Conv does
  not reduce the native-ORT maximum. No propagated/full-model improvement claim.
- Original/tapped logits, replay fidelity and signed telescoping residuals are
  zero. Saved state hashes match before/after. Separate audit verifies aggregate/
  private equality, source/lock/preparation/saved-model provenance, ignored details
  and 33 graph records. Graphs, weights and component tensors remain ignored.
- Documentation, ADR follow-through and HUMAN-QUEUE updated. No model/interface/
  threshold/temperature/budget change; every retained failure stays retained.

## Observed verification

- New arithmetic/replay subset: 15 PASS in 10.63s, 24 exporter deprecation
  warnings plus one test-only scalar/autograd warning. Added explicit detach to
  that test scalar; the full suite has only exporter warnings. No test failed,
  was skipped, removed or weakened.
- Diagnostic CLI exit 0: DIAGNOSTIC ONLY, M4 incomplete. The separate checksum
  audit first assumed a .pt filename; corrected the audit to the actual saved
  .safetensors file and it passed. No implementation/model change for this typo.
- bash scripts/check.sh: exit 0, 333 ML tests PASS in 48.97s, 58 legacy exporter
  warnings; Android SKIPPED, RESULT PASS. No APK claim. Root repository checks:
  6 PASS in 0.066s before final docs/records; final rerun recorded in JOURNAL.
- No toolchain/dependency/checkpoint/dataset acquisition, protected edits,
  review.sh run, review/check/gate files written, publish/push or messages.

## Open blockers and limits

Selected-baseline float and INT8 parity remains the implementation blocker.
Promoted local BN expressions improve some comparisons but do not exactly
recover native Python. All baseline exports remain rejected. M4 is not ready
for HANDOFF/review. Float64 Android support/performance, unseen-input parity,
clinical data approval, clinical/ethics/legal/native-language validation and
weight-notice approval are absent.

## Next concrete step

Predeclare a complete training-only preserved graph replacing all 34 saved BN
nodes with promoted rsqrt-affine expressions, retaining original Conv/head and
float32 boundaries. Audit the actual disabled runtime graph and measure complete
training raw/probability/decision parity, preserving state/reference/ADR-011.
Then explicitly declare and justify selective static QDQ scope from training
results before any new frozen evaluation. Resolve float64 mobile compatibility
before bundling. Request REVIEW M4 only when every acceptance item is met.
