# ADR-001 — Image evidence score with transparent symptom-first referral

Date: 2026-10-09

Status: Accepted (autopilot) — pending human review

## Context and evidence

WHO's cardinal signs include findings that a photo cannot establish, especially
definite sensory loss. [WHO fact sheet](https://www.who.int/news-room/fact-sheets/detail/leprosy)
(accessed 2026-10-09). The [clinical draft](../research/01-clinical-background.md)
documents reaction/nerve concerns and unverified Nepal field protocols. Under
[ADR-002](ADR-002-dataset-selection.md), task training uses synthetic data only.

## Options

- Direct photo `refer / don't refer`: reject; labelled controls can require care
  and photographic appearance cannot establish absent sensory signs.
- Multiclass or top-k diagnosis: defer for inadequate verified data and risk of
  volunteer diagnostic overconfidence.
- Binary image evidence plus explicit symptom/quality rules: selected for a
  reproducible, inspectable POC while preserving named source diagnoses.

## Decision

Implement a binary image score and a separate versioned referral engine after M0
gates. Preserve hierarchical labels and confirmation provenance. Do not learn
`refer_for_review` as a disease class. Start image-only; metadata fusion is optional
and may never disable independent symptom overrides.

Use the [methods plan](../research/04-models-and-methods.md): validation selects
an illustrative ≥0.95 sensitivity operating point; test reports the achieved
sensitivity and specificity at that frozen threshold. The target is an engineering
choice, not clinical approval. Unavailable calibration/selection remains explicit.

Rule precedence is urgent symptoms, then sensory/nerve concern, then incomplete
assessment or quality/model failure, then high image evidence, then qualified low
photo concern with follow-up. Unknown sensation cannot become normal sensation.
Rules return referral actions and reasons, never disease absence, treatment, PB/MB
classification or a clinically calibrated probability. Every synthetic POC result
says **PLACEHOLDER — not clinically validated**. Local clinical rules, translations,
urgency and receiving services require human approval before field use.

## Consequences and revisit trigger

Model metrics and workflow metrics are separate; low scores cannot cancel symptom
referral. The POC may demonstrate high referral burden and has no clinical accuracy
claim. Revisit thresholds and class design only with licensed representative
confirmed data, independent evaluation and clinical/ethical approval. A human
decision is required for real field use, not for continued synthetic development.

## Open questions

- Which Nepal referral protocols, urgency rules and follow-up wording will clinicians approve?
- What miss rate and workload are acceptable at the receiving services?

## Confidence

High for the need for non-photo safeguards; medium for this transparent software
design; low for any clinical operating point until representative validation.
