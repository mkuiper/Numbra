# M0 handoff — research and plan ready for harness review

Date: 2026-10-09

Builder requests M0 review; **no gate or approval is claimed**. Work is research
only. No training/app code, clinical photos, patient records, data archives or
model binaries acquired. No review.sh, publishing, pushes or external messages.

## Produced and acceptance evidence

- [Clinical background](../../research/01-clinical-background.md): WHO cardinal
  signs, differential vocabulary, non-photo findings, proposed symptom/urgency
  precedence and Nepal burden/pathway evidence with explicit access gaps.
- [Prior work](../../research/02-prior-work.md): required AI4Leprosy, WHO Kenya and
  independent leprosy evaluation, SkinApp, LEARNS, JMIR review, academic/general
  dermatology comparisons and future contact suggestions; nobody contacted.
- [Datasets](../../research/03-datasets.md): candidate provenance, rights/access,
  labels/confirmation/tone/grouping limits, mapping and combination risks. Every
  dataset claim has primary links or UNVERIFIED markers. No real source approved.
- [Models/methods](../../research/04-models-and-methods.md): CPU transfer proposal,
  score-versus-action framing, splits/calibration/threshold isolation, source
  holdout, subgroup/failure denominators and synthetic-only limitations.
- [Deployment](../../research/05-deployment-constraints.md): runtime/preprocessing/
  parity proposal, unmeasured budgets, offline/language/privacy design and platform
  interoperability with unknown local device/HMIS configuration.
- [Contribution governance](../../research/06-data-contribution-platform.md):
  provisional-to-confirmed provenance, separate consent scopes, minimisation,
  withdrawal/retention/residency, quality control, model promotion and local-only
  export; backend and federation deferred.
- [Ethics/regulation](../../research/07-ethics-regulatory-nepal.md): NHRC/IRC route,
  inspected Privacy Act text, DDA uncertainty, bounded FDA/EU comparisons,
  intended use/non-goals, risks and proposed future pilot conditions.
- [Synthesis](../../docs/01-phase0-synthesis.md), [brief](../../docs/00-project-brief.md),
  [glossary](../../docs/glossary.md), [source register](../../research/sources.md),
  [data layout](../../docs/DATA-LAYOUT.md), [setup](../../docs/DEV-SETUP.md), root
  README/LICENSE, scaffolding and repository-safety checks.
- Required [ADR-001 task](../../decisions/ADR-001-task-framing.md),
  [ADR-002 datasets](../../decisions/ADR-002-dataset-selection.md),
  [ADR-003 code licence](../../decisions/ADR-003-code-licence.md),
  [ADR-004 governance](../../decisions/ADR-004-contribution-governance.md), plus
  [ADR-005 runtime](../../decisions/ADR-005-baseline-runtime.md). All accepted
  autonomously with pending human review and queued in
  [HUMAN-QUEUE](../../notes/HUMAN-QUEUE.md).

M0 acceptance: all seven research documents, synthesis and required ADRs exist;
dataset evidence is linked or explicitly UNVERIFIED. Research documents end in
Open questions and Confidence. `data/` is wholly ignored; tracked layout docs
replace the brief's data README. All later models/reports/UI must say **PLACEHOLDER**.
The brief's attended review/human-wait steps are overridden by autopilot; the
harness owns the review, tests of record and gate.

## Verification and how to reproduce

Run from the repository root:

```bash
python3 -m unittest discover -s tests -v
bash scripts/check.sh
git diff --check
```

Builder observed five repository tests pass: ignore boundary, no tracked data,
local links, research uncertainty sections and source-register coverage. This
checks documentation/repository contracts, not factual correctness or clinical
rule effectiveness. `scripts/check.sh` exited 0 / RESULT PASS with **ML and Android
SKIPPED** because their projects do not exist. There is no APK, clinical performance,
parity or security implementation evidence at M0. The harness reruns its own checks.

## Top five uncertainties and requested scrutiny

1. **Usable task data:** AI4 repository rights/access and suitable confirmed
   positive/differential external cohorts remain unverified. Scrutinise whether
   synthetic-only ADR-002 is honest and whether survey exclusions follow the hard
   limits; public availability/code/paper licences never grant image rights.
2. **Clinical workflow:** local FCHV competency, urgency/sensory protocol and current
   receiving clinics are unverified. Scrutinise symptom precedence, missingness,
   low-photo wording, potential over-referral and lack of clinical threshold approval.
3. **Study comparability:** reported aggregate sensitivity, positive-only top-5
   recall, training usability and internal accuracy are different endpoints.
   Scrutinise metrics/denominators and abstract/indexed evidence limits, especially
   AI4 and the independent WHO evaluation; no borrowed Numbra performance claim.
4. **Engineering fitness:** pretrained binary access and notices, letterbox geometry,
   quantisation/parity and Nepal devices are untested. Scrutinise ADR-005's transfer
   workaround and fixed tolerances, group/duplicate/held-out leakage controls and
   explicit engineering-versus-clinical gates.
5. **Governance and law:** full NHRC/DDA opens failed twice; indexed evidence cannot
   settle current jurisdiction or software classification. Scrutinise consent,
   provisional/confirmed labels, export/withdrawal limits and missing custodian/
   retention/legal determinations. Autonomous ADRs authorise synthetic development
   only, never real collection, pilot or distribution.

## Known gaps and next boundary

Firecrawl has zero credits; earlier failed requests established the labelled
web-tool workaround. NHRC/DDA/current Nepal reports and several full papers have
access limits recorded beside claims and in the source register. These are
bounded research workarounds, not fabricated verification. All human decisions
and field gaps are queued. No new toolchains installed in this iteration.

After the harness's M0 gate, the next milestone is **M1 only**: pinned Python
scaffold, taxonomy/manifest/data-loading interfaces and generated synthetic tests.
No M1 work starts before that gate. Future clinical validation/approval is outside
this unattended roadmap's engineering completion.
