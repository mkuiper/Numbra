# Status

Updated: 2026-10-09T18:18:06Z

Current milestone: **M4 — On-device model export**, in progress. NEXT_ACTION:
CONTINUE. M0–M3 gates exist; no M4 gate, accepted export, app or APK.
All models/results remain **PLACEHOLDER**, synthetic-only under ADR-002.
All failed exports remain rejected; ADR-012's toy workaround is diagnostic only.

## M4 acceptance status

- **Quantised ONNX Runtime Mobile export: BUILT, ACCEPTANCE INCOMPLETE.**
  Original INT8 QDQ graphs still fail parity. No new quantisation fit, scope
  selection, deployment selection or mobile compatibility result this iteration.
- **Exported/Python parity: FAIL, budgets unchanged.** Prior ADR-022 rounded BN
  disabled/basic/extended maxima remain 0.000143051 raw / 0.00000183769
  probability, 13/21 violations, zero flips. No new selected-baseline forward,
  training replay, frozen inference, reference/state/fits/budget change or parity.
  Generated runner tests and selected static context are software/provenance
  evidence only; they do not establish selected-baseline numerical agreement.
- **Size ≤20 MB / preprocessing written and tested: BUILT.** Original float
  6,095,579 bytes; INT8 1,730,515/1,861,702; rounded diagnostic 6,255,113.
  RGB letterbox, float32 1×3×224×224 → raw_logit [1] unchanged. Android
  preprocessing/deployment metadata remain open; no new baseline graph written.

## This iteration's evidence

- Added export_remaining_run.py: complete saved/preparation/retained/source/
  current-code/dependency/ADR-022 report provenance and ordered training scope
  checked before setup; all actual runtime setup records audited before decode.
  Both graphs, native/original/captured/tapped observations, complete operator/
  origin/control scope, ordered persistence and exact original prior-logit bits
  connect to a read-only final streaming audit. Fresh ignored PLACEHOLDER outputs
  only; interrupted runs cannot publish a completed report.
- Added independent complete setup reconstruction: every whole/tapped/isolated/
  BN-control serialized graph binds exactly to saved constants and fixed recipe;
  every actual runtime expression/record and full file scope is reconstructed
  without sessions, forward calls, image decoding or evidence writes.
- ADR-022 historical source binding is explicit: full local source snapshot
  808cc3393ccf1cce95c2feeef91e5a8608b481e4 must match every recorded Python file
  and tree hash. Default prior audit retains current-code checks; live dependency
  pins/lock hashes stay exact. No historical fields/logits are overwritten, and
  source checks do not authenticate past inference. Rule recorded in ADR-023
  and HUMAN-QUEUE; current runner source/hardware provenance remains exact.
- Generated full-pipeline toy saved model and miniature residual/SE corruption
  fixtures exercise the runner/audits. Selected static context reconstructed
  twice for all 152 ordered training components with decode/forward/session
  creation blocked: ml/reports/PLACEHOLDER-m4-training-context1.json. No selected
  training image decoded or saved M3 forward run. Full selected replay is pending.

## Observed verification

- New guarded runner suite: **32 PASS** (29.37s), 20 warnings; no failed attempt.
- bash scripts/check.sh exit 0: **755 ML tests PASS** (171.03s), 544 warnings;
  includes all 32 new tests. Android SKIPPED, RESULT PASS. No APK claim.
- Root repository contracts: six PASS (0.074s) before final records; final
  documentation/whitespace verification recorded in JOURNAL.
- No saved reference/state/fits/budget change, baseline retraining/inference,
  quantisation fit, frozen evaluation, acquisition/install, protected edit,
  review.sh, REVIEW/CHECK/GATE write, external message/publication or push.

## Open blockers and limits

Selected-baseline float/INT8 parity still blocks M4. The complete guarded runner
is built and generated-fixture audited, but has not executed the selected 152
training inputs or generated selected replay observations. Local provenance and
retained observation reconstruction cannot authenticate historical inference.
Selective static QDQ scope and mobile double support/performance remain unresolved.
Clinical validation, ethics/legal, native-language review and weight notices still
need humans. Do not start M5 before M4 closes.

## Next concrete step

Execute the complete guarded training replay:
ml/.venv/bin/python -m numbra_ml.export_remaining_run
--profile-source-commit 808cc3393ccf1cce95c2feeef91e5a8608b481e4
--output data/exports/PLACEHOLDER-m4-remaining-training1
(use these three lines as one command). Retain every ordered training component,
fixed native reference/fits/preprocessing/profile/budgets and every control.
Independently run audit_training on the saved report with decode/forward/session
creation blocked; retain exact ADR-022 original-logit checks and complete runtime/
aggregate reconstruction. Declare selective QDQ scope from complete evidence
before a fit, then resolve mobile support before bundling. No favourable subset,
frozen inference or new fit at this diagnostic stage. REVIEW M4 only after acceptance.
