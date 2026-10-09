# ADR-007 — Synthetic preparation, component quarantine and frozen source holdout

Date: 2026-10-09

Status: Accepted (autopilot) — pending human review

## Context

M1 gate closed PASS WITH CHANGES. ADR-002 approves only generated synthetic data;
no real target dataset is suitable and authorised under the current decision.
M2 requires licence-bearing manifests, duplicate detection, patient/group splits
and a held-out source, with an honest synthetic fallback. M1 review requests
explicit conflict tests, quarantine semantics and future annotation metadata.

## Options

- Download a held real cohort: rejected; current ADR-002 authorises none.
- Split individual rows: rejected; repeated views and duplicates could leak.
- Generate deterministic fixtures; merge connected components before splitting:
  selected for the PLACEHOLDER pipeline only.

## Decision

Generate 64×64 RGB circle/square textures in three named procedural sources, two
views per invented patient/group. They are artificial engineering targets; the
labels do not represent skin conditions. Every source has both targets and
project-generator Apache-2.0 provenance. Default seed is 20261009, with 128
invented groups per source. CLI writes only a new run under ignored `data/` and
never downloads, overwrites or silently re-splits an existing run.

Merge all source-scoped patient/group, global byte hash, decoded oriented-pixel
hash and near-visual links transitively. Near-visual uses bilinear 16×16 RGB
thumbnail RMS ≤2 uint8 units; this is a chosen engineering heuristic, not a
validated medical duplicate detector. Search all pairs with an explicit 2000-row
limit; exceeding it fails rather than silently subsampling. Config is recorded
before split assignment. Never infer missing patient/group IDs from paths.

Quarantine the **entire component** for any contradictory resolved diagnoses,
missing group ID, ineligible label or connection across the preselected held-out
source boundary. Set quarantined label status without losing original labels;
report retains original statuses and reasons. Withheld/withdrawn labels are
never revived. No training target is exposed for quarantined rows. Quarantine
and unassigned are group-level partitions; mixed active/quarantine membership
fails ordinary manifest leakage validation.

Source C is preselected and used only as the synthetic external holdout. Other
components are deterministically ranked by seed/component hash, stratified by
binary target, and assigned train/calibration/threshold-validation/test in
60/15/15/10 proportions, with one component/class/partition minimum and largest
remainder rounding. Require at least four eligible development components/class
and both held-out classes after quarantine. Record assignment in a frozen
manifest and detailed companion component/duplicate/exclusion report. M3 must
aggregate by report component ID, including cross-source linked groups, rather
than treating views or original group IDs as independent evaluation units.

Amend ADR-006 schema to **1.1.0**, taxonomy unchanged at 1.0.0. Confirmation has
an allow-list with explicit weaker photo/source categories; real diagnosis and
family consistency is enforced, tone scheme/value/annotator is controlled and
capture site/device/body fields are optional. Schema 1.0.0 fails: regenerate
synthetic manifests; no automatic real-record migration. Method categories are
provisional software distinctions, not approval of clinical confirmation or
professional credentials. Real-source loading remains blocked.

## Consequences and revisit trigger

Synthetic leave-one-source-out tests mechanics only. Default threshold-validation
has 20 components/class, below ADR-001's 100/class requirement, so M3 must report
an **unselected refer-all fallback**. Calibration has 20/class, test 13/class and
held-out source 64/class; none establish clinical performance or calibration.
All downstream models, metrics, cards and UI must say **PLACEHOLDER**.

Visual matching can miss duplicates or merge unrelated images. This heuristic,
the split fractions, source definition and grouping are not sufficient for real
patient data. Revisit after an amended dataset ADR and independent patient/source
provenance and visual-duplicate review. Do not expand the row limit or loosen
conflict safeguards silently. No training, weights, model or app is added in M2.

## Open questions

- Which independently reviewed real cohort could eventually amend ADR-002?
- Do humans accept these provisional schema and synthetic split choices?
- What identity/duplicate adjudication and source holdout policy should real data use?

## Confidence

High for reproducible, tested synthetic mechanics; low for extrapolation to real
duplicate detection, patient independence or clinical performance.
