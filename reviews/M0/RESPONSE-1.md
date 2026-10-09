# M0 — response to Review 1

Date: 2026-10-09. Verdict received: REVISE. Builder requests another harness
review after research corrections; no M0 gate or clinical approval claimed.
All changes are research/documentation. No images, patient-row tables, weights,
training or app implementation acquired/built. Public Fitzpatrick17k labels were
counted transiently in memory; individual rows and image URLs were not retained.

## Blocking issues

1. **Accepted — DermaCon-IN added; unresolved label/rights audit deferred to humans.**
   `research/03-datasets.md` now has a full candidate record, linked README/schema,
   metadata export, data dictionary, licence analysis and access evidence.
   Ordinary API/page paths failed; Harvard's anonymous export worked, then both
   documentation files returned HTTP 200 without an account or acceptance step.
   Latest export lists v4.0, 17 unrestricted files and no extra terms/guestbook ID;
   that does not prove the image-download flow, which was not attempted.
   Schema **does document Subject_ID and subject-wise 80:20 splits**; the privacy
   wording cannot establish absent linkage. Actual ID integrity remains unaudited.
   README/schema/dictionary do not enumerate diagnoses. Leprosy and differential
   coverage remain **UNVERIFIED**, not presumed absent or negatives-only. Within
   the requested documentation-only boundary, no patient table was fetched to
   settle them. NC-SA/derived-weight questions, image-flow and permitted label/ID
   audits are queued in HUMAN-QUEUE. ADR-002 and synthesis now include this regional
   candidate and retain synthetic-only because task fitness/rights and an independent
   positive/control cohort are unresolved. This is a bounded research decision,
   not a finding that South Asian data do not exist.

2. **Accepted — AI4Leprosy record/backbone/code corrected throughout.**
   Direct Fiocruz HTML/API worked after web-tool failures. CC BY-NC 4.0, all
   1,456 files restricted and owner-request instructions are now verified;
   research/03, ADR-002, source register, synthesis and HUMAN-QUEUE supersede the
   stale unknown-licence entry. The API reports v1.10 released **2024-05-16**;
   2021 is the earlier deposit/publication era, not this version's release date.
   Generic guestbook HTML exists but the API ID is null: an active download
   guestbook is UNVERIFIED. Both distinctions preserve direct evidence over the
   review's finer assertions without changing exclusion.
   Europe PMC full text/supplement were inspected. Research/02 now identifies
   fine-tuned **ResNet-50 close-ups**, **MIT code**, and currently archived status
   (exact archive date not asserted). The inspected code listing supplies no task
   data/weights. Abstract accuracy 90% / AUC 96.46% is retained; main Table 3's
   metadata outputs plus patient-info row reports SEN 89% / SP 91%. Supplementary
   Table 3 contains refit coefficients, not alternate SEN/SP. Main Table 3 says
   40 held-out patients while Supplementary Fig. 6 describes CV averages: explicitly
   unresolved. The final refit includes test patients and cannot be an independent
   evaluation. Abstract versus results image/lesion count discrepancy is retained.
   Human action is now owner access/NC review and clarification of the evaluation,
   rather than locating an supposedly unopenable record. Nobody contacted.

3. **Accepted — intact sensation no longer clears proposed red flags.**
   Research/01, research/04 and ADR-001 explicitly say intact sensation cannot
   exclude leprosy/MB and volunteer touch-test sensitivity is UNVERIFIED. Direct
   HTTP retrieved the ILA PDF after HTTPS failures; S24–S25 confirms the warning.
   Its roughly 30% refers to **patients missed by a single criterion** in the
   cited study, not a universal percentage of lesions. Proposed photo-independent
   referral triggers now include >5 patches, many/widespread patches with unknown
   count, raised/nodular/thickened skin or earlobes, eyebrow loss, painless wounds/
   burns and close contact with the presenting concern. Incomplete required concern
   assessment goes to review. Research/04 specifies planned M6 tests for each trigger
   with intact sensation/zero score, boundaries, overlap and monotonicity. All are
   clinical-review proposals, no claim of complete MB detection. HUMAN-QUEUE also
   asks humans whether low-photo wording should exist in any future pilot.

## Non-blocking issues

1. **Accepted — macular PKDL.** Added to research/01's pale-lesion vocabulary/table
   using the inspected Nepal cohort, with local-ranking implications and no current
   national prevalence claim. Synthesis/HUMAN-QUEUE carry it forward.
2. **Accepted — Sarlahi context.** Research/01 adds Table 2's 31.8% illiteracy,
   historical 18-day basic training (distinct from one-day study orientation),
   36 passive-detection cases, training/referral incentive context and authors'
   stigma interpretation. Research/05 links these to low-literacy usability.
   The table conflicts with prose saying “majority”; the table is used explicitly.
3. **Accepted — 32-category compilation excluded.** Research/03 records Mendeley
   v2, depositor, subtype labels, CC BY declaration and upstream Kaggle provenance;
   no image acquisition. Missing upstream rights/confirmation/grouping cannot be
   repaired by a dataset-level declaration. Queued to prevent future reuse shortcuts.
4. **Accepted — Fitzpatrick17k label counts.** An in-memory CSV count confirms
   16,577 rows/114 labels, no leprosy label, and relevant named differential counts
   in research/03. No exact tinea/PKDL/morphea target labels found. Other pityriasis/
   lupus names are not remapped as synonyms. Atlas rights still matter for controls,
   but this source cannot provide a labelled leprosy positive. No images fetched.
5. **Accepted — Privacy Act ss.11/16.** Research/07 and source register now include
   personal medical documents and the qualified harmful photography/publication
   provisions, verified against the government-linked English text. Legal application
   remains deferred; this is not a blanket prohibition claim or clearance.
6. **Accepted — threshold counts and exact uncertainty.** Research/04 proposes
   at least 100 independent groups per class for threshold selection after separate
   calibration-fit with 20/class. Below counts selection is unavailable; an explicitly
   unselected refer-all fallback is used. Report the lower endpoint of two-sided 95%
   Clopper–Pearson sensitivity intervals, with counts and empirical-only status when
   the point estimate meets target but the bound does not. Selection intervals are
   descriptive after search; frozen-test intervals concern a fixed threshold.
   These are queued engineering choices, not a clinical sample-size calculation;
   M3 implementation/tests remain after M0's gate.
7. **Accepted — journal coverage.** Research/02 records new targeted Leprosy Review,
   IJDVL and IJL domain searches with linked commentary/review/editorial findings.
   No new diagnostic performance or image permission inferred. Survey remains
   targeted rather than claiming systematic completeness.

## Missed work and human questions

The three missed-work items are addressed in blocking 1/2 and non-blocking 1.
All four human questions are **deferred to humans**, with concrete HUMAN-QUEUE
entries: AI4 owner access/NC terms; DermaCon NC-SA/weights; whether any low-photo
outcome is acceptable; and review of all five ADRs. ADR-001/002 amendments keep
`Accepted (autopilot) — pending human review`. No collection/clinical use authorised.

## Verification

Repository-contract suite: five tests passed. Builder check and final diff results
are recorded in STATUS/JOURNAL and HANDOFF; the harness owns tests of record and
review/gate files. Documentation checks verify links/evidence bookkeeping and
repository boundaries, not clinical safety, data rights or scientific validity.
