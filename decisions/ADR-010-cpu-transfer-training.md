# ADR-010 — Fixed CPU PLACEHOLDER transfer training and conditional bootstrap

Date: 2026-10-09

Status: Accepted (autopilot) — pending human review

## Context and evidence

ADR-005 selected timm MobileNetV3Small frozen ImageNet features; ADR-002 permits
generated task data only. Anonymous metadata/access verified 2026-10-09:
[pinned publisher card](https://huggingface.co/timm/mobilenetv3_small_100.lamb_in1k/blob/1824797e7887cbec1990e4adbd6675960a36c589/README.md)
declares Apache-2.0 and ImageNet pretraining. The anonymous
[repository API](https://huggingface.co/api/models/timm/mobilenetv3_small_100.lamb_in1k?blobs=true)
returned private=false, gated=false, revision
`1824797e7887cbec1990e4adbd6675960a36c589`, safetensors size 10,241,912
and SHA-256 `46d2c063b18125884c48937afa4c49e18128869e52e8db96df48bf0a4d7ff697`.
Anonymous retrieval succeeded and matched those bytes/checksum. README/config
checksums are pinned in pretrained.py. No account, agreement, clinical or
ImageNet image acquisition. Publisher licence declaration is not a legal warranty
about all pretraining-image rights; humans must review notices before distribution.

The [official PyTorch previous-version instructions](https://pytorch.org/get-started/previous-versions/)
(accessed 2026-10-09) supply torch 2.8.0 / torchvision 0.23.0 CPU wheels.
Use those CPU versions, timm 1.0.22, safetensors 0.6.2 and huggingface-hub 0.36.0.
The latter is pinned for compatibility rather than adopting the resolver's latest
major hub version. A 35-wheel full runtime/test/build lock stores SHA-256 per wheel
for CPython 3.12 Linux x86_64. Other platforms are unverified. Pip validates hashes;
the training command rejects installed version drift and records the lock hash.

## Options

- Fine-tune a backbone / choose hyperparameters on validation: deferred. Synthetic
  metrics do not justify selection complexity or claim clinical representation.
- Frozen eval-mode pretrained embeddings + train-only standardisation/linear head:
  selected, reproducible and small enough for the upcoming export.
- Use publisher centre-crop geometry: retain as future comparison; use the existing
  deployment proposal's full-image letterbox consistently throughout task training.

## Decision

Load only the pinned local safetensors into timm with pretrained=False and strict
state-key checking, then remove its ImageNet classifier. Freeze all remaining
parameters and eval-mode buffers (including BatchNorm/dropout), check backbone
state hashes before/after extraction/training. Extract one first-sorted record-ID
image per preparation component via ADR-009. No augmentation or fitted image
transform. Fixed RGB uint8 bilinear letterbox at 224: half-pixel coordinate mapping,
clamped edges, no antialias, scaled dimensions half-up, RGB-128 centred padding,
odd remainder right/bottom, interpolated channels half-up before ImageNet
normalisation. This differs from publisher pretraining geometry. M4/M6 still own
export/decode/Android parity; M3 accepts oriented loader RGB, not arbitrary photos.

Fit feature population mean/std only on training components; replace std<1e-6 by
one, record its hash. Train one binary linear head with seeded full-batch AdamW,
300 epochs, learning rate 0.03, weight decay 0.01. Seed 20261009, two CPU threads,
feature batches 16. These are fixed engineering defaults, not tuned after observing
test scores. No early stopping, class weights, metadata fusion or sweep. Config
overrides are explicit and recorded; no claim of optimum performance. Save a
single raw-logit model with scaling buffers in ignored data/. Apply temperature/
sigmoid once in the later scoring layer, never inside the saved model.

Use the predeclared shapes-v2 selection_exercise fixture, source C held out, for
the initial operating-point demonstration; also run the smaller default fixture
to demonstrate unavailable selection and the unselected refer-all fallback.
This is a single held-out source (one leave-one-source-out fold), not rotation.
Use ADR-009 isolated calibration/thresholds without lowering its count guards.

Add ordinary, unstratified component bootstrap with 1,000 seeded draws per test/
held-out overall/source/synthetic-colour cohort at the frozen primary endpoint.
Use percentile 95% linear quantiles for sensitivity, specificity, tied-rank AUC,
Brier and ECE. Draw whole components, each represented by its index photo, never
individual views; do not pool partitions. Single-class draws contribute available
metrics only and report valid counts. Derive cohort seeds from the first four
SHA256 bytes of seed:split:cohort. This is conditional uncertainty at a fixed model,
temperature/threshold, **not** total training/fitting uncertainty. Exact binomial
intervals remain alongside bootstrap; tiny strata are unstable. No skin-tone/
fairness evidence follows from procedural colour bands.

Write aggregate JSON evaluation and a PLACEHOLDER model card in ml/reports/.
Write per-component predictions/weights only in ignored data/. Retain manifest,
preparation report, checkpoint, source tree, lock, frozen state, fit scores and
artifact hashes; record actual dependency versions, hardware, git revision/dirty
flag, config and elapsed time. Refuse overwrite and unsafe output paths.
Reproduction compares model/prediction hashes and report fields excluding clock,
elapsed time, git dirty flag and output directory. Equality is expected only in
the same pinned CPU environment, not promised across hardware.

## Consequences and revisit trigger

No clinical performance, calibrated risk, lesion/pure-neural representation or
field-safety claim. Every model/report/card/UI remains PLACEHOLDER. Humans must
review engineering thresholds/counts, weight rights, geometry and the one-fold
scope. Quantisation/parity/deployment belong to M4 onward; no export or APK here.
Revisit if independent licensed real data becomes available, a fit hits numerical
bounds, conversion fails, or device tests require a different implementation.
Never tune frozen test/source-C inputs to improve a report or silently widen parity.

## Open questions

- Do humans accept fixed training defaults, letterbox geometry and conditional bootstrap?
- Are publisher-declared permissions/notices sufficient for a future distribution?
- Which independent licensed cohorts/protocol replace these artificial targets?

## Confidence

High for observed anonymous access and tested synthetic software mechanics;
no evidence of clinical validity or on-device performance.
