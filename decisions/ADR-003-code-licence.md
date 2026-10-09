# ADR-003 — Apache-2.0 for project code

Date: 2026-10-09

Status: Accepted (autopilot) — pending human review

## Context and evidence

The phase-0 brief requests Apache-2.0. The official licence includes conditions for
redistribution, attribution, modifications, and a contributor patent grant:
[Apache-2.0 text](https://www.apache.org/licenses/LICENSE-2.0.txt)
(accessed 2026-10-09). This decision does not grant rights to datasets, pretrained
weights, third-party content, or clinical use.

## Options

- Apache-2.0: matches the brief and supplies explicit patent terms.
- MIT: shorter, but differs from the requested licence.
- Defer: leaves downstream code permission unclear during unattended work.

## Decision

Use the unmodified official Apache-2.0 text as LICENSE for project code. Keep each
dependency's notices and each dataset's permissions separate. Do not publish any
artifact during autopilot. The repository has no imported third-party code yet.

## Consequences and revisit trigger

Future dependency and model choices must be checked individually. A data licence
cannot be replaced by Apache-2.0. Humans can revisit before distributing the POC,
especially if a dependency creates incompatible distribution obligations.

## Open questions

- Do the human leads agree with this code licence for future distribution?
- Which notices will pretrained weights and Android dependencies require?

## Confidence

High that this matches the brief and official text; medium on future distribution
compatibility until dependencies and weights are selected.
