# M0 handoff — research and plan ready for harness review

Date: 2026-10-09

Builder requests M0 review; **no gate or approval is claimed**. Work is research
only. Review-1's numbered issues are answered in [RESPONSE-1](RESPONSE-1.md).
No training/app code, clinical photos, patient records, task-data archives or
model binaries acquired. No review.sh, publishing, pushes or external messages.
Publication text/PDFs, catalogues and documentation were inspected; Fitzpatrick17k
labels were counted in memory only with no images or individual rows retained.

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

1. **Usable task data:** AI4 CC BY-NC 4.0 is verified, all files restricted;
   DermaCon-IN adds South Asian capture, anonymous documentation, CC BY-NC-SA 4.0
   and documented Subject_ID/subject-wise splits. Target-label coverage, actual
   linkage, image flow and derived-weight obligations remain UNVERIFIED. Scrutinise
   the retained synthetic-only ADR-002 and these bounded deferrals; no negatives-only
   assumption or claim that South Asian candidates do not exist remains. Fitzpatrick
   counts confirm no leprosy label; the 32-category compilation is excluded.
2. **Clinical workflow:** local FCHV competency, urgency/sensory protocol and current
   receiving clinics are unverified. Scrutinise symptom precedence, missingness,
   low-photo wording, potential over-referral and lack of clinical threshold approval.
   Review-1 adds the intact-sensation/MB limitation and answer-based patch/skin/
   eyebrow/injury/contact referral triggers, with required-answer missingness and
   planned M6 zero-score regression tests. Macular PKDL and literacy/stigma findings
   inform local review. These proposed triggers do not guarantee all MB detection.
3. **Study comparability:** reported aggregate sensitivity, positive-only top-5
   recall, training usability and internal accuracy are different endpoints.
   Scrutinise metrics/denominators and abstract/indexed evidence limits, especially
   AI4 and the independent WHO evaluation; no borrowed Numbra performance claim.
   AI4 ResNet-50 and MIT code are verified. Main Table 3's SEN/SP 89/91% belong to
   metadata outputs plus patient info; supplement descriptions conflict about CV
   versus holdout and final refit includes test patients. No reconciliation invented.
4. **Engineering fitness:** pretrained binary access and notices, letterbox geometry,
   quantisation/parity and Nepal devices are untested. Scrutinise ADR-005's transfer
   workaround and fixed tolerances, group/duplicate/held-out leakage controls and
   explicit engineering-versus-clinical gates. Review-1 adds proposed threshold
   minimum group counts, insufficient-count refer-all fallback and exact 95%
   sensitivity lower bounds; these are unimplemented and not clinical evidence.
5. **Governance and law:** full NHRC/DDA opens failed twice; indexed evidence cannot
   settle current jurisdiction or software classification. Scrutinise consent,
   provisional/confirmed labels, export/withdrawal limits and missing custodian/
   retention/legal determinations. Autonomous ADRs authorise synthetic development
   only, never real collection, pilot or distribution. Review-1 adds Privacy Act
   sections 11/16 without claiming every photography circumstance is prohibited.

## Known gaps and next boundary

Firecrawl has zero credits; earlier failed requests established the labelled
web-tool/direct-document workaround. HTTP retrieved the ILA report after HTTPS
failed; Harvard's metadata export worked after ordinary API/page failures; direct
Fiocruz and Europe PMC access corrected earlier AI4 failed-open notes. DermaCon
README/schema/dictionary do not enumerate diagnosis values: target coverage is
explicitly deferred rather than acquiring unauthorised patient rows. NHRC/DDA/
current Nepal reports and several full papers have
access limits recorded beside claims and in the source register. These are
bounded research workarounds, not fabricated verification. All human decisions
and field gaps are queued. No new toolchains installed in this iteration.

After the harness's M0 gate, the next milestone is **M1 only**: pinned Python
scaffold, taxonomy/manifest/data-loading interfaces and generated synthetic tests.
No M1 work starts before that gate. Future clinical validation/approval is outside
this unattended roadmap's engineering completion.
