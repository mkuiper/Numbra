# Journal

Append-only log of Builder iterations.

## 2026-10-09T11:50:27Z — iteration

- Oriented in the required order: roadmap, initial STATUS, HARNESS, absence of M0
  review folder, and absence of AGENTS/ADRs. Harness contains two run-start messages
  and no failed checks or refused reviews. Current branch is autopilot/20261009-2242.
- Read the phase-0 brief and protected check script. Kept this iteration inside M0
  research, and did not run review.sh or create harness-owned review/gate files.
- Built the scaffold: README, AGENTS roles/protocol, official Apache-2.0 LICENSE,
  project brief, initial glossary, data-layout/setup documentation, research/ML/app
  purpose READMEs, ADR template, M0 review README, and ignore rules for data, model
  weights, secrets, research caches, virtualenvs and builds.
- Accepted ADR-003 (code licence) under autopilot authority, pending human review.
  Kept all of data/ ignored; documented its layout in docs/DATA-LAYOUT.md instead
  of force-adding a README from data/. Recorded both choices in HUMAN-QUEUE.
- Applied Firecrawl research skill. Existing CLI 1.14.8 is authenticated but has
  zero credits. Setup scrape and one-result search both failed. Used the available
  web search/open tool as the labelled workaround, without installing tools,
  creating accounts, spending on a subscription, or accepting data-use agreements.
- Inspected primary pages/papers for AI4Leprosy, Fitzpatrick17k, DDI, SCIN,
  PAD-UFES-20, DermNet, ISIC and the WHO Skin NTDs photo library. Added a source
  register and dataset survey covering permission/access, labels, modality,
  provenance, missingness, proposed taxonomy and mapping, and combination risks.
- AI4 dataset DOI and candidate landing-page opens failed; its licence remains
  UNVERIFIED. DDI requires agreement/registration. DermNet prohibits AI use of free
  images. SCIN custom terms and Fitzpatrick original-image rights are held. PAD's
  CC BY 4.0 is documented but its labels do not supply the target positives or key
  differentials. No patient images, metadata rows, or archives downloaded.
- Accepted ADR-002: only synthetic data is approved for the current baseline.
  Models, reports and app surfaces must say PLACEHOLDER; synthetic scores and held-out
  synthetic-source results demonstrate mechanics, not clinical performance.
- Added four standard-library repository/documentation checks. Initial test run
  failed on research/README.md linking to the not-yet-created sources.md. The
  scaffold logical commit was made before the source-register follow-up; added the
  missing source register and reran the unchanged tests: all 4 passed. No tests
  deleted, weakened or skipped. No disputed test for the human queue.
- Ran bash scripts/check.sh: exit 0, RESULT PASS, ML and Android SKIPPED as expected
  at M0. This is not a claim of ML evaluation or APK production. git diff --check
  passed before commits. Tests of record/review still belong to the harness.
- Logical commits: 4e5b442 (research scaffold/licence), e683ef2 (dataset survey and
  synthetic baseline). Final notes commit records CONTINUE; M0 is incomplete.
- Next: finish the remaining six research documents, two ADRs and synthesis, then
  write a concrete M0 handoff. No review request made this iteration.

## 2026-10-09T12:03:06Z — iteration

- Read roadmap, STATUS, HARNESS, current M0 folder, AGENTS, existing ADRs and the
  phase-0 brief. No new harness failure, review or gate. Stayed in M0 research;
  no ML/app implementation, review.sh, harness-owned files, push or messages.
- Applied Firecrawl research/search skills. CLI status confirms zero credits;
  used the previous iteration's labelled web-tool workaround without new
  accounts, terms acceptance, billing changes or toolchain installation.
- Wrote research/01-clinical-background.md: WHO cardinal signs/PB-MB, photo limits,
  national clinical differential vocabulary, reactions, proposed non-image capture
  fields and symptom precedence, Nepal context, historical FCHV evidence and
  explicit current protocol/pathway gaps. Clinical proposals are not an approved
  field protocol. No negative diagnosis or photo-derived treatment classification.
- Wrote research/02-prior-work.md: AI4Leprosy; WHO public education vs AI beta;
  Kenya preliminary field study; independent PAHO 2026 top-5 leprosy evaluation;
  UOC Ghana/Kenya training usability; NLR SkinApp; Philippine LEARNS; 2023 JMIR
  scoping review; IEEE/CMU, arXiv and published PLOS image studies; eSkinHealth and
  CO2Wounds; DDI/SCIN/PAD design evidence. Compared tasks/denominators and provided
  proposed human contact priorities. No contacts made; no artifact reuse assumed.
- Expanded dataset survey and source register. eSkinHealth release remains delayed
  for ethical/privacy/legal review; Yotsu pilot images explicitly not public;
  CO2Wounds paper/record conflict (CC BY-NC-ND vs CC BY-NC 3.0) plus task mismatch.
  Independent WHO cohort is positive-only. ADR-002 synthetic-only remains unchanged.
- Added sourced clinical morphology/reaction and evaluation notation to glossary;
  updated research README. All new research documents end with Open questions and
  Confidence. No clinical photos, archives, patient-level metadata or weights
  downloaded. Only publication/documentation text was inspected.
- Several full official Nepal report opens failed (HMIS/government errors,
  NHRC timeout, Bagmati 25 MB size limit). After genuine failures, documented the
  labelled indexed-primary-text workaround; current burden figures remain
  UNVERIFIED against full report and current district list is not asserted.
  AI4 full text and independent PMC access were also blocked; abstract-supported
  claims are bounded and unavailable architecture/rights/details marked UNVERIFIED.
- All 4 unchanged repository unittest checks passed, including after final glossary
  edits. bash scripts/check.sh returned exit 0 and RESULT PASS after final research
  edits; ML and Android SKIPPED (projects absent), no APK/clinical validation claimed.
  Documentation only; no functional implementation requiring new unit tests.
  git diff --check passed before c6ef558 (M0 clinical/prior-work logical commit).
- Queued current clinical/pathway, report-access, additional-data rights and WHO
  distribution ambiguities for humans. No new accepted ADR this iteration;
  symptom precedence and field procedures remain clearly labelled proposals.
- Remaining M0 work: methods, deployment, contribution governance, Nepal ethics/
  regulatory research, ADR-001/004 and synthesis. Set CONTINUE, not a review request.


## 2026-10-09T12:12:57Z — iteration

- Read roadmap, STATUS, HARNESS, M0 review workspace, AGENTS and existing ADRs in
  the required order. No review/gate or new harness action exists; stayed in M0.
- Added research/04-models-and-methods.md: audited architecture/weight candidates,
  selected an image-only frozen-feature transfer baseline, separated disease
  evidence from referral actions, and specified patient/group and duplicate
  isolation, calibration/threshold validation, sensitivity/specificity endpoints,
  held-out-source evaluation, subgroup missingness and abstention denominators.
- Added research/05-deployment-constraints.md: compared LiteRT and ONNX Runtime,
  proposed deterministic letterbox preprocessing/parity and measured-later budgets,
  documented offline behaviour, language/privacy needs and ODK/Kobo/DHIS2 options.
  None of these are implemented or measured; no clinical performance is claimed.
- Wrote ADR-001 task framing and ADR-005 baseline/runtime with status Accepted
  (autopilot) — pending human review, and queued both plus engineering/field gaps.
  ADR-002 remains synthetic-only. Every downstream artifact must say PLACEHOLDER.
- Primary publisher card declares Apache-2.0 for timm MobileNetV3Small weights;
  binary retrieval/pinning/checksum still await M3. Derm Foundation requires login
  and HAI-DEF acceptance and is excluded. No weights/photos/patient rows acquired.
- Rural Nepal FCHV device specifications remain UNVERIFIED after manufacturer/NTA
  searches. Labelled research workaround: explicit test profiles plus a regional
  Samsung hardware example, with no Nepal ownership claim. HMIS indexed government
  text identifies DHIS2; direct open failed HTTP 502, so authenticated integration
  schemas/permissions are UNVERIFIED. No account or integration attempt.
- Firecrawl skill/status checked: zero credits persists. Continued the earlier
  labelled web search/open workaround, with no billing/auth changes. Added access
  dates/limits and all new cited URLs to research/sources.md. A guessed Keras API
  subpage failed; followed the official index link and corrected the citation.
- Added safetensors extension to .gitignore and the existing ignore-boundary test;
  proposed pretrained cache is under ignored data/pretrained/. No toolchains installed.
- Observed verification: python3 -m unittest discover -s tests -v passed all 4
  repository tests; bash scripts/check.sh exit 0 / RESULT PASS with ML and Android
  explicitly SKIPPED (no projects). Source-register coverage check passed for all
  four new documents; git diff --check passed. These do not verify clinical truth,
  model parity or an APK. No tests weakened; no protected files edited.
- Metadata patches failed to parse (empty update hunk, then duplicate target
  operations) and made no changes; wrote STATUS and appended JOURNAL separately.
- Remaining M0: contribution governance, Nepal ethics/regulatory research, ADR-004,
  synthesis, consistency pass and HANDOFF. NEXT_ACTION remains CONTINUE; no review,
  gate writing, push, publishing or external messages performed.
