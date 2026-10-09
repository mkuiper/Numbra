# Status

Updated: 2026-10-09T13:50:03Z

Current milestone: **M3 — Baseline classifier**, in progress; **not ready for review**.
NEXT_ACTION: CONTINUE. M0/M1/M2 harness GATE files exist, PASS WITH CHANGES;
human review pending. No M3 review folder/gate, trained baseline, script-written
model evaluation report, model card, export, app or APK exists.

## Acceptance status

- **CPU transfer-learning / reproducible training: NOT BUILT.** ADR-005 still selects
  frozen pretrained MobileNetV3Small features plus a binary head. No new torch/timm
  dependency installation or pretrained acquisition this iteration. Verify anonymous
  access and publisher permission, pin revision/checksum and use ignored
  data/pretrained/ before acquisition. Hashed dependency locking remains required.
- **Script-generated evaluation: PARTIAL, NOT COMPLETE.** evaluation.py now implements
  one prespecified index image/component, manifest/report consistency/checksum checks,
  separate bounded temperature scaling, calibration 20/class and threshold 100/class
  guards, unselected refer-all fallback, high-sensitivity and secondary-specificity
  threshold selection, exact 95% binomial intervals, confusion/AUC/calibration metrics,
  source/synthetic-colour breakdowns and frozen single held-out-source reporting.
  No trained scores or script-written ml/reports artifact. Seeded component bootstrap,
  training integration and full run/checkpoint/dependency/hardware provenance remain.
- **Model card: NOT BUILT.** Must say PLACEHOLDER, synthetic circle/square targets,
  synthetic colour strata, no clinical validation/calibrated probability and no
  pure-neural/skin-lesion representation. C-only is one held-out-source fold.
- **Review readiness: NOT READY.** No M3 HANDOFF or review request. ADR-009 is
  Accepted (autopilot) — pending human review and queued in HUMAN-QUEUE.

## Completed this iteration

- Added component index/image selection by first sorted record ID before scores;
  exactly one score/active component, retained quarantine exclusions, rejected
  source/split/target/mapping disagreement and known linked-unit inflation.
- Isolated calibration and threshold fit splits; recorded fitting score hashes.
  Bounded temperature fit records boundary optima. Selected/fallback/degenerate
  statuses distinguish insufficient counts from actual selection.
- Added exact sensitivity/specificity intervals, stable-logit loss, tied-rank AUC,
  Brier, equal-width reliability bins/ECE, null unavailable metrics, source/colour
  counts/intervals and missing/conflicting component colour categories.
- Added 58 synthetic arithmetic/generated-fixture tests; documented implementation
  choices/limits in ADR-009 and docs/ML-EVALUATION.md; updated README/setup/queue.

## Observed verification

- bash scripts/check.sh: exit 0, **208 ML tests PASS** in 18.94s;
  Android SKIPPED, RESULT PASS. No APK or completed-M3 claim.
- Evaluation-specific suite: **58 PASS** in 5.11s.
- python3 -m unittest discover -s tests -v: **5 PASS** (Builder-attested only).
- pip check: no broken requirements. git diff --check PASS before final records;
  final whitespace/status validation performed before commit.
- Initial evaluation suite: 34 passed, 1 failed, 10 setup errors. New fixture used
  8 groups below the existing 16 minimum; corrected fixture/count assertions.
  New report emitted integer target-name keys; implementation now uses explicit
  string keys matching its JSON output contract. Existing tests were preserved.
- Existing shapes-v2 default and selection_exercise manifests loaded with checksum
  and partition checks: 384/768 active components, zero exclusions. Mechanical
  smoke exercise used constant invented logits, **no trained model**. Default
  calibration 20/class, threshold 20/class => both endpoints unavailable with
  unselected refer-all threshold 0. Larger calibration 52/class, threshold 102/class
  => primary selected threshold 0.5 explicitly degenerate refer_all, secondary
  above-one sentinel explicitly degenerate all_negative. These are code-path
  checks, not model/clinical performance. No report or generated data committed.

## Open blockers and carried limits

- No immediate implementation blocker. Checkpoint access/permission not yet attempted.
  Clinical/legal/ethics/native-language approvals remain pending.
- ADR-002 remains synthetic-only. Every downstream model/report/UI is PLACEHOLDER.
- Evaluation trusts preparation's decoded/near-visual links; real patient/source
  independence and duplicate adjudication remain unestablished. Temperature bounds
  and count guards are engineering choices; synthetic colour strata are not fairness.
- Future training must fit features/head/preprocessing only on permitted training
  components and never tune on frozen test/held-out scores. Fit-isolation tests
  cover the evaluation layer only, not a yet-unbuilt model producer.
- M6/M7 retain full ADR-001 symptom/concern/contact/missingness rules and consent/
  provenance/encrypted local storage requirements. No negative diagnosis wording.
- No protected edits, review.sh, review/check/gate writes, patient data, weights,
  publishing, messages or pushes. Harness owns reviews/gates/pushes.

## Next concrete step

Verify/install hashed CPU model dependencies and ADR-005 anonymous pretrained
checkpoint permission/access/revision/checksum. Implement the reproducible frozen-
feature training command using the component index and evaluation library; add
seeded component bootstrap uncertainty, script-written reports with run provenance,
training-isolation/reproduction tests and an honest PLACEHOLDER model card.
