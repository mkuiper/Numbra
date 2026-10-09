# Status

Updated: 2026-10-09T20:30:19Z

Current milestone: **M4 — On-device model export**, in progress. M0–M3 gates
exist; M4 acceptance remains incomplete. NEXT_ACTION: CONTINUE. All models and
results **PLACEHOLDER**, synthetic-only. No accepted deployment package, app or
APK. Every failed export remains rejected.

## M4 acceptance status

- **Quantised ONNX Runtime Mobile export: built, not accepted.** Original INT8
  QDQ graphs fail parity. No new selected-baseline fit, selective scope,
  deployment selection or mobile compatibility result.
- **Exported/Python parity: FAIL, budgets unchanged.** Previous complete ADR-023
  training report: preserved max raw/probability 0.000240326/0.00000279320
  (26/29 violations); rounded BN 0.000143051/0.00000183769 (13/21 violations).
  Zero threshold flips. No new selected-baseline numerical result this iteration.
- **Size ≤20 MB / preprocessing written and tested: built.** Existing original
  float/INT8/rounded diagnostic files meet the size ceiling. RGB letterbox
  float32 1×3×224×224 → raw_logit [1] unchanged. Android preprocessing and
  accepted deployment metadata remain open.

## This iteration

- Added export_arithmetic_replay.ArithmeticReplay: every ADR-024 fixed recipe
  built/audited on both unchanged graph contexts before supplied tensors run.
  Generated full-mobile scope: 39 targets, 77 recipes per context, 154 sessions,
  308 serialized/runtime graph files. Saved rounded binding, complete original
  controls, recipe expressions/constants/boundaries and file records checked.
- Supplied retained rows first pass complete original 159-node/control/lineage
  reconstruction. Both native/runtime operand origins drive all declared
  eager/runtime recipes. No native model calls, image decode, whole-model
  sessions or original control reruns. Original arrays shared/unmodified;
  all new outputs remain in memory. No completed arithmetic training report.
- Independent no-inference reconstruction covers complete target/recipe/origin/
  engine scope, original controls, signed native/eager/runtime/isolated/tapped
  comparisons and four-term accounting. The original tapped-boundary difference
  is labelled explicitly, without claiming replacement extraction equivalence.
- Generated-only tests include full random mobile scope, exhaustion of every
  generated guarded-reader row, corrupted/partial evidence, stale state/graph/
  expressions/hooks, complete file/runtime audits and signed-zero/nonzero drift.
  Documentation and ADR-024 observation updated. No new scientific decision.

## Observed checks

- Initial focused new suite: **32 PASS**, 12 deprecation warnings, 68.94s.
  Four additional output-refusal tests are included in the required full check.
- Root repository contracts: **six PASS**, 0.071s; whitespace clean.
- Required scripts/check.sh: exit 0, **872 ML PASS**, 586 warnings, 263.96s;
  Android SKIPPED (no app/gradlew), RESULT PASS. All 36 new tests included;
  no APK claim.

## Next concrete step and blockers

Implement lossless ordered arithmetic evidence persistence and its independent
streaming audit. Then complete the guarded runner connecting training_context,
training_rows and ArithmeticReplay with all 152 ordered retained components,
both graph contexts/input origins, every original control and exact prior bits.
Audit every recipe before exposing inputs; publish no report for partial runs.
Historical ADR-023 source: 50f7c65e7b6a6168a17d498be4d663c89b11742f;
ADR-022 source: 808cc3393ccf1cce95c2feeef91e5a8608b481e4.
Reuse retained tensors without new selected native-model runs or image decoding.
Generated primitive results cannot establish selected or whole-model parity.

Float parity, separately predeclared selective QDQ scope, acceptance evaluation
and mobile double compatibility/performance remain blockers. Clinical validation,
ethics/legal/native-language review and weight rights remain human questions.
No M5 or M4 review request until acceptance. No protected edits, review.sh,
REVIEW/CHECK/GATE writes, publication or push.
