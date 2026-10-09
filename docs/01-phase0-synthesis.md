# Phase-0 synthesis and recommended next phase

Evidence reviewed **2026-10-09**; primary links/access limits are in the
[source register](../research/sources.md). M0 has research and decisions, not a
trained model or app. The [roadmap](ROADMAP.md) controls engineering acceptance.

## Recommended baseline plan

Proceed after M0's harness gate with a **synthetic-only PLACEHOLDER** demonstrator.
The [dataset survey](../research/03-datasets.md) found no verified positive-plus-
differential cohort meeting anonymous access, permission and scientific needs;
this is a survey limitation, not proof none exists. No real dataset is approved
by [ADR-002](../decisions/ADR-002-dataset-selection.md). Generated sources/groups
exercise manifests, duplicates, patient/group splits and source holdout mechanics.
Review-1 correction: AI4Leprosy has verified CC BY-NC 4.0 but request-gated files;
DermaCon-IN adds a South Asian clinical smartphone/camera candidate with documented
patient IDs and CC BY-NC-SA 4.0. Its documentation downloads anonymously, but
target-label coverage, actual linkage and image flow remain UNVERIFIED. Humans
must assess NC-SA/derived-weight obligations. Fitzpatrick17k has no leprosy label;
the 32-category Kaggle compilation is excluded for unresolved upstream rights.
These corrections retain the synthetic-only decision, without claiming regional
data do not exist or assuming DermaCon-IN is negatives-only.

Use versioned `leprosy / leprosy_differential / other / unresolved` families with
original named diagnosis, explicit PB/MB and reaction status, source/licence,
confirmation and group provenance. Provisional/unresolved labels are not primary
ground truth. A referral action is separate from a disease label. The
[clinical research](../research/01-clinical-background.md) explains why photographs
cannot establish WHO's sensory cardinal sign. Local volunteer procedures and
referral routes remain UNVERIFIED.

[ADR-001](../decisions/ADR-001-task-framing.md) selects a binary image evidence score
with transparent symptom-first referral: urgent deterioration, sensory/nerve
concern, incomplete/failed assessment, then photo score. A low score permits only
qualified low-photo-concern wording with follow-up; never a negative diagnosis.
Every synthetic result says **PLACEHOLDER — not clinically validated**.
Intact sensation does not exclude MB disease. Proposed independent triggers now
also cover patch burden/distribution, raised/nodular/thickened skin/earlobes,
eyebrow loss, painless wounds/burns and close contact with the presenting concern.
M6 must test each with intact sensation and a zero score. Incomplete required
concern assessment refers; humans must decide if low-photo wording should exist
in any future pilot. Macular PKDL is added to the local differential vocabulary.

[ADR-005](../decisions/ADR-005-baseline-runtime.md) selects CPU PyTorch/timm
MobileNetV3Small frozen transfer features and a binary head, with quantised ONNX
Runtime Mobile export. Verify anonymous pretrained-binary access, revision/checksum
and notices before use; no weights acquired in M0. If access fails twice, its
labelled synthetic-pretraining transfer workaround preserves honest provenance.
Models stay ignored and must be regenerated/packaged locally.

The [methods plan](../research/04-models-and-methods.md) isolates train,
calibration/threshold-validation and test groups plus a held-out source. Freeze
the threshold chosen for illustrative validation sensitivity ≥0.95; report achieved
test sensitivity/specificity, AUC, calibration, uncertainty, source/presentation/
tone breakdowns where labels exist, and failures in workflow denominators. Report
secondary sensitivity at specificity ≥0.80 separately. Synthetic metrics are
software evidence only. Threshold selection requires at least 100 independent
groups per class after a separate calibration subset (20 per class); otherwise
selection is unavailable and the app uses a labelled refer-all fallback. Report
the exact 95% sensitivity lower bound alongside the point estimate; selection
intervals do not establish independent support or clinical approval. M4 measures
≤20 MB and parity at the proposed probability
tolerance 0.02; M6 tests preprocessing and conservative threshold handling.
[Deployment research](../research/05-deployment-constraints.md) proposes offline
bundling, neutral UI, reviewed-later Nepali, bounded decoding and encrypted records;
device budgets and actual Nepal hardware fitness are unmeasured.

## Five decisions queued for human review

All are **Accepted (autopilot) — pending human review**, permitting bounded POC
work while humans are unavailable; none authorises clinical use.

| ADR | Human scrutiny needed |
| --- | --- |
| [001: task framing](../decisions/ADR-001-task-framing.md) | Symptom/urgency/missingness rules, clinical language and referral burden/targets. |
| [002: data](../decisions/ADR-002-dataset-selection.md) | Synthetic-only constraint; verify real permissions and an independent representative cohort. |
| [003: code licence](../decisions/ADR-003-code-licence.md) | Apache-2.0 for code only; audit separate weight/data/dependency rights before distribution. |
| [004: governance](../decisions/ADR-004-contribution-governance.md) | Nepal custodian, consent, confirmation, retention, withdrawal, residency and community benefits. |
| [005: baseline/runtime](../decisions/ADR-005-baseline-runtime.md) | Weight provenance, Android compatibility, actual size/parity/device measurements. |

## Proposed phases and gates

| Phase | Deliverable and boundary |
| --- | --- |
| 0: research, M0 | Harness review/gate of these documents before any ML/app implementation. |
| 1: engineering baseline, M1–M4 | Synthetic scaffold/preparation/training/export and tests. Public real data remains contingent on an amended dataset ADR; no clinical validity claim. |
| 2: local protocol, future human-led work | Nepal partner, affected-person input, confirmed-label/consent plan, NHRC/IRC jurisdiction, privacy and DDA determinations. No collection authorised by autopilot. |
| 3: offline prototype, M5–M8 | Synthetic Android flow, encrypted records, explicit local export, end-to-end test and debug APK. Can proceed without phase-2 real collection; no server/upload/publishing. |
| 4: supervised field pilot, outside roadmap | Only after written approvals, representative clinical validation, native-language/device/usability review, receiving-service capacity and safety/stopping plan. |

[Contribution governance](../research/06-data-contribution-platform.md) separates
capture from confirmation and model promotion. [Nepal ethics research](../research/07-ethics-regulatory-nepal.md)
identifies authorities but marks unresolved processes/classification UNVERIFIED.
A completed roadmap or review-round-limit gate is not scientific or legal clearance.

## Open questions

- Can humans verify suitable leprosy/differential data, grouping and external validation rights?
- Which Nepal partner will approve volunteer practice, referral services and data stewardship?
- What current ethics/privacy/device obligations apply to an actual pilot?
- Will real devices and native-language users support the proposed workflow and budgets?

## Confidence

Medium for an achievable bounded synthetic POC; low for clinical utility or field
approval until representative data, institutional determinations and local validation exist.
