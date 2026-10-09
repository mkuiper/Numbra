# Status

Updated: 2026-10-09T12:44:00Z

Current milestone: **M0 — Research and plan**, Review-1 REVISE addressed and
**ready for harness re-review**. No GATE exists. NEXT_ACTION: REVIEW M0.
Research only; do not begin M1 until the harness closes M0.

## Acceptance status

- **Research documents, synthesis and required ADRs: SATISFIED.** Seven research
  documents, source register, synthesis and required ADR-001/002/003/004 exist;
  additional ADR-005 remains. All ADRs Accepted (autopilot) — pending human review.
  ADR-001/002 revised following review; amendments and unresolved choices queued.
- **Every dataset claim sourced or UNVERIFIED: SATISFIED.** DermaCon-IN added,
  AI4 restricted access/licence corrected, Fitzpatrick label counts checked and
  32-category compilation excluded. Target coverage/linkage/access gaps explicit.
  No real task dataset approved. Research retains Open questions/Confidence.
- **Review response: COMPLETE.** reviews/M0/RESPONSE-1.md answers all 3 blocking,
  7 non-blocking, missed-work and human-question items. HANDOFF updated.
- **Gate: PENDING.** No clinical, scientific, legal or milestone approval claimed.

## Verification observed

- `python3 -m unittest discover -s tests -v`: **5 tests PASS** after research edits;
  final documentation pass recorded in JOURNAL. No tests changed or weakened.
- `bash scripts/check.sh`: exit 0, RESULT PASS; ML and Android explicitly SKIPPED
  because projects do not exist. No APK, model performance or clinical validation.
- `git diff --check`: passed after review-response/handoff edits; staged whitespace
  and boundary checks recorded in JOURNAL before commit.
- No protected edits, review.sh, REVIEW/CHECK/GATE writes, training/app work,
  toolchain installation, clinical images, patient-row tables, weights, external
  messages, publishing or pushes. Fitzpatrick CSV counted transiently in memory
  only; no individual rows/image URLs retained. Publication PDFs/supplements,
  documentation and catalogues inspected as research evidence.

## Review findings, decisions and open blockers

- AI4Leprosy Fiocruz direct HTML/API verifies CC BY-NC 4.0, v1.10 release
  2024-05-16, 1,456 restricted files (1,231 JPEG / 225 JSON), owner request route.
  Excluded under unattended limits. Human access/NC decisions replace stale
  unknown-licence queue entry. No access requested. Actual guestbook requirement
  remains UNVERIFIED (generic UI but API guestbook ID null).
- AI4 full text/supplement and code verified: ResNet-50 close-ups, MIT code,
  currently archived. Main Table 3 SEN/SP 89/91% is metadata outputs plus patient
  info; supplement conflicts on CV/holdout description. Final refit includes
  testing patients. Abstract/results count discrepancy retained; no invented
  reconciliation or Numbra performance inferred.
- DermaCon-IN: regional clinical smartphone/camera candidate, CC BY-NC-SA 4.0,
  anonymous README/schema access, documented Subject_ID/subject-wise split.
  Actual target diagnoses, patient linkage, image flow and derived-weight terms
  unresolved. Documentation/dictionary omit diagnosis enumeration; **labelled
  documentation-only workaround** keeps coverage UNVERIFIED and queues a future
  permitted audit. No negatives-only assumption. ADR-002 remains synthetic-only;
  every downstream model/report/UI must say **PLACEHOLDER**.
- ADR-001 now includes intact-sensation/MB limitation and proposed independent
  patch/skin/eyebrow/injury/contact referral triggers; unknown required assessment
  refers. Planned M6 tests cover intact sensation/zero score, boundaries and
  monotonicity. Human clinical approval and whether low-photo wording is ever
  appropriate remain unresolved; added rules do not guarantee all MB detection.
- Proposed M3 threshold guardrails: 100 independent groups/class after separate
  calibration subset 20/class, exact 95% sensitivity bounds and explicitly
  unselected refer-all fallback below counts. Engineering choices queued; no
  clinical sample-size or supported-sensitivity claim.
- Added macular PKDL, historical Sarlahi literacy/training/incentive/stigma context,
  Privacy Act ss.11/16 and journal-targeted search coverage. Existing NHRC/DDA,
  Nepal field/device/language, governance/custodian and real-pilot gaps persist.
- Firecrawl credits remain zero; continued documented web-tool/direct-document
  workaround. ILA HTTP PDF works after HTTPS failures; Harvard export works after
  ordinary API/page failures. No auth/account/billing changes.

## Next concrete step

Harness reruns checks and M0 review. Read next REVIEW/CHECK in full; if still
REVISE, answer each numbered issue and fix within M0. If GATE exists, address cheap
non-blocking issues, queue remaining human decisions and begin **M1 only**.
