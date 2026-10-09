# ML data contract — M1 interfaces and M2 preparation

**PLACEHOLDER — synthetic demonstration, not clinically validated.**
The implementation is [numbra_ml](../ml/src/numbra_ml/__init__.py), governed by
[ADR-006](../decisions/ADR-006-ml-data-contract.md). This document describes actual
M1/M2 behaviour; it does not claim a clinically verified taxonomy or real-data rights.

## Schema and provenance

One UTF-8 JSON object per line, no blank lines or duplicate JSON keys. Row/schema version is `1.1.0`; taxonomy remains `1.0.0`. Version 1.0.0 rows
are rejected: regenerate synthetic fixtures; no real-row automatic migration. The executable
[JSON Schema](../ml/src/numbra_ml/schema.py) is the structural authority; generate
it with `ml/.venv/bin/python -m numbra_ml.schema`. The reader uses the same schema
with date format checking plus semantic constraints. Unknown fields, invalid
enums and unsupported versions fail. The full manifest is checked before filtering
by split so a subset cannot conceal patient, group or exact-hash split leakage.

| Required row field | Meaning |
| --- | --- |
| `schema_version`, `taxonomy_version`, `record_id` | Exact supported versions and unique opaque record ID. |
| `image_path`, `sha256` | Normalised relative POSIX file path below the selected data root; SHA-256 of original bytes. Absolute paths, traversal and symlink escapes fail. |
| `source` | `id`, `version`, `url`; one consistent release per source ID in a manifest. |
| `licence` | `id`, `url`, `attribution` retained per row; metadata is not itself approval. |
| `label` | Original label, mapped diagnosis/family, label status, explicit PB/MB and reaction status. |
| `confirmed_by` | Null, or allow-listed method/opaque confirmer-evidence reference/ISO calendar date (not future). A confirmed label needs this assertion and a resolved diagnosis; model predictions cannot confirm. Credentials are not verified by this schema. |
| `patient_id`, `group_id` | Explicit opaque tokens or null; namespaced by source. Group ID defines the primary evaluation unit; repeated patient IDs across groups must still stay in one split. Missing IDs are never inferred from filenames. |
| `split` | `unassigned`, `train`, `calibration`, `threshold_validation`, `test`, `held_out`, `quarantine`. Assignment follows ADR-007. Quarantine and unassigned remain group-level partitions; mixed active/quarantine rows in one connected group fail. |
| `synthetic`, `placeholder` | Explicit booleans. Synthetic rows require PLACEHOLDER, original labels beginning `SYNTHETIC:`, and no clinical confirmation. |
| `skin_tone` | Null or controlled scheme/value/assigned_by (Fitzpatrick I–VI, Monk 1–10, or synthetic colour). Generated data permits only `synthetic_colour`, never invented Fitzpatrick/Monk annotations. |
| `capture` (optional) | Nullable opaque site ID, device class and body site. Omission preserves null values; no guessed capture metadata. |
| `observations` | Object; all fields may be omitted in a manifest, preserving missingness for later workflow review. |

Confirmation methods are `clinical_examination`, `slit_skin_smear`, `histopathology`,
`dermatologist_photo_assessment` and `source_dataset_assertion`. The evidence
category property retains clinical-only, laboratory, photo-only weaker and
source-assertion-unverified distinctions. These categories do not verify evidence
or establish clinical eligibility. Other methods (including model/volunteer/self
assertions) fail. Real diagnosis codes must match the versioned family vocabulary;
unknown named conditions may only use `other`. Clinical approval remains pending.

The manifest loader can describe future real records, but the image-loading policy
enforces ADR-002: `synthetic=true`, `placeholder=true`, source ID `synthetic-*`,
source URL `urn:numbra:synthetic` and declared generator licence `Apache-2.0`.
These are engineering checks, not proof that arbitrary bytes are synthetic. Only
the repository's generated fixtures/pipeline may supply data. No real dataset is
approved, and the code has no network acquisition path or policy bypass flag.

## Taxonomy and eligibility

[Taxonomy code](../ml/src/numbra_ml/taxonomy.py) preserves `leprosy`,
`leprosy_differential`, `other`, `unresolved`; `PB`/`MB`/`unknown`; and independent
`type_1`/`type_2`/`none`/`unknown` reaction annotations. Non-leprosy labels cannot
carry PB/MB/reaction assertions. Neither patch count nor a model infers them.
`refer_for_review` is an action and is rejected as a disease family.

Exact-name proposed vocabulary comes from M0, including the explicit
tinea-versicolor → pityriasis-versicolor alias. Mapping always returns provisional
status. Unknown strings stay unresolved; no fuzzy/substring match, inferred
confirmation or source-specific import approval. Eczema/dermatitis priority still
needs clinical review. Named comparison conditions can themselves need referral.

Only resolved `confirmed` or explicitly `synthetic` labels expose a binary image
evidence target: leprosy family 1, labelled comparison family 0. Provisional,
unresolved, quarantined and withdrawn labels expose `None`. Zero is an image
training label and never a disease-absence or no-referral outcome. Synthetic
targets represent invented shapes, not disease presence. No synthetic label can
claim clinical confirmation.

`ManifestDataset.supervised_selection()` returns eligible rows and per-record
exclusion reasons, additionally excluding null groups and unassigned/quarantined
splits. It performs no training or scoring. M2 adds [component preparation](DATA-PREPARATION.md), synthetic source holdout,
near-visual candidate detection and group-wide conflict quarantine. The raw
manifest check alone is not the full preparation pipeline and does not prove
real patient independence.

## Observation contract for M6/M7

The canonical future referral rules are [research/04](../research/04-models-and-methods.md#proposed-transparent-rule-precedence).
M6 implements the ADR-001 superset; the roadmap question list is a minimum.
The manifest does not implement referral or relax the rule's required assessment.

- Sensation: `present`, `reduced`, `absent`, `uncertain`, `unknown`, `declined`,
  `not_tested`, plus optional method and assessor.
- Nullable nonnegative patch count and duration in days.
- Answers for widespread distribution, nerve symptoms, new weakness, eye symptoms,
  skin/earlobe changes, eyebrow loss, painless wounds/burns, volunteer concern and
  optional contact history: `yes`, `no`, `uncertain`, `unknown`, `declined`.

An omitted categorical answer stays `None`, distinct from an explicit unknown,
declined, no or not-tested value. No default-normal answers. Contact yes is a
proposed referral trigger; unknown/declined contact is optional. Volunteer concern
is an explicit required question in M6. M7 will add consent, lifecycle, detailed
capture and confirmation provenance, encryption and deliberate export; this
training manifest is not the complete clinical contribution record.

## Image interface

[ManifestDataset](../ml/src/numbra_ml/dataset.py) supports length, indexing,
iteration, explicit split selection and caller-supplied transforms. Each sample
contains row/provenance, optional target, pixel array and PLACEHOLDER notice.
`load_rgb` validates source/path, verifies bytes against the checksum, applies EXIF
orientation, and returns an owned uint8 RGB array in HWC layout. RGB/grayscale
single-frame images are supported; transparency, palette modes and multiple frames
are rejected until an explicit policy exists. Missing/corrupt/hash-mismatched
images fail visibly, with no substituted image, target or score.

No resize, letterbox, normalisation or tensor conversion is implicit. M4 must test
the eventual model preprocessing and Python/Android parity separately.

## Open questions

- Does clinical review approve the exact challenge vocabulary and question superset?
- Which future permitted cohort supplies auditable patient/group and confirmation provenance?
- Will real-data review accept an amended visual-duplicate policy, and how will M7
  extend confirmer/custodian/consent fields?

## Confidence

High for the tested synthetic schema/loading contracts; no clinical performance,
real-data permission, complete security review or Android integration is claimed.
