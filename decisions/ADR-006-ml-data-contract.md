# ADR-006 — Strict versioned Python data contract with synthetic-only loading

Date: 2026-10-09

Status: Accepted (autopilot) — pending human review

## Context

M0's harness gate is closed PASS WITH CHANGES. M1 requires a pinned Python project,
data interfaces, provenance/group/split schema, taxonomy code and tiny synthetic
tests. [ADR-002](ADR-002-dataset-selection.md) approves no real task data.
Review-2 asks that all canonical referral-trigger answers survive into M1/M7.

## Options

- Loose dictionaries and implicit source/label defaults: rejected; silently lose
  unknown answers, provenance or confirmation and conceal split leakage.
- Strict JSONL row schema and immutable records: selected; interoperable local
  records and explicit errors, with missingness preserved.
- Implement acquisition/training/referral now: defer to M2/M3/M6 respectively.

## Decision

Use Python 3.12, a src-layout package and exact M1 dependency pins including
transitive test/build dependencies. NumPy represents raw RGB arrays, Pillow decodes
images, JSON Schema validates structure and pytest verifies generated fixtures.
These are engineering choices, not recommendations based on comparative benchmarks.
Record observed installation commands in [DEV-SETUP](../docs/DEV-SETUP.md).

Version schema/taxonomy as `1.0.0`; preserve source/licence/original diagnosis,
confirmation assertion, source-scoped patient/group IDs, split, SHA-256 and explicit
synthetic/PLACEHOLDER fields. Accept null grouping for honest missingness but exclude
it from primary supervised selection. Clinical confirmation and synthetic label
status are separate. Versioned exact-name mappings remain provisional; unseen
names are unresolved. Do not turn a referral action into disease ground truth.

Implement the full ADR-001 observation superset as optional manifest fields with
explicit unknown/declined/not-tested values. Workflow requirements apply in M6;
manifest optionality cannot create normal answers. Keep detailed clinical consent,
lifecycle and encryption/export implementation for M7.

Reject unsupported schema versions, extra fields, duplicate JSON keys/record IDs,
inconsistent source provenance, unsafe paths, and patient/group/exact-hash split
leakage before split filtering. Raw loading returns oriented uint8 HWC RGB without
model preprocessing and requires generated synthetic PLACEHOLDER provenance.
No acquisition path, real-source approval switch, weights or training added.

## Consequences

Schema can describe future human-approved records but loaders block real sources
under current ADR-002. Strict versions require deliberate migration. Source IDs
namespace groups but cannot prove cross-source independence; M2 must merge
duplicate-connected components and quarantine conflicts before splitting.
The [data contract](../docs/ML-DATA-CONTRACT.md) documents these limits. Tests run
under ignored `ml/tests/.tmp/`; no image fixture or manifest is committed.

## Open questions

- Do humans accept Python/dependency pins and the strict migration requirement?
- Which additional confirmation and clinical contribution fields should M7 require?
- Will clinicians approve the M0 proposed vocabulary and referral-question superset?

## Confidence

High for synthetic software contracts once checks pass; no clinical, data-rights
or complete privacy/security assurance follows from this engineering choice.
