# ADR-004 — Local contribution records with separate confirmation and release gates

Date: 2026-10-09

Status: Accepted (autopilot) — pending human review

## Context and evidence

M7 requires consent/provenance records and an export format, explicitly without a
server/upload. [WHO governance principles](https://www.who.int/news/item/28-06-2021-who-issues-first-global-report-on-ai-in-health-and-six-guiding-principles-for-its-design-and-use)
support human control and accountability (accessed 2026-10-09). The
[contribution design](../research/06-data-contribution-platform.md) and
[Nepal ethics research](../research/07-ethics-regulatory-nepal.md) distinguish
proposals from legal facts and UNVERIFIED procedures. No real collection is approved.

## Options

- Automatic uploads and model updates: rejected; outside the POC and unsafe
  without consent, confirmed labels, custodian and independent evaluation.
- Local versioned records/export with later governed review: selected; permits
  synthetic development while preserving a path to externally confirmed labels.
- Federation/backend now: deferred; unnecessary for local inference, and does
  not resolve ownership, consent or clinical validation.

## Decision

Build only a local, encrypted, versioned screening/contribution record and explicit
metadata export after its roadmap gate. Separate care-storage, clinic-sharing and
future-research consent decisions; missing or withdrawn research consent blocks
research export/eligibility. Capture labels remain provisional. Confirmation needs
an externally recorded clinical method, confirmer provenance and date; a model
score can never supply it. The POC does not verify professional credentials or
connect to a real research cohort. All demo records and models are synthetic,
with models/UI labelled **PLACEHOLDER**.

Preview clinic summaries and contribution metadata separately; omit direct
identifiers and photos by default, record explicit sharing, and explain that a
recipient's copy cannot be recalled. No background sync, server, research image
transfer, account or publication. Test consent/missingness/withdrawal, provenance,
encrypted storage, deletion and minimum export fields in M7/M8.

For any future collection, require a Nepal institutional custodian and approved
protocol defining credential checks, retention, residency, withdrawal, licences,
community representation and benefit sharing. These are future conditions, not
an assertion of present legal ownership or approval. New submissions enter
quarantine, then a versioned approved dataset. Retraining, independent frozen
evaluation, clinical/ethics/data sign-off and separately authorised release are
required before promotion; never learn or deploy directly from submissions.

## Consequences and revisit trigger

The POC demonstrates schema and software safeguards, not a secure clinical service,
legally compliant collection programme or validated model. Legal/regulatory gaps
do not block synthetic development but block real collection/pilot proposals from
being treated as approved. Revisit when named institutions, affected people and
review bodies establish authority and permissions. Withdrawal plans must explain
recipient-copy and existing-model limitations; no automatic unlearning promise.

## Open questions

- Which institution and communities will govern future data and benefits?
- Which consent, retention and confirmation methods will local review approve?
- How should already exported records and affected model versions be handled after withdrawal?

## Confidence

High on matching the local-only roadmap boundary; medium on schema/governance
design; low on field/legal fitness until Nepal partners and review bodies assess it.
