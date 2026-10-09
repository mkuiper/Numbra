# Status

Updated: 2026-10-09T20:51:04Z

Current milestone: **M4 — On-device model export**, in progress. M0–M3 gates
exist; M4 acceptance remains incomplete. NEXT_ACTION: CONTINUE. All models and
results **PLACEHOLDER**, synthetic-only. No accepted deployment package, app or
APK. Every failed export remains rejected.

## M4 acceptance status

- **Quantised ONNX Runtime Mobile export: built, not accepted.** Original INT8
  QDQ graphs fail parity. No selected arithmetic replay, new whole-model
  candidate, selective QDQ scope, deployment selection or mobile support result.
- **Exported/Python parity: FAIL, budgets unchanged.** Complete ADR-023 training
  report: preserved max raw/probability 0.000240326/0.00000279320 (26/29
  violations); rounded BN 0.000143051/0.00000183769 (13/21 violations).
  Zero threshold flips. No new selected-baseline numerical outcome.
- **Size ≤20 MB / preprocessing written and tested: built.** Existing original
  float/INT8/rounded diagnostic files meet the ceiling. RGB letterbox float32
  1×3×224×224 → raw_logit [1] unchanged. Android preprocessing and accepted
  deployment metadata remain open.

## This iteration

- Added export_arithmetic_run guarded runner and independent report audit,
  connecting training_context/training_rows/ArithmeticReplay/ordered arithmetic
  persistence. Complete original historical-source/dependency/hardware/saved/
  preparation/prior/control evidence audited before session construction; every
  new serialized/runtime setup graph reconstructed before retained row access.
- Original report hash bound; separate caller-supplied retained/profile/new
  report source snapshots, exact live dependencies, state/fits/scope/budgets and
  prior bits. Exhaust reader including final scope check before finishing index;
  reconstruct complete original/new evidence before writing completed report.
  Failed final audit may leave ignored index, never completed report.
- Generated full runner round-trip blocks decode/native forward/original-control
  replay. Separate audit also blocks sessions/eager recipes/persistence.
  Interrupted reader/write/audit, final setup mutation, corrupt last original
  row, rehashed contexts/metrics/acceptance claims and snapshot bindings tested.
  No independently recomputed numerical truth or historical authentication claim.
  Whole-model recipe parity UNVERIFIED; deployment selection false.
- ADR-024/docs/ML README/DEV-SETUP updated under existing decision. No new
  scientific decision, selected experiment, new fit or parity result.

## Observed checks

- Focused new runner suite: **31 PASS**, six deprecation warnings, 92.15s.
  Hardware-corruption test subsequently tightened to actual machine field;
  included in the required full check.
- Root repository contracts: **six PASS**, 0.074s; whitespace clean.
- Required scripts/check.sh: exit 0, **940 ML PASS**, 594 deprecation warnings,
  364.89s; Android SKIPPED (no app/gradlew), RESULT PASS. All 31 new runner
  cases included; no accepted export or APK claim.

## Next concrete step and blockers

Execute and independently audit ADR-024's full retained training experiment:
all 152 ordered components, every fixed recipe, both unchanged graph contexts/
input origins, every original control and exact prior bit. Runner is now built;
use the documented fresh PLACEHOLDER-arithmetic-training1 output and explicit
historical ADR-023 source 50f7c65e7b6a6168a17d498be4d663c89b11742f and ADR-022
source 808cc3393ccf1cce95c2feeef91e5a8608b481e4. Exhaust reader and reconstruct
all persisted evidence before publishing a complete diagnostic report. Then
perform separate read-only guarded audit bound to the committed new source.
No image decoding or new selected native-model runs. Disk check observed 199 GB
available; original tensor archives are 68.6 GB. Allow adequate run duration.

Generated results cannot establish selected or whole-model parity. Float parity,
separately predeclared whole-model/selective QDQ scope, acceptance evaluation and
mobile double compatibility/performance remain blockers. Clinical validation,
ethics/legal/native-language review and weight rights remain human questions.
No M5 or M4 review until acceptance. No protected edits, review.sh, REVIEW/CHECK/
GATE writes, publication or push.
