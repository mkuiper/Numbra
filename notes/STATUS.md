# Status

Updated: 2026-10-09T14:29:21Z

Current milestone: **M4 — On-device model export**, in progress. NEXT_ACTION:
CONTINUE. M0–M3 gates exist, PASS WITH CHANGES; human review pending. M3 review
follow-through committed as d0e594f. No M4 gate, ONNX graph, Android app or APK.
Every task model/result remains **PLACEHOLDER**, synthetic-only under ADR-002.

## M4 acceptance status

- **Quantised ONNX Runtime Mobile export: PENDING.** ADR-005 runtime retained;
  conversion/runtime dependencies not installed yet. No conversion or quantisation
  experiment attempted. ADR-011 fixes budgets before experiments and requires
  training-only quantisation calibration, remaining-float operator inspection,
  held-out exported evaluation and no silent tolerance widening.
- **Exported/Python parity: FOUNDATION BUILT, ACCEPTANCE PENDING.** New saved-model
  reference/verify entry point strictly restores bundled backbone/scaling/head,
  checks artifact/preparation/state hashes and component metadata, and rescores.
  Actual baseline/reproduction/default: 768/768/384 components, max raw/probability
  errors 0, frozen-threshold flips 0. This is saved Python parity only.
  New tested parity reporter independently checks raw/probability budgets and zero
  flips, all failure cases, and separate conservative-margin added/lost referrals.
  Float budgets 1e-4 raw / 1e-6 probability; quantised 0.1 raw / 0.001 probability,
  zero original-threshold flips. Margin 0.001 cannot rescue a failed parity test.
- **Size ≤20 MB / preprocessing written and tested: PARTIAL.** ML-EXPORT.md writes
  the full RGB letterbox/rounding/normalisation contract; executable SPEC and tests
  remain authoritative. Planned graph input 1×3×224×224 float32 NCHW, raw-logit
  output. Original float safetensors 6,156,620 bytes is not an exported model.
  Actual quantised size/operator/Android decode/ABI checks remain pending.

## M3 post-gate follow-through

- RESPONSE-1 answers all 11 numbered issues. Issues 1–10 implemented/documented;
  real-data disclosure policy and optional clean-checkout wrapper deferred to
  HUMAN-QUEUE. All reviewer human questions relevant to Numbra queued.
- Test of record now runs train_run end to end on a 16-group fixture with an
  explicit toy backbone supplier, including artifacts/provenance/report/card,
  saved-model verification, tamper rejection and overwrite guard. CLI production
  supplier remains pinned/checksum verified; no mock/network/checkpoint in tests.
- Cards now show empirical evidence, confusion/exact intervals, below-target
  held-out sensitivity and per-row fallback markers. Evaluation 1.1.0 nulls
  pre-calibration threshold fields and suppresses source/colour AUC/calibration/
  bins/bootstrap below 20/class, with flags; identical bootstrap cohorts reuse
  seeds/results. All three tracked aggregate reports/cards rebuilt from verified
  stored logits, no retraining or fit changes. Original training provenance and
  report hashes remain; separate reporting revision hashes record the rebuild.
- ADR-010 amended for real-data model-selection/nested CV before calibration,
  display suppression limits and raw/probability/flip checks. ADR-011 queued.

## Observed verification

- Final bash scripts/check.sh: exit 0, **290 ML tests PASS in 27.13s**, Android
  SKIPPED, RESULT PASS. No debug APK claim. Earlier checks 258 PASS in 27.36s and
  288 PASS in 27.09s. No existing tests skipped/weakened.
- New targeted M3 suite: 108 PASS in 12.88s; saved-reference training subset
  36 PASS in 8.17s. Initial new parity subset: 29 PASS / 1 failed because its
  invented extreme fixture did not actually underflow at T=19.15; corrected to
  ±1e6 while retaining the exact expected assertion. Then 30 PASS in 1.92s;
  two additional float32-range guards included in final 290.
- Root repository contract suite: 5 PASS in 0.104s (Builder-attested only).
  pip check: no broken requirements. git diff --check clean before records.
- Current training/reference/reporting code differs from original fd93e34 training
  provenance by documented review changes; original saved weights/logits/fits and
  ignored historical run JSON remain intact. No tolerance/performance tuning.

## Open blockers and limits

No current implementation blocker. Quantisation operator support/parity may fail;
record two genuine attempts before a labelled workaround and amended ADR.
Strict finite-fixture parity cannot establish unseen-input/mobile/clinical safety.
No real task dataset approved; no patient/ImageNet images acquired. Clinical,
legal, ethics, native-language and pretrained-weight notices review still pending.
Synthetic source-C sensitivity remains 0.914063 below 0.95, specificity 0.078125;
no clinical or fairness claim. Small-cell display guard is not a privacy policy.
No publishing/pushes/messages/protected edits or committed data/weights/APK.

## Next concrete step

Read M4 folder/status/harness, verify primary ONNX/PyTorch export and runtime docs,
pin/hash-lock conversion/runtime dependencies in ml/.venv and document installs.
Export original selected PLACEHOLDER baseline float graph and run same-tensor raw/
probability/threshold parity; then static INT8 QDQ with train-only calibration,
independent generated stress inputs, all frozen test/held-out inputs, exported
held-out evaluation, operator/size report. Keep fixed ADR-011 budgets. Request
REVIEW M4 only when every M4 acceptance item has actual passing evidence.
