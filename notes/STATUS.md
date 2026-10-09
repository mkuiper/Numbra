# Status

Updated: 2026-10-09T16:49:23Z

Current milestone: **M4 — On-device model export**, in progress. NEXT_ACTION:
CONTINUE. M0–M3 gates exist (PASS WITH CHANGES); no M4 gate, app or APK.
All task models/results remain **PLACEHOLDER**, synthetic-only under ADR-002.
Every failed export remains rejected; diagnostic graphs are never bundles.

## M4 acceptance status

- **Quantised ONNX Runtime Mobile export: BUILT, ACCEPTANCE INCOMPLETE.** Both
  retained INT8 QDQ graphs fail parity after calibration on all/only 152 training
  components. No new quantisation fit or scope selection this iteration.
  ADR-012's labelled toy diagnostic workaround remains in force; mobile double
  operator/ABI support and performance remain unverified.
- **Exported/Python parity: FAIL, budgets unchanged.** ADR-021's complete
  e32-r32-a32-b64-o64 graph replaces every 34 saved BN, using all 152 ordered
  training inputs. Candidate max raw/probability errors 0.000143051/0.00000183769
  exceed 0.0001/0.000001, with 13/21 violations and zero flips. Control remains
  0.000240326/0.00000279320, 26/29 violations, zero flips. Original float, INT8,
  BN-only and joint failures retained. No frozen inference, model/fit/reference/
  budget change or deployment selection. Improved errors do not close acceptance.
- **Size ≤20 MB / preprocessing written and tested: BUILT.** Original float
  6,095,579 bytes, INT8 1,730,515/1,861,702; rounded-affine diagnostic 6,255,113.
  RGB letterbox, float32 1×3×224×224 → raw_logit [1] unchanged. No accepted
  deployment-metadata package or Android decoding/preprocessing.

## This iteration's evidence

- Predeclared/committed ADR-021 and queued human review before implementation
  or execution. Added one complete rounded-affine candidate and preserved
  control with independent NumPy/eager-PyTorch coefficient bits, saved parameter/
  epsilon/order audits, every actual runtime Cast/Mul/Add and float32 boundary.
- ml/reports/PLACEHOLDER-m4-rounded-bn2.json: both artifacts cover every ordered
  training index image only. Candidate retains 53 Conv/one Gemm; 34 BN replacements
  use 204 expression nodes and 136 Casts. Every other serialized original node,
  initializer, connection/interface retained. Feature-tap logit changes are zero.
  Candidate mean raw/probability errors 0.0000415946/0.000000485651; maximum feature
  error 0.0000121593. Remaining drift is not attributed solely to Conv.
- Independent no-inference audit PASS: eight graph records, complete input scope,
  coefficient bits, runtime expressions, fixed-budget parity/failures, feature
  aggregates/tap accounting, model/preparation/source/retained/dependency/code
  provenance and exact prior ADR-020 ordered Python/control logits. Private audit
  SHA-256 1388700ac2588a7a4334f4145303f5f59e99650fbb65ba4ae3e23bcd80c3b825.
- First run retained in PLACEHOLDER-m4-rounded-bn1.json. Subsequent prior audit
  raised KeyError: ADR-020 replay protocol has no temperature/threshold fields.
  Corrected fit binding through identical saved-run hash, added actual-schema
  regression, regenerated evidence with current code hashes. Both runs' artifact
  aggregates, graphs and ordered-detail hashes reproduce exactly; no inference
  arithmetic changed. No frozen inputs, new quantisation or deployment selection.

## Observed verification

- Initial subset: 20 PASS / 1 FAIL in 10.37s, 46 warnings. New fixture passed
  multi-output diagnostic graph to the strict single-output production helper.
  Corrected fixture to use diagnostic ORT session and integer centre-pixel Conv
  weights; exact assertions and production interface guard retained.
- Corrected combined rounded/promoted/joint subset: 34 PASS in 14.13s, 76 warnings.
  Expanded independent-bit/prior-control subset: 14 PASS in 2.15s, 12 warnings;
  repeated after actual-schema fix: 14 PASS in 2.15s. No existing test skipped,
  deleted, weakened or tolerance widened.
- First bash scripts/check.sh exit 0: 434 ML tests PASS in 70.03s, 170 warnings.
  Fresh full check after schema correction exit 0: 434 PASS in 70.00s, 170 warnings;
  Android SKIPPED, RESULT PASS. No APK claim.
- Root contract suites: 6 PASS in 0.092s initially and 6 PASS in 0.080s after
  evidence documentation; git diff --check clean. Independent audit exit 0/PASS.
- No install/dependency/acquisition, protected edit, review.sh, REVIEW/CHECK/GATE
  write, publication/push or external message.

## Open blockers and limits

Selected-baseline whole-model float and INT8 parity remains the blocker. Locally
exact BN expressions still fail complete-model training parity. Mobile double
support/performance, clinical data approval/validation, ethics/legal/native-language
review and weight-notice approval remain unresolved. No current export is accepted.

## Next concrete step

Predeclare a complete training-only experiment covering fixed ORT optimisation
profiles on the rounded-affine graph and preserved control. Audit constant folding
and runtime arithmetic semantics for every declared profile; no favourable subset,
reference/fit/budget change or frozen inference. Other float operators and Conv
kernel drift may still prevent acceptance. Declare selective static QDQ scope from
training evidence before a new quantisation fit/frozen evaluation; resolve mobile
arithmetic support before bundling. REVIEW M4 only after acceptance.
