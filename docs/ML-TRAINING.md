# CPU training — PLACEHOLDER only

**PLACEHOLDER — synthetic demonstration, not clinically validated.** No suitable
real task cohort is approved under ADR-002. This command demonstrates transfer
from publisher-provided ImageNet features to artificial circle/square targets.
It supplies no lesion, disease, Nepal or skin-tone performance evidence.

## Setup and one-command training

Use the hash-locked Python 3.12 Linux x86_64 environment in
[DEV-SETUP.md](DEV-SETUP.md). The publisher's card/config/safetensors are pinned to
revision/checksums in pretrained.py; see [ADR-010](../decisions/ADR-010-cpu-transfer-training.md).
Only checkpoint acquisition needs anonymous network access:

```bash
ml/.venv/bin/python -m numbra_ml.pretrained
```

Generated task data must be prepared before training. M2/M3 preparation acceptance
already verified these exact defaults; existing local directories are preserved.
For a clean checkout, generate the explicit selection-count exercise:

```bash
ml/.venv/bin/python -m numbra_ml.prepare --output data/prepared/synthetic-v2-selection --groups-per-source 256 --split-profile selection_exercise --seed 20261009
```

One offline CPU command trains the head and writes evaluation/model card:

```bash
ml/.venv/bin/python -m numbra_ml.train --output data/models/PLACEHOLDER-m3-verification --report-name PLACEHOLDER-m3-verification
```

The verification names avoid overwriting archived tracked reports. Pick a new
output/report name for each repeat. The original observed baseline invoked
train with no arguments; the remaining defaults are identical.

Defaults: seed 20261009, two CPU threads, 16-image feature batches, 300 full-batch
AdamW steps, learning rate 0.03, weight decay 0.01, 1,000 conditional bootstrap
replicates. No early stopping, search, augmentation, metadata fusion or fitted
pixel transform. These engineering defaults were declared before running the
baseline, not optimised for observed test scores. Overrides are explicit and
recorded. No data preparation or acquisition is hidden inside training.

Learning-rate and decay overrides are available as `--learning-rate` and
`--weight-decay`, alongside the documented epoch/seed/batch/thread switches.
One-command training assumes the environment, checkpoint and prepared fixture
already exist. A clean checkout requires the explicit setup/acquisition/preparation
commands above; there is no clean-checkout wrapper.

## Outputs and provenance

- Ignored data/models/PLACEHOLDER-m3-baseline/: combined backbone/scaling/head
  PLACEHOLDER-model.safetensors, component logits in PLACEHOLDER-predictions.json
  and PLACEHOLDER-run.json. No weights/individual observations in git.
- Tracked ml/reports/PLACEHOLDER-m3-baseline.json: aggregate evaluation including
  counts, exact intervals, two endpoints, AUC, reliability bins/ECE, Brier/log-loss,
  before-calibration summaries, overlapping source/synthetic-colour cohorts and
  frozen test/held-out conditional bootstrap. No patient/skin-tone fairness claim.
- Tracked ml/reports/PLACEHOLDER-m3-baseline-MODEL-CARD.md: intended use, targets,
  actual operating-point status, limitations and human work.

Source C is one predeclared held-out source (one leave-one-source-out fold); no
rotation. Below count guards, calibration/selection remain unavailable and the
primary threshold is an **unselected refer-all** zero, not a selected target.
No clinical interpretation of synthetic sensitivity/specificity/AUC follows.

M3 REVIEW-1 reporting revision: archived JSON/card names above now contain
evaluation version 1.1.0. These are reporting-only rebuilds from the checksum-
verified saved prediction files through `evaluation_report`, `add_bootstrap` and
`model_card`; no retraining, input or fitted temperature/threshold changes.
`reporting_revision` records original report hashes and generating source hashes;
`provenance` still records the original training run, not the later reporting code.
Pre-calibration threshold metrics are null. Source/colour cells below 20/class
flag the small cell and suppress AUC, calibration summaries/bins and bootstrap;
this is an engineering display guard, not real-data privacy protection. Identical
bootstrap cohorts reuse their first seed/result. Cards include empirical evidence,
confusion counts, exact intervals and explicit per-row refer-all fallback markers.
The ignored original run JSON remains intact as historical training evidence.

Reports retain manifest/preparation/checkpoint/lock/source-file hashes, actual
installed versions, CPU/build information, git revision/dirty flag, config and
fit hashes. Frozen backbone hashes must agree before/after all extraction/fitting.
The scaling and head see train only. Raw logits undergo isolated calibration and
threshold selection via ADR-009; frozen test/source-C scores cannot select fits.

Preprocessing accepts oriented uint8 RGB from the verified loader, bounds dimensions
at 4096, and explicitly implements the deployment letterbox proposal at 224.
Its half-pixel/clamped bilinear mapping, half-up pixel/dimension rounding,
RGB-128/odd-right-bottom padding and float32 ImageNet normalisation are tested.
Publisher pretraining uses different centre-crop/bicubic geometry. M4/M6 still
must verify exported/Android preprocessing, orientation/alpha/decode budgets,
operator/quantisation parity and threshold stability. M3 has no exported artifact.

Writes are restricted to ignored data/ and local ml/reports/; refuse overwrite,
path escape and symlinked parents. Dependency version drift fails before training.
No hub credential lookup or network is used by training; pretrained=False loads
only already-verified local safetensors with strict state-key matching.

## Reproduction and default fallback exercise

A second run uses the same inputs/config, new output/report names:

```bash
ml/.venv/bin/python -m numbra_ml.train --output data/models/PLACEHOLDER-m3-verification-reproduction --report-name PLACEHOLDER-m3-verification-reproduction
```

Compare saved model/prediction byte hashes, training hashes and aggregate
evaluation/bootstrap fields. Exclude provenance clocks/elapsed time, git_dirty and
output_directory from report equality; those should differ. Other hardware and
platforms are unverified, despite deterministic CPU algorithms.

Generate the smaller default fixture in a clean checkout (skip generation if it
already exists) and explicitly exercise unavailable threshold selection:

```bash
ml/.venv/bin/python -m numbra_ml.prepare --output data/prepared/synthetic-v2 --groups-per-source 128 --seed 20261009
ml/.venv/bin/python -m numbra_ml.train --prepared data/prepared/synthetic-v2 --output data/models/PLACEHOLDER-m3-verification-default --report-name PLACEHOLDER-m3-verification-default
```

## Observed verification

Full check before model runs: 254 ML tests passed in 25.74s; Android skipped,
RESULT PASS. New tests use generated fixture pixels/invented feature arithmetic
and real toy neural modules; no network, patient images, skips or downloaded
weights are needed. They test isolation, frozen buffers, reproduction, geometry,
serialization, output/checkpoint safeguards, tied bootstrap arithmetic and a
fixture-to-head-to-written-report path. Actual pinned-weight runs completed with source commit fd93e34, unchanged source
files and declared defaults: baseline 10.663s, repeat 10.605s, default fixture
5.661s on Intel Core Ultra 9 275HX / two CPU threads. These are desktop timings,
not low-end-device benchmarks. Baseline and repeat model/prediction SHA-256 and
all report fields match after excluding four declared dynamic provenance fields.
Saved combined model is 6,156,620 bytes; this is float safetensors, not M4 export.
Zero exclusions in either fixture. Baseline train 76/class, calibration 52/class,
threshold 102/class, test 26/class, source-C 128/class.

Baseline temperature 19.150006 (within bounds, near maximum), threshold
0.4007988174, primary/secondary endpoints selected. Selection sensitivity
97/102=0.950980, exact interval [0.889304,0.983894]; **empirical target only**,
not independent assurance of sensitivity >=0.95. Training loss 0.721871 to
0.002350 shows an overfit artificial head; report the observed generalisation.

| PLACEHOLDER partition | TP/FN/TN/FP | Synthetic sensitivity | Synthetic specificity | AUC | Brier | ECE |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| test | 26/0/4/22 | 1.000000 | 0.153846 | 0.766272 | 0.211035 | 0.131328 |
| held-out C | 117/11/10/118 | 0.914063 | 0.078125 | 0.592529 | 0.248321 | 0.087975 |

**Source-C sensitivity is below the illustrative 0.95 target**, with low
specificity/high artificial referral burden. Do not tune the frozen inputs to
improve this. The bootstrap/exact intervals and source/colour breakdowns are
in the generated JSON; none establish clinical performance.

Default fixture calibration 20/class fits temperature 16.296730; threshold
20/class correctly leaves both endpoints unavailable, threshold zero and
**unselected refer-all**. Test sensitivity 1/specificity 0 and source-C sensitivity
1/specificity 0 describe that fallback, never a selected operating point.
Actual saved-model strict re-load matched backbone/head state hashes; rescoring
all 768 components in the same feature batches reproduced raw logits exactly
(max absolute difference 0). This is serialization evidence, not M4 export parity.

The reload claim now has a repository entry point, using the saved full model
without the original pretrained checkpoint or network:

```bash
ml/.venv/bin/python -m numbra_ml.verify
ml/.venv/bin/python -m numbra_ml.verify --run data/models/PLACEHOLDER-m3-reproduction
ml/.venv/bin/python -m numbra_ml.verify --prepared data/prepared/synthetic-v2 --run data/models/PLACEHOLDER-m3-default
```

It verifies artifact/preparation/state hashes and component prediction metadata,
strictly restores the bundled backbone/scaling/head, rescores in original batches,
and fails on raw-logit error above 1e-5 or any frozen-threshold decision flip.
The test of record also runs `train_run` end to end on the 16-group fixture using
an explicitly injected toy backbone supplier, including saving, provenance,
report/card writing, reload parity, tamper rejection and overwrite guards. This
test requires no external weights/network; publisher-weight verification is an
additional Builder-attested command, not downloaded by the test suite.

Real-data tuning requires a model-selection split or nested cross-validation
before calibration; this synthetic exercise has neither and must not be tuned on
the held-out partitions. M4 raw/probability/threshold parity must replace the M0
0.02-probability-only proposal before any export acceptance.

Original generated baseline/repeat/default report and model-card filenames are
archived in ml/reports/. New verification commands above use fresh names.

## Open questions

- Do humans approve weight rights/notices, fixed training/geometry/count choices and conditional bootstrap?
- Which licensed cohorts and independently reviewed clinical protocol replace the artificial targets?
- What low-end Android performance/parity will M4–M8 actually measure?

## Confidence

High for tested synthetic mechanics and anonymous pinned access; no clinical or
device-validation evidence.
