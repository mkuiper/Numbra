# Status

Updated: 2026-10-09T16:31:45Z

Current milestone: **M4 — On-device model export**, in progress. NEXT_ACTION:
CONTINUE. M0–M3 gates exist (PASS WITH CHANGES); no M4 gate, app or APK.
All task models/results remain **PLACEHOLDER**, synthetic-only under ADR-002.
Every failed export remains rejected; diagnostics are never bundles.

## M4 acceptance status

- **Quantised ONNX Runtime Mobile export: BUILT, ACCEPTANCE INCOMPLETE.** Both
  retained INT8 QDQ graphs fail parity after calibration on all/only 152 training
  components. No new quantisation fit or scope selection. ADR-012's labelled
  toy diagnostic workaround remains in force; mobile operator/ABI support unverified.
- **Exported/Python parity: FAIL, budgets unchanged.** Complete BN rounding replay
  finds two locally exact recipes across all 34 BNs/both origins/all 152 training
  inputs, but builds no whole-model replacement. Original control reproduces all
  prior ordered logits/operator metrics exactly and still fails raw/probability
  budgets: maxima 0.000240326/0.00000279320 against 0.0001/0.000001, 26/29
  violations, zero flips. Original float, INT8, BN-only and joint failures retained.
  No frozen inference, model/fit/reference/budget change or deployment selection.
- **Size ≤20 MB / preprocessing written and tested: BUILT.** Original float
  6,095,579 bytes, INT8 1,730,515/1,861,702, BN-only 6,255,113, joint 6,265,822.
  New 517 control graph copies are ignored and cannot establish acceptance.
  RGB letterbox, float32 1×3×224×224 → raw_logit [1] unchanged. No accepted
  deployment-metadata package or Android decoding/preprocessing.

## This iteration's evidence

- Predeclared/committed ADR-020 and queued human review. Full Cartesian product:
  epsilon sum, reciprocal, alpha, beta and output rounding (32 recipes). Every
  saved BN in explicit module order, both exact Python/preserved-ORT input origins,
  all ordered training components; no favourable subset or adaptive additions.
- ml/reports/PLACEHOLDER-m4-bn-rounding2.json: independent NumPy/eager-PyTorch
  expressions and coefficient-bit records. e32-r32-a32-b64-o64 and
  e32-r32-a64-b64-o64 match native BN exactly on every tested layer/input/origin.
  These two alpha choices collapse on these parameters. Corresponding e64/r32
  recipes match 23/34 layers; the remaining 28 match no layer across all inputs.
  All 32 recipes' outputs agree between engines at every layer/origin. Float64
  reciprocal bits disagree at 23 e32/r64 or 19 e64/r64 BNs without changing the
  observed rounded float32 outputs. Rounded-double output is not hardware FMA.
- Native/primitive/promoted controls retain all 53 Conv/34 BN, 517 graph records,
  zero replay-fidelity/tap-logit/signed-accounting residuals and unchanged state.
  Independent no-inference audit PASS: coefficients, saved parameters/epsilon
  bits, complete aggregates, serialized/runtime arithmetic, ordered IDs,
  model/preparation/source/dependency/retained provenance, exact prior ADR-019
  logits/operator metrics and preserved fixed-budget parity reproduction.
- First diagnostic deliberately interrupted before writing a report after
  finding sorted JSON dictionary order cannot encode module order. Corrected
  audit verifies the explicit selection list; regression added. Partial first
  graphs/logs retained under ignored data/. Complete second run exit 0 means
  DIAGNOSTIC ONLY. Graphs/weights/ordered details/logs remain ignored.

## Observed verification

- Initial new/complete subset: 44 PASS / 16 FAIL in 12.06s, 36 warnings. New
  fixture wrongly assumed exact irrational reciprocal equality across libraries;
  observed difference 2^-54. Exact assertions retained on an exact-square
  fixture; original irrational case retained as measured-bit-disagreement regression.
  No production expression or budget changed; rationale queued for humans.
- Corrected combined subset: 61 PASS in 12.20s, 36 warnings. After JSON/module-order
  regression: 42 PASS in 7.05s, 8 warnings. No existing test skipped/deleted and
  no tolerance widened.
- First bash scripts/check.sh exit 0: 419 ML tests PASS in 74.38s, 152 warnings.
  Fresh full check after order correction exit 0: 419 PASS in 77.60s, 152 warnings;
  Android SKIPPED, RESULT PASS. No APK claim.
- Root repository-contract tests: 6 PASS in 0.070s after initial docs, 6 PASS in
  0.076s after evidence docs. Independent audit exit 0/PASS; git diff --check clean.
- No install/dependency/acquisition, protected edit, review.sh, REVIEW/CHECK/GATE
  write, publication/push or external message.

## Open blockers and limits

Selected-baseline whole-model float and INT8 parity remains the blocker. Local
exact BN expressions do not prove whole-model/unseen-input parity; native Conv
kernel differences remain throughout the backbone. Mobile double-operator support,
performance, clinical data approval/validation, ethics/legal/native-language
review and weight-notice approval remain unresolved. No current export is accepted.

## Next concrete step

Predeclare a single complete all-BN e32-r32-a32-b64-o64 replacement plus preserved
control for training-only whole-model parity. Audit every coefficient bit and
actual runtime Cast/Mul/Add expression against the declared recipe, preserving
float32 boundaries and original model/fits/budgets. No favourable layer subset
or frozen evaluation before training-only evidence. Conv drift may still prevent
acceptance. Declare selective static QDQ scope from training evidence before
new quantisation/frozen evaluation; resolve mobile double support before bundling.
REVIEW M4 only after acceptance.
