# Status

Updated: 2026-10-09T20:19:25Z

Current milestone: **M4 — On-device model export**, in progress. M0–M3 gates
exist; M4 acceptance remains incomplete. NEXT_ACTION: CONTINUE. All models and
results **PLACEHOLDER**, synthetic-only. No accepted deployment package, app or
APK. Every failed export remains rejected.

## M4 acceptance status

- **Quantised ONNX Runtime Mobile export: built, not accepted.** Original INT8
  QDQ graphs fail parity. No new selected-baseline quantisation fit, selective
  scope, deployment selection or mobile compatibility result.
- **Exported/Python parity: FAIL, budgets unchanged.** Complete ADR-023 training
  replay: preserved max raw/probability 0.000240326/0.00000279320 (26/29
  violations); rounded BN 0.000143051/0.00000183769 (13/21 violations). Zero
  threshold flips. This iteration produces no new selected-baseline parity.
- **Size ≤20 MB / preprocessing written and tested: built.** Original float
  6,095,579 bytes; INT8 1,730,515/1,861,702; rounded diagnostic 6,255,113.
  RGB letterbox float32 1×3×224×224 → raw_logit [1] unchanged. Android
  preprocessing and deployment metadata remain open.

## This iteration

- Extended audit_training with an explicit ADR-023 source_commit binding:
  every historical source file/hash and full tree must match that local commit.
  Live dependencies/locks/hardware and complete saved/preparation/prior/setup/
  ordered-array/metric/lineage/parity checks remain exact. Original report bytes
  are preserved; omitted or mismatching snapshots still fail. ADR-022's source
  commit remains separate. No historical-inference authentication claim.
- Added export_remaining_retained.training_rows: full original context/setup/
  observation audit before first yield, then per-access row/file/array/metric/
  lineage/prior-bit checks. Every original graph/origin/Conv/BN/remaining control
  is exposed read-only without decode, forward, eager recipes or sessions.
  Exhaustion checks complete array use; early stopping creates no completed
  experiment. Generated tests cover corruption before/after the full audit.
- No ADR-024 recipe execution on retained selected tensors yet. Primitive scope
  remains every 39 target node/77 fixed expressions, both graph contexts and
  input origins. New arithmetic persistence and guarded replay remain open.

## Observed checks

- Focused runner/retained-reader suite: **46 PASS**, 26 deprecation warnings,
  53.01s. Root repository contracts: six PASS (0.074s); whitespace clean.
- Required scripts/check.sh: exit 0, **836 ML PASS**, 574 warnings, 200.77s;
  Android SKIPPED, RESULT PASS. No APK claim.
- Complete historical-source selected audit: exit 0, **PASS** for all 152 rows,
  159 operators, 904 setup graphs, arrays/metrics/lineage/parity/prior bits.
  All five actual decode/native/session/eager/evidence-write guards active.
  Snapshot matches all 33 historical source files/tree; live dependencies exact.
  Aggregate: ml/reports/PLACEHOLDER-m4-remaining-training3-snapshot-audit.json.
  Original tracked/ignored report fingerprints unchanged and identical.

## Next concrete step and blockers

Integrate all ADR-024 fixed recipes and original-constant head isolation with
training_rows, all 152 ordered retained components, both graph contexts/input
origins and every original control. Build/audit every serialized/runtime recipe
before supplied inputs, persist all signed native/eager/runtime comparisons,
then independently reconstruct complete scope/metrics/lineage without inference.
Historical ADR-023 source: 50f7c65e7b6a6168a17d498be4d663c89b11742f;
ADR-022 source: 808cc3393ccf1cce95c2feeef91e5a8608b481e4.
Reuse verified retained tensors without another selected native-model run or
image decode. Local arithmetic results cannot establish a whole-model fix.

Float parity, separately predeclared selective QDQ scope, acceptance evaluation
and mobile double compatibility/performance remain blockers. Clinical validation,
ethics/legal/native-language review and weight rights remain human questions.
No M5 or M4 review request until acceptance. No protected edits, review.sh,
REVIEW/CHECK/GATE writes, publication or push.
