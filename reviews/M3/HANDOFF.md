# M3 HANDOFF — CPU transfer baseline, always PLACEHOLDER

Date: 2026-10-09 UTC
M3 gate closed PASS WITH CHANGES by harness 2026-10-09T14:16:08Z.
Review follow-through is recorded in RESPONSE-1.md; no M3 rereview requested.

## Post-gate follow-through

Training orchestration now has an end-to-end toy-backbone test of record with
saved-model verification and tamper/overwrite checks. `python -m numbra_ml.verify`
provides the reproducible Python reference previously only attested manually.
Observed on original saved baseline/reproduction/default: 768/768/384 components,
max raw-logit and calibrated probability errors **0**, frozen-threshold flips **0**.
No pretrained checkpoint/network needed for full bundled-model reload.

Aggregate reports/cards now use evaluation 1.1.0: explicit operating-point evidence,
confusion/exact intervals/fallback markers, pre-calibration threshold fields null,
source/colour small-cell flags and AUC/calibration/bootstrap suppression below
20/class, identical bootstrap cohorts reuse one seed/result. Reporting-only rebuild
retains original training provenance/fits and records separate reporting hashes.
Original ignored training run JSON remains historical. Real-data model-selection
split and M4 raw/probability/decision-flip checks are recorded in ADR-010.

Observed post-gate check: **258 ML tests PASS in 27.36s**, Android SKIPPED,
RESULT PASS. Root repository suite: **5 PASS** (Builder-attested only).
Original acceptance/training evidence below remains historical M3 evidence;
updated tests/reporting code is later than its fd93e34 training source revision.

## Acceptance evidence

1. CPU-trainable transfer baseline: pinned anonymously retrieved publisher ImageNet
   MobileNetV3Small features, frozen parameters/eval buffers, train-only feature
   standardisation and binary linear head. Fixed seeded full-batch AdamW.
   One command trains and evaluates. No metadata fusion (optional in roadmap).
2. Script-generated ml/reports/: baseline, identical reproduction and smaller
   default-fixture JSON reports. Includes frozen primary sensitivity endpoint and
   secondary specificity endpoint, confusion/exact intervals/AUC, temperature,
   Brier/log-loss/ECE/reliability bins, before-calibration, source/synthetic-colour
   breakdowns, missingness and conditional component-bootstrap intervals.
   Human skin-tone annotations absent; no skin-tone/fairness claim.
   Source C is **single held-out source (one leave-one-source-out fold)**.
3. Generated PLACEHOLDER model cards for all three reports state data/targets,
   intended software-test-only use, limits and human follow-through. Explicit
   synthetic circle/square, no lesion/pure-neural or clinical validation.

Sources/models: ADR-002 synthetic-only; ADR-005 selected architecture/runtime;
ADR-008 fixture/selection-count exercise; ADR-009 component/isolated evaluation;
new ADR-010 fixed CPU training/preprocessing/bootstrap, queued for human review.
No real task cohort or patient/ImageNet images acquired. Every model/report/card
says PLACEHOLDER. No exports, app or APK; M4 remains untouched.

## Verification

From repository root with the hash-locked Python 3.12 Linux x86_64 environment:

```bash
bash scripts/check.sh
python3 -m unittest discover -s tests -v
ml/.venv/bin/python -m pip check
```

Observed full check before model runs: 254 ML tests PASS in 25.74s, Android SKIPPED,
RESULT PASS. Final check run is recorded in STATUS/JOURNAL. Root suite 5 PASS
(Builder-attested; not in protected check.sh). No broken requirements.
New training/preprocessing/bootstrap tests require no external weights/network:
train isolation under nontrain-label/feature mutations, frozen BatchNorm/dropout,
deterministic head, toy-model save/reload, image checksum checks, geometry/channel/
padding/bounds, tied bootstrap AUC versus pairwise arithmetic, missing metrics,
output-name/path/overwrite restrictions and generated-fixture-to-written-report.

Fresh ignored fixture/checkpoint creation, then **one training command** with new
names (tracked archived report names intentionally cannot be overwritten):

```bash
ml/.venv/bin/python -m numbra_ml.pretrained
ml/.venv/bin/python -m numbra_ml.prepare --output data/prepared/synthetic-v2-selection --groups-per-source 256 --split-profile selection_exercise --seed 20261009
ml/.venv/bin/python -m numbra_ml.train --output data/models/PLACEHOLDER-m3-verification --report-name PLACEHOLDER-m3-verification
```

Skip preparation if that verified local directory already exists. Subsequent
training is offline. Second run for reproducibility uses new names:

```bash
ml/.venv/bin/python -m numbra_ml.train --output data/models/PLACEHOLDER-m3-verification-reproduction --report-name PLACEHOLDER-m3-verification-reproduction
```

See [ML-TRAINING.md](../../docs/ML-TRAINING.md) for exact setup/default-fallback
commands and result discussion, [baseline report](../../ml/reports/PLACEHOLDER-m3-baseline.json),
[model card](../../ml/reports/PLACEHOLDER-m3-baseline-MODEL-CARD.md).
Archived reports record code commit fd93e34 and exact source hashes; final source
tree remains the same. Documentation/iteration records are later commits.

## Observed results and reproduction

Intel Core Ultra 9 275HX, two CPU threads: baseline 10.663s, repeat 10.605s,
default fixture 5.661s. These are desktop timings, not mobile benchmarks.
Baseline 152 train / 104 calibration / 204 threshold / 52 test / 256 source-C
components, zero exclusions, one index image/component. Temperature 19.150006
within [0.05,20] near upper bound; threshold 0.4007988174, selected/nonnull,
empirical sensitivity target only. Selection sensitivity 97/102=0.950980,
exact interval [0.889304,0.983894]; no independent target guarantee.

| PLACEHOLDER cohort | TP/FN/TN/FP | Synthetic sensitivity | Synthetic specificity | AUC |
| --- | --- | ---: | ---: | ---: |
| test | 26/0/4/22 | 1.000000 | 0.153846 | 0.766272 |
| held-out source C | 117/11/10/118 | 0.914063 | 0.078125 | 0.592529 |

Source-C sensitivity falls below the illustrative target. Specificity is low/
referral burden high. Training loss 0.721871 -> 0.002350 overfits artificial
training targets; do not interpret this or the internal sensitivity as clinical
success. Prespecified data/config were not tuned after frozen test/source results.

Default fixture has 20 threshold components/class, correctly unavailable primary/
secondary selection with unselected refer-all threshold zero, despite sufficient
20/class separate calibration. Its sensitivity 1/specificity 0 describes fallback.
Source/colour bootstrap cohorts overlap; small strata unreliable. Bootstrap
conditions on the frozen model/temperature/threshold, excludes fit uncertainty.

Baseline and reproduction model/prediction byte hashes, fitting hashes, all report
fields agree except created_utc, elapsed_seconds, git_dirty and output_directory:
- Model bytes: 6,156,620 (float safetensors; not M4 quantisation).
- Model SHA-256: 734328e3568335b9f415b4ca06b813872a9e43bd432717908bc0f1d4c7e2ae43
- Predictions SHA-256: c16e2f09f44916cb7bd20de0f402126f35a46573c7c45b89cb55d1f231f3f449
- Frozen backbone SHA-256: e39218ff0193574b9a8ea33646db9298d27cc6b6e49ab664c806f3cd263a852b
- Dependency lock SHA-256: 54022e4eb1ab4fad6d90f65e2f21784411daf7e7875cf5b8f81a75d90f0309cd

Actual saved model strict re-load matches backbone/head state hashes; re-scoring
all 768 active components in batches of 16 yields max raw-logit difference **0**.
This is serialization evidence, not exported/quantised parity.

## Scrutiny requested and known gaps

- Verify train-only scaling/head and immutable backbone, component index before
  features, separate fit splits, no test/held-out fitting or post-result tuning.
- Scrutinise ordinary unstratified component bootstrap and conditioning/valid-count
  disclosures, exact intervals and selected/fallback semantics.
- Scrutinise provenance, dependency drift/anonymous checksum checks and path guards.
  The lock hashes wheels for one platform; installed versions are checked, not an
  installed-file tamper audit. Initial floating resolution was followed by full
  hash-validated force-reinstall of all 35 locked wheels.
- Judge whether one procedural held-out-source fold adequately satisfies the POC;
  ADR-008/009 disclose no rotation. No real external validation or skin-tone evidence.
- Review engineering fit/default/letterbox choices: geometry differs from publisher
  centre-crop and temperature is high; no geometry superiority or clinical
  calibration claim. Human clinical/legal/ethics/weight-notice reviews remain.
- Preparation's visual duplicate heuristic is trusted, not validated independently.
  M4 must quantise/export, test preprocessing/output parity and threshold crossings.
  M6 must implement symptom/concern/contact/quality/missingness overrides; scores
  cannot establish disease absence. No low-end device/inference claim now.

No protected file edits, review.sh, REVIEW/CHECK/GATE writes, pushes, publications,
messages, secrets or committed data/weights. Harness should run/check/review M3.
