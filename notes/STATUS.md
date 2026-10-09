# Status

Updated: 2026-10-09T13:38:44Z

Current milestone: **M3 — Baseline classifier**, in progress; **not ready for review**.
NEXT_ACTION: CONTINUE. M0/M1/M2 harness GATE files exist, PASS WITH CHANGES;
human review pending. M2 Review-1 is answered in reviews/M2/RESPONSE-1.md.
No M3 gate, trained model, evaluation report, exported model, app or APK exists.

## Acceptance status

- **CPU transfer-learning / reproducible training: NOT BUILT.** This iteration
  prepares M3 fixtures and resolves M2 follow-through only. ADR-005 still selects
  frozen pretrained MobileNetV3Small features plus a binary head. No torch/timm
  dependency installation or pretrained-weight acquisition yet. Before download,
  verify anonymous access, declared permission, revision/checksum and use ignored
  data/pretrained/. Exact/hashed dependency locking remains required M3 work.
- **Script-generated evaluation: NOT BUILT.** shapes-v2 and preparation 1.1.0
  now support source-membership × class splits, labelled threshold-count exercise,
  honest target names, background-derived synthetic colour strata and nearest
  unlinked-component distance audit. Default fixture requires unselected refer-all;
  explicit selection_exercise fixture has 102 threshold and 52 separate calibration
  components/class. Actual calibration, count guards, selection, exact intervals,
  sensitivity/specificity/AUC, breakdowns and held-out-source metrics remain work.
- **Model card: NOT BUILT.** Must say PLACEHOLDER, synthetic circle/square targets,
  synthetic colour strata, no clinical validation, no pure-neural/skin-lesion
  representation, and no clinically calibrated probability. Source C alone must
  be described as single held-out source (one leave-one-source-out fold).
- **Review readiness: NOT READY.** No M3 HANDOFF/review requested. ADR-008 carries
  Accepted (autopilot) — pending human review and is queued for humans.

## Completed this iteration

- Addressed all ten M2 non-blocking review items in RESPONSE-1, with M3-specific
  report/card enforcement and source-fold reporting explicitly carried forward.
- shapes-v2: matched exact circle/square pixel areas, overlapping signed contrasts,
  group-level 0.10 Bernoulli rendered-shape flips, stronger procedural source styles.
  Diagnoses now synthetic_circle/synthetic_square; audit names the artificial targets.
- Source-membership × target stratification keeps linked groups whole and reports
  explicit per-split/source/class counts. New selection_exercise 30/20/40/10 profile
  reaches the existing ADR-001 guard within generator 256-group / 2000-row caps.
- Boundary tests at/below/above RMS 2, unrelated component counts, nearest unlinked
  pair, symlink-parent escape, checkout root discovery and alternate holdout isolation.
- Updated preparation/setup/data-contract/README documentation and M2 handoff;
  original shapes-v1 evidence remains historical and local runs untouched.

## Observed verification

- bash scripts/check.sh: exit 0, **150 ML tests PASS**, Android SKIPPED, RESULT PASS.
- python3 -m unittest discover -s tests -v: **5 PASS** (Builder-attested only).
- ml/.venv/bin/python -m pip check: no broken requirements; git diff --check PASS.
- Preparation-specific suite: **40 PASS**. Initial new nested-root negative test
  failed because a valid outer checkout existed; corrected to assert discovery
  of that checkout and failure without any checkout ancestor. Rationale is queued.
- Default 128 groups/source: 384 components / 768 image rows; train/calibration/
  threshold-validation/test/held-out components 148/40/40/28/128. Threshold 20/class,
  calibration 20/class, test 14/class. Source A/B counts equal in each partition/class.
- selection_exercise 256 groups/source: 768 components / 1536 image rows;
  components 152/104/204/52/256. Threshold 102/class, calibration 52/class,
  test 26/class, held-out 128/class. No exclusions/quarantine in either observed run.
- Default reproduction: all **771 generated files byte-identical**.
  Default manifest SHA-256:
  0a4adb62e625bed27271c42abbc8aef27bb28a05f5bd9ea018a14471738d7b58.
  Selection-exercise manifest SHA-256:
  2d141bc62205d88b7116cbe410e9262a96d771dec34c30e88ae6ad9c4bee839e.
- Nearest unlinked RMS 8.586645 default / 8.204261 larger, vs link cutoff 2.
  Default best mean-intensity threshold balanced accuracy 0.541667 (fixture check).
  None of these numbers are model performance or clinical results.
- No protected edits, review.sh, reviewer/check/gate writes, patient data, weights,
  publishing, messages or pushes. Harness owns tests of record/review/gates/pushes.

## Carried requirements and limitations

- No immediate implementation blocker. Clinical/legal/ethics/native-language
  review remains pending; pretrained checkpoint access/permission not yet attempted.
- Real data remains unapproved under ADR-002. All models/UI/reports stay PLACEHOLDER.
- Component IDs are evaluation units; choose a deterministic index image before
  scores, never treat views as independent or tune on frozen test/held-out rows.
- Fixture difficulty and label noise do not prove clinical realism. Colour strata
  are generated background luminance, never fairness evidence. Visual heuristic,
  one-label-per-component quarantine and invented source/group IDs remain unfit
  for unaudited real cohorts. Quadratic duplicate search cap remains 2000.
- M6 must implement full ADR-001 question superset, explicit volunteer concern
  and contact-yes referral; missingness never means normal. M7 retains trigger
  answers and detailed consent/confirmation/custodian provenance in encrypted
  local storage. No negative diagnosis wording is permitted.

## Next concrete step

Implement M3 component/index-image selection and evaluation primitives with tests:
calibration/threshold-fit isolation, count-guard refer-all fallback, sufficient-count
selection, tie boundaries, exact sensitivity intervals, AUC/calibration summaries,
missing/single-class subgroup handling and frozen held-out-source reporting.
Then verify/install hashed CPU model dependencies and check ADR-005 weight access
before adding reproducible frozen-feature transfer training and a model card.
