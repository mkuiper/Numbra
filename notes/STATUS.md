# Status

Updated: 2026-10-09T13:05:05Z

Current milestone: **M1 — ML project scaffold**, implemented and **ready for
harness review**. NEXT_ACTION: REVIEW M1. M0 GATE exists: PASS WITH CHANGES,
closed by harness 2026-10-09T12:48:54Z; human approval pending. M0 Review-2
follow-through is documented in reviews/M0/RESPONSE-2.md. No M1 gate yet.

## Acceptance status

- **Python project, pinned dependencies, ml/tests: SATISFIED.** src-layout package,
  pyproject.toml, exact direct/transitive dependency versions in requirements-dev.txt,
  repository-local ml/.venv on existing Python 3.12.3. Editable install succeeded;
  pip check green. No JDK/SDK installed. Commands recorded in docs/DEV-SETUP.md.
- **Data-loading interfaces, manifest and taxonomy: SATISFIED.** Strict versioned
  executable JSON Schema plus JSONL reader/writer, source/licence/original/mapped
  label, confirmed-by assertion, source-scoped patient/group IDs, split and hashes.
  Taxonomy preserves all M0 families, explicit PB/MB/reaction and label provenance;
  exact vocabulary mappings remain provisional. Loaders enforce synthetic-only
  PLACEHOLDER policy, hash integrity, safe paths and group/patient/hash split
  checks before filtering. Missingness stays explicit and eligibility exclusions
  are reported. All new canonical referral-trigger answers have observation fields.
- **Tiny generated synthetic tests: SATISFIED.** Eight in-code RGB-block fixtures
  across families/two sources; no real images or committed generated data.
  Tests run in ignored ml/tests/.tmp. Current suite: 83 passing tests.
- **Handoff/review: READY.** reviews/M1/HANDOFF.md states evidence, reproduction,
  limits and requested scrutiny. ADR-006 Accepted (autopilot) — pending human
  review and queued. Harness owns review/check/gate files.

## Verification observed

- bash scripts/check.sh: exit 0, **83 ML tests PASS**, Android explicitly SKIPPED,
  RESULT PASS. No APK, model, clinical validation, M2 split algorithm or M4 parity.
- python3 -m unittest discover -s tests -v: **5 PASS**; root suite remains
  Builder-attested only because protected check.sh does not run it.
- ml/.venv/bin/python -m pip check: no broken requirements.
- git diff --check: PASS; final staged boundary/whitespace checks in JOURNAL.
- No protected edits, review.sh, REVIEW/CHECK/GATE writes, patient data, clinical
  images, weight download, app implementation, external messages, publishing or pushes.

## Decisions, carried requirements and open blockers

- No blocking M1 issue known; clinical/legal review remains pending for real use.
- ADR-002 still approves no real dataset: M2 will generate synthetic-only data.
  Every downstream model/report/UI must say **PLACEHOLDER**.
- M0 Review-2 consistency fixed: research/04 canonical integrated referral list;
  contact yes refers, unknown/declined remains optional; volunteer concern is one
  explicit required yes/no/uncertain question. **M6 must implement the ADR-001
  question superset; protected roadmap list is a minimum.** Clinical approval and
  whether any low-photo outcome is appropriate remain open in HUMAN-QUEUE.
- Research/06 and ADR-004 preserve all trigger answers for M7 summaries; M1
  observations carry this superset. Manifest optionality never supplies normal
  workflow answers. M7 confirmation/consent/credential/custodian details remain work.
- M0 Review-2: stable IJDVL landing page cited; ignored publication PDFs deleted.
  DermaCon descriptor examples mention leprosy but do not establish released labels.
  Web catalogue fetch and direct export HTTP 403 failed; labelled documentation-only
  workaround retains reviewer weight/archive enumeration as UNVERIFIED. All held
  under NC-SA; no patient-row audit/archives/weights acquired. Humans queued.
- JSONL checks detect exact-hash split leakage but M2 must handle connected groups,
  perceptual duplicates/conflicts, deterministic assignment and held-out sources.
- Raw loader EXIF/RGB conversion is not complete model preprocessing; M4 still
  must document/test letterbox, normalisation and exported-model parity.

## Next concrete step

Harness runs M1 checks/review. Read resulting REVIEW/CHECK in full, answer all
numbered issues and revise if needed. If M1 GATE exists, address cheap follow-ups,
queue the rest and begin **M2 only**. Do not start training or Android work here.
