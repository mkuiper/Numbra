# Status

Updated: 2026-10-09T20:39:18Z

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

- Added export_arithmetic_evidence.OrderedArithmeticEvidence and independent
  streaming audit: complete original control/array tree and every fixed recipe,
  both unchanged graphs/input origins/engines. Explicit tree ordering, all
  float32/int64 bits/signed zeros, file/content hashes and exact prior checks.
  Partial runs have no completed index. Protocol binds ordered targets/recipes,
  source/plan, fixed fits and unchanged ADR-011 budgets.
- Shared ADR-023 storage/audit via narrow protocol reconstruction hooks;
  original format and all existing control/lineage/parity checks retained.
  Arithmetic graph-context and engine order checks tightened.
- Independent audit reconstructs all original controls and signed recipe/
  accounting metrics, every numeric/boolean aggregate, original-graph parity
  and exact ADR-022 prior bits. Per-row cache released before next component.
  No decode/native calls/sessions/eager recipes/evidence writes during audit.
  Recorded observations cannot authenticate historical inference or establish
  independently recomputed arithmetic truth. Recipe whole-model parity
  UNVERIFIED; deployment selection false. No selected arithmetic experiment.
- Generated-only two-component round-trips, partial/reordered scope, corrupt/
  rehashed evidence, signed-zero/nonzero errors, per-row memory release and
  protocol/acceptance-claim rejection tested. ADR/docs/HUMAN-QUEUE updated.
  No new scientific decision, selected-model execution or parity outcome.

## Observed checks

- Initial focused new/original persistence suites: **72 PASS**, four
  deprecation warnings, 15.49s. Four additional protocol/acceptance-claim cases
  added before full check; new arithmetic suite collects 37 tests.
- Root repository contracts: **six PASS**, 0.061s; whitespace clean.
- Required scripts/check.sh: exit 0, **909 ML PASS**, 588 warnings, 273.91s;
  Android SKIPPED (no app/gradlew), RESULT PASS. All 37 new arithmetic tests
  included. No accepted export or APK claim.

## Next concrete step and blockers

Complete the guarded runner connecting training_context, training_rows,
ArithmeticReplay and OrderedArithmeticEvidence with all 152 ordered retained
components, both graph contexts/input origins, every original control and exact
prior bits. Audit full original context/historical-source/dependency evidence
and every new setup recipe before exposing inputs. Exhaust the reader and
independently reconstruct complete persisted evidence before publishing any
completed report; partial runs publish none.
Historical ADR-023 source: 50f7c65e7b6a6168a17d498be4d663c89b11742f;
ADR-022 source: 808cc3393ccf1cce95c2feeef91e5a8608b481e4.
Reuse retained tensors without new selected native-model runs or image decoding.
Generated primitive results cannot establish selected or whole-model parity.

Float parity, separately predeclared selective QDQ scope, acceptance evaluation
and mobile double compatibility/performance remain blockers. Clinical validation,
ethics/legal/native-language review and weight rights remain human questions.
No M5 or M4 review request until acceptance. No protected edits, review.sh,
REVIEW/CHECK/GATE writes, publication or push.
