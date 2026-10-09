# Status

Updated: 2026-10-09T11:50:27Z

Current milestone: **M0 — Research and plan**, in progress. No review requested;
no GATE exists. Work remains research only.

## Acceptance status

- **All research/0x documents, synthesis, and four ADRs: INCOMPLETE.** Repository
  scaffold, project brief, initial glossary, dataset survey (`03-datasets.md`),
  source register, and ADR-002 (dataset selection) / ADR-003 (code licence) are
  written. Still needed: `01-clinical-background.md`, `02-prior-work.md`,
  `04-models-and-methods.md`, `05-deployment-constraints.md`,
  `06-data-contribution-platform.md`, `07-ethics-regulatory-nepal.md`,
  `docs/01-phase0-synthesis.md`, ADR-001 task framing, and ADR-004 contribution
  governance. Extend glossary after clinical/methods sourcing. HANDOFF waits for
  all M0 deliverables.
- **Every dataset claim sourced or UNVERIFIED: SATISFIED for the current survey.**
  Primary-source links and access limits are explicit. No image/archive download
  or patient-row inspection occurred; no suitable real positive cohort/licence
  verified. Additional published-study datasets must be considered when writing
  prior-work research.

## Verification observed

- `python3 -m unittest discover -s tests -v`: 4 tests passed, including ignore
  boundaries, no tracked data, local document links and research uncertainty
  sections. The first run found a missing source-register link; adding the planned
  source register fixed it without changing the test.
- `bash scripts/check.sh`: exit 0, RESULT PASS; both ML and Android explicitly
  SKIPPED because their projects do not yet exist. No APK or ML validation claimed.
- `git diff --check`: passed before logical commits. No protected files edited.

## Decisions and blockers

- ADR-002: **synthetic data only** for downstream work until an amended, evidenced
  acquisition decision. Every downstream model, UI and report says PLACEHOLDER.
- ADR-003: Apache-2.0 code; dataset/weight rights remain separate.
- AI4 repository licence/access unverified after two failed page-open attempts.
  DDI registration/agreement and DermNet free-image AI prohibition exclude them;
  other sources have scientific-fit or rights gaps. These do not block synthetic POC.
- Firecrawl zero credits: two requests failed; available web tool is the recorded
  research workaround. No new account or terms accepted.
- Humans must later review ADRs, local clinical/ethics fitness, and language/device
  assumptions. Queue entries exist; unattended work does not await replies.

## Next concrete step

Continue M0: source WHO clinical guidance and Nepal primary health/ethics material,
then write clinical background and prior-work comparisons (including WHO Kenya
and independent leprosy evaluations, NLR SkinApp, LEARNS, JMIR scoping review and
academic image work). Complete methods/deployment/contribution/regulatory research,
ADR-001/004 and synthesis before preparing HANDOFF and setting REVIEW M0.
