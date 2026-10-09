# Development setup

Current setup: existing system Python 3.12.3, git and bash, plus the repository-local
`ml/.venv` installed at M1. No JDK or Android SDK yet. Run checks with:

```
python3 -m unittest discover -s tests -v
bash scripts/check.sh
```

At M0 check.sh skipped both projects; M1 now runs pytest from `ml/` using its venv.
Android remains skipped and no APK verification is claimed. Later milestones
must document actual JDK/SDK commands here. Android command-line tools belong
under `$HOME/Android/Sdk`.

## M1 Python setup — observed 2026-10-09

Existing system Python: **3.12.3**; venv bootstrap pip: **24.0**. Only the
repository-local `ml/.venv` was installed; no system package, JDK or Android SDK
was installed. Reproduce from the repository root:

```bash
python3 -m venv ml/.venv
PIP_NO_CACHE_DIR=1 ml/.venv/bin/python -m pip install -r ml/requirements-dev.txt
PIP_NO_CACHE_DIR=1 ml/.venv/bin/python -m pip install --no-build-isolation --no-deps -e ml
ml/.venv/bin/python -m pip check
bash scripts/check.sh
python3 -m unittest discover -s tests -v
```

Initial install used pip's default cache; later installs disabled it. The exact
direct/transitive pins in `ml/requirements-dev.txt` match the observed Python 3.12
environment. `pyproject.toml` restricts support to Python 3.12 until other versions
are tested. pytest's basetemp is `tests/.tmp/` relative to the working directory; `.tmp/`
is ignored at every depth and regenerated per run. Editable installation succeeded with pinned setuptools/wheel, without
build isolation or dependency re-resolution. No task data or model weights fetched.

Firecrawl CLI 1.14.8 is installed and authenticated, but status showed zero credits.
The setup scrape and a one-result search both failed with insufficient credits.
The research iteration used the available web search/open tool as a labelled
workaround; no new account, subscription, authentication, or licence acceptance
was performed. `.firecrawl/` is ignored and must never store tracked content.

## M2 fixture preparation — observed 2026-10-09

No additional toolchain/dependency installation. Historical shapes-v1 command;
current generator is shapes-v2. Use the M3 commands below for new runs; the original
local run is preserved. From repository root at M2:

```bash
ml/.venv/bin/python -m numbra_ml.prepare --output data/prepared/synthetic-v1 --groups-per-source 128 --seed 20261009
```

Observed 768 generated images/384 components, all byte hashes and decodes verified.
See [preparation evidence](DATA-PREPARATION.md). This does not train or download a
model. The output and raw/prepared manifests/audit remain entirely ignored.

## M3 fixture follow-through — observed 2026-10-09

No toolchain/dependency addition or pretrained weight acquisition yet.

```bash
ml/.venv/bin/python -m numbra_ml.prepare --output data/prepared/synthetic-v2 --groups-per-source 128 --seed 20261009
ml/.venv/bin/python -m numbra_ml.prepare --output data/prepared/synthetic-v2-selection --groups-per-source 256 --split-profile selection_exercise --seed 20261009
```

Observed 768/1536 procedural images; source-stratified component counts and
threshold-count exercise described in [data preparation](DATA-PREPARATION.md).
These commands do not train or download a model. M3 dependencies, weight licence/
revision/checksum verification, training and evaluation are still pending.

## M3 component evaluation — observed 2026-10-09

No additional toolchain/dependency installation or pretrained acquisition.
Evaluation uses the existing pinned NumPy plus standard-library arithmetic.
Observed verification from the repository root:

```bash
ml/.venv/bin/python -m pytest ml/tests/test_evaluation.py -q
bash scripts/check.sh
python3 -m unittest discover -s tests -v
ml/.venv/bin/python -m pip check
```

Evaluation subset: 58 passed. Full check: 208 ML tests passed; Android skipped,
RESULT PASS. Root contract suite: 5 passed. No broken Python requirements.
See [evaluation contract](ML-EVALUATION.md). Training/checkpoint/dependency-lock
setup remains pending; these checks do not establish a trained model or APK.

## M3 CPU transfer environment — observed 2026-10-09 UTC

Python remains 3.12.3. CPU torch 2.8.0+cpu / torchvision 0.23.0+cpu,
timm 1.0.22, safetensors 0.6.2 and huggingface-hub 0.36.0 installed in ml/.venv.
The 35-wheel full runtime/test/build lock is ml/requirements-cpu.lock; it includes
all transitive pins and one SHA-256 per wheel for CPython 3.12 Linux x86_64.
No system packages/JDK/SDK installed. From repository root:

```bash
mkdir -p data/toolchains/wheels ml/.tmp/pip
PIP_NO_CACHE_DIR=1 ml/.venv/bin/python -m pip download --only-binary=:all: --no-deps --index-url https://download.pytorch.org/whl/cpu --dest data/toolchains/wheels 'torch==2.8.0+cpu' 'torchvision==0.23.0+cpu'
```

Initial dependency resolution downloaded M1 requirements plus timm/safetensors;
it selected hub 2.2.0. Before installing, explicitly chose hub 0.36.0 for timm
compatibility, resolved again into data/toolchains/m3-wheels with the M1 pins
and torch/torchvision/timm/safetensors/hub pins, then generated the lock by reading
each wheel's dist-info/METADATA name/version and hashing the wheel bytes. The
original M1 requirements list is available in git history. No floating dependency
resolution is needed for subsequent installs. Reproduce the final environment:

```bash
TMPDIR="$PWD/ml/.tmp/pip" PIP_NO_CACHE_DIR=1 ml/.venv/bin/python -m pip download --require-hashes --dest data/toolchains/m3-wheels -r ml/requirements-cpu.lock
TMPDIR="$PWD/ml/.tmp/pip" PIP_NO_CACHE_DIR=1 ml/.venv/bin/python -m pip install --force-reinstall --no-index --find-links data/toolchains/m3-wheels --require-hashes -r ml/requirements-cpu.lock
TMPDIR="$PWD/ml/.tmp/pip" PIP_NO_CACHE_DIR=1 ml/.venv/bin/python -m pip install --no-build-isolation --no-deps -e ml
ml/.venv/bin/python -m pip check
ml/.venv/bin/python -m numbra_ml.pretrained
```

The force-reinstall was observed, including all previously installed M1 wheels,
so installed dependencies were read from hash-checked archives. Earlier pip's
editable build used its automatic transient /tmp directory; subsequent installs
set TMPDIR inside ignored ml/.tmp. No unrelated files manually modified.
Checkpoint anonymous access, licence/revision/checksums and installed environment
are recorded in ADR-010 and the training report provenance. All downloaded wheels,
README/config and weights remain ignored under data/. Firecrawl still has zero
credits; reused the documented web/direct-anonymous-HTTP workaround with no
account, subscription or credential changes.

Training/reproduction commands and results: [ML-TRAINING.md](ML-TRAINING.md).
Existing synthetic-v2/default and selection fixtures are not regenerated/tuned
in response to scores. No Android or clinical performance evidence.

## M3 review / M4 reference foundation — observed 2026-10-09 UTC

No additional toolchain, dependency, checkpoint or dataset installation.
M3 follow-through and M4 reference/parity arithmetic use the existing 35-wheel
CPU hash lock. Saved baseline/reproduction/default verification commands:

```bash
ml/.venv/bin/python -m numbra_ml.verify
ml/.venv/bin/python -m numbra_ml.verify --run data/models/PLACEHOLDER-m3-reproduction
ml/.venv/bin/python -m numbra_ml.verify --prepared data/prepared/synthetic-v2 --run data/models/PLACEHOLDER-m3-default
```

Observed 768/768/384 components, raw-logit/probability max error 0, threshold
flips 0. This verifies saved Python models; there is no ONNX conversion/runtime
dependency installed or exported graph yet. M4 dependency setup is the next step;
record exact verified pins/install commands here before claiming export acceptance.
See [ML-EXPORT.md](ML-EXPORT.md) for the fixed preprocessing/parity contract.

## M4 ONNX export environment — observed 2026-10-09 UTC

Added onnx 1.19.1, onnxruntime 1.23.2, coloredlogs 15.0.1, flatbuffers 25.12.19,
humanfriendly 10.0, ml-dtypes 0.6.0, protobuf 7.36.2 in ml/.venv. The final combined
export lock has 42 unique wheel pins/hashes and includes the unchanged 35-package
CPU lock. No JDK/SDK/system install or model/dataset acquisition this iteration.
Commands observed from repository root:

```bash
mkdir -p data/toolchains/m4-wheels ml/.tmp/pip
TMPDIR="$PWD/ml/.tmp/pip" PIP_NO_CACHE_DIR=1 ml/.venv/bin/python -m pip download --only-binary=:all: --dest data/toolchains/m4-wheels --constraint data/toolchains/m4-constraints.txt 'onnx==1.19.1' 'onnxruntime==1.23.2'
TMPDIR="$PWD/ml/.tmp/pip" PIP_NO_CACHE_DIR=1 ml/.venv/bin/python -m pip install --no-index --find-links data/toolchains/m4-wheels --find-links data/toolchains/m3-wheels --require-hashes -r ml/requirements-export.lock
TMPDIR="$PWD/ml/.tmp/pip" PIP_NO_CACHE_DIR=1 ml/.venv/bin/python -m pip install --no-build-isolation --no-deps -e ml
ml/.venv/bin/python -m pip check
```

The ignored constraint file is generated from existing CPU-lock name/version pins
with hash/options removed, retaining old dependencies during initial resolution.
An initial attempt using the hashed CPU lock directly as a constraint failed:
pip required hashes for the new ONNX requirement too. No install occurred from
that failed attempt. Wheel METADATA and SHA-256 produced the additions lock before
install. The first generated additions also duplicated `typing_extensions` as
`typing-extensions` at the identical version/hash. Removed that redundant alias
after the experiments; reports retain historical lock hashes. Reconstruct that
historical lock by appending the CPU lock's typing_extensions line with its name
normalised to typing-extensions to the final export lock; dependency bytes match.

For a new environment, use the final checked-in lock instead of regenerating
constraints or resolving versions:

```bash
TMPDIR="$PWD/ml/.tmp/pip" PIP_NO_CACHE_DIR=1 ml/.venv/bin/python -m pip download --require-hashes --dest data/toolchains/m4-wheels -r ml/requirements-export.lock
TMPDIR="$PWD/ml/.tmp/pip" PIP_NO_CACHE_DIR=1 ml/.venv/bin/python -m pip install --no-index --find-links data/toolchains/m4-wheels --require-hashes -r ml/requirements-export.lock
TMPDIR="$PWD/ml/.tmp/pip" PIP_NO_CACHE_DIR=1 ml/.venv/bin/python -m pip install --no-build-isolation --no-deps -e ml
```

Observed editable installation and pip check succeeded. Export/summary commands
and rejected-model results are in [ML-EXPORT.md](ML-EXPORT.md). ONNX library
temporaries now use the ignored export output directory; the first prototype
used library defaults before this confinement was added. No unrelated files
manually modified. Firecrawl still has zero credits; official documentation read
through the prior labelled web-tool workaround without credentials/auth changes.

## M4 training-only diagnostics — observed 2026-10-09 UTC

No toolchain/dependency installation, checkpoint or dataset acquisition.
The existing 42-package hash-locked environment ran:

```bash
ml/.venv/bin/python -m pytest ml/tests/test_export_diagnostics.py -q
ml/.venv/bin/python -m numbra_ml.export_diagnostics --output data/exports/PLACEHOLDER-m4-diagnostics1
bash scripts/check.sh
python3 -m unittest discover -s tests -v
```

Observed diagnostic subset: 8 passed in 5.92s. Diagnostic command exit 0 produced
**DIAGNOSTIC ONLY** evidence; all original-graph training profiles fail parity.
Full check: 312 ML tests passed in 35.90s, 18 legacy-export deprecation warnings;
Android skipped, RESULT PASS. Root checks: 6 passed in 0.062s. Graph copies,
per-component diagnostics and library artifacts stay under ignored data/.
See [ML-EXPORT.md](ML-EXPORT.md); no M4 completion or APK evidence.

## M4 BatchNorm-preserving diagnostics — observed 2026-10-09 UTC

No toolchain/dependency installation, checkpoint or dataset acquisition. The
existing 42-package hash-locked environment ran, from the repository root:

```bash
ml/.venv/bin/python -m pytest ml/tests/test_export_batchnorm.py -q
ml/.venv/bin/python -m numbra_ml.export_batchnorm --output data/exports/PLACEHOLDER-m4-batchnorm1
ml/.venv/bin/python -m numbra_ml.export_batchnorm --output data/exports/PLACEHOLDER-m4-batchnorm2
bash scripts/check.sh
python3 -m unittest discover -s tests -v
```

First subset run: 4 passed in 5.69s. Inspection exposed mismatched combined
BatchNorm/activation boundaries in the first diagnostic report; its boundary
evidence is explicitly INVALID. Corrected pre-activation hooks and two regression
fixtures gave 6 passed in 5.85s. Both diagnostic CLI runs exit 0 to mean evidence
generated, **not** acceptance; every original-graph training comparison fails.
The corrected report retains all 87 boundaries. Saved states/graphs/details and
source hashes were separately verified against that aggregate. Models and
per-component outputs remain ignored, including the unchanged first-run details.

Full check: **318 ML tests passed in 39.53s**, 34 legacy-export deprecation
warnings; Android skipped, RESULT PASS. Root checks: **6 passed in 0.064s**.
ORT warns that all-profile serialized optimized graphs may be hardware-specific;
these are diagnostic copies labelled never bundle, not Android artifacts.
See [export evidence](ML-EXPORT.md) and ADR-014. No M4 completion or APK claim.

## M4 same-input operator replay — observed 2026-10-09 UTC

No toolchain/dependency installation, checkpoint or dataset acquisition. The
existing 42-package hash-locked environment ran from the repository root:

```bash
ml/.venv/bin/python -m pytest ml/tests/test_export_replay.py -q
ml/.venv/bin/python -m numbra_ml.export_replay --output data/exports/PLACEHOLDER-m4-replay1
bash scripts/check.sh
python3 -m unittest discover -s tests -v
```

First subset run: 5 passed, 1 failed (5.59s). The provenance guard incorrectly
required boundary diagnostics on a passing toy export, although ADR-014 only
generates those when parity fails. Fixed the guard to accept passing profiles
without taps, require valid boundary evidence on failures, and always reject
explicit invalid evidence. No test expectation was removed/weakened. The next
subset run: **6 passed in 5.99s**, 16 exporter deprecation warnings. Added further
invalid-boundary/swapped-graph rejection cases before the full suite.

Replay command exit 0 means **DIAGNOSTIC ONLY**: all 152 training components,
four first stem/depthwise Conv/BN operators, two exact input origins and three
fixed BN formulas. No frozen evaluation, new fit or deployment selection.
Source, preserved/extracted/formula/runtime graphs and private-detail hashes
were separately checked against the aggregate. All generated models/graphs and
ordered component diagnostics stay ignored. See [ML-EXPORT.md](ML-EXPORT.md).

Full check: **324 ML tests passed in 43.92s**, 50 legacy exporter deprecation
warnings; Android skipped, RESULT PASS. Root checks: **6 passed in 0.066s**.
M4 remains incomplete; no accepted deployment artifact or APK.

## Open questions

- What exact dependency versions and Android device targets will later ADRs select?

## Confidence

High for observed research/Python/export setup; Android toolchain setup is pending.
