# Numbra ML — PLACEHOLDER data pipeline

**PLACEHOLDER — synthetic demonstration, not clinically validated.**
M0/M1 harness gates are closed. M2 adds deterministic generated data, duplicate
components and frozen splits. No training, real-data acquisition, model export or
Android implementation occurs here.
[ADR-002](../decisions/ADR-002-dataset-selection.md) approves generated fixtures
only. Every future synthetic model, report and app result must say PLACEHOLDER.

Use Python 3.12 (observed 3.12.3) from the repository root:

```bash
python3 -m venv ml/.venv
PIP_NO_CACHE_DIR=1 ml/.venv/bin/python -m pip install -r ml/requirements-dev.txt
PIP_NO_CACHE_DIR=1 ml/.venv/bin/python -m pip install --no-build-isolation --no-deps -e ml
bash scripts/check.sh
python3 -m unittest discover -s tests -v
```

Or from `ml/`: `.venv/bin/python -m pytest -q`. All direct and transitive M1
runtime/test/build dependencies are version-pinned in `requirements-dev.txt`.
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
    root=Path("data/prepared/synthetic-v1"),
    path=Path("data/prepared/synthetic-v1/manifest.jsonl"),
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


Generate the M2 PLACEHOLDER run from repository root (output must be new/empty):

```bash
ml/.venv/bin/python -m numbra_ml.prepare --output data/prepared/synthetic-v1 --groups-per-source 128 --seed 20261009
```

The companion preparation report identifies connected evaluation components and
the held-out source. M3 must use those components, preserve frozen splits and
report the insufficient-count threshold fallback; synthetic metrics are not
clinical performance. No model weights exist yet.
