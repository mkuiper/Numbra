# Working glossary

These are research and engineering terms, not field instructions.

| Term | Meaning in this project |
| --- | --- |
| Hansen's disease | Another name for leprosy; see the WHO source below. |
| PB / MB | Paucibacillary / multibacillary treatment classifications. WHO defines PB as 1–5 lesions without bacilli demonstrated in a smear; MB includes more than five lesions, nerve involvement, or a positive smear. The app will not assign either from a photo. |
| Cardinal sign | A clinical finding sufficient for clinical diagnosis under WHO criteria; the photo model does not establish one. |
| Provisional label | A suggested condition awaiting confirmation; it is not training ground truth. |
| Confirmed label | A label accompanied by a recorded confirmation method and provenance; this does not imply every method has equal reliability. |
| Patient/group split | Proposed evaluation rule: all images of the same patient or defensible grouping belong to one split. |
| Held-out source | A source excluded from training and threshold selection to probe performance on a different acquisition setting. |
| PLACEHOLDER | A synthetic or stub model demonstrating mechanics without evidence of clinical utility. |
| Referral outcome | A rule-engine action, distinct from the image model's score or a disease diagnosis. |

Clinical definitions: [WHO leprosy fact sheet](https://www.who.int/news-room/fact-sheets/detail/leprosy),
23 January 2026, accessed 2026-10-09. Other rows define proposed project conventions.
The clinical-background and methods research will extend this glossary with
reaction, macule, calibration, and operating-point terminology after sourcing.

## Open questions

- Which locally understood Nepali terms should replace the English clinical vocabulary?
- Which confirmation methods will the local clinical partner accept for future labels?

## Confidence

High for the linked WHO definitions; medium for proposed project conventions,
which remain subject to milestone review.
