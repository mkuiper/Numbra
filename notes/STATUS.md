# Status

Updated: 2026-10-09T15:59:42Z

Current milestone: **M4 — On-device model export**, in progress. NEXT_ACTION:
CONTINUE. M0–M3 gates exist (PASS WITH CHANGES); no M4 gate, app or APK.
Every task model/result remains **PLACEHOLDER**, synthetic-only under ADR-002.
Every failed export remains rejected; diagnostic copies are never bundles.

## M4 acceptance status

- **Quantised ONNX Runtime Mobile export: BUILT, ACCEPTANCE INCOMPLETE.** Two
  retained INT8 QDQ graphs fail parity; both calibrated on all/only 152 training
  components. No new fit or scope selection. ADR-012's labelled toy diagnostic
  workaround remains in force; Android operator/ABI support is unverified.
- **Exported/Python parity: FAIL, budgets unchanged.** New joint promoted stem/
  all-BN graph fails training raw/probability budgets: maxima
  0.000200748/0.00000256741 against 0.0001/0.000001, zero flips. Worse maxima
  than BN-only, lower means; both controls reproduce retained evidence exactly.
  No frozen test/held-out/stress inference, reference/fit/budget change or
  deployment selection. All earlier failures retained.
- **Size ≤20 MB / preprocessing written and tested: BUILT.** New float32/float64
  joint diagnostic 6,265,822 bytes (runtime 6,165,050), BN-only 6,255,113,
  original float 6,095,579 and INT8 1,730,515/1,861,702. RGB letterbox,
  float32 1×3×224×224 → raw_logit [1] unchanged. No accepted deployment-metadata
  package or Android decoding/preprocessing.

## This iteration's evidence

- Predeclared and committed ADR-018, queued for humans. New export_joint embeds
  ADR-016's promoted patch/MatMul stem with one float32 output boundary;
  validates saved geometry/parameters/connectivity. Composes all 34 ADR-017 BN
  expressions; all other serialized nodes/original initializers/interface retained.
  BN substitution now matches BN boundaries independently of Conv substitutions.
  Original checkpoint, Conv/head/activation reference, fits and state unchanged.
- ml/reports/PLACEHOLDER-m4-joint1.json: all 152 training components only.
  Joint raw/probability violations 25/32 (BN-only 23/32, preserved 26/29).
  Maxima 0.000200748/0.00000256741; means 0.0000554888/0.000000648783.
  All graphs FAIL. Max feature drift 0.0000152588; induced Python-head max
  error 0.000206947. Separate maxima are not additive causal accounting.
- Actual disabled CPU/sequential/two intra-op/one inter-op runtime audits pass
  exact stem/BN expressions, constant bits and float32 boundaries. Joint retains
  52 Conv, one promoted MatMul and one Gemm. ORT removes unused original
  initializers and expands HardSwish. Reshape allowzero=0 declared explicitly
  to preserve exact auditing of its runtime serialization. Full byte identity
  of every other runtime node is not asserted. Tap/original logits equal.
- Separate audit PASS: aggregate/private equality, recomputed parity, ordered
  training IDs, saved-model/source/dependency/preparation provenance, exact
  reproduction of both controls and 14 graph records. Graphs/weights/details
  ignored. Updated ADR, HUMAN-QUEUE, export/setup docs and ML README.

## Observed verification

- Initial joint/BN subsets: 22 PASS / 2 FAIL in 9.75s and 10.09s (56 warnings).
  Fixed production BN matching and explicit Reshape default. Existing assertions
  retained; added default-attribute corruption regression. Corrected subset:
  25 PASS in 10.19s, 58 exporter warnings. No test weakened/skipped/deleted.
- CLI exit 0: DIAGNOSTIC ONLY; independent audit PASS, M4 incomplete.
- bash scripts/check.sh exit 0: 358 ML tests PASS in 56.27s, 116 exporter
  deprecation warnings; Android SKIPPED, RESULT PASS. No APK claim.
- Root repository-contract checks: 6 PASS in 0.078s after documentation changes;
  final 6 PASS in 0.074s after all iteration records.
  git diff --check clean; NEXT_ACTION exactly CONTINUE.
- No install/dependency/checkpoint/dataset acquisition, protected edit,
  review.sh, REVIEW/CHECK/GATE write, publication/push or external message.

## Open blockers and limits

Selected-baseline float and INT8 parity remains the implementation blocker.
Joint substitution fails both budgets and worsens BN-only maxima. No current
baseline export is accepted. Float64 Android compatibility/performance, unseen
input parity, clinical data approval, clinical/ethics/legal/native-language
validation and weight-notice approval remain unresolved.

## Next concrete step

Predeclare complete saved Conv/BN same-input replay on training only, expanding
ADR-015's two pairs to every 53 Conv/34 BN. Compare all BNs against native and
both existing promoted coefficient recipes, with all native Conv replays and
complete signed propagation/kernel accounting. Use this to identify actionable
residual arithmetic before more whole-graph replacements. No favourable layer
subset, frozen evaluation or fit/budget change. Declare selective static QDQ
scope from training evidence before new quantisation/frozen evaluation and
resolve float64 mobile support before bundling. REVIEW M4 only after acceptance.
