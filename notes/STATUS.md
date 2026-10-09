# Status

Updated: 2026-10-09T14:11:27Z

Current milestone: **M3 — Baseline classifier**, implementation ready for harness
review; **no M3 GATE yet**. NEXT_ACTION: REVIEW M3. M0/M1/M2 gates exist,
PASS WITH CHANGES; human review pending. M4 export and Android/app/APK work have
not started. All task models/results remain **PLACEHOLDER** under ADR-002.

## Acceptance status

- **CPU transfer training / reproducible command: BUILT.** Pinned anonymously
  retrieved publisher ImageNet MobileNetV3Small, frozen eval-mode features and
  train-only standardisation/binary head. Fixed seeded full-batch AdamW; no metadata
  fusion/search/early stopping. 35-wheel Python 3.12 Linux x86_64 hash lock.
  Training is offline; checkpoint acquisition is separate and checksum verified.
- **Script-generated evaluation: BUILT.** Baseline, identical reproduction and
  default-fallback JSON in ml/reports/. Isolated calibration/threshold partitions,
  unchanged component-count guards, high-sensitivity/secondary-specificity points,
  exact intervals, AUC/Brier/log-loss/ECE/reliability bins, pre-calibration metrics,
  source/synthetic-colour breakdowns/missingness and seeded conditional component
  bootstrap. Human skin-tone labels absent, explicitly unavailable as evidence.
  C is a single held-out source (one leave-one-source-out fold), no rotation.
- **Model card: BUILT.** Script-generated PLACEHOLDER cards name synthetic circle/
  square targets, data/intent/provenance/limits; no lesion, pure-neural, clinical
  calibration/accuracy or field-safety evidence. Weights/predictions remain ignored.
- **Review readiness: READY.** reviews/M3/HANDOFF.md supplies commands/evidence,
  source commit fd93e34/checksums, known limitations and requested scrutiny.
  New ADR-010 Accepted (autopilot) — pending human review, queued for humans.

## Observed results and verification

- Final bash scripts/check.sh: exit 0, **254 ML tests PASS** in 25.67s,
  Android SKIPPED, RESULT PASS. No APK claim.
- Earlier full check: 254 PASS in 25.74s. Initial new subset: 45 PASS in 6.38s;
  subsequently added fixture-to-written-report integration test, included in full
  254. No ML failures/skips/xfails or weakened existing tests.
- Root repository suite: 5 PASS (Builder-attested only). Initial root run reported
  four missing source-register entries for new technical setup URLs; added access
  bookkeeping to research/sources.md, then 5 PASS. No test changes.
- pip check: no broken requirements. Full force-reinstall of all 35 locked wheels
  used require-hashes; exact source/lock checksums still match baseline provenance.
- Baseline/repeat: 10.663/10.605s on desktop Intel Core Ultra 9 275HX/two threads.
  Model/prediction SHA-256 and reports match excluding four declared dynamic
  provenance fields. Combined float safetensors is 6,156,620 bytes (not M4 export).
  Strict saved-model reload matches backbone/head hashes; all 768 component logits
  reproduced exactly. Default-fallback run: 5.661s, zero exclusions in both fixtures.
- Baseline: train 76/class, calibration 52/class, threshold 102/class, test 26/class,
  C 128/class. Temperature 19.150006, selected threshold 0.4007988174; empirical
  selection sensitivity 97/102 with exact interval [0.889304,0.983894]. Internal
  test sensitivity 1/specificity 0.153846/AUC 0.766272. C sensitivity 0.914063/
  specificity 0.078125/AUC 0.592529: **below illustrative sensitivity target**.
  Low specificity/high referral burden and overfit training loss remain disclosed.
- Default: calibration 20/class sufficient, threshold 20/class insufficient:
  primary/secondary unavailable, **unselected refer-all** threshold zero.
  Sensitivity 1/specificity 0 describe fallback, never selected clinical performance.

## Open blockers and carried limits

- No implementation blocker; M3 harness review pending. Clinical/legal/ethics/
  native-language/weight-notice decisions still pending human review.
- No real task dataset approved; ImageNet/patient images were not downloaded.
  Publisher-declared Apache-2.0 checkpoint licence is not an image-rights warranty.
- Conditional bootstrap excludes model/calibration/threshold-fit uncertainty;
  exact post-selection intervals descriptive. Tiny/overlapping strata unstable.
  Synthetic colour bands are not skin-tone/fairness labels. One source fold only.
- Preparation visual links are trusted, unvalidated for real data. Training
  defaults/scaling/geometry/count guards are engineering decisions, not approval.
  High temperature is within bounds; frozen inputs/defaults were not tuned after
  results. Hardware/other-platform reproduction is unverified.
- M4 must quantise/export/check preprocessing and probability/threshold parity.
  M6 retains all ADR-001 symptom/contact/concern/quality/missingness rules; image
  score cannot establish disease absence. M7 needs encrypted consent/provenance.
- No protected edits, review.sh, REVIEW/CHECK/GATE writes, publishing/messages/
  pushes, secrets, tracked data/weights or APK. Harness owns tests/reviews/gates.

## Next concrete step

Harness runs M3 check/review. Next Builder iteration reads its messages/review in
full, answers every numbered issue and fixes them. Start M4 only after M3 gate.
