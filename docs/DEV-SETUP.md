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

## Open questions

- What exact dependency versions and Android device targets will later ADRs select?

## Confidence

High for observed research/Python setup; Android and later ML build setup is pending.
