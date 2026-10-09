# Status

Updated: 2026-10-09T13:20:58Z

Current milestone: **M2 — Data acquisition and preparation**, implemented and
**ready for harness review**. NEXT_ACTION: REVIEW M2. M0/M1 GATE files exist,
PASS WITH CHANGES; human review pending. M1 Review-1 follow-through is answered
in reviews/M1/RESPONSE-1.md and committed as 9610650. No M2 gate exists yet.

## Acceptance status

- **Only approved acquisition / ignored data: SATISFIED via synthetic fallback.**
  ADR-002 approves no real dataset. New `python -m numbra_ml.prepare` CLI generates
  procedural images only into a new run below ignored data/, refuses overwrites
  and path escapes, and contains no network download, registration or agreement.
  768 generated images and all manifests/audits are local and ignored.
- **Licence manifest, duplicates, patient/group splits and held-out source:
  SATISFIED.** Schema 1.1.0 JSONL with provenance/licence per row. Verify all
  checksums/decodes, merge source-scoped patient/group and global exact/decoded/
  near-visual links transitively, quarantine whole components for conflicts,
  missing groups/ineligible labels or cross-source-C boundary links. Freeze
  class-stratified deterministic train/calibration/threshold-validation/test
  splits, with source C held out. Report maps records to evaluation components.
- **No suitable real task data / PLACEHOLDER: SATISFIED.** HUMAN-QUEUE explicitly
  states no suitable approved real task data under current ADR-002; generated
  fixture source holdout has no clinical validity. Every downstream model,
  report/card/UI must say PLACEHOLDER. No real images/weights acquired.
- **Handoff/review: READY.** reviews/M2/HANDOFF.md states commands, evidence,
  scrutiny and limitations. ADR-007 Accepted (autopilot) — pending human review
  and queued. Harness owns REVIEW/CHECK/GATE and pushes.

## Observed verification

- bash scripts/check.sh: exit 0, **136 ML tests PASS**, Android SKIPPED, RESULT PASS.
- python3 -m unittest discover -s tests -v: **5 PASS** (Builder-attested only).
- ml/.venv/bin/python -m pip check: no broken requirements; git diff --check PASS.
- Full default command ran twice: all **771 generated files byte-identical**.
  Manifest SHA-256 ff0e5d1749bf1f33fe64ac4234e7b788ea36e7db0996aa6c13208e76459911c4.
- 384 components/768 rows: train 150/300, calibration 40/80,
  threshold_validation 40/80, test 26/52, held_out 128/256. Balanced classes.
  384 near-visual view pairs, no default quarantine/conflicts; explicit adversarial
  tests cover conflict/duplicate/transitive/holdout/missing/withdrawn cases.
- No model/card/clinical metric/export/parity/app/APK claimed. No protected edits,
  review.sh, reviewer/check/gate writes, patient data, messages, publishing or pushes.

## Carried requirements and limitations

- No blocking M2 issue known. Clinical/legal/ethics/native-language review pending.
- Visual-thumbnail RMS matching is an unvalidated fixture heuristic; false matches
  and missed transformations remain possible. Quadratic search caps at 2000 rows.
  Patient/source tokens do not prove real independence. One-label-per-component
  quarantine can reject valid multi-condition patients in future real data.
- M3 must use audit **component IDs** as independent units and preserve frozen
  partitions. Threshold validation has only **20 components/class**, below ADR-001
  100/class: use unselected refer-all fallback, never claim a selected operating
  point. Calibration 20/class, test 13/class, held-out 64/class are synthetic only.
- M3 must keep pure-neural/no-skin-lesion limitation in model card, consider hashed
  torch dependency pins, and follow ADR-005 weight permission/revision/checksum
  checks before downloading any pretrained weights. No weights downloaded at M2.
- M1 follow-ups: confirmation allow-list/evidence strength, diagnosis/family checks,
  controlled tone annotator metadata, optional capture fields, strict IDs/dates,
  palette/transparency loader rejection, universal .tmp ignore, stale-doc cleanup.
  Clinical confirmation eligibility remains pending human review; real loading
  still blocked. Schema 1.0.0 rejected; regenerate synthetic rows at 1.1.0.
- M6 must implement full ADR-001 question superset (roadmap list is minimum),
  explicit volunteer concern and contact yes referral. Manifest missingness
  never supplies normal answers. M7 must preserve trigger answers and add detailed
  consent/confirmation/custodian/credential provenance and encrypted local storage.
- Real dataset rights/labels/patient linkage remain unresolved; do not treat M0/M1
  gates or synthetic metrics as real field/data permission.

## Next concrete step

Harness runs M2 checks/review. Read resulting REVIEW/CHECK in full, answer each
numbered issue and revise if required. If M2 GATE exists, fix cheap follow-ups,
queue the rest and start **M3 only**. No training or Android work in this iteration.
