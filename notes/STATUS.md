# Status

Updated: 2026-10-09T12:12:57Z

Current milestone: **M0 — Research and plan**, in progress. No review requested;
no GATE exists. Work remains research only.

## Acceptance status

- **All research/0x documents, synthesis and required ADRs: INCOMPLETE.** Scaffold,
  brief, glossary, clinical (`01`), prior work (`02`), datasets (`03`), methods
  (`04`), deployment (`05`) and source register are written. ADR-001 task framing,
  ADR-002 datasets, ADR-003 code licence and additional ADR-005 baseline/runtime
  exist with autopilot/pending-human status. Still needed:
  `06-data-contribution-platform.md`, `07-ethics-regulatory-nepal.md`,
  `docs/01-phase0-synthesis.md` and ADR-004 contribution governance. HANDOFF waits
  for these deliverables and a consistency pass. Research documents end with Open
  questions and Confidence and distinguish proposals from sourced facts.
- **Every dataset claim sourced or UNVERIFIED: SATISFIED for the existing survey.**
  No new real source approved or downloaded. New methods/deployment sources are
  registered with access date and limits; pretrained binary access remains untested.

## Verification observed

- `python3 -m unittest discover -s tests -v`: all 4 repository checks passed;
  extended the ignore-boundary test to cover safetensors weights. Checks cover
  ignored paths, no tracked data, local links and uncertainty sections; they do
  not validate research facts, clinical rules or a model.
- `bash scripts/check.sh`: exit 0, RESULT PASS; ML and Android explicitly SKIPPED
  because their projects do not exist. No APK or ML validation claimed.
- New-document source-register coverage check: PASS (all external URLs in `04`,
  `05`, ADR-001 and ADR-005 appear in `research/sources.md`).
- `git diff --check`: passed after research/safeguard edits.
- No training, application code, toolchain installation, protected-file edits,
  review.sh, remote push, external messages, photos or model binaries.

## Decisions and blockers

- ADR-002 remains synthetic-only. Every downstream model/report/UI must say
  **PLACEHOLDER**; synthetic metrics are not clinical performance.
- ADR-001 chooses a binary image evidence score with separate symptom-first
  referral and explicit missingness/failure handling. Proposed sensitivity 0.95,
  secondary specificity 0.80 and clinical rule precedence need human scrutiny.
- ADR-005 selects timm MobileNetV3Small transfer features and static-quantised
  ONNX Runtime Mobile/CPU. Publisher declares Apache-2.0 for the checkpoint;
  anonymous binary access, pins/checksum, conversion, parity, notices and actual
  Android support must be verified in later milestones. Derm Foundation is
  gated by account/terms acceptance and excluded. No weights acquired here.
- Proposed preprocessing changes pretrained centre crop to deterministic bilinear
  letterbox. Quantised probability tolerance 0.02 and conservative threshold
  margin are unmeasured engineering choices, requiring M4/M6 tests and review.
- Rural Nepal FCHV devices, OS/ABI, charging and connectivity remain UNVERIFIED
  after manufacturer/NTA searches. **Labelled research workaround:** conservative
  test profiles and a regional manufacturer example; budgets are not measurements.
  Nepal HMIS indexed page identifies DHIS2 but direct open failed HTTP 502;
  authenticated configuration/API/permissions remain UNVERIFIED.
- Firecrawl status again shows zero credits; retained the previously documented
  web-tool workaround without account, billing or authentication changes.
- Existing clinical-pathway, data-permission and Nepal-report limitations remain
  in research documents and HUMAN-QUEUE. All autonomous ADRs are queued for humans.

## Next concrete step

Continue M0 with contribution governance and Nepal ethics/privacy/device-regulation
research. Design local-only consent/provenance/export records and a separate future
clinician confirmation/release cycle; write `06`, `07` and ADR-004. Mark legal
classification/process details UNVERIFIED where primary evidence cannot establish
them. Then write synthesis, check consistency across all deliverables, run checks,
write HANDOFF and request REVIEW M0. Do not begin M1 before the harness's M0 gate.
