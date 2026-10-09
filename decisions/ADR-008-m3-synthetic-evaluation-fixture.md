# ADR-008 — Harder PLACEHOLDER fixture and a threshold-selection exercise profile

Date: 2026-10-09

Status: Accepted (autopilot) — pending human review

## Context

M2's harness gate closed PASS WITH CHANGES. Review-1 identifies a brightness/area
shortcut, weak procedural source differences, uneven source counts, arbitrary
colour strata and a fixture cap that cannot reach ADR-001's threshold-selection
minimum with the default fractions. These would obscure M3 evaluation failures.
ADR-002 still permits generated pixels only. No training has occurred yet.

## Options

- Raise the generator and quadratic duplicate-search caps: rejected for this step;
  larger fixtures are unnecessary to exercise the count guard.
- Lower ADR-001's count guard: rejected; small fixture scores must retain the
  unselected refer-all fallback.
- Add a declared synthetic selection profile and a harder generator version:
  selected. Preserve default fixtures to exercise insufficient-count behaviour.

## Decision

Replace newly generated fixtures with **shapes-v2**; never overwrite shapes-v1.
Give square and circular shapes the same exact pixel-area distribution. Use
signed, overlapping foreground/background intensities, source-dependent channel
gains, illumination and texture noise. Independently flip the rendered shape
with probability 0.10 per group while preserving its assigned artificial target;
both views share this intentional label noise. This is a software stress fixture,
not a disease simulator. Finite samples may remain easy for a particular model;
M3 must report observed performance and degeneracy, never promise a miss rate.

Name diagnoses `synthetic_circle` and `synthetic_square`. Retain existing binary
family encoding for schema compatibility, but every M3 report/card must use the
explicit **synthetic circle / synthetic square** target names in the generator
audit, never interpret the internal family as a clinical metric. Colour strata
are bands of the generated pre-texture background's weighted luminance (<85,
85..<170, >=170), after source channel gains. They are synthetic colour strata,
not human skin-tone or fairness annotations.

Preparation 1.1.0 stratifies by complete source-membership tuple × binary target,
then hash-ranks whole components. Use minimum one/stratum/partition when at least
four components exist; smaller strata use largest-remainder allocation without a
minimum. Every development partition must still contain both classes, or fail.
A cross-source component is never separated to satisfy source balance. Report
per-split/source/class counts; multi-source components count in each represented
source and quarantined components have null targets.

Keep the default 60/15/15/10 train/calibration/threshold-validation/test fractions.
Add explicit `selection_exercise` fractions **30/20/40/10**. With 256 groups/source
and the default seed, the latter has 102 threshold components and 52 separate
calibration components per class, without exceeding 1536 rows or the 2000-row
cap. M3 may use this profile for its PLACEHOLDER operating-point demonstration;
check actual eligible component counts before fitting/selecting. The default
128-group run remains below the threshold count guard and must use fallback.
These counts establish software-path availability only, never clinical adequacy.

Record the nearest pair in distinct final connected components as an audit of
the visual-distance margin. Keep the cutoff unchanged. A bounded float32 pair
matrix uses at most 16 MB at the existing cap. No real duplicate validation follows.

Default source C remains one predeclared held-out-source fold. Expose holdout
configuration to support later separate A/B/C runs, but require M3 to say
**single held-out source (one leave-one-source-out fold)** if it reports C only.
Do not call that a rotation or train on C then reuse that backbone in its fold.
Pretrained-image features remain subject to ADR-005's separate acquisition checks.

## Consequences and revisit trigger

Regenerate manifests into new ignored run directories. Version-1 evidence remains
historical. No model, weight, clinical score, export or Android app is supplied by
this change. The model must remain PLACEHOLDER even if a selected artificial
threshold is available. Full M3 calibration, count guards, exact bounds, frozen
thresholds, component index-image selection, reports and model card remain work
for the next step. Amend this ADR if training needs different fixture parameters;
never tune fixtures or splits to make an evaluation look favourable.

## Open questions

- Do humans accept intentional artificial label noise and this count-exercise profile?
- Is one held-out-source fold sufficient for the POC, or should later work run all three?
- Which real cohort and validation plan could eventually replace the PLACEHOLDER?

## Confidence

High for the observed fixture/split mechanics after tests; no evidence of clinical
validity, field safety, real source robustness or clinical sample-size adequacy.
