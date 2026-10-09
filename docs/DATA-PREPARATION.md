# M2 data preparation

**PLACEHOLDER — synthetic demonstration, not clinically validated.**
[ADR-002](../decisions/ADR-002-dataset-selection.md) approves no real dataset;
[ADR-007](../decisions/ADR-007-synthetic-preparation.md) specifies this synthetic
pipeline. No image download or clinical photo scraping exists. All generated
images, manifests and detailed audits remain under ignored `data/`.

## Reproduce a run

From repository root after [Python setup](DEV-SETUP.md):

```bash
ml/.venv/bin/python -m numbra_ml.prepare --output data/prepared/synthetic-v1 --groups-per-source 128 --seed 20261009
bash scripts/check.sh
```

Output must be a new/empty directory beneath this repository's `data/`; existing
nonempty runs are refused, with no force/overwrite switch. To reproduce alongside
a previous run, choose `data/prepared/synthetic-v1-reproduction`. Relative CLI
paths resolve from repository root, even when launched from `ml/`. The library
functions accept test directories; tests keep them in ignored `.tmp/` paths.
A failed write can leave partial generated files; it never reports success or
silently substitutes another source. Review partial files before local cleanup.

Each run contains `images/`, `unassigned.jsonl`, `manifest.jsonl` and
`preparation-report.json`. Schema version is 1.1.0, taxonomy 1.0.0. The generator
uses NumPy/Pillow pins already installed in M1; no new toolchain is needed.
The same seed, config and pinned environment produce identical image/manifest
bytes and audit JSON; this is tested across two independent output directories.

## Duplicate and split order

1. Require approved synthetic provenance and an entirely unassigned manifest.
   Verify every file path, byte SHA-256 and image decode before selection.
2. Merge source-scoped group/patient IDs, global exact hashes and decoded oriented
   RGB hashes. Compare **all** bilinear 16×16 RGB thumbnails with RMS distance
   ≤2 uint8 units, and merge visual candidates transitively. Pair distances,
   byte/pixel matches and complete component membership are audited.
3. Quarantine each whole component if any resolved diagnosis conflicts, any group
   is missing, any label lacks a target, or it crosses the held-out source boundary.
   Report original statuses/reasons; never infer group identities or confirm labels.
4. Freeze source C as held-out. Hash-rank remaining components with the chosen
   seed and stratify by binary target into train/calibration/threshold_validation/
   test at 60/15/15/10%, with one/class/partition minimum and largest remainder.
   Insufficient class components fail explicitly. Both held-out targets are required.
5. Validate the completed manifest and write the companion report, including
   unresolved counts per source/original label, component targets/splits, per-row
   component IDs, and the completed manifest checksum.

A patient can have multiple groups. A duplicate can link different patients or
sources. These links form a **single connected component** and cannot cross
splits. Source namespaces retain original identifiers; no fabricated global
patient IDs. Identical bytes with incompatible active diagnoses fail the reader
as well as preparation tests; unassigned conflicts may enter preparation so they
can be quarantined. Quarantine is group-wide, not a row-level exemption.

For M3, `preparation-report.json` is a required companion: aggregate evaluation
by `record_components` and freeze training/calibration/threshold-validation/test
partitions. The selected source is a synthetic leave-one-source-out pipeline
result, not independent real-world evidence. Do not train or tune on test/held-out
rows, including on quarantined links into the holdout.

## Observed default-run evidence

Run on 2026-10-09 with the command above, under the pinned M1 environment:

| Partition | Components | Generated image rows | Components per binary class |
| --- | ---: | ---: | ---: |
| Train | 150 | 300 | 75 |
| Calibration | 40 | 80 | 20 |
| Threshold validation | 40 | 80 | 20 |
| Test | 26 | 52 | 13 |
| Held-out synthetic source C | 128 | 256 | 64 |
| Total | 384 | 768 | 192 |

All 768 generated files decoded with verified byte hashes, all rows passed
supervised eligibility and carried Apache-2.0/PLACEHOLDER provenance. The audit
found 384 near-visual pairs (two views per invented group), zero exact/decoded
matches, zero conflicts/quarantine/unresolved rows. Explicit adversarial tests
exercise these failure cases separately. Source styles affect both targets.
Synthetic background strata are invented colour labels, never Fitzpatrick/Monk
annotations. Capture site/device fields explicitly describe procedural generation.

Observed completed manifest SHA-256:
`ff0e5d1749bf1f33fe64ac4234e7b788ea36e7db0996aa6c13208e76459911c4`.

Threshold validation has only 20 components/class, below ADR-001's 100/class
minimum: M3 must use its unselected refer-all fallback, retaining honest bounds
and counts. No accuracy/sensitivity/calibration/model result exists at M2.

## Limits

The one-label-per-component policy can quarantine valid multi-condition patients
in a future real cohort; it is intentionally conservative for this one-target
synthetic generator and would need real-data review.
The near-visual rule can miss transformed duplicates and merge unrelated images;
patient tokens and procedural sources cannot establish real patient independence.
The quadratic implementation explicitly refuses >2000 rows; it is a fixture
pipeline, not a scalable clinical ingestion service. Re-encoding and small edits
are covered in tests, not every transformation or real image distribution.
No real-data loader/acquisition bypass, registration, agreements or rights
acceptance is implemented. Real acquisition requires an amended ADR-002.

## Open questions

- Which future licensed cohort supplies confirmed target labels and patient identities?
- What real-data duplicate adjudication, site holdout and unresolved-label audit is appropriate?
- Which synthetic demonstration outputs will humans want expanded at M3?

## Confidence

High for the tested deterministic synthetic preparation and software split
invariants; no clinical validity, real-world leakage guarantee or real-data rights.
