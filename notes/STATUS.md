# Status

Updated: 2026-10-09T16:16:35Z

Current milestone: **M4 — On-device model export**, in progress. NEXT_ACTION:
CONTINUE. M0–M3 gates exist (PASS WITH CHANGES); no M4 gate, app or APK.
Every task model/result remains **PLACEHOLDER**, synthetic-only under ADR-002.
Every failed export remains rejected; diagnostic copies are never bundles.

## M4 acceptance status

- **Quantised ONNX Runtime Mobile export: BUILT, ACCEPTANCE INCOMPLETE.** Both
  retained INT8 QDQ graphs fail parity, calibrated on all/only 152 training
  components. No new quantisation fit or scope selection. ADR-012's labelled
  toy diagnostic workaround stays in force; mobile operator/ABI support unverified.
- **Exported/Python parity: FAIL, budgets unchanged.** Complete same-input
  training-only replay now covers every 53 Conv/34 BN, with both promoted BN
  recipes. It builds no whole-model replacement. The preserved control exactly
  reproduces prior ordered logits/parity: raw/probability maxima
  0.000240326/0.00000279320 against 0.0001/0.000001, 26/29 violations, zero flips.
  Joint and BN-only graphs still fail. No frozen evaluation, model/fit/reference/
  budget change or deployment selection; every earlier failure retained.
- **Size ≤20 MB / preprocessing written and tested: BUILT.** Original float
  6,095,579 bytes, INT8 1,730,515/1,861,702, BN-only 6,255,113, joint 6,265,822.
  New 517 diagnostic graph copies are ignored and cannot establish acceptance.
  RGB letterbox, float32 1×3×224×224 → raw_logit [1] unchanged. No accepted
  deployment-metadata package or Android decoding/preprocessing.

## This iteration's evidence

- Predeclared/committed ADR-019 and queued human review. Complete replay matches
  every saved Conv/BN by module order and saved parameter names, checks exact
  float32 parameter bits (including signed zero), geometry, epsilon/inference
  mode and one-to-one node scope. Includes Conv without a following BN.
- ml/reports/PLACEHOLDER-m4-complete-replay1.json: all 152 ordered training inputs.
  Every native graph and both promoted BN recipes pass serialized/actual runtime
  audits. All 87 operators have zero Python/ORT replay-fidelity differences;
  all taps preserve logits and every signed-accounting residual is zero.
  Four signed float64 terms separate Python replay, propagation, kernel and
  extraction drift; min/max/mean aggregates include all layers.
- Local native differences remain at 48/53 Conv and all 34 BN. Same-Python-input
  maxima 0.00000190735/0.00000762939; propagated maxima
  0.0000308752/0.000339508. Separate maxima are not additive causal accounting.
  Both promoted BN recipes match their Python expression exactly at every BN on
  both origins, but neither matches native Python across tested inputs at any BN.
  Rsqrt lowers/equal maxima at 22/12 layers on Python input, 23/11 on ORT input;
  divide lowers/equal/raises at 9/14/11 and 9/18/7. No favourable subset selected.
- Independent audit PASS: aggregate/private equality and reconstruction, 517
  graph records, runtime arithmetic/parameter audits, ordered training IDs,
  model/preparation/source/dependency/retained provenance and exact control
  logits/parity reproduction. Saved state unchanged; audit uses no inference.
  Graphs/weights/ordered details/logs stay ignored. Updated ADR, HUMAN-QUEUE,
  export/setup docs and ML README.

## Observed verification

- Initial combined replay subset: 32 PASS / 1 FAIL in 15.24s, 52 warnings.
  Duplicate correctly rejected but lacked expected one-to-one error wording.
  Production now adds scope to the boundary error; assertion retained.
  Corrected subset: 33 PASS in 16.07s, 52 warnings. After evidence-audit and
  partial-recipe-refusal additions: complete subset 19 PASS in 7.05s, 28 warnings.
  No test weakened/skipped/deleted.
- Diagnostic CLI exit 0: DIAGNOSTIC ONLY; independent audit PASS, M4 incomplete.
- bash scripts/check.sh exit 0: 377 ML tests PASS in 111.72s (alongside replay),
  144 legacy-export warnings; Android SKIPPED, RESULT PASS. No APK claim.
- Root repository-contract tests: 6 PASS in 0.068s after command documentation;
  final 6 PASS in 0.080s after all docs/iteration records. git diff --check clean;
  NEXT_ACTION exactly CONTINUE.
- No install/dependency/checkpoint/dataset acquisition, protected edit,
  review.sh, REVIEW/CHECK/GATE write, publication/push or external message.

## Open blockers and limits

Selected-baseline float and INT8 parity remains the implementation blocker.
Complete replay shows residual local native arithmetic throughout the backbone;
exact agreement between promoted ONNX/Python formulas does not reproduce the
native reference. No current baseline export is accepted. Float64 mobile support/
performance, unseen-input parity, clinical data approval, clinical/ethics/legal/
native-language validation and weight-notice approval remain unresolved.

## Next concrete step

Predeclare complete BN coefficient/epsilon-rounding replay against native Python,
using all 34 saved BNs, both existing input origins and all ordered training
components. Specify all recipes before execution, including epsilon/reciprocal/
alpha/beta rounding boundaries and unchanged saved bits. Audit expressions and
report all layers; do not select a favourable subset or assume a full-graph fix.
Conv kernel drift remains unresolved. Declare selective static QDQ scope from
training evidence before new quantisation/frozen evaluation, and resolve mobile
float64 support before bundling. REVIEW M4 only after acceptance.
