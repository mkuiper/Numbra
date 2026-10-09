# Numbra ML — PLACEHOLDER data pipeline

**PLACEHOLDER — synthetic demonstration, not clinically validated.**
M0–M3 harness gates are closed. M3 supplies generated data, frozen component splits, CPU frozen-feature transfer
training, isolated evaluation and PLACEHOLDER model-card/report generation. Real
task data and Android implementation remain later work. M4 now exports and tests
ONNX graphs; both baseline INT8 attempts failed the fixed parity budgets. See
[export evidence](../docs/ML-EXPORT.md); no accepted deployable model yet.
[ADR-002](../decisions/ADR-002-dataset-selection.md) approves generated fixtures
only. Every future synthetic model, report and app result must say PLACEHOLDER.

Use Python 3.12 (observed 3.12.3) from the repository root:

```bash
python3 -m venv ml/.venv
PIP_NO_CACHE_DIR=1 ml/.venv/bin/python -m pip install --require-hashes -r ml/requirements-dev.txt
PIP_NO_CACHE_DIR=1 ml/.venv/bin/python -m pip install --no-build-isolation --no-deps -e ml
bash scripts/check.sh
python3 -m unittest discover -s tests -v
```

Or from `ml/`: `.venv/bin/python -m pytest -q`. Direct and transitive dependencies are pinned with wheel
hashes in `requirements-cpu.lock` plus `requirements-export.lock`, included by `requirements-dev.txt`. The combined lock
supports CPython 3.12 Linux x86_64 only. Install before the editable project so
pip can find the CPU-specific torch versions without dependency re-resolution.
Tests set their temporary directory to ignored `ml/tests/.tmp/`; their PNG/GIF
pixels are generated in code and contain no people or clinical data. No external
dataset, network service, weight or model is needed to run them.

The [data contract](../docs/ML-DATA-CONTRACT.md) describes the versioned JSONL
schema, taxonomy and loading interfaces. Export the row schema to stdout with:

```bash
ml/.venv/bin/python -m numbra_ml.schema
```

Typical use (the manifest and images are local generated files):

```python
from pathlib import Path
from numbra_ml.dataset import ManifestDataset

dataset = ManifestDataset.from_manifest(
    root=Path("data/prepared/synthetic-v2"),
    path=Path("data/prepared/synthetic-v2/manifest.jsonl"),
    split="train",
)
eligible, exclusions = dataset.supervised_selection()
for sample in dataset:
    # sample.image is oriented uint8 HWC RGB; no model preprocessing yet.
    print(sample.notice, sample.row.record_id, sample.binary_target)
```

No example manifest/image is committed. Missing/unconfirmed labels return no
target, and the explicit supervised selection also excludes missing groups and
unassigned/quarantined rows. Evaluation code must retain exclusion counts.
M2 implements deterministic generation, deduplication and group/source split
assignment; see [data preparation](../docs/DATA-PREPARATION.md). M3 adds training/evaluation; M4 specifies and tests model preprocessing.
The raw loader's RGB conversion is not the future model's full preprocessing spec.


Generate a current PLACEHOLDER run from repository root (output must be new/empty):

```bash
ml/.venv/bin/python -m numbra_ml.prepare --output data/prepared/synthetic-v2 --groups-per-source 128 --seed 20261009
```

The companion preparation report identifies connected evaluation components and
the held-out source. M3 must use those components, preserve frozen splits and
report the insufficient-count threshold fallback for the default profile. Use
`--groups-per-source 256 --split-profile selection_exercise` in a separate new
run to exercise sufficient threshold-selection counts (102/class) under ADR-008.
Both profiles remain PLACEHOLDER. Future reports/cards must name the targets
synthetic circle / synthetic square, never clinical classes; describe source C
as a single held-out-source fold. Synthetic metrics are not clinical performance.
The [evaluation library](../docs/ML-EVALUATION.md) now implements component index
selection, calibration/threshold isolation, count guards and metric summaries.
See [CPU training](../docs/ML-TRAINING.md) for checkpoint acquisition, the one-command
training run, provenance, reproduction and limitations. Only the checkpoint command
uses the network; task training/evaluation is offline. Weights/predictions stay
under ignored data/, aggregate reports/model cards under ml/reports/.

See [export and diagnostics](../docs/ML-EXPORT.md) for the fixed M4 budgets,
retained failed ONNX/INT8 attempts and training-only runtime/head attribution.
It also documents BatchNorm-preserving graphs, audits of actual ORT graphs and
corrected pre-activation boundary taps. These still fail the unchanged baseline
parity contract. All exports remain **PLACEHOLDER**; diagnostic success does not
close M4.

Same-input stem/depthwise Conv/BN replay is available as
`python -m numbra_ml.export_replay --output data/exports/PLACEHOLDER-<new-name>`.
It uses training images only, reports propagation separately from local kernel
arithmetic, and compares three fixed BN primitive formulas. See the export
document and ADR-015 for measured evidence; these copies are never app bundles.
