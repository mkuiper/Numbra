# Status

Updated: 2026-10-09T12:03:06Z

Current milestone: **M0 — Research and plan**, in progress. No review requested;
no GATE exists. Work remains research only.

## Acceptance status

- **All research/0x documents, synthesis, and four ADRs: INCOMPLETE.** Scaffold,
  brief, glossary, clinical background (`01`), prior work (`02`), dataset survey
  (`03`), source register and ADR-002/003 are written. Still needed:
  `04-models-and-methods.md`, `05-deployment-constraints.md`,
  `06-data-contribution-platform.md`, `07-ethics-regulatory-nepal.md`,
  `docs/01-phase0-synthesis.md`, ADR-001 task framing and ADR-004 contribution
  governance. HANDOFF waits for these deliverables. Clinical and prior-work
  documents include explicit limitations, Open questions and Confidence sections.
- **Every dataset claim sourced or UNVERIFIED: SATISFIED for the expanded survey.**
  Added WHO independent evaluation, Yotsu pilot, eSkinHealth, CO2Wounds-V2 and
  academic image-study records, with rights/access/confirmation/grouping gaps
  explicit. No patient photos, image archives, per-image URLs or patient rows
  acquired. No additional real source approved.

## Verification observed

- `python3 -m unittest discover -s tests -v`: all 4 existing repository checks
  passed after final research/glossary edits. These check ignore boundaries,
  tracked data absence, local links and uncertainty sections, not clinical truth.
- `bash scripts/check.sh`: exit 0, RESULT PASS after final research edits;
  ML and Android explicitly SKIPPED because their projects do not exist. No APK
  or ML validation claimed. No tests added/changed because this iteration built
  documentation only, covered by existing repository checks.
- `git diff --check`: passed before logical commit c6ef558.
- No protected files edited; no review.sh, remote push or external messages.

## Decisions and blockers

- Existing ADR-002 remains synthetic-only for downstream work. Every downstream
  model, UI and report must say PLACEHOLDER; synthetic metrics are not clinical.
- eSkinHealth authors' February 2026 notice still holds release for ethical/legal
  review. CO2Wounds paper and Mendeley disagree on licence and its wound
  segmentation task does not supply initial leprosy triage labels. Yotsu's 2023
  pilot data are explicitly non-public. Queue entries record these findings.
- Firecrawl CLI still has zero credits; retained the previously documented web
  research workaround without billing/account changes.
- Full Nepal reports failed on multiple official endpoints (timeout/size limit).
  **Labelled workaround:** indexed primary-document text, with current burden
  figures UNVERIFIED against full reports. Current complete endemic-district
  list and local FCHV sensory/referral protocols remain UNVERIFIED.
- WHO initiative page says public app lacks AI while its 2024 news update uses
  broader availability wording. Exact public/offline AI release and reuse rights
  remain UNVERIFIED; no available classifier assumed.
- Humans must review local clinical procedures/urgent rules, language, receiving
  services, referral completion, data rights and existing ADRs before field use.

## Next concrete step

Continue M0 with methods/evaluation and deployment research: verify mobile
backbones and pretrained-weight licences, choose a CPU-trainable/exportable
synthetic PLACEHOLDER baseline, specify threshold selection and grouped/held-out
source evaluation, and write ADR-001. Then research contribution governance and
Nepal ethics/privacy/device-regulation sources, write ADR-004 and synthesis.
Only after all M0 deliverables are ready, write HANDOFF and set REVIEW M0.
