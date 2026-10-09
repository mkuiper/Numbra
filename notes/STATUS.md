# Status

Updated: 2026-10-09T16:59:54Z

Current milestone: **M4 — On-device model export**, in progress. NEXT_ACTION:
CONTINUE. M0–M3 gates exist (PASS WITH CHANGES); no M4 gate, app or APK.
All task models/results remain **PLACEHOLDER**, synthetic-only under ADR-002.
Every failed export remains rejected; ADR-012's toy diagnostic workaround stays
in force and cannot substitute for accepted selected-baseline parity.

## M4 acceptance status

- **Quantised ONNX Runtime Mobile export: BUILT, ACCEPTANCE INCOMPLETE.** Both
  original INT8 QDQ graphs fail parity, calibrated on all/only 152 training
  components. No new quantisation fit or scope/deployment selection this iteration.
  Mobile double operator/ABI support and performance remain unverified.
- **Exported/Python parity: FAIL, budgets unchanged.** All eight ADR-022 graph/
  runtime-profile comparisons FAIL on every ordered training input. Rounded-BN
  disabled/basic/extended maxima remain 0.000143051 raw / 0.00000183769 probability
  (13/21 violations); all maxima increase to 0.000310421 / 0.00000394886 (11/15).
  All profiles have zero flips. Preserved control and every prior failure retained.
  No frozen evaluation, reference/model/fit/budget change or accepted bundle.
- **Size ≤20 MB / preprocessing written and tested: BUILT.** Original float
  6,095,579 bytes; INT8 1,730,515/1,861,702; unchanged rounded diagnostic 6,255,113.
  All new runtime copies <20 MB. RGB letterbox, float32 1×3×224×224 → raw_logit [1]
  unchanged. No accepted deployment metadata or Android decoding/preprocessing.

## This iteration's evidence

- Predeclared/committed ADR-022 before implementation/execution; queued human
  review. Added fixed disabled/basic/extended/all comparison runner, original and
  separate feature-tapped runtime graphs, exact folded-coefficient semantics
  audits and independent no-inference evidence/provenance reconstruction.
- ml/reports/PLACEHOLDER-m4-runtime-profiles1.json retains both unchanged graphs
  × all four profiles × all 152 ordered training index images. Every numeric
  failure retained. Basic/extended do not fix candidate errors; all increases
  maxima. Every comparison has zero feature-tap changes and frozen-threshold flips.
- All eight candidate runtime BN-expression audits PASS. Disabled retains 204
  expression nodes/68 coefficient Casts; others fold all 68 Casts into exact
  double coefficient bits and retain 136 expression nodes. Every double Mul/Add
  and float32 boundary checked. Extended/all change Conv/fusion/layout operators
  outside BN; their arithmetic equivalence and mobile support remain UNVERIFIED.
- Independent audit PASS: 20 graph records, complete profile/input/reference
  scope, coefficients, parity/failures/features/taps, saved model/preparation/
  retained/source/prior/current-code/dependency provenance. Disabled details
  reproduce ADR-021 exactly for both graphs. Private audit SHA-256:
  ecde48f2f7b89dd3107b5b3908b2470102671983b6f45e634896b8b3bfbe351f.

## Observed verification

- Initial new subset: 25 PASS in 9.27s, 28 warnings. Strengthened same-boundary
  test initially 4 FAIL in 2.15s because it assumed upstream native/ORT hard-swish
  inputs were identical. Corrected to use actual runtime BN inputs; exact output
  assertions and production budgets retained. Corrected subset: 25 PASS in 9.55s.
- Added four stale-prior/empty-experiment rejection cases before opening inputs.
  Full bash scripts/check.sh exit 0: **463 ML tests PASS** in 77.49s, 198 warnings;
  Android SKIPPED, RESULT PASS. No APK claim. No existing test skipped/deleted/
  weakened, and no parity tolerance widened.
- Root contract suites: 6 PASS in 0.072s; git diff --check clean. Baseline
  diagnostic and independent no-inference audit exit 0/PASS (evidence only).
- No install/acquisition, protected edit, review.sh, REVIEW/CHECK/GATE write,
  publishing/push, external message or app implementation.

## Open blockers and limits

Selected-baseline whole-model float and INT8 parity remains the blocker. Runtime
profiles cannot resolve it; exact BN expression alone is insufficient. Other
activation/pooling/head arithmetic and Conv propagation remain to isolate.
Mobile double support/performance, clinical data approval/validation, ethics/
legal/native-language review and weight-notice approval remain unresolved.

## Next concrete step

Predeclare a bounded complete training-only same-input replay of remaining
activations, pooling and head boundaries, including saved/tapped runtime inputs,
local arithmetic versus propagation, actual serialized/runtime operator audits
and complete scope reconstruction. Preserve all existing Conv/BN controls and
fixed budgets; do not repeat failed profiles or select a favourable layer/input
subset. Declare selective static QDQ scope from training evidence before a new
quantisation fit/frozen evaluation; resolve mobile support before bundling.
REVIEW M4 only after acceptance; roadmap order prevents starting M5.
