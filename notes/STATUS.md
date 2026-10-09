# Status

Updated: 2026-10-09T19:46:12Z

Current milestone: **M4 — On-device model export**, in progress. M0–M3 gates
exist; M4 acceptance remains incomplete. NEXT_ACTION: CONTINUE. All models and
results **PLACEHOLDER**, synthetic-only; every failed export remains rejected.
No M4 gate, accepted deployment package, app or APK.

## M4 acceptance status

- **Quantised ONNX Runtime Mobile export: built, not accepted.** Original INT8
  QDQ graphs fail parity. No new selected-baseline quantisation fit, selective
  scope, deployment selection or mobile compatibility result.
- **Exported/Python parity: FAIL, budgets unchanged.** Complete ADR-023 training
  replay reproduces prior original logits exactly at all 152 inputs. Preserved
  max raw/probability 0.000240326/0.00000279320 (26/29 violations); rounded BN
  0.000143051/0.00000183769 (13/21 violations); zero threshold flips for both.
  This is training-only diagnostic evidence, never acceptance or clinical proof.
- **Size ≤20 MB / preprocessing written and tested: built.** Original float
  6,095,579 bytes; INT8 1,730,515/1,861,702; rounded diagnostic 6,255,113.
  RGB letterbox float32 1×3×224×224 → raw_logit [1] unchanged. Android
  preprocessing and deployment metadata remain open.

## This iteration

- First runner stopped before decode/forward on 136 unused original BN
  initializers removed by disabled ORT. Audit now allows only directly unused
  original initializers without graph input/output roles to disappear, recording
  every name; all live/Identity/tapped/Constant and retained-bit checks remain.
  Generated nondefault BN plus eight corruption regressions PASS.
- Second runner interrupted deliberately after 25 rows, without completed
  index/report, because compressed persistence/full audits risked the default
  iteration timeout. ADR-023's **PLACEHOLDER storage workaround** uses lossless
  uncompressed NPZ with every bit/type/shape/hash/order/metric check preserved.
  Reader supports previous compressed evidence without rewriting it. New
  ZIP_STORED/both-format regressions PASS; storage benchmark 2.336s vs observed
  roughly 28s/input overall compressed run; these are distinct timing scopes.
- Third runner completes all 152 ordered training inputs and all 159 computational
  nodes on both unchanged graphs/input origins, including every Conv/BN control.
  Setup reconstructs 904 serialized/runtime graphs before image decoding;
  complete final reconstruction PASS precedes report publication.
  Aggregate: ml/reports/PLACEHOLDER-m4-remaining-training3.json; readable derived
  summary: ml/reports/PLACEHOLDER-m4-remaining-training3-summary.json.
- All native replay/capture and whole original/tapped logits exact; all signed
  telescoping residuals zero. Extraction exact at 158 nodes; Gemm alone differs
  (max 0.0000152588 preserved / 0.0000114441 rounded). All 19 HardSwish, nine
  HardSigmoid/nine ReduceMean, final pool/head and 48/53 Conv have same-input
  drift; all 34 rounded BNs match native on both origins. Exact local remaining
  elementwise/layout operations still propagate upstream differences. No sum
  of separate maxima is presented as causal whole-model accounting.
- Ignored completed index: 481,293 unique arrays, 68,554,263,856 archive bytes,
  68,427,202,504 decoded bytes. Old attempts retained incomplete; no weights,
  arrays, individual IDs/logits/failure observations tracked.
- Separate complete audit PASS with image decode, native module calls, ORT
  session construction, eager recipes and evidence writes blocked. Full saved/
  preparation/retained/source/dependency/prior, 904 setup graphs and every
  ordered array/metric/lineage/parity/prior-bit check reconstructed without
  inference or historical authentication. Record:
  ml/reports/PLACEHOLDER-m4-remaining-training3-audit.json. All fingerprints
  agree. Current source snapshot 50f7c65e7b6a6168a17d498be4d663c89b11742f
  independently matches all 33 Python files/full tree; live dependency pins
  exact. Historical ADR-022 source remains 808cc3393ccf1cce95c2feeef91e5a8608b481e4.

## Observed checks

- Focused runtime/runner: 112 PASS, 164 warnings, 35.45s.
- Focused evidence/runner after storage change: 71 PASS, 22 warnings, 34.07s.
- Required check after final code changes: exit 0, **766 ML PASS**, 564 warnings,
  179.41s; Android SKIPPED, RESULT PASS. Six root contracts PASS after report
  documentation (0.070s); git diff --check clean. No APK claim.

## Next concrete step and blockers

Predeclare bounded complete activation/reduction arithmetic experiments and
constant-preserved head isolation from the full retained observations, keeping
all existing Conv/BN/other controls and every ordered training input. The dynamic
vs constant head parameter context is an observed structural difference; kernel
packing causality remains UNVERIFIED. Resolve float arithmetic before a new
selective QDQ fit/frozen acceptance evaluation. No model/reference/fits/budget
change, selected-baseline retraining, frozen inference, acquisition/install,
protected edit, review.sh, REVIEW/CHECK/GATE write, publication or push.
Mobile float64 support/performance, clinical validation, ethics/legal, native
language review and weight rights remain open. Do not start M5 or request M4
review until acceptance.
