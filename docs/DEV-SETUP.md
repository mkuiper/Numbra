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

## Open questions

- What exact dependency versions and Android device targets will later ADRs select?

## Confidence

High for observed research/Python setup; Android and later ML build setup is pending.
