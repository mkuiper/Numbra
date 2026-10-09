# M2 handoff — original review snapshot and post-gate follow-through

Date: 2026-10-09

M2's harness gate closed **PASS WITH CHANGES** on 2026-10-09. All ten non-blocking
issues are answered in [RESPONSE-1](RESPONSE-1.md). shapes-v2/preparation 1.1.0
updates and current observed evidence are in [data preparation](../../docs/DATA-PREPARATION.md)
and [ADR-008](../../decisions/ADR-008-m3-synthetic-evaluation-fixture.md). No new M2
review requested; M3 is in progress.

The remaining sections preserve the **original shapes-v1 review snapshot**;
their commands/counts/versions and “next step” describe the initial submission,
not current generator behaviour. New runs must use the version-2 commands linked
above. No historical run is overwritten.

At initial submission, Builder requested **M2** review. M0 and M1 harness GATE files exist, both PASS WITH
CHANGES; human review is pending. M1 Review-1 is answered in
[RESPONSE-1](../M1/RESPONSE-1.md). No M2 gate is claimed.

## Acceptance evidence

- **Only approved data:** [ADR-002](../../decisions/ADR-002-dataset-selection.md)
  approves generated synthetic fixtures only; no real task dataset is approved.
  [Generator](../../ml/src/numbra_ml/synthetic.py) produces procedural 64×64 RGB
  textures in three invented sources, two views per invented patient/group,
  both binary targets in each source. No network/image download code, real
  photos, registrations, signed agreements or licence acceptance.
- **Manifest and preparation:** [CLI](../../ml/src/numbra_ml/prepare.py) generates
  only below ignored `data/`, refuses nonempty outputs, and writes unassigned
  and prepared JSONL plus a duplicate/component audit. Every row carries
  source/release/Apache-2.0 generator licence/original label/patient/group/SHA-256
  and explicit synthetic/PLACEHOLDER flags. CLI paths cannot escape via existing
  symlink parents. No images/manifests/audits are committed.
- **Duplicates, groups and holdout:** [preparation](../../ml/src/numbra_ml/preparation.py)
  verifies all bytes/decodes, merges patient/group/exact/decoded/near-visual links
  transitively, quarantines whole components with conflicts, missing groups,
  ineligible labels or links across source-C holdout, then freezes deterministic
  class-stratified train/calibration/threshold-validation/test splits. Complete
  source C remains held out. The audit is required for component-level M3 metrics.
- **Explicit conflict acceptance tests:** [M2 tests](../../ml/tests/test_preparation.py)
  cover exact-byte opposing labels, whole-patient quarantine, transitive
  cross-source/group links, decoded re-encoding, small pixel edits, held-out
  contamination, unresolved/missing/withdrawn labels, inadequate cohorts, policy
  and checksum failure, determinism, seed changes, overwrite refusal and row cap.
  Ordinary readers also reject conflicting active exact-byte labels.
- **Fallback plainly recorded:** [HUMAN-QUEUE](../../notes/HUMAN-QUEUE.md) states
  no suitable approved real task data is available under ADR-002; models/reports/UI
  remain **PLACEHOLDER**. [ADR-007](../../decisions/ADR-007-synthetic-preparation.md)
  records unattended choices, pending human review. M1 schema 1.1.0 follow-ups are
  documented there and in the [data contract](../../docs/ML-DATA-CONTRACT.md).

## Reproduce and verify

From repository root, with existing M1 environment:

```bash
ml/.venv/bin/python -m numbra_ml.prepare --output data/prepared/synthetic-v1 --groups-per-source 128 --seed 20261009
bash scripts/check.sh
python3 -m unittest discover -s tests -v
ml/.venv/bin/python -m pip check
```

Use another new output name if that directory already exists. Documentation:
[preparation](../../docs/DATA-PREPARATION.md), [layout](../../docs/DATA-LAYOUT.md),
[setup](../../docs/DEV-SETUP.md) and [ML README](../../ml/README.md).

Builder observed:

- check.sh: exit 0, **136 ML tests PASS**, Android **SKIPPED**, RESULT PASS.
- Root repository-contract suite: **5 PASS** (Builder-attested; protected check
  does not run it). Includes `.tmp/` ignore checks from root and ml working dirs.
- pip check: no broken requirements. No toolchain additions at M2.
- Full default CLI and second reproduction: **771 files byte-identical** (768
  generated PNGs, two manifests and one report). All 768 image checksums/decodes
  verified, eligible rows 768, excluded 0. No accuracy or clinical metric produced.
- 384 components: train 150, calibration 40, threshold validation 40, test 26,
  held-out 128. Each partition has both targets, balanced by components.
- Audit: 384 near-visual pairs (two views per group), zero exact/decoded matches,
  conflicts/quarantine/unresolved rows in default fixtures; adversarial tests
  exercise those paths independently.
- Manifest SHA-256:
  `ff0e5d1749bf1f33fe64ac4234e7b788ea36e7db0996aa6c13208e76459911c4`.

## Requested scrutiny and limits

1. **Split leakage and quarantine:** inspect connected transitive grouping and
   global duplicate links, especially cross-source holdout quarantine. No row-level
   quarantine exemptions. M3 must aggregate by audit component IDs, never by views.
2. **Visual heuristic:** bilinear 16×16 RGB RMS ≤2 uint8 units is a chosen fixture
   heuristic. It can miss transformations or merge unrelated images. All-pairs
   search refuses >2000 rows; no claim of scalable/validated real-data ingestion.
   One-diagnosis-per-component policy may over-quarantine legitimate multi-condition
   patients in a future cohort and needs an amended real-data design.
3. **Threshold fallback:** default threshold validation has **20/class**, below
   ADR-001's 100/class selection guard. M3 must use unselected refer-all fallback;
   calibration 20/class, test 13/class, source-C 64/class are artificial counts only.
   Source-C holdout tests mechanics, not real generalisation or clinical safety.
4. **Source and annotation honesty:** synthetic flags/licence fields cannot prove
   arbitrary bytes' provenance. CLI itself only generates; library loading policy
   still blocks real sources. Invented colours are not skin-tone annotations.
   The schema can describe future real rows but cannot verify confirmer credentials.
5. **Reproduction boundary:** same pins/config yield byte-identical fixture files;
   this does not promise identity across untested dependency versions or platforms.
   Version-only dependency pins remain disclosed; hashed torch pins are M3 work.
6. **Milestone boundary:** no model, weights, training, export, app or APK. No
   clinical performance, clinical-data permissions, field approval or M3 completion.
   No publishing, messages, push or review/check/gate writes; harness owns them.

## Next step

Harness runs M2 check/review. Read its full REVIEW/CHECK and answer every numbered
issue. Proceed to M3 only after M2 GATE exists, addressing cheap follow-ups and
queuing human decisions. Preserve synthetic PLACEHOLDER labels and all M0 safeguards.
