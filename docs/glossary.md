# Working glossary

These are research and engineering terms, not field instructions.

| Term | Meaning in this project |
| --- | --- |
| Hansen's disease | Another name for leprosy; see the WHO source below. |
| PB / MB | Paucibacillary / multibacillary treatment classifications. WHO defines PB as 1–5 lesions without bacilli demonstrated in a smear; MB includes more than five lesions, nerve involvement, or a positive smear. The app will not assign either from a photo. |
| Cardinal sign | A clinical finding sufficient for clinical diagnosis under WHO criteria; the photo model does not establish one. |
| Reaction / neuritis | An inflammatory episode associated with leprosy / inflammation of a nerve. Reactions can damage nerve function and require skilled assessment; see WHO's reaction guidance below. |
| Macule / patch | A flat area of changed skin colour, usually under 10 mm / a larger flat area, usually over 10 mm, in the cited clinical terminology reference. Not a diagnosis. |
| Papule / plaque / nodule | A small palpable raised lesion / a larger palpable lesion / a deeper firm lesion extending into the dermis or subcutaneous tissue. See the clinical reference below; volunteers need reviewed plain-language equivalents. |
| Sensory-test status | Proposed capture values: present, reduced, absent, uncertain, not tested. Unknown/not tested is not a normal examination. |
| Provisional label | A suggested condition awaiting confirmation; it is not training ground truth. |
| Confirmed label | A label accompanied by a recorded confirmation method and provenance; this does not imply every method has equal reliability. |
| Patient/group split | Proposed evaluation rule: all images of the same patient or defensible grouping belong to one split. |
| Held-out source | A source excluded from training and threshold selection to probe performance on a different acquisition setting. |
| PLACEHOLDER | A synthetic or stub model demonstrating mechanics without evidence of clinical utility. |
| Referral outcome | A rule-engine action, distinct from the image model's score or a disease diagnosis. |
| Sensitivity / specificity | Evaluation definitions: TP/(TP+FN) / TN/(TN+FP), for an explicitly stated positive class, unit (image/patient) and threshold. Undefined when the relevant denominator is zero. |
| Top-5 recall | Whether the true label appears among five suggestions; distinct from a correct single prediction or a successful referral. |
| Abstention | Proposed workflow: defer an unusable input or uncertain assessment to retake/clinical review; do not silently call it negative. |

Clinical definitions: [WHO leprosy fact sheet](https://www.who.int/news-room/fact-sheets/detail/leprosy),
23 January 2026; reactions/nerve assessment:
[WHO reaction guidance](https://www.who.int/publications/i/item/9789290227595).
Morphology terminology: [Benedetti, MSD Manual Professional, August 2026](https://www.msdmanuals.com/professional/dermatologic-disorders/approach-to-the-dermatologic-patient/description-of-skin-lesions).
All accessed 2026-10-09; text only, no clinical photos downloaded. The MSD page
is an authored clinical reference, not a primary diagnostic-performance study.
Other rows define evaluation notation or proposed project conventions. The pending
methods document will specify calibration and operating-point selection.

## Open questions

- Which locally understood Nepali terms should replace the English clinical vocabulary?
- Which confirmation methods will the local clinical partner accept for future labels?

## Confidence

High for the linked WHO definitions; medium for proposed project conventions,
which remain subject to milestone review.
