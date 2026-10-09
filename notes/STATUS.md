# Status

Updated: 2026-10-09T17:30:32Z

Current milestone: **M4 — On-device model export**, in progress. NEXT_ACTION:
CONTINUE. M0–M3 gates exist; no M4 gate, accepted export, app or APK.
All task models/results remain **PLACEHOLDER**, synthetic-only under ADR-002.
Every failed export remains rejected; ADR-012's toy workaround remains diagnostic
only and cannot replace selected-baseline parity.

## M4 acceptance status

- **Quantised ONNX Runtime Mobile export: BUILT, ACCEPTANCE INCOMPLETE.** Original
  INT8 QDQ graphs still fail parity. No new quantisation fit, changed scope or
  deployment selection this iteration. Mobile operator/ABI/performance unverified.
- **Exported/Python parity: FAIL, budgets unchanged.** Prior ADR-022 comparisons
  still all fail; rounded BN disabled/basic/extended maxima remain 0.000143051
  raw / 0.00000183769 probability, 13/21 violations, zero flips. No new saved
  baseline inference/parity result, frozen inputs, reference/model/fits/budget
  change or accepted bundle this iteration.
- **Size ≤20 MB / preprocessing written and tested: BUILT.** Original float
  6,095,579 bytes; INT8 1,730,515/1,861,702; rounded diagnostic 6,255,113.
  RGB letterbox, float32 1×3×224×224 → raw_logit [1] unchanged. Android
  preprocessing/deployment metadata remain open; no new baseline graph written.

## This iteration's evidence

- Implemented ADR-023 native capture foundation in export_remaining_native.py:
  exact one-to-one native owner/type/geometry mapping, actual-call interception
  with copies before in-place mutation, immediate output copies, all binary and
  saved-constant operands, complete ordered graph-edge bit checks, separate eager
  fidelity, and full static taps for both unchanged graphs. Fail closed on partial
  scope, altered settings/bits/boundaries, foreign hooks, shared owners and state
  changes; remove hooks/interception on success and failure.
- Generated full mobile architecture uses new random weights and generated input,
  never saved M3 weights/index images. All 159 computational nodes captured;
  72 remaining independent recipes match captured native outputs exactly, and
  captured/untapped native logits match exactly. Generated small residual/SE
  fixtures also check every Conv/BN recipe and both disabled-ORT original/tapped
  graph logits. This is fixture evidence only, never saved-baseline parity.
- ml/reports/PLACEHOLDER-m4-native-mapping1.json verifies saved baseline static
  mapping for all 159 computational nodes (87 controls + 72 remaining), and all
  373 original operand/output boundaries on each unchanged graph. No image decode,
  saved-model forward or ORT session permitted: all blocked with raising guards.
  Full saved/preparation/prior/graph/source/dependency/mapping/tap reconstruction
  PASS without inference. Report SHA-256:
  70c9fd66955783e22c92564a4dea034a5ee93f406192a8a6918a52f1797e6f3b.
- The ignored mapping audit script validates historical checkout context and
  reconstructs every other field exactly. Its SHA-256:
  955e96aa301498c4464b8464f95aea86209371cc18b62702b52ccb7f04a2f02a.
  Earlier preflight reports remain retained with their historical source hashes.

## Observed verification

- New capture subset first 6 FAIL/17 PASS (4.76s), then 3 FAIL/20 PASS (4.44s),
  then 1 FAIL/22 PASS (4.08s): fixed Tensor method metadata/dispatch, selected
  float/int original boundaries in double-internal rounded graphs, and added the
  fixture's asserted ReLU. Expanded combined run 1 FAIL/105 PASS (11.44s)
  exposed altered rounded expression outside initial tap scope; added full graph
  binding and complete original boundary reconstruction with corruption tests.
- Corrected combined subset 107 PASS (11.65s). Final capture suite with static
  decode/forward/session guards: 39 PASS (4.94s). Exact assertions retained.
- bash scripts/check.sh exit 0: **571 ML tests PASS** (87.56s), 314 warnings;
  Android SKIPPED, RESULT PASS. Six root contract tests PASS (0.063s).
  git diff --check clean. No APK claim.
- No existing test deleted/skipped/weakened, saved model/reference/fits change,
  retraining, frozen evaluation, install/acquisition, protected edit, review.sh,
  REVIEW/CHECK/GATE write, publishing/push or external message.

## Open blockers and limits

Selected-baseline float/INT8 parity remains the blocker. Native capture and static
maps do not establish whole-model export agreement. The complete saved-training
runner, actual runtime graph expression audits, both input-origin replays,
original/tapped logits, signed accounting and independent ordered-row/prior-logit
reconstruction are still incomplete. Selective static QDQ and mobile double
support/performance remain unresolved. Clinical data/validation, ethics/legal,
native-language review and weight notices still need humans.

## Next concrete step

Complete ADR-023's two-graph training runner before opening any existing ordered
training images: use native capture and all static taps, retain every Conv/BN
control, replay every remaining operator on native and tapped-runtime operand
tuples, audit serialized and actual disabled-runtime arithmetic, and record all
original/tapped native/runtime logits separately. Support head output ranks in
four-term signed accounting. Independently reconstruct every ordered component,
operator/origin/graph/metric and exact ADR-022 disabled logits. Then run on all
152 ordered training components only. No favourable subset, frozen inference,
changed budgets or new fit. Declare selective QDQ scope from that evidence before
fitting; resolve mobile support before bundling. REVIEW M4 only after acceptance;
do not start M5.
