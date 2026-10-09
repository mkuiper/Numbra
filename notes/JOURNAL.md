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

## 2026-10-09T14:11:27Z — iteration

- Oriented roadmap -> STATUS -> HARNESS -> absent M3 review folder -> AGENTS/ADRs;
  M3 only. No new harness blockers. Read M2 closed-review follow-through.
- Firecrawl skill applied for selected-checkpoint/toolchain verification; status
  still zero credits, reused recorded web/direct-anonymous-HTTP workaround.
  Publisher public/ungated revision/card licence checked; anonymous safetensors
  acquisition succeeded, matched pinned size/SHA-256. No account/agreement or
  ImageNet/patient images. README/config/weights and wheels ignored under data/.
- Added full 35-wheel runtime/test/build CPython 3.12 Linux x86_64 hash lock.
  Initial resolver chose hub 2.2.0; pinned hub 0.36.0 before installation for timm
  compatibility. All 35 wheels force-reinstalled with require-hashes, including
  M1 packages. CPU torch 2.8.0+cpu / torchvision 0.23.0+cpu / timm 1.0.22 /
  safetensors 0.6.2. Setup commands documented. No JDK/SDK/system installs.
- Implemented pinned offline frozen-backbone extraction, train-only scaling and
  fixed linear-head AdamW; deterministic explicit letterbox preprocessing;
  nonfinite/checksum/state/output guards; aggregate JSON/model-card generation
  and per-component prediction/combined-model files confined to ignored data/.
  Added fixed-score ordinary whole-component bootstrap with independent cohort
  seeds, tied AUC and valid-replicate/unavailable reporting. No fit uncertainty.
- ADR-010 records autonomous training/geometry/bootstrap/platform decisions with
  required status; queued it and poor synthetic generalisation for humans.
  Committed logical implementation step fd93e34 before actual baseline runs.
- Observed new subset 45 PASS in 6.38s; additional generated-fixture-to-report test
  included in full check: 254 PASS in 25.74s initially and **254 PASS in 25.67s**
  final; check.sh exit 0, Android SKIPPED, RESULT PASS. No ML failures/skips/xfails.
  Root suite initially failed four missing setup URL source-register entries;
  fixed bookkeeping (no new clinical survey), then 5 PASS; final root run
  5 PASS in 0.127s. No existing tests changed/skipped/weakened. pip check clean.
- Baseline 10.663s / repeat 10.605s, same desktop two-thread environment.
  Byte hashes/model weights/predictions and all evaluation fields identical after
  excluding declared dynamic provenance (created_utc/elapsed_seconds/git_dirty/
  output_directory). Model 6,156,620 bytes float safetensors, ignored, not M4 export.
  Strict real saved-model reload state hashes PASS; all 768 raw logits reproduced
  exactly. Current source/lock hashes match archived provenance.
- Baseline calibration 52/class T=19.150006, selection 102/class threshold
  0.4007988174, 97/102 sensitivity, exact interval [0.889304,0.983894], empirical
  target only. Test TP/FN/TN/FP=26/0/4/22, sensitivity1/specificity0.153846,
  AUC0.766272. C=117/11/10/118, sensitivity0.914063/specificity0.078125,
  AUC0.592529. C misses illustrative0.95 target; no frozen-input/default tuning.
  Training loss0.721871->0.002350 demonstrates overfit artificial head. All
  outputs PLACEHOLDER, synthetic circle/square, colour bands and one held-out fold.
- Default run 5.661s: calibration20/class fitted, threshold20/class insufficient,
  both endpoints unavailable/unselected refer-all0; sensitivity1/specificity0
  describe fallback. Zero exclusions both fixtures. Synthetic-only/no clinical
  claim preserved; metrics/provenance/model cards committed as aggregate reports.
- Wrote M3 HANDOFF/STATUS, requested REVIEW M3. No M3 gate/reviewer result yet.
  No protected edits, review.sh/REVIEW/CHECK/GATE writes, tracked data/weights,
  messages/publishing/pushes or app/APK. Final whitespace/link/tracked-file checks
  performed before final commit. Next iteration responds to harness M3 review.

## 2026-10-09T14:29:21Z — iteration

- Oriented in required order; harness M3 GATE is PASS WITH CHANGES. Read all of
  REVIEW-1, CHECK-1, HANDOFF, gate, AGENTS and relevant ADRs. No review.sh run.
- Fixed inexpensive M3 follow-ups and wrote RESPONSE-1 for every numbered issue.
  Explicit toy backbone supplier lets train_run execute end to end in tests of
  record without external weights/network/mocks; test covers three ignored
  artifacts, aggregate report/card, provenance, overwrite and tamper safeguards.
  Added numbra_ml.verify to strictly reload full bundled Baseline with checksum,
  preprocessing, state-hash, preparation and component-metadata checks; rescores
  in original feature batches with 1e-5 raw tolerance and zero decision flips.
- Actual verifier baseline/reproduction/default: 768/768/384 components; all raw
  and calibrated max differences **0**, threshold flips **0**. Models unchanged;
  original pretrained checkpoint/network not required for bundled reload.
- Reporting evaluation v1.1.0 nulls pre-calibration threshold metrics, flags
  source/colour small cells and suppresses AUC/calibration/bins/bootstrap below
  20/class; identical bootstrap component sets reuse results/seeds. Cards expose
  empirical-only evidence, exact intervals/counts, below-target held-out wording
  and per-row fallback markers; rounded display, full-precision JSON. Rebuilt
  all three tracked aggregates/cards from checksum-verified ignored predictions.
  Preserved original training provenance/parameters, added reporting source and
  original report hashes; ignored original run JSON stays historical.
- CLI learning-rate/weight-decay switches added; guard test checks stderr. Amended
  ADR-010/queued real-data model-selection split/nested CV, independent privacy
  controls and stricter M4 parity. Deferred optional clean-checkout wrapper (11)
  and relevant human questions; explicit setup then single offline train remains.
- M3 targeted 108 PASS in 12.88s, reference subset 36 PASS in 8.17s; full check
  258 PASS in 27.36s, Android SKIPPED, RESULT PASS. Committed logical M3 step
  d0e594f. No fitted outputs/input tuning or relaxed existing tests.
- Started M4 foundation: ADR-011 predeclares float max errors 1e-4 raw/1e-6
  probability, quantised 0.1 raw/0.001 probability, zero frozen-threshold flips
  and separate conservative 0.001 margin accounting. Added tested parity reporter
  with independent budget checks, all failed components, directional flips,
  margin-added/lost referrals, finite/matched/unique/float32-range guards.
  Failure cases must remain ignored; no export/quantisation experiment attempted.
- Wrote ML-EXPORT.md full preprocessing/planned interface, reference commands,
  actual scope and remaining work; DEV-SETUP records no new installs. No ONNX
  runtime/conversion dependency, quantised graph, app or APK claimed.
- Initial new parity test was wrong about underflow at ±1e4/T19.15 (1.64e-227 is
  representable). Corrected the invented fixture to ±1e6, retaining the same exact
  expected assertion; 29 PASS/1 failure became 30 PASS in 1.92s. No production
  test weakened/skipped. Initial reporting rebuild guessed a wrong default report
  name after successfully rebuilding two; used actual default name for the third.
  Initial default verification similarly used wrong run suffix; corrected to saved
  provenance directory and then obtained exact PASS. All failures resolved.
- Full check before extra range guards 288 PASS in 27.09s; final check after them
  **290 ML tests PASS in 27.13s**, exit 0, Android SKIPPED, RESULT PASS.
  Root contract suite 5 PASS in 0.104s (not in protected tests of record), pip check
  clean, whitespace clean. No new research/network/toolchain acquisition.
- Updated STATUS, appended JOURNAL and set NEXT_ACTION CONTINUE for M4 dependency
  verification/pinning then float/static-INT8 export under fixed budgets. M4 not
  ready for review; M0–M3 gates closed. No protected files, review.sh/REVIEW/CHECK/
  GATE writes, committed data/weights/secrets, publishing/messages/pushes.

## 2026-10-09T14:50:43Z — iteration

Worked only on M4 after ordered roadmap/status/harness/review-folder (absent)/
AGENTS/ADR orientation. No new harness message. Installed ONNX 1.19.1 and ORT
1.23.2 plus transitive pins in ml/.venv; hash-locked seven additions, unchanged
35-package CPU lock, 42 unique packages total. Initial pip download with hashed
constraints failed because new requirements lacked hashes; resolved with ignored
unhashed existing-version constraints, generated wheel METADATA/SHA-256 lock,
then installed hashes offline. Initial duplicate typing name alias had identical
version/hash; removed duplicate, retain historical experiment lock hashes and
reconstruction instructions. Editable install/pip check succeeded. Toolchain
commands in DEV-SETUP. Firecrawl scrape failed at zero credits; reused labelled
web-tool fallback for official PyTorch/ONNX Runtime docs, no auth changes.

Built numbra_ml.export: strict saved-reference/environment verification, confined
new PLACEHOLDER outputs, fixed 1×3×224×224 float32 opset-17 ONNX, static QDQ INT8,
all/only 152 train images for MinMax calibration, graph size/operator audit,
same-single-tensor raw/probability/threshold parity on 768 components and 14 fixed
independent stress inputs, separate 308 frozen test/held-out comparison, margin
accounting and exported metrics at frozen M3 fits. Per-component logits/failures
and weights stay ignored. Aggregate summary validates original run/preparation,
graph hashes/ordered logits and parity; reporting revision rebuilds source/colour
aggregates from saved logits (corrects first prototype grouping), no inference or
refitting. Reports also disclose original saved-batch vs single-image Python raw
max difference 0.000383378, zero flips. Original-batch saved verification exact.

Two genuine predeclared experiments executed: per-tensor then per-channel INT8
weights. Both CLIs and summary CLIs exit 1/FAIL, no false test-pass claim. Float
6,095,579 bytes, identical graph: test/held-out max raw/probability errors
0.000272334/0.00000355427, zero flips, exceeds both fixed budgets. Per-tensor INT8
1,730,515 bytes: 50.784990/0.506519, 26 test/held-out flips; per-channel 1,861,702:
62.403598/0.612635, 28 flips. All-component/stress parity also fails. INT8 graphs
have 53 Conv/one Gemm with INT8 QDQ weights; remaining float operators reported.
Per-channel source-C sensitivity 1.0/specificity 0.0 demonstrates changed scores,
not better screening. Sizes pass ≤20 MB; numerical acceptance remains blocked.
No budgets, frozen inputs/fits, selected baseline or training changed.

ADR-012 and HUMAN-QUEUE document **PLACEHOLDER labelled workaround — generated
toy-model diagnostic export only** after two failures. Retain rejected baseline
artifacts and continue training-only precision/operator diagnostics; toy evidence
cannot close M4 or replace the selected reference. No review request/HANDOFF until
acceptance. Source/command/evidence docs updated; M5 remains unstarted.

Tests: initial new export subset 11 PASS/2 FAIL. One expected 42 dependencies but
lock duplicated typing alias; fixed lock rather than changing expected count.
Other assumed pooled untrained toy would meet float budgets; actual runtime
rounding disproved it. Retained that fixture as a FAIL regression and retained
strict PASS assertion with independent centre-pixel toy; no tolerance widening.
Final export subset 14 PASS in 6.85s, including generated preparation→toy training→
strict save/restore→actual ONNX/INT8 runtime→summary path, tamper/unsafe/overwrite
rejection. Full bash scripts/check.sh exit 0: 304 PASS in 32.09s, six upstream
legacy-export deprecation warnings; Android SKIPPED, RESULT PASS, no APK.

Additional root contract suite initially failed (four upstream Privacy.md links
in ignored installed ORT and missing new PyTorch documentation source). Disputed
checker scope documented in HUMAN-QUEUE; git tracked/nonignored untracked
markdown discovery corrects Builder ownership, regression explicitly retains new
Builder documents while excluding ignored third-party files. No Builder
link/citation assertion removed; source-register entry added. Final root suite
6 PASS in 0.070s. pip check no broken requirements; git diff --check clean before
records. Model/individual output files remain ignored; no protected file edit,
review invocation, patient data, push, publication or external messages.

Next: original-baseline float runtime/fusion and INT8 activation/weight precision
diagnostics on training inputs; predeclare next graph strategy, preserve all
failures and original budgets. NEXT_ACTION CONTINUE. Commit iteration records
and all Builder changes before finishing.

## 2026-10-09T15:02:55Z — iteration

Current milestone M4; M0–M3 gates already exist. Read ROADMAP, STATUS, HARNESS,
confirmed no M4 review folder, then AGENTS and relevant ADRs. No new harness
message or review to answer. Both original baseline exports remain rejected.

Added ADR-013 (Accepted (autopilot) — pending human review) and HUMAN-QUEUE entry
before running new training-only export diagnostics. Added explicit validated
ORT disabled/basic/extended/all session options while preserving the existing
all/default runtime behavior. New numbra_ml.export_diagnostics verifies retained
experiment/model/preparation/graph hashes and installed lock versions; uses every
training component index image and no non-training/stress pixels; deduplicates
identical float graphs, retaining both source-report hashes. Separate diagnostic
copies expose features at the saved head boundary, carry PLACEHOLDER/never-bundle
metadata and fail the strict deployment interface. Original and instrumented
graphs run independently to expose instrumentation-induced changes. Full outputs,
feature attribution and graph copies remain ignored data/; aggregates alone tracked.

Observed command:
ml/.venv/bin/python -m numbra_ml.export_diagnostics --output data/exports/PLACEHOLDER-m4-diagnostics1
returned 0 and generated ml/reports/PLACEHOLDER-m4-diagnostics1.json, explicitly
DIAGNOSTIC ONLY. All 152 training components × three original graphs × four ORT
profiles fail original ADR-011 budgets. Float/all max raw/probability error
0.000323295593/0.00000411753037; disabled/basic/extended each
0.000365257263/0.00000465195989; zero flips. Every per-tensor INT8 profile has
59.8606148/0.6444904 errors and 32 flips; every per-channel profile
82.7891731/0.7874631 and 36 flips. This is training evidence, distinct from the
retained frozen-test/held-out reports. No fits/inputs/reference execution changed.

Float/all maximum feature error 0.0000212192535 induces saved-Python-head error
0.000322341919; remaining head/runtime discrepancy max 0.0000114440918. Effective
head coefficient max 59.6626235, L1 sum 1,362.464654. Evidence points mainly to
feature drift amplified by head scaling, not yet to a particular backbone operator.
Maxima can belong to different components; no exact worst-case sum claimed.
INT8 has substantial feature and head-path discrepancy. Instrumentation logit
change is exactly zero for every measured graph/profile; broader equivalence
unverified. Runtime optimisation changes alone do not resolve parity.

Local inspection: saved Python backbone contains 34 BatchNorm2d modules; retained
float ONNX has no BatchNormalization nodes after folding. Next concrete strategy
is to predeclare and test a BatchNorm-preserving export, verify actual graph nodes,
prevent runtime re-fusion, and measure training-only first. This is a hypothesis,
not an observed remedy. Keep original saved model/fits/budgets and declare
quantised/mixed-precision operator scope before the next frozen evaluation.
ADR-012's generated toy-model workaround remains diagnostic-only. No M4 review
request/HANDOFF or deployment model approval; NEXT_ACTION overwritten CONTINUE.

Verification observed:
- New diagnostic subset: 8 PASS in 5.92s, 12 legacy-export warnings. Tests include
  corrupting all non-training image bytes, source-graph immutability, graph/fit
  tamper rejection before output creation, explicit runtime profiles, affine
  bound/signed-effect arithmetic, input validation and instrumented-graph rejection.
- bash scripts/check.sh: exit 0; 312 ML tests PASS in 35.90s, 18 legacy-export
  deprecation warnings; Android SKIPPED (no app/gradlew), RESULT PASS. No APK claim.
- Root contract suite: initial 6 PASS in 0.062s; final after documentation updates
  6 PASS in 0.071s. Builder links and source register remain valid.
- git diff --check clean before final records; staged verification before commit.
  No tests failed, skipped or weakened by Builder. One initial notes patch was
  rejected for duplicate target operations before any file changed; corrected
  using explicit repository-local file writes.

Updated ML-EXPORT, DEV-SETUP, ml/README and ADR-013 with observed results and
interpretation limits. STATUS overwritten, JOURNAL appended and NEXT_ACTION
CONTINUE. No new dependency/toolchain/dataset/checkpoint acquisition; existing
42-package export lock unchanged. No patient data, weights or graph copies in git;
no protected edits, review.sh run, publishing, push or messages. Baseline parity,
clinical data/validation, weight notices and mobile execution remain open.

## 2026-10-09T15:18:10Z — iteration

- Oriented in required order: ROADMAP, STATUS, HARNESS, absent M4 review folder,
  AGENTS and relevant ADRs. No new harness message; M4 still incomplete.
- Predeclared ADR-014 and queued human review before executing the new graph
  experiment. Added BatchNorm-preserving export and optional actual ORT graph
  serialization/audit; retained original strict runtime interface and budgets.
- Exported same saved selected baseline with folding disabled and eval PRESERVE.
  Verified 34 inference BN nodes in export and disabled sessions, zero with all
  optimisation; fresh unmarked folded control matches retained graph bytes.
  Saved model state is unchanged. No new quantisation fitting or frozen/stress
  inference, retraining, weight acquisition, fit/preprocessing/budget change.
- First new suite 4 PASS (5.69s). First diagnostic command exit 0 generated only
  diagnostic evidence. Inspection caught a Builder error: combined timm BN/act
  Python outputs were post-activation while ONNX BN taps were pre-activation.
  First tracked report's boundary attribution explicitly marked INVALID, with
  erratum and original-report hash; ignored original report/details retained.
  Original-graph parity/head-feature evidence unaffected. Corrected pre-hooks at
  drop input, copied before in-place activation; added negative-input ReLU and
  HardSwish regression tests. Expanded suite 6 PASS (5.85s, 16 warnings).
- Corrected rerun: ml/reports/PLACEHOLDER-m4-batchnorm2.json, all 152 training
  components, DIAGNOSTIC ONLY exit 0. Preserved/disabled max raw/probability drift
  0.000240326/0.00000279320, still FAIL (26/29 violations) and zero flips. Folded/
  disabled 0.000365257/0.00000465196, 40/50 violations; both all profiles
  0.000323296/0.00000411753, 36/44 violations. Preserved graph 6,188,494 bytes.
- All 87 corrected boundaries included: 53 Conv, 34 BN. Stem Conv drift reaches
  0.000000476837, stem BN 0.00000667572, first depthwise Conv 0.000000953674, its
  BN 0.0000457764. Original/instrumented logits match on training inputs. These
  are accumulated graph differences, not isolated local arithmetic. Same-input
  kernel replay is the next declared diagnostic step. No deployed graph chosen.
- Checked corrected aggregate's source/model/run/graph/detail hashes against
  current files. Updated ML-EXPORT, ML README, DEV-SETUP, ADR-014 and HUMAN-QUEUE;
  recorded the diagnostic error, correction, measured failures and limitations.
- bash scripts/check.sh exit 0: 318 ML tests PASS in 39.53s, 34 legacy exporter
  deprecation warnings; Android SKIPPED, RESULT PASS. Root contract checks 6 PASS
  in 0.064s; git diff --check clean. No existing test skipped/weakened. ORT warns
  that all-profile serialized graphs can be hardware-specific; diagnostic copies
  are labelled never bundle. No JDK/SDK/dependency/checkpoint/dataset acquisition.
- M4 remains open, no HANDOFF/review request or APK. ADR-012 labelled toy pipeline
  workaround remains in force. NEXT_ACTION CONTINUE. No protected files edited,
  reviews/tests-of-record logs/gates written, publishing, pushing or messaging.

## 2026-10-09T15:30:37Z — iteration

- Oriented in required order: ROADMAP, STATUS, HARNESS, absent M4 review folder,
  AGENTS and relevant ADRs. No new harness message. Worked only on open M4.
- Predeclared ADR-015 and queued human review before executing same-input
  stem/first depthwise Conv/BN replay. Added numbra_ml.export_replay with strict
  saved/preparation/retained/preserved provenance, fixed layer selection, copied
  Python/ONNX inputs and raw pre-activation outputs, hook cleanup, exact operator
  extraction, actual runtime graph audits and three fixed primitive BN formulas.
- First subset: 5 PASS, 1 FAIL in 5.59s. Builder provenance code incorrectly
  required boundary diagnostics for a passing toy graph; ADR-014 creates taps
  only on failure. Fixed guard to permit legitimate absence when all profiles
  pass, require valid evidence on failed profiles and always reject explicitly
  invalid evidence. Tests unchanged; no disputed/weakened assertion. Next subset
  6 PASS in 5.99s, 16 warnings. Added invalid-boundary/swapped-graph rejection
  branches to the same fixture before the full suite.
- Replay command exit 0: DIAGNOSTIC ONLY. Tracked aggregate
  ml/reports/PLACEHOLDER-m4-replay1.json, all 152 existing training components,
  no frozen test/held-out/stress inference or quantisation fitting. Original
  model/fits/inputs/budgets preserved; saved state hashes before/after match.
- Python and ONNX replay fidelity, original/instrumented logits and signed
  telescoping residuals are zero. Same-input local kernel maxima: stem Conv
  0.000000476837, stem BN 0.000000953674, first depthwise Conv 0.000000119209,
  its BN 0.00000762939. Propagated maxima respectively 0, 0.00000667572,
  0.000000953674, 0.0000457764. Maxima may occur on different components/elements
  and cannot be added as an exact worst-case decomposition. This narrows local
  propagation/arithmetic; no full-backbone causal or model improvement claim.
- Each predeclared BN primitive formula exactly matches its Python equivalent,
  but none matches native Python BN exactly. Rounded float64 formula also
  differs. No graph/deployment selected; next declare promoted stem accumulation
  and fused-affine BN emulation, retaining native saved float32 reference.
- Independently checked aggregate source/graph/runtime/private-detail hashes
  and equality of tracked/private aggregate reports. Updated ML-EXPORT, ML README,
  DEV-SETUP, ADR-015 and HUMAN-QUEUE. Original failed experiments remain intact;
  graphs/weights and component evidence are ignored, not committed.
- bash scripts/check.sh exit 0: 324 ML tests PASS in 43.92s, 50 exporter
  deprecation warnings; Android SKIPPED, RESULT PASS. Root repository checks
  6 PASS in 0.066s before final docs/records. No existing test skipped/weakened.
- M4 remains open, no HANDOFF/review request or APK. ADR-012 labelled toy pipeline
  workaround remains in force; NEXT_ACTION CONTINUE. No toolchain/dependency,
  checkpoint or dataset acquisition; no protected edits, review.sh invocation,
  REVIEW/CHECK/GATE files written, publishing, pushing or messaging.
- Final repository-contract rerun after docs/records: 6 PASS in 0.065s. Saved model/run, preparation and both dependency-lock hashes match the aggregate; NEXT_ACTION contract verified. git diff --check clean.

## 2026-10-09T15:40:15Z — iteration

- Oriented in required order: roadmap, STATUS, HARNESS, current M4 review folder
  (absent), AGENTS and relevant ADRs. No new harness messages or M4 review/gate.
  M0–M3 gates closed; worked only on M4 and retained ADR-012's labelled toy
  diagnostic workaround. No delegation or human question.
- Predeclared ADR-016 (Accepted (autopilot) — pending human review), queued it,
  and built promoted operator arithmetic. Reused ADR-015 provenance/input/replay
  guards, native saved Python reference and exact float32 parameter bits.
  First stem Conv uses explicit zero Pad/strided-dilated patch extraction,
  float64 MatMul and bias, one float32 boundary cast. Both BNs use two existing
  float32 affine coefficient recipes and promoted multiply/add/float32 cast.
  Actual disabled ORT graphs audited; original profile/thread settings unchanged.
- Tests independently check convolution ordering, border zeros, stride/dilation,
  non-square geometry, bias, rejected unsupported geometry/inputs, saved weight
  bits, affine cancellation versus unfused float32, both origins, pre-activation
  replay and hook cleanup. Existing end-to-end replay/provenance fixture now also
  runs promoted mode with deliberately corrupt non-training pixels; only training
  is read, saved inputs/graphs remain unchanged, output details stay private.
- First subset: 15 PASS in 10.63s, 24 exporter warnings plus test-only scalar/
  autograd warning. Added detach to the test scalar; full suite has only exporter
  warnings. No failure, skipped/deleted/weakened test or tolerance change.
- Promoted CLI exit 0: DIAGNOSTIC ONLY, all 152 training inputs and no frozen
  evaluation/quantisation fit/deployment selection. Tracked aggregate:
  ml/reports/PLACEHOLDER-m4-precision1.json. All promoted ONNX/Python expressions
  agree exactly on both origins; native Python differences remain. Stem Conv max
  0.000000476837 (same maximum as native ORT); stem BN rsqrt-affine
  0.0000000596046 versus native ORT 0.000000953674. Stem divide max
  0.000000178814. First depthwise BN max 0.00000381470 / 0.00000762939 on Python/
  ORT origins with either recipe. Local improvements do not imply propagated or
  complete-model improvement; no expression exactly recovers native Python.
- Original/tapped logits, replay-fidelity errors and signed residuals are zero;
  before/after state hashes match. Checksum audit first used an assumed .pt path
  and failed FileNotFoundError; corrected the audit command to the actual
  PLACEHOLDER-model.safetensors and passed. Aggregate/private equality,
  source/lock/preparation/saved-model provenance, details and 33 graph records
  verified. No implementation/model change for this audit typo.
- Updated ML-EXPORT, ML README, DEV-SETUP, ADR-016 and HUMAN-QUEUE. Graphs, weights,
  tensors and ordered component details stay ignored. Existing failed exports,
  fits/reference/preprocessing and ADR-011 budgets unchanged.
- bash scripts/check.sh exit 0: 333 ML tests PASS in 48.97s, 58 legacy exporter
  deprecation warnings; Android SKIPPED, RESULT PASS. Root repository suite
  6 PASS in 0.066s before final docs/records. No APK or M4 completion claim.
- Next predeclare complete preserved-graph promoted rsqrt-BN substitution on
  training components with original Conv/head and float32 boundaries, then choose
  explicitly declared selective static QDQ scope before any frozen evaluation.
  Mobile float64 compatibility remains unresolved. NEXT_ACTION CONTINUE; no
  HANDOFF/review request. No installs/acquisition, protected edits, review.sh,
  REVIEW/CHECK/GATE writes, publication/push or messages.
- Final repository-contract rerun after docs/records: 6 PASS in 0.068s. git diff --check clean; NEXT_ACTION is exactly CONTINUE. All generated data/graphs remain ignored.

## 2026-10-09T15:49:45Z — iteration

- Oriented in required order: ROADMAP, STATUS, HARNESS, absent M4 review folder,
  AGENTS and relevant export/runtime ADRs. M0–M3 gates remain closed; no new
  harness instructions. Worked on M4 only; no delegation or human question.
- Predeclared ADR-017 (Accepted (autopilot) — pending human review), queued it
  and committed the protocol as 3056350 before experiment execution. Initial
  atomic ADR/queue patch rejected a mismatched queue heading; reread and applied
  the corrected patch, with no partial edits.
- Built numbra_ml.export_promoted_bn: verify source/model/preparation/retained
  graph/report/detail provenance; validate saved BN weights/bias/mean/variance/
  epsilon; replace all 34 BNs with existing promoted rsqrt-affine expressions.
  Exact rounded float32 coefficients, double multiply/add, one float32 stage
  output cast. Every other serialized node/initializer/interface retained.
  Native saved Python reference, Conv/head/activation/fits and budgets unchanged.
- Tests cover whole-graph connections and independent arithmetic through both
  BN/timm activations, parameter/source/state retention, actual runtime audits,
  corrupted coefficient/cast/expression/Conv, invalid epsilon/parameter/extra
  BN/training/collision/nonfinite input, ignored outputs, stale provenance and
  complete synthetic pipeline. Non-training pixel bytes deliberately corrupted
  after preparation: complete diagnostics read only training images.
- Initial subset: 11 PASS, 1 FAIL in 6.17s with 28 exporter warnings. Extra BN
  was rejected correctly by saved parameter matching, but node-count validation
  occurred too late for the declared guard. Moved production count check before
  matching; unchanged test passes. Corrected subset: 12 PASS in 6.15s with 28
  warnings. No test removed/skipped/weakened or budget changed. Committed tested
  implementation as 7fbfdff before the complete baseline experiment.
- Diagnostic command exit 0, DIAGNOSTIC ONLY: all 152 ordered training components,
  preserved control and full BN substitute. Tracked aggregate:
  ml/reports/PLACEHOLDER-m4-promoted-bn1.json. No frozen evaluation, quantisation
  fit, deployment selection or acquisition. All graphs/weights/details ignored.
- Both comparisons FAIL. Preserved control reproduces raw/probability maxima
  0.000240326/0.00000279320. Complete substitute lowers them to
  0.000189304/0.00000240022, still above unchanged 0.0001/0.000001 budgets.
  Mean raw/probability errors increase 0.0000558684/0.000000653101 to
  0.0000575436/0.000000667205. Raw violations 26→23; probability violations
  29→32; flips and instrumentation logit changes zero in both graphs.
  Maximum feature drift increases, induced Python-head maximum decreases;
  these are diagnostic statistics, not proof of causal improvement or deployment.
- New serialized candidate 6,255,113 bytes; actual runtime 6,156,135. It is
  float32/float64, not quantised. Actual disabled ORT original/tapped audits
  verify all 204 expression nodes/136 casts/coefficient bits/float32 boundaries
  and 53 Conv/one Gemm counts. ORT reports unused original BN initializer removal
  and expands HardSwish even when optimisation disabled; full runtime identity
  of all other nodes is not asserted. Source/model state unchanged.
- Independent audit PASS: tracked/private report equality, recomputed private and
  aggregate parity, 152 ordered training IDs/hash, model/source/lock/preparation
  provenance and nine graph records. data/ ignored and no tracked data files.
- Updated ADR-017 observed evidence, HUMAN-QUEUE, ML-EXPORT, DEV-SETUP and ML README.
  M4 remains incomplete; ADR-012's labelled toy diagnostic workaround remains
  in force. No HANDOFF/review request; NEXT_ACTION CONTINUE. Next declare joint
  promoted stem/all-BN graph on training only; improvement uncertain. Explicit
  quantised scope and float64 mobile compatibility remain unresolved.
- bash scripts/check.sh exit 0: 345 ML tests PASS in 52.62s, 86 exporter
  deprecation warnings; Android SKIPPED, RESULT PASS. No APK claim. No installs,
  protected edits, review.sh, REVIEW/CHECK/GATE writes, publishing/push or messages.
- Final repository-contract rerun after documentation/records: 6 PASS in 0.077s.
  git diff --check clean; NEXT_ACTION exactly CONTINUE. No protected/data files
  changed or staged. All iteration changes committed before ending.

## 2026-10-09T15:59:42Z — iteration

- Oriented in required order: ROADMAP, STATUS, HARNESS, absent reviews/M4 folder,
  AGENTS and relevant runtime/training/export ADRs. No new harness intervention;
  M0–M3 gates exist, M4 still open. Clean starting worktree.
- Predeclared ADR-018 and HUMAN-QUEUE; committed 75c442d before implementation/
  experiment. Joint stem/all-BN diagnostic on training only; unchanged saved
  model/reference/fits/inputs/budgets. No new quantisation scope or frozen run.
- Implemented export_joint and composed guarded ADR-017 runner. Stem validates
  saved float32 parameters/geometry/input connection before embedding ADR-016's
  double patch/MatMul with one float32 boundary. All BN expressions and other
  serialized nodes/constants/interface retained. Actual runtime audits enforce
  exact expressions/constant bits and 52 Conv/one MatMul/one Gemm counts.
- Added synthetic multi-pixel border/channel arithmetic through both timm
  in-place activations, corruption guards for saved geometry/weights/connection/
  namespace/eval state and expression casts/constants/patch geometry/Reshape/
  Conv counts/other-node retention. End-to-end diagnostic test corrupts all
  non-training pixel bytes and checks unchanged inputs/state, private outputs,
  three controls, complete training IDs and stale-provenance rejection.
- Initial subset 22 PASS / 2 FAIL in 9.75s (56 warnings): BN substitution reused
  all-Conv matching after stem replacement. Fixed production to independently
  validate every saved BN boundary, retaining all parameter/count assertions.
  Second subset 22 PASS / 2 FAIL in 10.09s (56 warnings): exact runtime audit
  found ORT adding Reshape default allowzero=0. Explicitly declared the default
  in the composed expression, retaining exact node-byte checks and adding a
  corruption regression. No test deleted/skipped/weakened. Corrected subset:
  25 PASS in 10.19s, 58 exporter warnings. Committed d71bf32 before experiment.
- Diagnostic CLI exit 0, DIAGNOSTIC ONLY. All 152 ordered training inputs and
  preserved/BN-only/joint controls; report ml/reports/PLACEHOLDER-m4-joint1.json.
  No frozen test/held-out/stress inference, fit, selection or acquisition.
- Both controls exactly reproduce retained graph hashes and diagnostic
  aggregates. Joint still FAILS: raw/probability maxima
  0.000200748/0.00000256741 versus fixed 0.0001/0.000001, 25/32 violations,
  zero flips. BN-only maxima 0.000189304/0.00000240022 are smaller; joint means
  0.0000554888/0.000000648783 are lower. Mixed statistics do not imply passing
  parity or causal improvement. All earlier failures remain rejected.
- Joint serialized size 6,265,822 bytes (runtime 6,165,050); float32/float64,
  no INT8 weights. Exact stem/all-BN runtime audits PASS; ORT removes unused
  original initializers and expands HardSwish even at disabled optimisation.
  Other runtime-node byte identity is not claimed. Original/tapped logits equal,
  saved-state hashes unchanged. Feature/head maxima reported separately.
- Independent audit PASS: tracked/private equality, recomputed private/aggregate
  parity, 152 ordered training IDs/hash, model/source/locks/dependencies/
  preparation provenance, both prior controls and 14 graph records. No additional
  inference. Models/graphs/weights/individual details/logs stay ignored in data/.
- Updated ADR-018 follow-through, HUMAN-QUEUE, ML-EXPORT, DEV-SETUP and ML README.
  M4 incomplete; ADR-012 labelled toy workaround remains diagnostic only.
  NEXT_ACTION CONTINUE, no HANDOFF/review request. Next predeclare complete
  same-input Conv/BN replay before further graph substitutions; quantised scope
  and mobile float64 compatibility remain unresolved.
- bash scripts/check.sh exit 0: 358 ML tests PASS in 56.27s, 116 legacy-export
  warnings; Android SKIPPED, RESULT PASS. Root checks 6 PASS in 0.078s after
  documentation changes; final root check 6 PASS in 0.074s after iteration
  records. git diff --check clean. No APK/completion claim.
- No toolchain/dependency/acquisition changes, protected edits, review.sh,
  REVIEW/CHECK/GATE writes, publishing/push or external messages. All changes
  committed before ending.

## 2026-10-09T16:16:35Z — iteration

- Oriented in required order: ROADMAP, STATUS, HARNESS, absent M4 review folder,
  AGENTS, relevant M4/data/runtime ADRs. No new harness instruction or M4 review.
  Worked only on M4; all baseline exports remain rejected, no app or gate claim.
- Predeclared ADR-019, queued humans and committed 0858a72 before experiments.
  Implemented complete guarded same-input replay for every saved Conv/BN,
  native saved-bit/geometry audits, both promoted BN runtime expression audits,
  four-term signed accounting and full aggregate/detail/graph/source auditing.
  Old two-pair replay/precision behavior retained. Added generated fixtures for
  grouped Conv, Conv without following BN, plain/in-place timm BN, signed-zero
  parameter corruption, node ambiguity, partial recipes, runtime corruption,
  cancellation, hook cleanup, training-image isolation and stale provenance.
- Initial subset 32 PASS / 1 FAIL in 15.24s (52 warnings): duplicate graph
  correctly refused by existing boundary matcher, but error lacked new
  one-to-one scope wording. Added production scope context, retaining exact
  test assertion. Corrected combined subset 33 PASS in 16.07s, 52 warnings.
  After audit/refusal additions, complete-only subset 19 PASS in 7.05s,
  28 warnings. No test weakened/skipped/deleted. Committed aabfb06 before run.
- Diagnostic CLI exit 0: all and only 152 ordered training component inputs,
  every 53 Conv/34 BN, 517 graph records. Report
  ml/reports/PLACEHOLDER-m4-complete-replay1.json. No frozen test/held-out/stress
  inference, quantisation fit, reference/model/budget change or deployment.
- Native/promoted serialized/runtime audits PASS. Python/ORT replay fidelity,
  original/tapped logit changes and four-term signed residuals are zero at all
  87 layers. Saved-state hashes match. Local native kernel differences remain
  at 48/53 Conv and all BNs; Python-origin maxima 0.00000190735/0.00000762939,
  propagated maxima 0.0000308752/0.000339508. Separate maxima do not add as
  worst-case causal accounting. Complete min/max/mean evidence retained.
- Both promoted BN recipes match their Python expressions at all 34 layers on
  both origins, but neither exactly matches native Python across all tested
  inputs at any layer. Rsqrt local maxima lower/equal at 22/12 Python-origin
  and 23/11 ORT-origin layers; divide lower/equal/higher at 9/14/11 and 9/18/7.
  No favourable subset or whole-model improvement selected from those counts.
- Independent audit PASS without inference: tracked/private equality,
  reconstructed complete aggregates, all 517 graphs, recomputed runtime audits,
  ordered training IDs, saved-model/preparation/source/dependency/retained
  provenance and exact prior preserved ordered Python/ORT logits/parity.
  Preserved still FAILS raw/probability budgets (0.000240326/0.00000279320,
  26/29 violations, zero flips). No new whole-model or INT8 artifact accepted.
  Graphs, weights, component details, command/check/audit logs stay ignored.
- Updated ADR follow-through, HUMAN-QUEUE, ML-EXPORT, DEV-SETUP and ML README.
  M4 incomplete; ADR-012 labelled toy workaround stays diagnostic only.
  NEXT_ACTION CONTINUE; no HANDOFF/review request. Next predeclare all-BN
  coefficient/epsilon-rounding replay; Conv drift/QDQ/mobile support unresolved.
- bash scripts/check.sh exit 0: 377 ML tests PASS in 111.72s, 144 exporter
  warnings (ran alongside diagnostic replay); Android SKIPPED, RESULT PASS.
  Root tests after command docs: 6 PASS in 0.068s. No APK/completion claim.
- No toolchain/dependency/acquisition changes, protected edits, review.sh,
  REVIEW/CHECK/GATE writes, publishing/push or external messages.
- Final root repository-contract checks: 6 PASS in 0.080s after all docs and
  iteration records; git diff --check clean. NEXT_ACTION exactly CONTINUE.
  Changed paths contain no protected files and data/ has no tracked files.
  All changes committed before ending.
