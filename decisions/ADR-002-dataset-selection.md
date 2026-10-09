# ADR-002 — Synthetic-only baseline until a suitable public cohort is verified

Date: 2026-10-09

Status: Accepted (autopilot) — pending human review

## Context and evidence

The hard limits prohibit account creation, signed agreements and accepting terms
on another person's behalf. The [dataset survey](../research/03-datasets.md)
documents primary-source evidence and UNVERIFIED fields. AI4Leprosy repository
verification failed on the DOI and a candidate landing page; no suitable positive
archive has been verified. [DDI](https://ddi-dataset.github.io/index.html) requires
registration/agreement. [DermNet](https://dermnetnz.org/image-licence) prohibits AI
use of free website images. [PAD](https://data.mendeley.com/datasets/zr7vgbcyr2/1)
has a documented CC BY 4.0 licence but the wrong target taxonomy.

## Options

- Pool readily found photos: rejected because public visibility is insufficient
  permission and mixing positive-only and negative-only sources risks shortcuts.
- Acquire custom-terms or registration-gated sources: excluded during autopilot.
- Synthetic-only demonstrator: permits honest, reproducible development while
  real-data permissions and scientific fitness remain unresolved.

## Decision

Approve **only generated synthetic data** for the current M1–M4 baseline. No real
dataset is approved for download by this ADR. Generate fixture pixels in code,
store generated runs under ignored `data/`, and never commit patient photos.
Every downstream model and app surface must say **PLACEHOLDER**. Reports must state
that synthetic metrics are not clinical performance. Synthetic sources provide
pipeline leave-one-source-out tests only.

Retain source, version, licence, original and mapped label, confirmation provenance,
group ID and split per manifest row. Real-source permission is separate from
Apache-2.0 for code. Never silently promote provisional labels into ground truth.

## Consequences and revisit trigger

The prototype can verify mechanics, offline inference and referral rules; it cannot
establish safety, diagnostic accuracy or clinical calibration. Real-data acquisition
requires an amended ADR with a verified primary licence, anonymous access, suitable
positive and differential labels, defensible patient grouping and external validation
plan. An unavailable source should not prevent completion of the synthetic POC.

SCIN's bespoke licence is held conservatively for human review, rather than treated
as CC BY. This restriction is a project policy under the unattended hard limit,
not a legal opinion on whether any custom public licence is unusable.

## Open questions

- Can humans verify AI4Leprosy permission and a compatible external validation cohort?
- Which local clinical/ethics partner could govern future Nepal data collection?
- Do humans agree with the conservative hold on custom-terms data?

## Confidence

High that synthetic-only stays inside the hard limits; low that any surveyed real
combination yet supports a clinically meaningful leprosy baseline.
