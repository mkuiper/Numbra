# Status

Updated: 2026-10-09T17:56:57Z

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
  0.00000183769 probability, 13/21 violations, zero flips. No new saved-baseline
  inference, reference/state/fits/budget change or frozen evaluation. Generated
  complete replay does not establish selected-baseline agreement.
- **Size ≤20 MB / preprocessing written and tested: BUILT.** Original float
  6,095,579 bytes; INT8 1,730,515/1,861,702; rounded diagnostic 6,255,113.
  RGB letterbox, float32 1×3×224×224 → raw_logit [1] unchanged. Android
  preprocessing/deployment metadata remain open; no new baseline graph written.

## This iteration's evidence

- Added export_remaining_replay.py supplied-tensor integration: separately
  measured uncaptured/captured native logits, both original/tapped whole-runtime
  pairs, every remaining operator and saved Conv/BN on both exact input origins,
  with full rank-general four-term signed accounting. All binary operands,
  saved parameters and squeeze axes remain explicit ordered isolated inputs.
- Retained complete Conv/BN controls: native ONNX, three primitive BN formulas,
  two promoted affine formulas, float64 expression and 32 two-engine rounding
  recipes, on both native/runtime origins and both graphs. Paired recipe/engine
  differences and all instrumentation/extraction discrepancies are unsuppressed.
- Before any supplied input runs, independently rebuild the complete rounded
  graph from fixed saved coefficients and audit all whole/isolated runtime
  expressions. Changed serialized coefficients/expressions, stale model state,
  geometry/mode/hooks and invalid inputs fail before inference.
- Independent no-inference row reconstruction validates source/plan binding,
  complete ordered operator/graph/operand/origin/control scope, tensor specs,
  exact saved constant/axis bits, and native/runtime boundary lineage through
  final logits, then recomputes every signed metric. Recorded arrays are
  observations; this is not an independent recomputation of inference results
  or historical authentication. Persistence/ordered-source/prior auditing remains.
- Generated-only complete random mobile replay covers all 159 computational
  nodes (53 Conv, 34 BN, 72 remaining), both graphs/origins and complete controls.
  Every generated native replay is exact; original/captured and original/tapped
  fixture logits are exact, while local HardSwish drift remains measured.
  All weights/tensors generated anew; no selected saved model or training image
  was opened for inference. Historical aggregate reports remain unchanged.

## Observed verification

- Initial integration suite: **34 PASS** (40.36s), 64 warnings. Expanded suite:
  **42 PASS / 1 FAIL** (42.78s), 82 warnings; a new corruption test used a wrong
  graph prefix. Replaced the test-only literal with the existing PREFIX constant;
  its four serialized-corruption cases then **4 PASS** (2.29s), 40 deselected,
  eight warnings. Exact corruption assertions retained; no production tolerance
  or existing test changed.
- bash scripts/check.sh exit 0: **686 ML tests PASS** (134.03s), 522 warnings;
  includes all **44 new tests**. Android SKIPPED, RESULT PASS. No APK claim.
  Root repository contracts: six PASS (0.098s) before final records; final
  documentation checks recorded in JOURNAL. git diff --check clean.
- No saved reference/state/fits/budget change, baseline retraining, frozen
  inference, quantisation fit, acquisition/install, protected edit, review.sh,
  REVIEW/CHECK/GATE write, external message/publication or push.

## Open blockers and limits

Selected-baseline float/INT8 parity remains the blocker. Complete generated
replay and row reconstruction do not establish saved whole-model agreement.
The guarded training-scope runner, ignored tensor/row persistence, complete
ordered-component/aggregate/source/saved/prior reconstruction and exact ADR-022
disabled-logit checks remain incomplete. Selective static QDQ and mobile double
support/performance remain unresolved. Clinical validation, ethics/legal,
native-language review and weight notices still need humans.

## Next concrete step

Build the ADR-023 guarded training-scope runner around CompleteReplay. Finish
ignored evidence persistence, complete ordered-component/aggregate/provenance
reconstruction and exact ADR-022 disabled-logit checks before opening an existing
ordered training image. Then run all 152 ordered training components only, with
fixed reference/fits/preprocessing/profile/budgets. No favourable subset, frozen
inference or new fit. Declare selective QDQ scope from that evidence before
fitting; resolve mobile support before bundling. REVIEW M4 only after acceptance;
do not start M5.
