# Status

Updated: 2026-10-09T14:50:43Z

Current milestone: **M4 — On-device model export**, in progress. NEXT_ACTION:
CONTINUE. M0–M3 gates exist, PASS WITH CHANGES; human review pending. No M4 gate,
Android app or APK. Every task model/result remains **PLACEHOLDER**, synthetic-only
under ADR-002. Both baseline export experiments are rejected for app bundling.

## M4 acceptance status

- **Quantised ONNX Runtime Mobile export: BUILT, ACCEPTANCE INCOMPLETE.** Pinned
  ONNX 1.19.1 / ORT 1.23.2 added with seven new hash-locked packages (42 unique
  total). Legacy PyTorch opset-17 fixed single-image float export and static signed
  INT8 QDQ run offline. MinMax uses all/only 152 training components. Attempt 1
  per-tensor / attempt 2 per-channel weights, predeclared before the first run.
  Each INT8 graph has 53 Conv/one Gemm with INT8 QDQ weights, remaining float
  nonlinear/pool/arithmetic operators fully reported. Actual desktop CPU runtime
  loading succeeds; Android/ABI compatibility unverified.
- **Exported/Python parity: FAIL, budgets unchanged.** Float identical across both
  attempts; test/held-out 308 inputs: max raw error 0.000272334, probability error
  0.00000355427, zero flips. Both numeric budgets exceeded. INT8 per-tensor:
  50.784990 / 0.506519 errors, 26 flips; per-channel: 62.403598 / 0.612635, 28 flips.
  All 768 components and 14 independently generated stress inputs also tested;
  each artifact fails. Complete failure cases/ordered logits remain ignored.
  Separate conservative-margin accounting never rescues parity. Saved Python
  verification (original batch size) remains exact. Single-image Python vs saved
  batch max raw difference 0.000383378, zero flips; independently disclosed.
- **Size ≤20 MB / preprocessing written and tested: BUILT.** Float 6,095,579 bytes;
  INT8 1,730,515 / 1,861,702 bytes. SPEC letterbox/rounding/normalisation unchanged;
  runtime validates rgb float32 1×3×224×224 → raw_logit float32 [1]. Size passing
  alone cannot close M4. No accepted deployment metadata package or Android decode.

## Built evidence and labelled workaround

- numbra_ml.export verifies the saved model/environment/preparation, rejects unsafe
  or existing outputs, converts, calibrates train-only, inspects graph operators,
  checks numerical/threshold/stress parity and generates frozen exported metrics
  without refitting calibration or threshold. Aggregate evidence in
  ml/reports/PLACEHOLDER-m4-attempt1.json and PLACEHOLDER-m4-attempt2.json;
  source/weight/lock/report hashes retained. Reporting revision 1.0.1 corrects
  initial subgroup grouping and adds batch diagnostics without re-inference.
- ADR-012: **PLACEHOLDER labelled workaround — generated toy-model export for
  diagnostic pipeline testing only**, after two genuine baseline failures.
  Complete generated preparation→toy training→save/restore→ONNX/QDQ→ORT path is
  tested. Toy evidence cannot replace the selected baseline or justify review.
  No tolerance, threshold, model or frozen fixture tuning. ADR queued for humans.
- docs/ML-EXPORT.md and DEV-SETUP.md record commands, rejected results and library
  temporary confinement. No checkpoint/task dataset acquired this iteration.
- Root Builder markdown checker now uses tracked + nonignored untracked git files
  instead of scanning installed wheel documentation. New regression retains
  untracked Builder documents and excludes ignored third-party files. Source
  register includes checked official PyTorch 2.8 exporter docs.

## Observed verification

- bash scripts/check.sh: exit 0, **304 ML tests PASS in 32.09s**, six exporter
  deprecation warnings; Android SKIPPED; RESULT PASS. No APK claim.
- Export subset: initial 11 PASS / 2 failed (duplicate dependency-name alias and
  mistaken PASS expectation for actual runtime rounding); corrected final subset
  **14 PASS in 6.85s**, including a retained rounding-failure regression and full
  export/summary/tamper tests. No budget or existing Builder assertion weakened.
- Root contract suite initially failed on four ignored third-party broken links
  plus one missing source entry. Corrected discovery with regression and added
  source entry; final **6 PASS in 0.070s**. pip check: no broken requirements.
- Both actual baseline experiment CLIs and their summary CLIs returned 1/FAIL,
  as required by failed parity. Both summaries verify graph hashes and ordered
  logits, retain original source/lock provenance, report only aggregate data.
- git diff --check clean including iteration records; all generated artifacts ignored.

## Open blockers and limits

Baseline numerical/quantised parity is the implementation blocker. Two genuine
attempts completed; diagnostic-only workaround documented, not accepted as the
baseline. No M4 HANDOFF/review request. No suitable approved real task data,
clinical/ethics/legal/native-language validation, or weight-notice approval.
Per-channel source-C sensitivity 1.0 has specificity 0.0; not improved screening.
Finite desktop tests do not establish unseen-input or mobile safety/performance.
No protected edits, patient data, weights/APK in git, publishing, push or messages.

## Next concrete step

Diagnose the original selected baseline's float ONNX rounding and INT8 drift,
using training-only operator/activation evidence. Predeclare next graph/runtime
strategy before running (e.g. inspect CPU graph fusions and precision-sensitive
feature scaling/head; consider selective mixed precision with every float operator
reported). Keep ADR-011 budgets and frozen inputs/fits. Retain all attempts;
request REVIEW M4 only after the selected baseline meets every acceptance item.
