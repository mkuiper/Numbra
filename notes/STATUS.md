# Status

Updated: 2026-10-09T19:57:14Z

Current milestone: **M4 — On-device model export**, in progress. M0–M3 gates
exist; M4 acceptance remains incomplete. NEXT_ACTION: CONTINUE. All models and
results **PLACEHOLDER**, synthetic-only. No M4 gate, accepted deployment
package, app or APK; every failed export remains rejected.

## M4 acceptance status

- **Quantised ONNX Runtime Mobile export: built, not accepted.** Original INT8
  QDQ graphs fail parity. No new selected-baseline quantisation fit, selective
  scope, deployment selection or mobile compatibility result.
- **Exported/Python parity: FAIL, budgets unchanged.** Latest complete ADR-023
  training replay: preserved max raw/probability 0.000240326/0.00000279320
  (26/29 violations); rounded BN 0.000143051/0.00000183769 (13/21 violations).
  Zero threshold flips. This iteration has no new selected-baseline parity.
- **Size ≤20 MB / preprocessing written and tested: built.** Original float
  6,095,579 bytes; INT8 1,730,515/1,861,702; rounded diagnostic 6,255,113.
  RGB letterbox float32 1×3×224×224 → raw_logit [1] unchanged. Android
  preprocessing and deployment metadata remain open.

## This iteration

- ADR-024 predeclares exactly two activation/reduction recipes per operator,
  plus original-constant Gemm isolation. Saved reference/model/fits/budgets and
  all existing Conv/BN/remaining controls remain fixed. Decision queued for humans.
- Added supplied-graph export_remaining_arithmetic: float32 clamp/add/product
  followed by division or rounded reciprocal; float32 sum/divide or double
  mean/cast; original initializer/Constant/Identity head dependency closure.
  It has no dataset/saved-baseline execution entry point.
- Complete generated random mobile scope covers every 39 target node and all
  77 recipe graphs, identical across both generated contexts. Existing complete
  scope validation checks all 87 Conv/BN controls before recipe construction.
  Static test guards block decode, model forward and runtime sessions.
- Serialized audits reconstruct full expressions/constants/interfaces; actual
  disabled-runtime audits use ADR-023's unchanged complete auditor. Signed
  runtime/eager drift is reported without suppression or native equivalence.
- Generated constant-head Gemm differs from eager linear by 0.0000019073486.
  Initial exact-equality test was unjustified: documented as disputed, replaced
  with exact original constant-context ONNX equality and full signed metric
  checks. Protobuf fixture insertion also fixed. Existing parity tests/budgets
  and activation/reduction equality assertions remain intact.
- No selected saved-model inference, retained training-observation replay,
  whole-model candidate, frozen inference, new quantisation fit or mobile claim.

## Observed checks

- First focused run: six FAIL, 42 PASS (one disputed equality assumption and
  five protobuf fixture errors). Follow-through: 48 PASS; final expanded suite
  **56 PASS**, four deprecation warnings, 12.02s.
- Required scripts/check.sh: exit 0, **822 ML PASS**, 568 warnings, 172.81s;
  Android SKIPPED, RESULT PASS. No APK claim.
- Final root repository contracts: six PASS (0.081s); whitespace clean.

## Next concrete step and blockers

Integrate ADR-024 with the complete retained ADR-023 training observations.
First bind historical source provenance to exact snapshot
50f7c65e7b6a6168a17d498be4d663c89b11742f after these code additions, retaining
exact live dependencies and all saved/prior/ordered-array/metric/lineage checks.
Then replay every fixed recipe and constant-head isolation on every 152 ordered
training input, both graph contexts/input origins, alongside all existing controls.
Use independently verified retained tensors where possible; do not decode or run
the selected native model again unnecessarily. Guarded replay and persistence
remain unimplemented. Local arithmetic results cannot establish a whole-model fix.

Float parity, separately predeclared selective QDQ scope, acceptance evaluation
and mobile double compatibility/performance remain blockers. Clinical validation,
ethics/legal/native-language review and weight rights remain human questions.
No M5 or M4 review request until acceptance. No protected edits, review.sh,
REVIEW/CHECK/GATE writes, publication or push.
