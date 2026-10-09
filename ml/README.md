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

Promoted stem Conv / affine BN arithmetic is available as
`python -m numbra_ml.export_precision --output data/exports/PLACEHOLDER-<new-name>`.
It retains training-only replay and tests float64 accumulation with float32
boundaries against native saved operators. ADR-016 and the export document
record local BN improvement and remaining differences; M4 stays incomplete.

Complete promoted BN substitution is available as
`python -m numbra_ml.export_promoted_bn --output data/exports/PLACEHOLDER-<new-name>`.
ADR-017 and the export document record all 34 replacements, training-only
whole-model parity and actual runtime audits. It lowers maximum errors but
still fails both fixed numeric budgets; no deployment artifact is accepted.

Joint promoted stem/BN substitution is available as
`python -m numbra_ml.export_joint --output data/exports/PLACEHOLDER-<new-name>`.
ADR-018 and the export document record training-only controls, exact runtime
expression audits and unchanged-model provenance. The joint graph still fails
both numerical budgets, with worse maxima than BN-only. M4 remains open.

Complete same-input Conv/BN replay is available as
`python -m numbra_ml.export_complete_replay --output data/exports/PLACEHOLDER-<new-name>`.
[ADR-019](../decisions/ADR-019-complete-same-input-replay.md) extends the guarded
training-only replay to every saved Conv/BN, including Conv without a following
BN. It measures both promoted BN recipes, audits saved parameters and runtime
arithmetic, and reports four-term signed accounting. Graphs and ordered rows
remain ignored. Aggregate reconstruction/checksum success is diagnostic only;
no baseline export is accepted and M4 remains incomplete.


Complete BN coefficient-rounding diagnostics are available as
`python -m numbra_ml.export_bn_rounding --output data/exports/PLACEHOLDER-<new-name>`.
[ADR-020](../decisions/ADR-020-batchnorm-rounding-replay.md) fixes 32 epsilon,
reciprocal, alpha, beta and output rounding recipes before execution. It compares
independent NumPy/eager-PyTorch expressions against every native BN on both
training input origins, records coefficient bits and audits full scope. All
existing Conv/BN replay controls remain; no replacement graph or deployable
model is produced. M4 acceptance still requires whole-model quantised parity.

Complete rounded-affine BN substitution is available as
`python -m numbra_ml.export_rounded_bn --output data/exports/PLACEHOLDER-<new-name>`.
[ADR-021](../decisions/ADR-021-rounded-affine-whole-model.md) fixes one complete
`e32-r32-a32-b64-o64` candidate and preserved control before execution. It rejects
independent coefficient-bit disagreement, audits every saved BN and actual runtime
expression, and reconstructs fixed-budget parity from ignored ordered details.
The complete candidate reduces training errors but still fails both numeric budgets.
All copies remain **PLACEHOLDER diagnostic only, never bundle**; no quantisation,
frozen evaluation or deployment selection occurred.

ADR-023 remaining-operator preflight is available as
`python -m numbra_ml.export_remaining --output data/exports/PLACEHOLDER-<new-name>`.
It performs no image decoding or model inference. The companion
`export_remaining_native` module provides complete native owner mapping,
pre-mutation multi-operand capture, full static taps and separate eager-fidelity
metrics. Its generated-only tests cover the full random mobile architecture;
saved-baseline mapping is static only. `export_remaining_runtime` adds complete
original/tapped disabled-runtime graph audits, validated multi-operand taps and
unsuppressed instrumentation measurements for both graphs. Generated fixtures
also cover both complete random mobile graphs; no saved-baseline replay is run.
`export_remaining_replay` integrates both graphs and exact input origins on a
supplied tensor, including separate original/captured native logits, every
remaining operator, complete Conv/BN formula/promoted/rounding controls, and
four-term signed accounting. It retains arrays for independent metric and exact
boundary-lineage reconstruction without inference. All serialized rounded-BN
expressions and coefficients are first bound to the unchanged saved recipe.
The generated full mobile fixture covers all 159 computational nodes.
`export_remaining_evidence` adds ignored lossless deduplicated NPZ arrays,
explicit ordered component/operator trees, partial-run rejection, and independent
streaming reconstruction of every row metric, full aggregates and fixed-budget
original-graph parity. It checks original native/runtime logit bits against
supplied ADR-022 disabled observations. Generated two-component tests exercise
these checks without saved M3 inference. `export_remaining_run` now connects
complete static saved/preparation/retained/source checks, the ADR-022 report
audit, actual runtime setup reconstruction and ordered observations. It audits
every expression before decoding the first ordered training image and streams
the full final evidence audit without inference. Generated pipeline tests cover
these guards; the selected baseline has only a static context check so far.

The guarded training command is:

```bash
python -m numbra_ml.export_remaining_run \
  --profile-source-commit 808cc3393ccf1cce95c2feeef91e5a8608b481e4 \
  --output data/exports/PLACEHOLDER-m4-remaining-training1
```

The explicit source commit must exactly match every historical ADR-022 source
file hash and its complete source-tree hash. Dependencies remain checked against
the current installed pins. This preserves historical report bytes and all
original logits; it does not authenticate historical inference. Output must be
new, and all graphs/tensors/individual observations remain ignored. Exit 0 means
complete diagnostic evidence, including parity failures, rather than M4 acceptance.
No selected-baseline training replay has been executed or new export accepted.
See [the export document](../docs/ML-EXPORT.md) for scope and evidence limits.
