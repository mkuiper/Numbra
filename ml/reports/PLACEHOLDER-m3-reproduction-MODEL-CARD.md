# PLACEHOLDER model card — PLACEHOLDER-m3-reproduction

**PLACEHOLDER — synthetic demonstration, not clinically validated.** Intended use: software pipeline/offline integration
testing on generated pixels only. No clinical or volunteer screening use.

Frozen timm MobileNetV3Small ImageNet features, train-only standardisation and a
binary linear head, fixed full-batch AdamW. No metadata fusion. Target 0 is
**synthetic square**, target 1 is **synthetic circle**. These are artificial shape
targets, never disease labels. Report: [PLACEHOLDER-m3-reproduction.json](PLACEHOLDER-m3-reproduction.json).

Task data: shapes-v2 generated under ADR-002/008, source-dependent texture/channel
changes and intentional 0.10 group-level rendered-shape flips. One first-sorted
record-ID image per duplicate-connected component; excluded components are
counted in the JSON report. No patient data or ImageNet images acquired.
Training components: 152; scaling and head fitting use train
only. Calibration and threshold selection use separate frozen partitions.
No early stopping, hyperparameter search or test/source-C tuning.

Primary endpoint status: **selected**; evidence **empirical_target_only**;
threshold 0.4008 (full precision in JSON),
inclusive score >= threshold. Target sensitivity 0.95 is illustrative, never a
clinical promise. Fallback: none. **Observed sensitivity below the illustrative target in: held_out.** Calibration status:
fitted; temperature 19.1500,
boundary none. Scores are not calibrated
clinical risk. JSON includes secondary specificity endpoint, exact binomial
intervals, reliability bins, ECE, Brier, pre-calibration metrics and component
bootstrap percentile intervals conditional on the fixed model/operating point.

| PLACEHOLDER partition | Components | TP/FN/TN/FP | Synthetic sensitivity [95% exact interval] | Synthetic specificity [95% exact interval] | AUC | Brier |
| --- | ---: | --- | --- | --- | ---: | ---: |
| test (frozen selected point) | 52 | 26/0/4/22 | 1.0000 [0.8677, 1.0000] | 0.1538 [0.0436, 0.3487] | 0.7663 | 0.2110 |
| held_out (frozen selected point) | 256 | 117/11/10/118 | 0.9141 [0.8514, 0.9563] | 0.0781 [0.0381, 0.1390] | 0.5925 | 0.2483 |

**Single held-out source (one leave-one-source-out fold):**
synthetic-source-c. No source rotation or independent
clinical external validation. Per-source and **synthetic colour strata** results
are in JSON; they overlap and cannot establish skin-tone fairness. Human skin-tone
labels are absent. Source/colour cells below 20/class suppress AUC, calibration bins
and bootstrap; this is an engineering display guard, not a real-data privacy policy.
Small strata/single-class bootstrap draws have explicit valid
counts or unavailable metrics. Calibration-fit metrics are in-sample; threshold-
selection intervals are descriptive after search. Bootstrap excludes training,
calibration and threshold-fitting uncertainty.

Preprocessing: RGB 224-pixel bilinear letterbox with RGB-128 padding, explicit
half-pixel coordinates and half-up uint8 rounding, ImageNet normalisation;
differs from publisher centre-crop. M4/M6 must test exported/Android parity.
Model output is one uncalibrated logit; apply saved temperature/sigmoid once.
Weights live only under ignored data/; checksums and full run provenance are in
JSON. Publisher-declared Apache-2.0 pretrained licence is separate from code/data
and is not a warranty about all pretraining-image rights.

## Limitations and safeguards

No lesion, Nepal, clinical accuracy, diagnosis, calibration or field-safety evidence.
Photos cannot represent pure-neural disease without a skin lesion or establish
sensation loss. Synthetic scores cannot cancel symptom/contact/concern/quality or
missing-assessment referrals. The app must never infer disease absence. Every
downstream app surface must identify this model as **PLACEHOLDER**.
Independent licensed data, patient grouping/duplicate adjudication, prospective
clinical validation, clinical/ethics/legal approval and native Nepali review remain
human work. No export, on-device performance or APK is claimed by M3.

## Open questions

- Do humans approve ADR-005/008/009/010, training/preprocessing/fit choices and the one-fold scope?
- Which licensed independent clinical cohorts and evaluation protocol can replace synthetic targets?

## Confidence

Software verification only; **no confidence in clinical performance**.
