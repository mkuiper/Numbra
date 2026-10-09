# M2 Response-1 — post-gate follow-through for M3

Date: 2026-10-09

M2 GATE exists: PASS WITH CHANGES. This response answers all ten non-blocking
issues without requesting a new M2 review. M3 remains in progress, not complete.
No protected reviewer/check/gate file was edited.

1. **Accepted.** ADR-008 adds `selection_exercise` 30/20/40/10 fractions without
   raising generator/row caps or lowering ADR-001's guard. The observed 256-group
   shapes-v2 run has 102 threshold-selection and 52 calibration components/class.
   A full-size regression test checks these counts. Default 128-group runs still
   require unselected refer-all. M3 must implement actual eligibility guards;
   sufficient fixture counts alone do not mean selection has been implemented.
2. **Accepted.** shapes-v2 matches exact raster areas, overlaps signed contrast
   and background intensities, introduces group-level 0.10 Bernoulli shape flips,
   and adds stronger source channel/illumination/noise differences. Area tests
   and a fixed-seed best-mean-threshold regression check pass; observed balanced
   accuracy is 0.541667. This does not promise difficult training or clinical
   realism. No model trained; no false-negative/AUC claim made.
3. **Accepted.** Preparation 1.1.0 stratifies whole components by full source
   membership × target. Report includes explicit per-split/source/class counts.
   Both default and larger runs balance A/B in every development partition.
   Rare linked multi-source strata stay whole; counts include each represented
   source with that convention documented. Existing transitive-link tests pass.
4. **Accepted.** `colour_stratum` derives fixed bands from the generated weighted
   background luminance after source gains. Boundary and generated-annotation
   tests verify the relationship. All documentation says synthetic colour strata,
   never real skin-tone or fairness evidence.
5. **Accepted for fixture contract; report/card enforcement pending M3.** Diagnoses
   are now `synthetic_circle` / `synthetic_square`; audit supplies target names
   synthetic circle / synthetic square. ADR-008 and ML/preparation docs require
   those names on every M3 metric/card, with PLACEHOLDER. Existing binary family
   encoding remains internal schema compatibility, never a disease endpoint.
6. **Accepted.** Tests cover RMS just below 2 (~1.999023), exactly 2 (inclusive),
   and just above 2 (~2.001627). Tests assert 48 components for 16 groups/source
   and 768 for 256, proving unrelated generated groups remain separate at those
   seeds. Audit records nearest-unlinked pair after final transitive linking:
   RMS 8.586645 default / 8.204261 larger run. Heuristic remains unvalidated for
   real data and capped at 2000 rows.
7. **Accepted.** CLI regression creates an ignored `data/` symlink parent pointing
   to another ignored test directory, attempts an output through it, asserts exit
   2 and no generated output, then removes the symlink. No outside files modified.
8. **Accepted.** `repository_root` walks up from the invocation directory to both
   `.git` and `docs/ROADMAP.md`; no `__file__.parents[3]` assumption remains. Tests
   cover normal-install-style nested site-packages, worktree `.git` file, fallback
   to an outer checkout and failure without any checkout ancestor. CLI must run
   within the repository, explicitly documented.
9. **Accepted via accurate single-fold wording.** ADR-008/ML/preparation docs require
   “single held-out source (one leave-one-source-out fold)” for C-only M3 results.
   CLI also supports predeclared other holdouts and tests verify source isolation,
   but no rotation/training result is claimed. All-fold training is deferred to
   later work or human preference; one fold satisfies the roadmap.
10. **Accepted.** DEV-SETUP's M2 section and new M3 commands precede its final Open
    questions and Confidence sections. Original shapes-v1 evidence is historical;
    new reproducible commands use new shapes-v2 directories.

## Verification

- Preparation subset: **40 passed** (observed).
- Full `scripts/check.sh`, root repository suite, environment consistency and
  reproduction results are recorded in the iteration STATUS/JOURNAL and current
  [preparation documentation](../../docs/DATA-PREPARATION.md).
- No pretrained weights, real data, model training, app, export or APK in this step.
  M3 will continue with dependency/weight checks, CPU training and evaluation.
