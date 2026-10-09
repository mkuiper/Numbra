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
ml/.venv/bin/python -m numbra_ml.train
```

Defaults: seed 20261009, two CPU threads, 16-image feature batches, 300 full-batch
AdamW steps, learning rate 0.03, weight decay 0.01, 1,000 conditional bootstrap
replicates. No early stopping, search, augmentation, metadata fusion or fitted
pixel transform. These engineering defaults were declared before running the
baseline, not optimised for observed test scores. Overrides are explicit and
recorded. No data preparation or acquisition is hidden inside training.

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
ml/.venv/bin/python -m numbra_ml.train --output data/models/PLACEHOLDER-m3-reproduction --report-name PLACEHOLDER-m3-reproduction
```

Compare saved model/prediction byte hashes, training hashes and aggregate
evaluation/bootstrap fields. Exclude provenance clocks/elapsed time, git_dirty and
output_directory from report equality; those should differ. Other hardware and
platforms are unverified, despite deterministic CPU algorithms.

Generate the smaller default fixture in a clean checkout (skip generation if it
already exists) and explicitly exercise unavailable threshold selection:

```bash
ml/.venv/bin/python -m numbra_ml.prepare --output data/prepared/synthetic-v2 --groups-per-source 128 --seed 20261009
ml/.venv/bin/python -m numbra_ml.train --prepared data/prepared/synthetic-v2 --output data/models/PLACEHOLDER-m3-default --report-name PLACEHOLDER-m3-default
```

## Observed verification

Full check before model runs: 254 ML tests passed in 25.74s; Android skipped,
RESULT PASS. New tests use generated fixture pixels/invented feature arithmetic
and real toy neural modules; no network, patient images, skips or downloaded
weights are needed. They test isolation, frozen buffers, reproduction, geometry,
serialization, output/checkpoint safeguards, tied bootstrap arithmetic and a
fixture-to-head-to-written-report path. Actual pinned-weight training/reproduction
results will be recorded after the commands complete.

## Open questions

- Do humans approve weight rights/notices, fixed training/geometry/count choices and conditional bootstrap?
- Which licensed cohorts and independently reviewed clinical protocol replace the artificial targets?
- What low-end Android performance/parity will M4–M8 actually measure?

## Confidence

High for tested synthetic mechanics and anonymous pinned access; no clinical or
device-validation evidence.
