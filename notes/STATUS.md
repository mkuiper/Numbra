# Status

Updated: 2026-10-09T18:26:49Z

Current milestone: **M4 — On-device model export**, in progress. M0–M3 gates
exist; M4 acceptance remains incomplete. All models/results **PLACEHOLDER**.
NEXT_ACTION: CONTINUE. No app or APK.

## M4 acceptance status

- Quantised ONNX Runtime Mobile export: built but not accepted. Original INT8
  graphs fail parity; no new fit, scope selection or mobile result.
- Exported/Python parity: FAIL at unchanged ADR-011 budgets. Original ADR-022
  rounded BN max raw/probability error 0.000143051/0.00000183769, 13/21
  violations, zero flips. Full ADR-023 training replay is now running.
- Size ≤20 MB and preprocessing: built/tested; unchanged original float
  6,095,579 bytes; INT8 1,730,515/1,861,702; rounded diagnostic 6,255,113.
  RGB letterbox float32 1×3×224×224 → raw_logit [1]. Deployment metadata open.

## Current progress

First runner attempt stopped during rounded runtime setup before image decoding
or forward: disabled ORT removed 136 directly unused original BN initializers.
Corrected audit records only removals without direct consumers or input/output
roles; all live/Identity/tapped/Constant and retained-bit checks remain.
Generated nondefault BN and eight corruption regressions added; focused suite
112 PASS. Static selected runtime audit PASS without inference.

Fresh PLACEHOLDER-m4-remaining-training2 is executing all 152 ordered training
inputs, unchanged saved model/state/fits/preprocessing/profile/budgets and all
controls. Seven rows retained at this checkpoint; prior-logit bits exact per row.
No completed report or final evidence-audit claim yet.

Required check exit 0: 764 ML PASS, 564 warnings, 176.43s; Android SKIPPED.
Six root contracts PASS. All observations/weights/graphs ignored; no protected
edit, review.sh, REVIEW/CHECK/GATE write, push or publication.

## Next concrete step and blockers

Finish the running full replay and independently reconstruct its saved report
with decode/forward/session/recipe/writes blocked. Inspect full arithmetic
evidence before predeclaring any graph/QDQ strategy. Selected float/INT8 parity
and mobile support still block M4; do not request review or start M5 yet.
