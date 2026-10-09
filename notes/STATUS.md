# Status

Updated: 2026-10-09T18:05:10Z

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
  persistence/reconstruction tests do not establish selected-baseline agreement.
- **Size ≤20 MB / preprocessing written and tested: BUILT.** Original float
  6,095,579 bytes; INT8 1,730,515/1,861,702; rounded diagnostic 6,255,113.
  RGB letterbox, float32 1×3×224×224 → raw_logit [1] unchanged. Android
  preprocessing/deployment metadata remain open; no new baseline graph written.

## This iteration's evidence

- Added export_remaining_evidence.py: lossless compressed dtype/shape/bit-addressed
  array files deduplicate only identical tensors; explicit ordered trees preserve
  complete component/operator/operand/graph/origin/control observations. All files
  stay under ignored data/ in fresh PLACEHOLDER directories. No pickle or symlink
  evidence reads; partial runs have no completed index.
- Before persisting a row, reconstruct every metric and require exact original
  native/runtime logit bits against supplied ADR-022 disabled prior observations.
  Original/captured/tapped instrumentation differences remain unsuppressed.
- Independent streaming reconstruction checks complete files/arrays/rows, hashes,
  specs, existing saved-constant/axis/boundary lineage and every metric, all numeric
  and boolean aggregate leaves, both fixed-budget original parity reports and
  supplied exact prior bits. No decode, eager recipe, forward or runtime session
  needed. Aggregate reports omit IDs, logits and individual failure observations.
- Generated two-component miniature architecture includes Conv/BN controls,
  residual/SE/activation/pooling/head arithmetic. Its prior logits are fixture
  observations, never selected saved M3 evidence. Tests establish persistence
  mechanics; no independent recomputation/authentication of historical inference.
  Full saved/preparation/source/dependency/prior report integration remains open.

## Observed verification

- New persistence suite: **37 PASS** (6.59s), two warnings; no failing attempt.
- bash scripts/check.sh exit 0: **723 ML tests PASS** (137.51s), 524 warnings;
  includes all 37 new tests. Android SKIPPED, RESULT PASS. No APK claim.
- Root repository contracts before final records: six PASS (0.066s).
  git diff --check clean; final documentation checks recorded in JOURNAL.
- No saved reference/state/fits/budget change, baseline retraining, frozen
  inference, quantisation fit, acquisition/install, protected edit, review.sh,
  REVIEW/CHECK/GATE write, external message/publication or push.

## Open blockers and limits

Selected-baseline float/INT8 parity remains the blocker. Persistence verifies
supplied observations, not saved provenance or historical inference authenticity.
The guarded training-scope runner and complete saved/preparation/source/current
code/dependency/prior report/runtime-expression reconstruction remain unfinished.
Exact ADR-022 logit comparisons are implemented but not run on selected saved
training observations. Selective static QDQ and mobile double support/performance
remain unresolved. Clinical validation, ethics/legal, native-language review and
weight notices still need humans.

## Next concrete step

Build the ADR-023 guarded training-scope runner around CompleteReplay and
OrderedEvidence. Independently reconstruct complete saved/preparation/retained/
source/current-code/dependency/ADR-022 prior report and all runtime expression
records, then audit a generated full-run fixture before opening an existing
ordered training image. Run all 152 ordered training components only with fixed
reference/fits/preprocessing/profile/budgets; repeat exact prior original-logit
checks and streaming aggregate reconstruction. No favourable subset, frozen
inference or new fit. Declare selective QDQ scope from that evidence before
fitting; resolve mobile support before bundling. REVIEW M4 only after acceptance;
do not start M5.
