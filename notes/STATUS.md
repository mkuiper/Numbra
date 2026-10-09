# Status

Updated: 2026-10-09T17:17:20Z

Current milestone: **M4 — On-device model export**, in progress. NEXT_ACTION:
CONTINUE. M0–M3 gates exist; no M4 gate, accepted export, app or APK.
All task models/results remain **PLACEHOLDER**, synthetic-only under ADR-002.
Every failed export remains rejected. ADR-012's toy diagnostic workaround
remains diagnostic only and cannot replace selected-baseline parity.

## M4 acceptance status

- **Quantised ONNX Runtime Mobile export: BUILT, ACCEPTANCE INCOMPLETE.** Both
  original INT8 QDQ graphs fail parity. No new quantisation fit, changed scope
  or deployment selection this iteration. Mobile operator/ABI and performance
  remain unverified.
- **Exported/Python parity: FAIL, budgets unchanged.** Prior ADR-022 comparisons
  still all fail; rounded BN disabled/basic/extended maxima remain 0.000143051
  raw / 0.00000183769 probability, with 13/21 violations and zero flips.
  No new baseline inference/parity result this iteration; no frozen inputs,
  reference/model/fits/budget change or accepted bundle.
- **Size ≤20 MB / preprocessing written and tested: BUILT.** Original float
  6,095,579 bytes; INT8 1,730,515/1,861,702; rounded diagnostic 6,255,113.
  No new baseline graph produced. RGB letterbox, float32 1×3×224×224 →
  raw_logit [1] unchanged. Android preprocessing/deployment metadata remain open.

## This iteration's evidence

- Predeclared/committed ADR-023 before implementation, including staged complete
  remaining-operator replay; queued human review. Stage one is implemented:
  fail-closed no-inference preflight, saved head parameter bits, complete
  topological graph scope, static shapes/dtypes, unchanged rounded-graph nodes
  and constants, isolated multi-operand eager/ORT replay and runtime audits.
  Stage two's native mapping/capture and full training replay are UNIMPLEMENTED.
- ml/reports/PLACEHOLDER-m4-remaining-preflight2.json covers all 160 preserved
  serialized nodes: 87 saved Conv/BN controls, 72 remaining replay operators,
  one Constant, plus all 212 initializers. All remaining/control nodes are
  byte-identical in the rounded graph. Explicit complete training scope is
  152 ordered components; no images decoded or baseline inference performed.
- Both baseline preflights executed with image decode, Module forward and
  ORT session creation blocked by raising guards. Independent complete
  no-inference reconstruction PASS, including saved model/preparation/prior/
  graphs/code/dependencies. PASS means static scope only, never export parity.
- Retained preflight1. Its post-commit audit failed because historical git
  context was compared to current HEAD/dirty. Corrected auditor verifies the
  recorded commit exists and dirty flag is boolean; all other fields are
  reconstructed exactly. Preflight2 reproduces complete original plan/scope/
  graph/model/preparation/prior evidence. Fresh post-commit audit PASS.
  Independent preflight2 audit SHA-256:
  f449c827bc230e14f0025dc5dbff3382273bed5155450670aa3966ebd7ae4245.

## Observed verification

- Initial new subset: 16 FAIL/42 PASS (2.60s), exposing Identity-alias fixtures
  and runtime unused domain imports; next 2 FAIL/56 PASS (2.51s), isolating
  disabled-runtime HardSwish function expansion. Fixed alias resolution and
  audited only the precise declared HardSigmoid/Mul expression. Corruption
  regressions retained; no test expectations or production budgets weakened.
- Corrected primitives: 58 PASS (2.32s); complete guarded pipeline and expansion
  corruption suite: 66 PASS (8.31s). After historical-context fix: 69 PASS
  (8.90s), including invalid metadata and current-checkout change regressions.
- First full bash scripts/check.sh exit 0: 529 PASS (83.86s). Fresh final full
  check after the audit fix exit 0: **532 ML tests PASS** (85.38s), 236 warnings;
  Android SKIPPED, RESULT PASS. No APK claim. Six root contract tests PASS
  (0.063s); git diff --check clean.
- No existing test deleted/skipped/weakened, model/reference/fits change,
  baseline retraining, frozen evaluation, install/acquisition, protected edit,
  review.sh, REVIEW/CHECK/GATE write, publishing/push or external message.

## Open blockers and limits

Selected-baseline float/INT8 parity remains the blocker. Static scope and
isolated generated recipes cannot establish native whole-model agreement.
Native remaining-boundary mapping and training-only replay are incomplete;
Conv propagation, selective static QDQ and mobile double support/performance
remain unresolved. Clinical data/validation, ethics/legal/native-language
review and weight-notice approval still need humans.

## Next concrete step

Implement ADR-023 stage two: map every saved remaining module/functional boundary,
copy native inputs/outputs before in-place mutation, tap every runtime operand
and output on both unchanged graphs, retain all original/tapped logits and
Conv/BN controls, and replay the complete scope on all ordered training inputs.
Report native replay fidelity, local arithmetic versus propagation, four-term
signed accounting and independent complete reconstruction/exact ADR-022 disabled
logits. No favourable subset, frozen inference, changed budgets or new fit.
Then declare selective QDQ scope from training evidence before fitting; resolve
mobile support before bundling. REVIEW M4 only after acceptance; do not start M5.
