# Status

Updated: 2026-10-09T15:02:55Z

Current milestone: **M4 — On-device model export**, in progress. NEXT_ACTION:
CONTINUE. M0–M3 gates exist (PASS WITH CHANGES); no M4 gate, Android app or APK.
Every task model/result remains **PLACEHOLDER**, synthetic-only under ADR-002.
Both retained baseline exports remain rejected for app bundling.

## M4 acceptance status

- **Quantised ONNX Runtime Mobile export: BUILT, ACCEPTANCE INCOMPLETE.** Existing
  per-tensor/per-channel static signed INT8 QDQ graphs run on desktop CPU. Each
  has 53 Conv/one Gemm with quantised weights; remaining float operators reported.
  Calibration uses only 152 training components. Both fail parity; Android/ABI
  compatibility remains unverified. No new quantisation fit this iteration.
- **Exported/Python parity: FAIL, budgets unchanged.** Retained test/held-out
  float raw/probability maxima 0.000272334/0.00000355427, zero flips; INT8 per
  tensor 50.784990/0.506519, 26 flips; per channel 62.403598/0.612635, 28 flips.
  Original all-component/stress failures retained. New diagnostics use training
  only; no new test/held-out/stress inference. Saved model/inputs/fits unchanged.
- **Size ≤20 MB / preprocessing written and tested: BUILT.** Retained float
  6,095,579 bytes; INT8 1,730,515/1,861,702 bytes. RGB letterbox/rounding/normalisation
  and float32 1×3×224×224 → raw_logit [1] contract unchanged. No accepted deployment
  metadata package or Android decoding/preprocessing yet.

## This iteration's evidence

- ADR-013 declares training-only runtime/head diagnostics before execution, queued
  for humans. New numbra_ml.export_diagnostics checks model/preparation/experiment/
  graph provenance and locked environment, uses all/only training index images,
  deduplicates identical float graphs and compares four ORT optimisation levels.
- ml/reports/PLACEHOLDER-m4-diagnostics1.json: 152 training inputs, three original
  graphs × disabled/basic/extended/all profiles. Every profile FAILS. Float/all max
  raw/probability error 0.000323296/0.00000411753; other float profiles each
  0.000365257/0.00000465196; zero flips. INT8 per tensor every profile
  59.860615/0.644490 with 32 flips; per channel 82.789173/0.787463 with 36 flips.
  Top-level DIAGNOSTIC ONLY; command success is not acceptance.
- Float/all feature error 0.0000212193 induces Python-head error 0.000322342;
  remaining head/runtime discrepancy 0.0000114441. Effective coefficient max
  59.6626235, L1 sum 1,362.464654. Evidence points mainly to amplified feature drift;
  underlying operator cause unknown. INT8 has large feature/head drift. Maxima
  can occur on different components and cannot be added as an exact decomposition.
- Separate instrumented copies expose head-input features. Measured original/
  instrumented logit difference is 0 in every profile. Copies have PLACEHOLDER/
  never-bundle metadata and fail the strict deployment interface. Graphs and
  per-component outputs/failures remain ignored data/; aggregates only tracked.
- Saved Python backbone has 34 BatchNorm2d modules; retained float ONNX graph has
  none after export folding. Preserving them is the next hypothesis to investigate.
  ADR-012 toy-model diagnostic workaround remains in force; it cannot close M4.

## Observed verification

- New diagnostic suite: **8 PASS in 5.92s**, 12 legacy-export warnings. Tests corrupt
  every non-training image to prove isolation; retain original graph hashes;
  reject graph/fit tampering; test profiles, affine arithmetic, instrumentation
  and confined paths. No existing test weakened/skipped.
- Diagnostic CLI exit 0: DIAGNOSTIC ONLY; every original-graph profile fails parity.
- bash scripts/check.sh: exit 0, **312 ML tests PASS in 35.90s**, 18 exporter
  deprecation warnings; Android SKIPPED; RESULT PASS. No APK claim.
- Root checks: **6 PASS in 0.071s** after documentation updates. No toolchain/dependency/checkpoint/dataset acquisition.
  Existing 42-package export lock retained; no protected edits/publish/push/messages.

## Open blockers and limits

Selected-baseline float and INT8 parity remains the implementation blocker. Two
original export attempts and new training-only diagnosis retained; every current
baseline export rejected. No M4 HANDOFF/review request. Suitable approved real
clinical data, clinical/ethics/legal/native-language validation and weight-notice
approval remain absent. Finite desktop diagnostics establish neither unseen-input
parity nor mobile/clinical safety/performance.

## Next concrete step

Predeclare a BatchNorm-preserving export strategy, verify actual node presence,
prevent runtime re-fusion, and compare training-only inputs first. Keep the same
selected saved baseline, tensor interface, fits and ADR-011 budgets. Folding is a
hypothesis; if it fails, retain the evidence and isolate the next operator using
training-only taps. Declare mixed-precision/quantised operator scope before the
next frozen evaluation. Request REVIEW M4 only when every acceptance item is met.
