# ADR-009 — Component index images and isolated PLACEHOLDER evaluation

Date: 2026-10-09

Status: Accepted (autopilot) — pending human review

## Context

M3 needs the evaluation protocol already specified in ADR-001 and the methods
plan. ADR-007 supplies duplicate-connected component IDs; original group IDs and
multiple views must not inflate the sample size. ADR-008 supplies circle/square
labels, synthetic colour strata, and an explicit threshold-count exercise profile.
No baseline has been trained. ADR-002 remains synthetic-only.

## Options

- Average/maximise across views or choose an image after scoring: defer; would
  change the single-photo protocol and require separate threshold validation.
- Select one image with a deterministic record-ID rule before any scoring: chosen.
- Add a numerical optimisation/statistics dependency now: defer; bounded convex
  temperature fitting and binomial-tail inversion work with existing NumPy and
  the standard library, independently tested against closed forms and count cases.

## Decision

Within each preparation component, use the lexicographically first record ID.
Read the manifest with its companion preparation report, verify its SHA-256 and
exact partition membership, and reject source/split/target disagreement. Verify
that known patient/group/byte-hash links do not span separate components, even
within the same split. Retain quarantined component IDs and reasons as exclusions.
Do not recompute or change frozen splits or visual links during evaluation.
The index rule depends on identifiers only, never on scores or target values.

Fit one temperature on calibration components only. Minimise binary logistic
negative log likelihood by bisection of its convex inverse-temperature derivative.
Restrict temperature to [0.05, 20]; record a boundary optimum rather than presenting
it as an unrestricted fit. All-zero logits have an indeterminate objective;
record the deterministic maximum-temperature boundary result. Fewer than 20
components of either class yields temperature=1 and unavailable calibration.
Bounds and fitting method are engineering choices, not clinical approval.

Threshold-validation is a separate named split. Require 100 components of each
class and available separate calibration before either illustrative endpoint is
selected. Retain ADR-001's inclusive `score >= threshold` convention and highest
observed qualifying threshold at sensitivity >=0.95. For the secondary specificity
>=0.80 endpoint, choose the lowest observed qualifying threshold, using the next
representable float above one as an all-negative sentinel when necessary. Below
counts, both endpoints remain unavailable with an **unselected refer-all** threshold
zero. Label tied/degenerate selections explicitly. Never describe a fallback as a
selected high-sensitivity operating point.

Report exact two-sided 95% Clopper–Pearson sensitivity and specificity intervals
by binomial-tail inversion, confusion counts, tied-rank ROC AUC, Brier score,
stable-logit loss, and ten equal-width reliability bins/ECE. Empty or single-class
subsets have null unavailable metrics rather than fabricated zeros. Save fitting
split score hashes; selection intervals are descriptive after search. Freeze all
fitting before test and the single held-out-source fold. Source/colour summaries
include class/component counts, uncertainty and missing/conflicting colour
fraction. Multi-source components count once per represented source; these
breakdowns overlap. Partial or inconsistent component colour labels get their
own `conflicting_or_partial` category rather than choosing a favourable view.

Every report says **PLACEHOLDER**, synthetic circle / synthetic square, synthetic
colour strata, and single held-out source (one leave-one-source-out fold).
Temperature scaling is not clinically calibrated risk. Calibration-split metrics
are in-sample after fitting, and raw-score threshold metrics are descriptive
because the threshold was fitted after scaling. No clinical subgroup, pure-neural
or human skin-tone/fairness evidence follows from generated pixels.

## Consequences and revisit trigger

This iteration supplies a tested evaluation library, not a trained model or
complete M3 report. Training/dependency/weight permission checks, model card,
script-written reports, seeded group bootstrap uncertainty and run provenance
remain required follow-through. The eventual training command must use this
component index before feature extraction, train its head on training components
only, and retain all manifest/preparation/checkpoint/dependency checksums.

The preparation report remains the authority for decoded/near-visual links;
evaluation does not independently validate that heuristic. Independent real
patient grouping/duplicate adjudication and a new dataset ADR are needed before
real data. Revisit numerical bounds if an observed fit hits one; do not tune the
bounds or fixture to improve frozen-test results.

## Open questions

- Do humans accept the single record-ID index-image rule and bounded temperature fit?
- Which independently validated clinical sample-size/threshold protocol replaces these engineering guardrails?
- Should later experiments rotate all procedural source folds rather than retain one?

## Confidence

High for the tested synthetic arithmetic and fit isolation; no evidence of
clinical accuracy, calibration, real patient independence or field safety.
