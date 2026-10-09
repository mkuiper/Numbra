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


## 2026-10-09T12:24:10Z — iteration

- Read roadmap, STATUS, HARNESS, M0 workspace, AGENTS and relevant ADRs in order.
  No review/gate or new harness instruction exists. Stayed in M0 research only.
- Completed 06 contribution design: role/credential boundaries, provisional versus
  confirmed label assertions, separate consent scopes, minimisation/redaction,
  local encryption/export proposals, retention and withdrawal limits, future QC,
  dataset/evaluation/human-release cycle, Nepal stewardship and federation deferral.
- Completed 07 ethics/privacy/device research: NHRC/IRC route, inspected official
  English Privacy Act, bounded DDA/FDA/MDCG comparisons, POC versus future intended
  use, non-goals and proposed risk/stopping controls. No clinical/legal clearance.
- NHRC eLibrary full guidance timed out and NHRC-hosted copy failed; DDA catalogue,
  record and directive opens failed. After two genuine attempts, labelled workaround
  is indexed primary text and institution-owned scope statement, with jurisdiction,
  current procedural details and software classification UNVERIFIED. Initial NIC
  law PDF returned 404; followed Law Commission's government link and inspected text.
- Applied Firecrawl search/scrape skills; status still zero credits. Continued the
  earlier labelled web-tool fallback, no account/auth/billing changes. Registered
  access dates, primary URLs and limits; no photos or patient data downloaded.
- Wrote ADR-004 Accepted (autopilot) — pending human review and queued institutional
  governance plus NHRC/privacy/DDA gaps. No real-data acquisition decision changed.
- Wrote phase-0 synthesis and M0 HANDOFF with deliverable/acceptance mapping, top
  five uncertainties and review focus. Updated README/research index and removed
  stale pending-methods/framing wording. No training or app implementation.
- Added a meaningful source-register citation coverage test; preserved all existing
  tests. Observed all 5 tests PASS after final handoff edits. check.sh exit 0 /
  RESULT PASS with ML and Android SKIPPED because neither project exists. No APK,
  parity, model/clinical performance or legal validation claimed. URL coverage
  audit and git diff/staged whitespace checks passed.
- Logical research/handoff commit: 29dc47b. End-of-iteration STATUS/JOURNAL/NEXT_ACTION
  request REVIEW M0. Harness must run review/tests of record and close the gate;
  no review.sh, REVIEW/CHECK/GATE writes, protected edits, toolchain installs,
  external messages, pushes, publication or M1 work performed.

## 2026-10-09T12:44:00Z — iteration

- Oriented in required order and read Review-1/CHECK-1 in full. Harness requested
  REVISE M0; no gate. Stayed research-only and addressed all 10 numbered issues.
- Added DermaCon-IN record and amended ADR-002/synthesis: South Indian smartphone/
  camera candidate, CC BY-NC-SA 4.0, anonymous documentation, Subject_ID and
  documented subject-wise splits. Ordinary Harvard API/page failed; metadata
  export then README/schema/dictionary succeeded. Documentation omits disease
  enumeration: labelled documentation-only workaround keeps target coverage
  UNVERIFIED, queues permitted label/linkage/rights audit, assumes no negative-only
  role and retains synthetic-only. No patient tables/images/weights acquired.
- Corrected AI4 via direct Fiocruz HTML/API: CC BY-NC 4.0 and 1,456 restricted
  files, v1.10 release 2024-05-16. API null guestbook ID means generic UI alone
  cannot establish a download guestbook requirement. Updated obsolete queue/source
  notes. Europe PMC full text/supplement confirms ResNet-50, main Table 3's 89/91%
  SEN/SP row and unresolved CV/holdout descriptions; final refit includes test
  patients. Abstract/results count discrepancy retained. MIT code/current archive
  verified with repository README/licence/file listing; no data/weights reused.
- ILA HTTPS/web/direct opens failed; HTTP publication PDF/text succeeded. Confirmed
  intact sensation cannot exclude MB, and 30% concerns missed patients using one
  criterion in a cited study, not universal lesion prevalence. Amended 01/04/ADR-001
  with independent patch/skin/eyebrow/injury/contact triggers, missingness handling
  and planned M6 intact-sensation/zero-score, boundary/overlap/monotonicity tests.
  Clinical proposals/low-photo permissibility queued; no rule safety claim.
- Addressed smaller issues: macular PKDL; Sarlahi Table 2 literacy plus training,
  incentives/passive detection/stigma context; excluded 32-category upstream Kaggle
  compilation; transient in-memory Fitzpatrick label counts (no leprosy); verified
  Privacy Act ss.11/16; minimum group-count/exact-interval threshold plan; targeted
  Leprosy Review/IJDVL/IJL searches. No patient rows/image URLs retained or followed.
- Applied Firecrawl skills; status confirms zero credits. Continued documented
  web-tool/direct-document workaround without accounts, billing or terms submission.
  Updated source register/access limits and HUMAN-QUEUE. No toolchains installed.
- Wrote RESPONSE-1 addressing all blocking/non-blocking issues, missed work and
  human questions; updated HANDOFF, STATUS and REVIEW M0 request. Two patch calls
  failed verification before applying changes; corrected the patches. No protected
  files changed. No review.sh, reviewer/check/gate writes, publishing or pushes.
- Observed five repository tests PASS and bash scripts/check.sh exit 0 / RESULT
  PASS (ML/Android SKIPPED, no projects). git diff --check PASS. Final suite and
  staged boundary/whitespace verification recorded below before committing.
- Final documentation suite: all 5 tests PASS; staged diff --check PASS. Staged
  boundary audit confirms 16 builder files, no protected/data files, and exact
  single-line REVIEW M0 request. Commit: M0: address first research review.

## 2026-10-09T12:52:42Z — iteration

Read roadmap, status, harness, M0 review files, AGENTS and ADRs in order. Harness closed M0 PASS WITH CHANGES. Addressed Review-2 consistency issues in RESPONSE-2: canonical referral list, explicit volunteer concern/contact handling, observation superset, count-bound interpretation, stable IJDVL landing page, and publication PDF cleanup. DermaCon catalogue confirmation failed via web export then direct HTTP 403; labelled documentation-only workaround preserves reviewer file enumeration as UNVERIFIED and holds weights/archives. No patient-row audit or image acquisition. Root unittest: 5 PASS; git diff --check PASS. Starting M1 only; Python 3.12.3 venv created in ml/.venv, pinned M1 dependency installation underway. No protected edits, reviews, publishing, messages or pushes.

### 2026-10-09T13:05:05Z — M1 implementation and iteration completion

Implemented one milestone, M1: pinned Python src-layout project, strict versioned
JSONL schema/typed records, M0 taxonomy and exact provisional mappings, optional
full canonical observation superset, integrity/source/path/RGB interfaces,
supervised selection with explicit exclusions and patient/group/exact-hash split
validation before filtering. Fixtures are generated shapes only; synthetic labels
cannot claim clinical confirmation or real skin-tone annotation. ADR-006 accepted
in autopilot pending human review and queued; documented setup/data contract.

Installed toolchain dependencies only into ml/.venv using existing Python 3.12.3;
editable install succeeded and pip check reports no broken requirements. Pins
include the observed typing-extensions transitive dependency. Initial direct test
command mistakenly repeated ml/ inside the ml working directory (exit 127);
corrected command ran 78 tests PASS, then added missing-image/EXIF/multiframe and
missingness/tone cases. No failing test removed, skipped or weakened. One combined
documentation patch rejected duplicate operations on README and applied nothing;
corrected it as a single update.

Final scripts/check.sh: exit 0, 83 ML tests PASS, app SKIPPED, RESULT PASS. Root
unittest: 5 PASS; Builder-attested only, harness script unchanged. git diff --check
PASS. Wrote M1 HANDOFF and overwrote STATUS/NEXT_ACTION with REVIEW M1. No model,
training, clinical metric, parity, APK or future milestone completion claimed.
No protected edits, reviewer/check/gate writes, patient data, clinical image
acquisition, external messages, publishing or pushes. M0 cleanup commit a8e076a
precedes the M1 logical commit. Harness owns the next review and remote actions.

Final staged audit: 22 text/code files, no protected/data/image/weight paths;
NEXT_ACTION is exactly REVIEW M1. Final link/contract rerun after HANDOFF: 5 PASS.
Staged whitespace check caught one trailing blank line in new pyproject.toml
(earlier unstaged check did not include untracked files); removed it and reran
the staged whitespace check before commit.

## 2026-10-09T13:11:21Z — iteration

Read roadmap, status, harness, M1 HANDOFF/REVIEW-1/CHECK-1/GATE, AGENTS and ADRs in
order. M1 closed PASS WITH CHANGES. RESPONSE-1 answers all 14 numbered issues and
missed work/human questions. Fixed validation, loader, temporary-path ignores and
stale documentation; introduced explicit schema 1.1.0 (regenerate synthetic rows,
no automatic real-row migration). Queued clinical vocabulary/confirmation and M3
hash pins/pure-neural limitation. Added 27 behavioural cases: check.sh 110 ML PASS,
Android SKIPPED, RESULT PASS. Initial run 1 failed/109 passed due to policy ordering;
fixed code to reject unapproved source first, preserving the existing test. No
reviewer files or protected files edited. Starting M2 synthetic-only as ADR-002
requires; no acquisition attempts for held real datasets are authorised or needed.

### 2026-10-09T13:20:58Z — M2 implementation and iteration completion

Committed M1 follow-ups as 9610650, then implemented M2 only: procedural fixture
acquisition CLI with no network, licence-bearing unassigned/prepared manifests,
verified image decoding, source-scoped patient/group/global byte/decoded-pixel/
near-visual connected components, whole-component quarantine and deterministic
class-stratified frozen partitions with synthetic source C held out. Ordinary
manifest readers now reject active exact-byte diagnosis conflicts. Added explicit
M2 conflict/leakage/transitive/re-encoding/small-edit/quarantine/withdrawal/missing/
seed/source/policy/integrity/cohort/cap/reproduction/overwrite tests. ADR-007 records
schema 1.1.0, duplicate heuristic, synthetic splits and threshold fallback, pending
human review; HUMAN-QUEUE plainly says no approved suitable real task data.

Observed documented default CLI: 768 generated 64×64 RGB images/384 components,
all images verified/decoded, all eligible, licence/PLACEHOLDER metadata retained.
Split components: train150, calibration40, threshold-validation40, test26,
held-out128, balanced per target. Audit has 384 near-visual view pairs, no default
quarantine; adversarial cases tested separately. Second default run produced all
771 files byte-identical, including 2 manifests and report. Manifest checksum:
ff0e5d1749bf1f33fe64ac4234e7b788ea36e7db0996aa6c13208e76459911c4. All generated
runs remain ignored data/. No real dataset, model/weights/training/app acquired.

Final check.sh: exit0, 136 ML tests PASS, app SKIPPED, RESULT PASS. Root repository
suite 5 PASS (Builder-attested; protected check script unchanged). pip check: no
broken requirements. git diff --check PASS. No M2 implementation tests failed or
were weakened/skipped. No additional toolchain installed. Wrote HANDOFF, STATUS
and exact REVIEW M2 request. M3 must aggregate audit components, honour frozen
splits, and use ADR-001's unselected refer-all fallback (threshold validation only
20/class, not100/class). Synthetic metrics cannot establish clinical performance.

No protected edits, review.sh, REVIEW/CHECK/GATE writes, data/image/weight commits,
external messages, publishing or pushes. Harness owns review and gate closure.

Final staged audit: 17 builder code/text files, no protected/data/image/weight
paths; NEXT_ACTION exactly REVIEW M2. Staged whitespace check PASS. Final root
link/contract suite after HANDOFF/STATUS: 5 PASS. Commit: M2: prepare deterministic
PLACEHOLDER fixtures and source holdout.

## 2026-10-09T13:38:44Z — iteration

Read ROADMAP, STATUS, HARNESS, M2 HANDOFF/REVIEW-1/CHECK-1/GATE, AGENTS and
relevant ADRs in order. Harness has closed M2 PASS WITH CHANGES; advanced to M3
preparation and answered every M2 numbered issue in RESPONSE-1. No review requested.

Implemented shapes-v2 matched exact areas, overlapping contrast, intentional 0.10
Bernoulli group-level rendered-shape flips and stronger procedural source styles.
Synthetic target diagnoses/names are circle/square; colour strata derive from
actual pre-texture background luminance. Preparation 1.1.0 stratifies by complete
source membership × class, preserves whole linked components, reports source/class
counts and nearest pair across final distinct components. ADR-008 selects an explicit
30/20/40/10 selection_exercise profile within existing caps; default still exercises
insufficient-count fallback. Queued decision for human review. No model trained.

Added tests at RMS just below/exactly/above 2, unrelated group counts, full-size
threshold counts, same raster area, weak mean-intensity separation, colour provenance,
symlink-parent escape, installed-path/worktree root discovery and alternate holdouts.
Initial new subset run: 34 passed, 1 failed. The new root-discovery test erroneously
expected no checkout after deleting nested markers, although the valid outer Numbra
checkout remained. Fixed the test to verify correct ancestor discovery plus a separate
no-ancestor failure at filesystem root; production root discovery was already correct.
No existing test removed, skipped or weakened. Documented rationale in HUMAN-QUEUE.
Final preparation subset: 40 passed.

Observed check.sh exit 0: 150 ML tests passed in 13.90s; Android SKIPPED, RESULT PASS.
Root repository suite 5 passed; pip check no broken requirements. Initial diff check
caught a documentation trailing blank line, fixed; final git diff --check passed.
Default and larger generation completed with all hashes/decodes checked; no conflicts,
quarantine or unrelated-group merges. Default 384 components/768 images; larger
768/1536. Selection-exercise threshold 102/class and separate calibration 52/class;
default threshold 20/class. Source A/B balanced in each development partition/class.
Nearest unlinked RMS 8.586645/8.204261. Mean-intensity-threshold balanced accuracy
0.541667 on default generated groups only. No model/clinical performance claimed.
Default command repeated in new run: 771 generated files byte-identical, manifest
SHA-256 0a4adb62e625bed27271c42abbc8aef27bb28a05f5bd9ea018a14471738d7b58.
Larger manifest SHA-256 2d141bc62205d88b7116cbe410e9262a96d771dec34c30e88ae6ad9c4bee839e.

Updated docs/DEV-SETUP to place setup before final uncertainty sections; preserved
historical shapes-v1 evidence and clarified new commands. Updated README/data contract/
preparation docs and M2 HANDOFF with post-gate status. No real data/weights/downloads,
new toolchains, protected edits, review/check/gate writes, publishing or pushes.
M3 remains incomplete: next implement tested component evaluation, then verify CPU
dependencies/checkpoint permission and build reproducible transfer training/model card.
NEXT_ACTION CONTINUE; committing the logical fixture/evaluation-preparation step.

## 2026-10-09T13:50:03Z — iteration

Oriented from ROADMAP, STATUS, HARNESS, absent M3 review folder, AGENTS and relevant
ADRs. No new harness action; M0/M1/M2 gates remain closed. Worked only on M3's
carried component/evaluation step. No review requested; NEXT_ACTION CONTINUE.

Implemented evaluation.py with deterministic first-sorted-record index images
chosen before scoring, exact manifest/report coverage and checksum validation,
source/split/target checks, quarantine exclusion reasons and known patient/group/
byte-hash component consistency. One finite logit per active component is required;
views cannot inflate independent counts. Partial/conflicting colour labels remain
explicit. Evaluation trusts the existing decoded/near-visual preparation audit;
no real-data grouping claim or re-splitting.

Implemented bounded temperature scaling fit only on calibration with 20/class,
threshold fit only on threshold_validation with 100/class and separate sufficient
calibration, guarded unselected refer-all, primary sensitivity >=0.95 and secondary
specificity >=0.80 selection, inclusive ties and above-one all-negative sentinel.
Reports freeze settings for test/one held-out-source fold, retain fit score hashes,
exact two-sided 95% Clopper–Pearson intervals, tied AUC, Brier/stable loss/reliability/
ECE, unavailable metrics and source/synthetic-colour summaries. Selection intervals
are explicitly descriptive; fitted calibration is in-sample; every metric block
says PLACEHOLDER. ADR-009 records index/temperature/summary choices with required
Accepted (autopilot) — pending human review status; queued for humans.

Initial new suite observed 34 pass, 1 failure and 10 setup errors. New fixture used
8 groups below the existing generator's 16 minimum. Changed the new fixture to
16 and asserted its actual 48 components/96 rows. The new report exposed integer
Python keys where the test expected JSON string keys; changed production report
target names to explicit string keys. No existing tests deleted/skipped/weakened.
Final expanded evaluation suite: 58 passed in 5.11s. Tests cover independent class
count boundaries, wrong fitting splits, frozen test/holdout independence, known
linked-unit inflation, component/checksum/quarantine integrity, calibration optimum,
threshold ties/sentinel, exact closed-form binomial endpoints/interior, one-class/
empty/missing strata, tied AUC and stable extreme logits.

Observed scripts/check.sh exit 0: 208 ML tests passed in 18.94s, Android SKIPPED,
RESULT PASS. Root suite 5 passed (Builder-attested); pip check no broken requirements.
Existing default/larger shapes-v2 manifests passed index/checksum/partition checks:
384/768 active components, zero exclusions. Constant invented-logit mechanical
exercise: default 20 threshold groups/class yields unavailable unselected refer-all;
larger 102/class with separate 52/class calibration exercises selected primary
0.5 degenerate refer_all and selected secondary above-one degenerate all_negative.
No model was involved; these numbers are code paths, not model/clinical performance.
No generated report/image/manifest was tracked. README, setup and new evaluation
contract document completed primitives and outstanding work.

M3 still lacks training, pretrained/dependency permission/lock evidence, bootstrap
uncertainty, script-written model reports, full runtime provenance and model card.
Next verify/install hashed CPU dependencies/checkpoint access, then integrate the
reproducible frozen-feature baseline with this library. No new toolchain, patient
data/weights, protected edits, review.sh or reviewer/check/gate writes, publication,
messages or pushes. Final diff/status validation precedes the logical-step commit.
