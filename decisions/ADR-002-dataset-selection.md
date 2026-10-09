# ADR-002 — Synthetic-only baseline until a suitable public cohort is verified

Date: 2026-10-09

Status: Accepted (autopilot) — pending human review

## Context and evidence

The hard limits prohibit account creation, signed agreements and accepting terms
on another person's behalf. The [dataset survey](../research/03-datasets.md)
documents primary-source evidence and UNVERIFIED fields. The
[AI4Leprosy catalogue](https://arcadados.fiocruz.br/api/datasets/:persistentId/?persistentId=doi:10.35078/1PSIEL)
now verifies CC BY-NC 4.0 and restricted, request-gated files; it is excluded under
the hard limits, rather than held because its licence is unknown. DermaCon-IN's
[documentation](https://dataverse.harvard.edu/api/access/datafile/11362259) verifies
patient IDs/subject-wise splits and the South Asian candidate improves the survey.
Anonymous documentation access is verified; leprosy/differential label coverage,
actual patient linkage and image download flow are UNVERIFIED. Its CC BY-NC-SA 4.0
terms and possible derived-weight obligations need human review. It must not be
assumed negative-only without a label audit. [DDI](https://ddi-dataset.github.io/index.html) requires
registration/agreement. [DermNet](https://dermnetnz.org/image-licence) prohibits AI
use of free website images. [PAD](https://data.mendeley.com/datasets/zr7vgbcyr2/1)
has a documented CC BY 4.0 licence but the wrong target taxonomy.

## Options

- Pool readily found photos: rejected because public visibility is insufficient
  permission and mixing positive-only and negative-only sources risks shortcuts.
- Acquire custom-terms or registration-gated sources: excluded during autopilot.
- Approve DermaCon-IN now: defer; promising domain and documented patient IDs
  do not resolve target labels, linkage audit or NC-SA weight obligations.
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

- Will humans seek AI4Leprosy access via the owner and accept non-commercial data terms?
- Can DermaCon-IN's target labels, patient linkage, image access and NC-SA/weight obligations be verified?
- Is there a compatible independent positive/control validation cohort?
- Which local clinical/ethics partner could govern future Nepal data collection?
- Do humans agree with the conservative hold on custom-terms data?

## Confidence

High that synthetic-only stays inside the hard limits; low that any surveyed real
combination yet supports a clinically meaningful leprosy baseline.
