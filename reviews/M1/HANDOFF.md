# M1 handoff — Python data scaffold ready for harness review

Date: 2026-10-09

Builder requests **M1** review. M0's harness-owned GATE is closed PASS WITH CHANGES;
its remaining consistency items are answered in
[RESPONSE-2](../M0/RESPONSE-2.md). No M1 gate or human approval is claimed.

## Acceptance evidence

- **Python project/pinned dependencies/tests:** [pyproject.toml](../../ml/pyproject.toml),
  src-layout package, exact direct/transitive runtime/test/build pins in
  [requirements-dev.txt](../../ml/requirements-dev.txt), and
  [tests](../../ml/tests/test_manifest.py). Installed in ignored `ml/.venv` using
  existing Python 3.12.3; editable package installation and pip check succeeded.
- **Data interfaces/schema/taxonomy:** executable [row schema](../../ml/src/numbra_ml/schema.py),
  [JSONL reader/writer and typed records](../../ml/src/numbra_ml/manifest.py),
  [taxonomy](../../ml/src/numbra_ml/taxonomy.py), and
  [dataset/RGB interfaces](../../ml/src/numbra_ml/dataset.py). Preserve source,
  release, licence/attribution, original/mapped label, confirmation, patient/group,
  split and checksum. Required provenance is explicit even when values are null.
  Full canonical M0 trigger-question superset exists as optional observations.
- **Tiny synthetic fixtures/tests:** eight generated RGB block images across four
  families/two named synthetic sources, plus in-code grayscale, orientation,
  corrupt and multi-frame cases. No committed PNG/JPEG/GIF/manifest/clinical row.
  Fixtures generated in ignored `ml/tests/.tmp/`. No network needed for tests.
- **Documentation/decision:** [data contract](../../docs/ML-DATA-CONTRACT.md),
  [ML README](../../ml/README.md), [DEV-SETUP](../../docs/DEV-SETUP.md),
  [ADR-006](../../decisions/ADR-006-ml-data-contract.md), queued for human review.

## Verification observed by Builder

From repository root:

```bash
bash scripts/check.sh
python3 -m unittest discover -s tests -v
ml/.venv/bin/python -m pip check
git diff --check
```

Observed check.sh: exit 0, **83 ML tests PASS**, Android **SKIPPED** (no wrapper at
M1), RESULT PASS. Root contract suite: **5 PASS**, still Builder-attested because
the protected harness check does not run it. pip check reports no broken
requirements; whitespace check passes. Harness must rerun its tests of record.

Coverage includes JSONL round-trip and malformed rows, source/taxonomy version and
enum rejection, required provenance, duplicate record/JSON keys, missingness,
synthetic confirmation/tone restrictions, group/patient/global exact-hash leakage,
source namespacing, policy blocking before file access, path traversal/symlinks,
checksum/corrupt/missing failures, EXIF/grayscale/RGB loading, explicit transforms,
split filtering and supervised eligibility with retained exclusion reasons.

## Requested scrutiny and limits

1. **Semantic boundaries:** source/licence flags are not proof of synthetic bytes
   or future permission. Loaders have no real-source bypass; only generated
   PLACEHOLDER provenance is currently accepted. Future source approval needs an
   amended ADR-002 and suitable documented permissions.
2. **Ground truth versus actions:** exact vocabulary mapping remains provisional;
   unseen names remain unresolved. Synthetic labels cannot claim clinical
   confirmation. Zero is an image training target, never disease absence or a
   referral decision. No referral engine, training, model or clinical metric exists.
3. **Grouping:** source namespaces plus patient/group/hash validation reject split
   conflicts, but do not merge duplicates or prove real patient independence.
   M2 must assign splits, merge duplicate-connected groups, detect perceptual
   duplicates and quarantine conflicting labels. Missing grouping stays explicit
   and is excluded by the supervised selection interface.
4. **M6/M7 consistency:** manifests can omit observations for honest import
   missingness. M6 must enforce the canonical complete-assessment rules and ask
   the explicit volunteer-concern question. M7 must extend consent/lifecycle/
   detailed confirmer provenance, encrypt records and preserve referral reasons.
5. **Input:** loader returns oriented uint8 HWC RGB only; supports single-frame
   RGB/grayscale and rejects transparency/palette/multi-frame. No implicit resize,
   letterbox or normalisation. M4 must define/test full preprocessing and parity.
6. **Environment:** tested only on existing Python 3.12.3; project requires 3.12.
   Exact versions are pinned, not artifact hashes. Dependency notices and model
   rights still need later distribution audit. No release/publish/push attempted.

## Next boundary

Read the harness M1 review/check in full and answer every numbered issue. If it
closes M1, begin **M2 only**: deterministic synthetic generation/preparation,
duplicate/group handling, held-out source and generated local manifest. No real
task dataset is approved. All downstream models, reports and UI remain PLACEHOLDER.
