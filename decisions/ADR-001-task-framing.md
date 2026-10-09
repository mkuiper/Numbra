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

The single canonical rule list is [research/04, Proposed transparent rule
precedence](../research/04-models-and-methods.md#proposed-transparent-rule-precedence).
M6 implements that full list; the roadmap's question list is a minimum, not the
complete clinical-review proposal. Unknown sensation cannot become normal sensation.
Rules return referral actions and reasons, never disease absence, treatment, PB/MB
classification or a clinically calibrated probability. Every synthetic POC result
says **PLACEHOLDER — not clinically validated**. Local clinical rules, translations,
urgency and receiving services require human approval before field use.

Review-1 amendment: **intact patch sensation does not exclude leprosy or MB**;
the [ILA Technical Forum report, S24–S25](http://ila.ilsl.br/pdfs/v70n1s1a05.pdf)
warns against relying on anaesthetic patches alone. Volunteer touch-test sensitivity
is UNVERIFIED. Before interpreting scores, the proposed engine also refers for
more than five patches, many/widespread patches with unknown count, raised/nodular/thickened
skin or earlobes, eyebrow loss, painless hand/foot wounds/burns, close contact
with the presenting skin concern, or an explicit volunteer-concern answer.
Ask: “Are you concerned that this person needs clinical assessment despite the
other answers?” Use yes/no/uncertain: yes refers; uncertain, declined or missing
routes to incomplete-assessment review. Contact history is optional: yes refers,
unknown/declined is neither a trigger nor required-answer missingness, and no
never lowers an outcome. Incomplete required
assessment routes to clinical review. These proposals cannot guarantee detection
of all MB disease; future humans must explicitly approve whether low-photo wording
is appropriate at all. M6 must test each override with intact sensation and score
zero, overlap, boundaries and monotonicity. The methods plan now sets minimum
group counts and exact sensitivity bounds before threshold selection; insufficient
counts use a labelled unselected refer-all fallback. This amendment retains
Accepted (autopilot) — pending human review status and synthetic-only authority.

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
