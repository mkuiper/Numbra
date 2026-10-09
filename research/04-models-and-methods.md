# Models, task framing and evaluation plan

Evidence accessed **2026-10-09**. This document specifies future work; no model
was trained, exported or benchmarked in M0. Under
[ADR-002](../decisions/ADR-002-dataset-selection.md), all task data are generated
synthetic fixtures. Every resulting model and metric surface must say
**PLACEHOLDER — synthetic demonstration, not clinically validated**.

## Architecture and weight candidates

MobileNetV3 was designed with mobile CPU constraints in mind; its authors present
Small and Large variants. This does not establish speed or clinical fitness on
Numbra devices. [Original paper](https://arxiv.org/abs/1905.02244).
EfficientNet is another transfer-learning candidate, with compound scaling of
depth, width and resolution; a particular Lite checkpoint's rights and export
support would need a separate audit. [Original paper](https://arxiv.org/abs/1905.11946).

| Candidate | Verified primary evidence | Numbra disposition |
| --- | --- | --- |
| `timm/mobilenetv3_small_100.lamb_in1k` | Publisher's [model card](https://huggingface.co/timm/mobilenetv3_small_100.lamb_in1k/raw/main/README.md) declares Apache-2.0, ImageNet-1k training, approximately 2.5M parameters and 224-pixel input. [File listing](https://huggingface.co/timm/mobilenetv3_small_100.lamb_in1k/tree/main) exposes a safetensors checkpoint; binary anonymous retrieval has **not** been tested. | Selected candidate: frozen pretrained features plus a small binary head trained on synthetic data. Publisher-declared weight licence is evidence, not a legal warranty about every pretraining image. No ImageNet image acquisition. |
| Keras MobileNetV3Small | [API](https://keras.io/api/applications/mobilenet/mobilenet_models/) exposes ImageNet or random initialisation; [Keras code licence](https://github.com/keras-team/keras/blob/master/LICENSE) is Apache-2.0. Weight-specific permission was not separately verified here. | Alternative architecture; do not equate library code licence with all weights. |
| Google Derm Foundation | [Publisher card](https://huggingface.co/google/derm-foundation) describes a BiT ResNet101x3 embedding model, 448-pixel input and 6,144-dimensional output, under HAI-DEF terms. Download requires login and agreeing to conditions. | Excluded during unattended work. Mobile conversion, size and target-task performance **UNVERIFIED**; not a drop-in leprosy classifier. |
| TorchVision pretrained backbones | [Official documentation](https://docs.pytorch.org/vision/stable/models.html) explicitly warns pretrained models may have dataset-derived terms separate from the library licence. | Useful comparison, but no blanket permission inferred. |

**Selected design**, recorded in [ADR-005](../decisions/ADR-005-baseline-runtime.md):
PyTorch/timm on CPU; remove the ImageNet classifier, freeze the feature extractor
in evaluation mode and train a regularised binary linear head. Cache features to
make repeated synthetic experiments cheap. Record the actual checkpoint revision,
SHA-256, declared licence, dependency pins and deterministic seed. Later unfreezing
is an optional controlled experiment, not required for the first baseline. Report
hardware, thread count, runtime and reproducibility limitations; no CPU speed has
been measured yet. If anonymous checkpoint access fails twice, use the ADR's
labelled synthetic-pretraining transfer workaround rather than calling random
initialisation transfer learning.

Start **image-only**. Optional later metadata fusion can concatenate standardised
numeric features and categorical/missingness indicators to frozen image features,
with preprocessing fitted on training groups only. The
[AI4Leprosy study](https://pmc.ncbi.nlm.nih.gov/articles/PMC9903738/) motivates
comparing images and metadata; its results do not validate Numbra. Compare
image-only, metadata-only and fused scores on the same splits. Site, patient ID,
diagnostic confirmation and clinician's final diagnosis must not become predictors.
Sensation and urgent symptoms remain explicit rule inputs even if a research
fusion variant later uses them. Missing or declined answers are not zeros.

## Task framing: disease evidence and action are separate

[ADR-001](../decisions/ADR-001-task-framing.md) accepts a binary **image evidence
score** for explicitly labelled leprosy versus explicitly labelled comparison
conditions, followed by a separate transparent referral rule. In synthetic runs
the target is an invented fixture label, never the presence of an actual disease.
Retain the hierarchical taxonomy, PB/MB, reaction, original diagnosis and label
provenance from [the dataset survey](03-datasets.md) for later stratification.
Unresolved/provisional labels are excluded from primary supervised accuracy
metrics and reported separately; `refer_for_review` is an action flag, not a class.

| Framing | Tradeoff and decision (project reasoning) |
| --- | --- |
| Direct binary `refer / don't refer` from a photo | Rejected: a control diagnosis may still need referral, and a photo cannot assess the cardinal sensory sign. A negative action target would conceal symptom overrides. |
| Binary disease-evidence score plus rules | Selected for the smallest demonstrator. The UI shows an action and reasons, never disease absence or a clinically calibrated percentage. |
| Multiclass differential | Preserve labels for future research; defer predictions until adequate confirmed examples and clinically reviewed class coverage exist. |
| Top-k list | Defer: inclusion of leprosy somewhere in a list does not measure sensitivity of a referral action, and may promote volunteer diagnostic overconfidence. |

WHO's cardinal signs and the implications for photographs are sourced in the
[clinical document](01-clinical-background.md) and
[WHO fact sheet](https://www.who.int/news-room/fact-sheets/detail/leprosy).
The decision is a POC safety design, not a validated Nepal clinical protocol.
Intact sensation does not exclude leprosy, especially MB disease; the
[ILA report, sections 2.1–2.2](http://ila.ilsl.br/pdfs/v70n1s1a05.pdf) explains
the limitations of an anaesthetic-patch-only criterion. Volunteer touch-test
sensitivity in Nepal remains UNVERIFIED. Photo and touch results cannot clear
the person of disease.

## Proposed transparent rule precedence

Evaluate all symptoms before interpreting a score. Return the highest-priority
action plus every applicable reason, rule version, model version and quality state.

1. New weakness, eye pain/difficulty closing an eye, or other clinically reviewed
   urgent deterioration → **refer urgently**, regardless of image or score.
2. Reduced/absent patch sensation, concerning nerve symptoms, or volunteer concern
   → **refer**, regardless of score. Also refer for **>5 patches; many/widespread
   patches with unknown count; raised, nodular or thickened skin/earlobes; eyebrow
   loss; painless hand/foot wounds or burns; or reported close contact with the
   presenting skin concern**. Intact sensation and low score cannot cancel these
   triggers. These are clinical-review proposals, not validated MB detection rules.
   A deterioration flag may elevate urgency.
3. Unknown/uncertain/not-tested sensation or incomplete required patch/skin/nerve
   concern assessment, unusable image, missing/failed/non-finite
   model output → **refer for clinical review**; offer a retake without delaying
   symptom-based action. Never silently substitute a low score on failure.
4. Usable photo, completed symptom assessment and score at/above the frozen
   threshold → **refer**.
5. Otherwise → **low concern from photo; refer if sensation loss or change**.
   This is qualified photo wording, not exclusion of disease or a discharge decision.

Duration contextualises the summary and cannot rule out disease. Contact history
stays optional/private; absent/unknown/declined contact never cancels referral and
does not alone force a positive answer. Other required concern fields use explicit
yes/no/uncertain; uncertain/declined/omitted required fields route to rule 3, while
any positive trigger still routes to rule 2. Patch count never assigns PB/MB.
Even with all negative answers, disease may be missed; humans must decide whether
any low-photo outcome should exist in a future pilot. Urgent candidates derive from
[WHO reaction guidance](https://www.who.int/publications/i/item/9789290227595)
and [the clinical draft](01-clinical-background.md); symptom cutoffs, timing and
local competency remain **UNVERIFIED**. Future M6 tests must cover each rule,
overlapping reasons, missingness, score boundaries, failures and monotonicity
(adding a red flag cannot lower urgency). **Planned M6 regression cases:** sensation
present, usable photo and score zero, paired separately with each new trigger,
must refer; >5 versus exactly 5, widespread/unknown count, contact declined,
uncertain morphology and omitted required fields must preserve the stated rules.
Adding any trigger must suppress low concern at every finite model score, even
under overlap with urgency/failure. These tests are planned, not executed in M0.
Test every returned outcome against
negative-diagnosis language, including translated equivalents under native review.
Every POC result includes **PLACEHOLDER**.

## Proposed reproducible evaluation protocol

These are project specifications for M1–M4, not claimed empirical findings.

- **Unit and splits:** use patient/group ID, with source namespacing. Merge
  duplicate-connected groups across sources before splitting; quarantine conflicting
  labels. A lesion ID does not prove patient independence. If real grouping cannot
  be established, report that limitation and exclude the source from the primary
  patient-independent claim. Assign train, calibration/threshold-validation and
  frozen test groups by a recorded seed. Synthetic fixtures have explicit groups
  and several sources, with both labels in each source.
- **Unit of scoring:** for the initial single-photo protocol, choose one index
  image per group by a prespecified deterministic rule before inspecting scores.
  Report image-level secondary results separately. This prevents patients with
  many photos from dominating the primary estimate. A future maximum-over-photos
  rule would require a new prespecified workflow and threshold evaluation.
- **Calibration:** split validation groups into calibration-fit and
  threshold-selection subsets when counts permit. Fit temperature scaling to
  logits on calibration-fit only, freeze it, then choose the threshold. If either
  subset lacks a class, report calibration/threshold selection as unavailable;
  do not fit on the test set. Temperature scaling is supported by
  [Guo et al.](https://arxiv.org/abs/1706.04599), not proven to correct Nepal domain
  shift. Report Brier score, log loss, reliability bins with counts and ECE with
  its bin definition, before and after calibration. A sigmoid is not proof of
  calibrated clinical risk.
- **Primary operating point:** target validation sensitivity **≥0.95**, an
  engineering demonstration target pending humans, not a clinically established
  requirement. Predict positive for `score >= threshold`; choose the highest
  observed threshold meeting that target on threshold-validation groups (hence
  the most specific qualifying threshold). Save threshold, target, counts,
  selection rule and split hashes. Freeze it for test and held-out source; report
  actual sensitivity and specificity with no promise test sensitivity reaches
  0.95. **Proposed minimum:** 100 independent positive and 100 negative groups
  in threshold-selection, after a separate calibration-fit subset of at least
  20 groups per class. These are conservative engineering guardrails, not a
  clinical sample-size calculation. Below these counts, mark selection
  `unavailable_insufficient_groups` and use an explicitly unselected refer-all
  fallback (`threshold=0` for bounded probabilities); never manufacture a
  “selected” threshold from a tiny fixture. Small unit fixtures exercise that
  fallback; generated M3 runs should meet the counts in each feasible source fold.
  Save TP/FN counts and the **lower endpoint of a two-sided 95% Clopper–Pearson
  interval** with sensitivity, on selection, frozen test and reported subgroups.
  [NIST exact binomial interval construction](https://www.itl.nist.gov/div898/handbook/prc/section2/prc241.htm).
  If the point estimate meets 0.95 but its lower bound does not, label it
  `empirical_target_only`, never “supported sensitivity ≥0.95”. Selection-set
  intervals are descriptive after threshold search; use the independent frozen
  test for a fixed-threshold interval. Synthetic intervals concern fixtures only.
- **Secondary requested endpoint:** sensitivity at validation specificity
  **≥0.80**, a separate illustrative target. Choose the lowest threshold meeting
  that specificity, with a prespecified above-maximum sentinel for the all-negative
  classifier if needed; apply unchanged to test. Report unattainability/degeneracy
  and class counts. Do not confuse this endpoint with specificity at the primary
  high-sensitivity operating point.
- **Report:** confusion counts, ROC AUC (only with both classes), primary and
  secondary threshold results, calibration and 95% uncertainty intervals.
  Bootstrap whole groups with a fixed seed, recording resample count and invalid
  single-class resamples; tiny groups need explicit instability warnings. For
  synthetic POC results, intervals describe generated fixtures only. No Nepal
  prevalence, PPV, NPV or clinical accuracy claim follows from synthetic scores.
- **Leave one source out:** train, calibrate and select thresholds using only the
  other sources, then evaluate the untouched source. Exclude all groups linked
  to held-out records from training, even across source names. Produce at least
  one fold and ideally all feasible folds; do not transfer a model trained on
  the held-out source into its fold. One-class folds get explicit unavailable
  specificity/AUC fields, never fabricated zeros. Synthetic source shifts test
  pipeline mechanics, not external clinical validity.
- **Breakdowns:** source, skin tone (preserve annotation scheme and missingness),
  PB/MB and classical/reactional/atypical presentation where explicit labels exist.
  Include group/class counts, missing-label fraction and uncertainty; no tone or
  subtype inferred from pixels to fill gaps. Generated colour categories must
  say **synthetic colour strata**, not Fitzpatrick/Monk fairness evidence.
- **Abstention and full workflow:** report failure/quality-abstention rates and
  reasons across all attempted screenings. Report successful-image metrics and
  the full referral-rule confusion table separately; include failed photos in
  workflow denominators. Compare symptom-only to symptom-plus-image referral
  rate, missed confirmed cases and urgent actions on the same groups. A model's
  softmax confidence alone is not an out-of-distribution detector.

Future tests should assert disjoint patient/duplicate groups, held-out-source
exclusion, calibration/threshold isolation, ties at thresholds, one-class and
empty subsets, transparent unavailable metrics, count guards, exact-bound
zero/all-success cases and insufficient-count fallbacks.
The model card must record
data/licences, intended use, excluded populations, input spec, rules, thresholds,
evaluation limits and **PLACEHOLDER** status. No model promotion follows from a
green synthetic report; a clinical programme needs independent representative
validation and human governance.

## Open questions

- What sensitivity target, acceptable referral burden and missed-case interval do local clinicians require?
- Are pretrained-weight provenance and publisher-declared permission sufficient for later distribution?
- Which sensory, urgent and missing-answer rules can Nepal partners approve and teach reliably?
- What representative confirmed external cohort can establish generalisation, calibration and subgroup performance?

## Confidence

High for the checked model documentation and separation of photo evidence from
referral; medium for software feasibility before conversion/CPU testing; low for
clinical threshold or deployment fitness because all task data remain synthetic.
