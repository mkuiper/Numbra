# M3 RESPONSE-1 — closed gate follow-through

Date: 2026-10-09 UTC. M3 GATE exists, PASS WITH CHANGES. No review rerun requested;
the following reporting/reference fixes preserve the original fitted parameters.

1. **Accepted.** `train_run` accepts an explicit Python backbone supplier returning
   a module and its evidence. CLI retains the pinned verified production supplier.
   `test_train_run_end_to_end_with_explicit_toy_loader` uses the 16-group generated
   fixture and actual repository environment/provenance, asserts all three ignored
   artifacts plus aggregate JSON/card, and exercises overwrite rejection. No mock,
   monkeypatch, network or downloaded checkpoint is used in tests of record.
2. **Accepted.** `numbra_ml.verify` strictly restores the bundled full `Baseline`,
   verifies hashes/state/preprocessing/component metadata, rescores and checks raw
   logits and frozen-threshold decisions. Toy integration also checks tampering.
   Actual original baseline: 768 components, max raw/probability error 0, flips 0.
   Same command for reproduction/default is documented in ML-TRAINING.md.
3. **Accepted.** Cards now include `target_evidence`, TP/FN/TN/FP, exact intervals,
   explicit below-target wording and per-row fallback markers; display numbers
   round to four digits while JSON keeps full precision. None/boundary wording is
   readable. All three tracked aggregate reports/cards were rebuilt from verified
   original prediction files; original training provenance and fits are retained,
   and `reporting_revision` records reporting source/original report hashes.
4. **Accepted.** ADR-010 and HUMAN-QUEUE supersede the probability-only 0.02 proposal:
   M4 must check raw logits, calibrated probabilities and count every frozen-
   threshold flip, with budgets fixed before export and separate margin accounting.
5. **Accepted.** `before_calibration_metrics` nulls confusion counts, sensitivity,
   specificity and their intervals, with a machine-readable reason. AUC/calibration
   metrics remain. Regression tests assert this directly; aggregate reports rebuilt.
6. **Accepted for synthetic display guard; real privacy design deferred to humans.**
   Source/colour blocks now carry `minimum_per_class=20`/`below_minimum_cell`,
   suppress AUC/calibration/bins below it, and suppress subgroup bootstrap. Boundary
   tests cover two/class and 20/class. Overall partition summaries remain descriptive
   to preserve default fallback evidence. No patient data is present; sparse bins
   in larger cohorts and complete disclosure controls require future human policy.
7. **Accepted.** ADR-010 explicitly requires a real-data model-selection split or
   nested cross-validation before calibration/threshold selection. Synthetic fixed
   defaults remain unchanged; no held-out tuning or performance-improvement claim.
8. **Accepted.** CLI now exposes `--learning-rate` and `--weight-decay`; both feed
   validated TrainingConfig and saved config. ML-TRAINING documents the flags.
9. **Accepted.** The CLI guard test now asserts the exact ignored-data path error
   on stderr as well as exit 1; unrelated failures cannot satisfy it.
10. **Accepted.** Bootstrap caches identical component sets, so overall/source-C
    use exactly the same seed and intervals. A regression test checks identical
    results; separately tiny subgroups retain their suppression rule.
11. **Deferred to humans as optional convenience.** Clean-checkout setup, anonymous
    checkpoint acquisition and fixture preparation are separate explicit commands.
    A single offline training invocation meets the accepted roadmap requirement;
    ML-TRAINING now states its prerequisites and lack of a wrapper plainly. A
    convenience wrapper would introduce new acquisition/overwrite policy beyond
    this reporting follow-through; queued with the remaining non-blocking item.

Reviewer human questions are queued, excluding the unrelated connector tooling
note (no connectors used or required). M4 will use the saved Python reference;
the original selected model remains PLACEHOLDER and below target on source C.
