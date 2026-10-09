# Status

Updated: 2026-10-09T17:42:49Z

Current milestone: **M4 — On-device model export**, in progress. NEXT_ACTION:
CONTINUE. M0–M3 gates exist; no M4 gate, accepted export, app or APK.
All task models/results remain **PLACEHOLDER**, synthetic-only under ADR-002.
Every failed export remains rejected; ADR-012's toy workaround is diagnostic
only and cannot replace selected-baseline parity.

## M4 acceptance status

- **Quantised ONNX Runtime Mobile export: BUILT, ACCEPTANCE INCOMPLETE.**
  Original INT8 QDQ graphs still fail parity; no new quantisation fit, scope
  selection, deployment selection or mobile compatibility result this iteration.
- **Exported/Python parity: FAIL, budgets unchanged.** Prior ADR-022 results
  remain unchanged: rounded BN disabled/basic/extended maxima 0.000143051 raw /
  0.00000183769 probability, 13/21 violations, zero flips. No saved-baseline
  inference, reference/state/fits/budget change, frozen evaluation or new parity
  result. Complete-runtime fixture audits do not establish baseline agreement.
- **Size ≤20 MB / preprocessing written and tested: BUILT.** Original float
  6,095,579 bytes; INT8 1,730,515/1,861,702; rounded diagnostic 6,255,113.
  RGB letterbox, float32 1×3×224×224 → raw_logit [1] unchanged. Android
  preprocessing/deployment metadata remain open; no new baseline graph written.

## This iteration's evidence

- Added export_remaining_runtime.py: separate original/tapped disabled sessions,
  complete actual-runtime expression/constant/boundary audits, validated complete
  operand taps and separately measured whole logits/instrumentation drift.
  Every original expression is checked once by output connectivity; runtime
  independent scheduling may change, while exact operand order/bits remain.
  Allowed changes are the declared HardSwish expansion, exact Constant lowering,
  attribute order and bounded default materialisation. Every internal rounded-BN
  Cast/Mul/Add/coefficient is audited. No numerical-equivalence claim.
- Preserve feed lifetimes for pass-through input taps and copy every returned
  array. Invalid input fails before session inference; altered taps/constants,
  graph expressions, interfaces and partial plans fail closed. Nonzero
  instrumentation drift is reported without suppression.
- Four-term signed accounting supports head/flatten ranks and retains float32,
  finite/nonempty, same-shape and exact telescoping checks. Existing Conv/BN
  NCHW input validation is unchanged.
- Generated-only complete random mobile fixtures cover all 159 original
  computational nodes/373 original boundaries on both graphs, all actual runtime
  expressions and exact original/tapped logits on the fixed generated input.
  These are new random weights/generated tensors, never saved M3 artifacts or
  ordered training images. Historical reports retain historical source hashes;
  no new saved static reconstruction or selected-baseline result is claimed.

## Observed verification

- New runtime suite: initial 10 PASS/52 ERROR (5.61s), then 58 PASS/4 FAIL
  (6.27s), then 62 PASS (6.17s). Fixed independent runtime node scheduling,
  pass-through feed lifetime and two test-only protobuf/prefix mistakes.
  Exact assertions and corruption regressions retained.
- Expanded runtime/native/complete subset: **129 PASS** (16.63s), 230 warnings;
  includes 71 new tests and full random mobile runtime coverage.
- bash scripts/check.sh exit 0: **642 ML tests PASS** (94.51s), 438 warnings;
  Android SKIPPED, RESULT PASS. Six root contract tests PASS (0.068s) before
  final documentation; final documentation verification recorded in JOURNAL.
  git diff --check clean. No APK claim.
- No existing test deleted/skipped/weakened, saved model/reference/fits change,
  retraining, frozen evaluation, acquisition/install, protected edit, review.sh,
  REVIEW/CHECK/GATE write, publishing/push or external message.

## Open blockers and limits

Selected-baseline float/INT8 parity remains the blocker. Runtime expression
integrity and generated tap agreement do not establish saved whole-model export
agreement. Full guarded training runner, both-origin isolated replay integration,
all Conv/BN controls, native original/captured logits and independent ordered-row/
prior-logit reconstruction remain incomplete. Selective static QDQ and mobile
double support/performance remain unresolved. Clinical validation, ethics/legal,
native-language review and weight notices still need humans.

## Next concrete step

Finish ADR-023's complete runner before opening any existing ordered training
image: integrate native capture, both complete audited runtime graphs, both-origin
isolated remaining replay, every Conv/BN control and rank-general signed
accounting. Independently reconstruct every ordered component/operator/origin/
graph/metric and exact ADR-022 disabled logits without inference. Then run all
152 ordered training components only, with fixed reference/fits/preprocessing/
profile/budgets. No favourable subset, frozen inference or new fit. Declare
selective QDQ scope from that evidence before fitting; resolve mobile support
before bundling. REVIEW M4 only after acceptance; do not start M5.
