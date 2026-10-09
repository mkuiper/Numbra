# M1 Response to Review-1 (gate already closed)

The harness closed M1 PASS WITH CHANGES. Follow-through before starting M2:

1. **Accepted.** Confirmation uses an allow-list in schema 1.1.0; evidence-category
   property distinguishes clinical-only, laboratory, photo-only weaker and
   source-assertion-unverified methods. Five unapproved methods tested. Humans
   still determine clinical training eligibility; real loading remains blocked.
2. **Accepted.** Non-synthetic diagnoses must match code/family vocabulary or be a
   named unknown under `other`. Mismatch/unknown tests added.
3. **Accepted for M2.** Explicit M2 tests will cover identical bytes with opposite
   labels and group-wide quarantine, not just documentation.
4. **Accepted.** Quarantine/unassigned are whole-component partitions, with a
   mixed-quarantine/patient test proving rejection. M2 propagates quarantine.
5. **Accepted.** `.tmp/` ignored at every depth. Existing basetemp retained inside
   repository to respect filesystem scope.
6. **Accepted.** Identifier/hash patterns require absolute end with a portable
   negative lookahead. Newline rejection cases added.
7. **Accepted.** Calendar-date pattern plus future-date check; compact, week,
   newline and future cases tested.
8. **Accepted.** Schema 1.1.0 has controlled Fitzpatrick/Monk ranges and annotator
   provenance, reserving generator for synthetic colours. Tests added.
9. **Accepted.** Optional capture site/device/body fields added before M2, no
   invented clinical metadata. Version 1.0.0 rejected; regenerate fixtures.
10. **Accepted.** Single-frame palette and grayscale/RGB transparency-chunk tests;
    loader rejects transparency and wraps ValueError/SyntaxError as DataError.
11. **Accepted for M2.** Preserve strict mapping; M2 reports unresolved counts per
    source/original label. No change to existing case-sensitive tests.
12. **Deferred to M3.** Hashed dependency locking for torch-class dependencies
    queued for follow-through. Version-only pins disclosed.
13. **Accepted.** DEV-SETUP header now describes installed M1 venv.
14. **Accepted.** DATA-LAYOUT names schema 1.1.0 and remaining M2 audit work.

Missed-work clinical vocabulary candidates are **UNVERIFIED reviewer judgement**
and queued for clinical partner review. No new medical claims/vocabulary introduced.
Pure-neural/image target limitation is queued explicitly for the M3 model card.
Human questions 1–3 remain pending review of ADR-006, confirmation and vocabulary.
Question 4 remains queued to harness maintainers; protected scripts unchanged.
Question 5 needs no action: connectors were not used.

Observed check.sh: 110 ML tests PASS, Android SKIPPED, RESULT PASS. Initial
validation-order failure fixed in code: reject unapproved sources before semantic
validation or file access; no existing failing test weakened or skipped.
