# PLACEHOLDER data preparation

**PLACEHOLDER — synthetic demonstration, not clinically validated.**
[ADR-002](../decisions/ADR-002-dataset-selection.md) approves no real dataset.
[ADR-007](../decisions/ADR-007-synthetic-preparation.md) defines component quarantine;
[ADR-008](../decisions/ADR-008-m3-synthetic-evaluation-fixture.md) updates fixture and
split mechanics for M3. No image download or clinical photo scraping exists.
Generated images, manifests and audits remain under ignored `data/`.

## Reproduce a run

From within the repository after [Python setup](DEV-SETUP.md):

```bash
ml/.venv/bin/python -m numbra_ml.prepare --output data/prepared/synthetic-v2 --groups-per-source 128 --seed 20261009
ml/.venv/bin/python -m numbra_ml.prepare --output data/prepared/synthetic-v2-selection --groups-per-source 256 --split-profile selection_exercise --seed 20261009
bash scripts/check.sh
```

Output must be new/empty below this repository's `data/`; nonempty runs are refused.
Choose another run name to reproduce. Root discovery walks upward from the
invocation directory to both `.git` and `docs/ROADMAP.md`, including git worktrees
and normal package installs; outside a checkout it fails. Relative output paths
resolve from that root. Symlink parent escapes are rejected and tested. Library
functions accept ignored test directories. Failed writes can leave partial files;
there is no silent fallback, overwriting or resplitting.

Each run has `images/`, `unassigned.jsonl`, `manifest.jsonl` and
`preparation-report.json`. Schema is 1.1.0, taxonomy 1.0.0, generator shapes-v2,
preparation 1.1.0. NumPy/Pillow pins are unchanged. Equal config/environment yields
identical image/manifest/audit bytes, tested in independent output directories.
Existing shapes-v1 runs remain unchanged; their original M2 evidence is historical.

## Fixture semantics

Both assigned targets occur in every source. Circles and squares have matched
exact raster areas, overlapping signed contrast, noise and stronger procedural
source differences. A group-level Bernoulli probability 0.10 intentionally renders
the opposite shape; both views retain the assigned target. This exercises imperfect
scores, without representing a skin condition. Per-source label-noise fractions
are not guaranteed to equal 0.10 in finite samples.

Use **synthetic circle / synthetic square** names in every future model card and
metric report, from the audit's `generator.target_names`. Internal binary family
encoding is retained for schema compatibility and has no disease interpretation.
Synthetic colour bands describe weighted luminance of the generated background
before texture/shape/illumination, after channel gains: <85, 85..<170, >=170.
They are never Fitzpatrick/Monk or fairness evidence. Capture metadata names
procedural generation. No pure-neural disease or clinical skin lesion is represented.

## Duplicate and split order

1. Require approved synthetic provenance and all-unassigned input; verify every
   safe path, byte checksum and image decode.
2. Merge source-scoped patient/group IDs, global byte/pixel hashes and all bilinear
   16×16 RGB thumbnail pairs with RMS ≤2 uint8 units. Merge transitively before
   splitting. Record matching pairs and nearest pair in distinct final components.
3. Quarantine whole components for conflicting diagnoses, missing group IDs,
   ineligible labels or links across the predeclared holdout boundary. Preserve
   original statuses/reasons. Never invent identities or clinical confirmation.
4. Hold source C out by default (`--held-out-source` permits a predeclared other
   source). Hash-rank development components within source-membership tuple ×
   target strata. Default fractions are 60/15/15/10, selection_exercise 30/20/40/10.
   Give one per partition when a stratum has ≥4 components, then largest-remainder
   rounding. Smaller strata have no minimum. Require both classes in every
   development partition and holdout; fail otherwise. Keep cross-source links whole.
5. Validate the manifest; report components, per-row component IDs, original label
   statuses, exclusions, licence-bearing rows and final manifest SHA-256. Include
   per-split/source/class component counts with explicit zeros. A multi-source
   component counts once per represented source; quarantined targets are null.

M3 must use the audit component IDs as independent evaluation units and choose
one deterministic index image per component before scoring. Preserve frozen
train/calibration/threshold-validation/test splits. The default C evaluation is
**single held-out source (one leave-one-source-out fold)**, not a rotation or
real external validation. Separate source rotations need independent training,
calibration and threshold selection without their held-out records.

## Observed version-2 evidence

Run on 2026-10-09 with the commands above under the pinned M1 environment:

| Partition | Default components (per class) | Selection-exercise components (per class) |
| --- | ---: | ---: |
| Train | 148 (74) | 152 (76) |
| Calibration | 40 (20) | 104 (52) |
| Threshold validation | 40 (20) | 204 (102) |
| Test | 28 (14) | 52 (26) |
| Held-out C | 128 (64) | 256 (128) |
| Total | 384 (192) | 768 (384) |

Two rows per component: default 768 images, selection-exercise 1536. All hashes
and decodes verified; all rows Apache-2.0/synthetic/PLACEHOLDER, no quarantine or
unresolved labels. Audits find exactly 384/768 near-visual view pairs, no byte/pixel
matches and nearest-unlinked RMS 8.586645/8.204261, against cutoff 2. Source A/B
counts match within each development partition/class. Boundary tests exercise
RMS just below, exactly at and just above 2; unrelated-group count is asserted.

Manifest hashes, respectively:

- `0a4adb62e625bed27271c42abbc8aef27bb28a05f5bd9ea018a14471738d7b58`
- `2d141bc62205d88b7116cbe410e9262a96d771dec34c30e88ae6ad9c4bee839e`

For the fixed default seed, the best mean-intensity threshold (either direction)
has balanced accuracy 0.541667 over one view/group. This is a fixture regression
check only; it cannot establish a model's difficulty or clinical performance.
The default threshold-selection count remains insufficient: use ADR-001's
unselected refer-all fallback. The larger profile permits exercising the guard,
but actual count checking, calibration, selection and evaluation are **not built**
yet. No model performance or clinically calibrated score is claimed.

## Limits

One-label-per-component quarantine can reject valid multi-condition patients in
future real data. The visual rule can miss transformed duplicates and merge
unrelated images; invented groups/source styles do not prove real independence.
The quadratic search refuses >2000 rows and keeps a ≤16 MB distance matrix; it is
an artificial-fixture pipeline. Boundary/re-encoding/edit tests do not validate
real duplicate detection. Real acquisition needs an amended ADR-002 and human
review; no registration, agreements or rights acceptance path exists.

## Open questions

- Which future licensed cohort supplies confirmed target labels and patient identities?
- What real-data duplicate adjudication and source holdout policy will humans approve?
- Should future PLACEHOLDER evaluation run all three source folds?

## Confidence

High for tested synthetic mechanics; no clinical validity, real-world leakage
guarantee, skin-tone fairness evidence or real-data rights.
