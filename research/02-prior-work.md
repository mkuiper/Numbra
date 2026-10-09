# Prior work: image assistance, training and referral systems

Evidence accessed **2026-10-09**. This is a targeted landscape survey, not a
systematic review. Searches covered PubMed, IEEE Xplore, arXiv and medRxiv, plus
WHO, implementing organisations and author repositories. No clinical images,
image archives or weights were acquired. No organisations were contacted.
**Reported metrics below belong to those studies, not Numbra.**
Review-1 added targeted journal-domain searches for leprosy AI/imaging in
**Leprosy Review, IJDVL and Indian Journal of Leprosy**, initially omitted.
Search results found [Leprosy Review's 2024 WHO-app commentary](https://leprosyreview.org/article/95/2/20-24030),
[IJDVL's AI review](https://ijdvl.com/?article=f95403cc7ddbe468fc249d9a2284fcb6kOH1AhQgusZg2Q%3D%3D&embedded=true&view-pdf=1)
and [IJL's 2025 research editorial](https://www.ijl.org.in/published-articles/26032025110641/1_Editorial__VMK_Jan_March_2025_final_print_version.pdf).
These are context/commentary, not new primary diagnostic-accuracy estimates;
no metrics or image rights are borrowed from them. The search remains targeted,
not exhaustive or a systematic review.

## AI4Leprosy — multimodal research, not a transferable clinical guarantee

Barbieri et al. (Fiocruz, Microsoft and Novartis Foundation collaborators) studied
222 patients at a Brazilian referral centre, with 1,229 images and 585 metadata
sets. Their CNN image model and clinical metadata model fed a combined approach;
the abstract reports elastic-net logistic regression accuracy 90% and AUC
96.46%. Its figure caption separates 182 training patients from 40 test patients.
Important metadata included thermal sensory loss and foot paraesthesia. Smartphone
and broader-population validation were described as future work.
[Authors' abstract and figure captions, Lancet Regional Health – Americas 2022](https://pubmed.ncbi.nlm.nih.gov/36776278/).

**Limit:** this is a small single-centre internal test, not prospective Nepal
volunteer validation. Accuracy/AUC do not establish sensitivity at Numbra's chosen
operating point. Full text is now inspected via
[Europe PMC XML](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9903738/fullTextXML)
after the web tool's PMC browser check. **ResNet-50, fine-tuned on close-up images**
was selected over Inception-v4 for Model 1. In main Table 3, elastic-net Model-2
outputs plus patient information reports sensitivity **89%** and specificity
**91%**, with the caption identifying 40 held-out patients; this is not the
photo-only result. The abstract reports accuracy/AUC, not sensitivity/specificity.
The [supplement](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9903738/supplementaryFiles)
does not supply an alternate final sensitivity/specificity: Supplementary Table 3
is coefficients from a refit including the testing patients. Supplementary Fig. 6
describes Tables 2/3 as cross-validation averages, conflicting with Table 3's
held-out caption. The operating cutoff and resolution of that description are
**UNVERIFIED**; preserve the source attribution and do not invent reconciliation.
Also retain the abstract's 1,229 images/585 metadata sets versus results text's
1,226 images/582 lesions as a discrepancy.

The linked [Microsoft code repository](https://github.com/microsoft/leprosy-skin-lesion-ai-analysis)
is currently archived; its [README](https://raw.githubusercontent.com/microsoft/leprosy-skin-lesion-ai-analysis/main/README.md)
documents ResNet-50 experiments and research-only intended use, and its
[code licence](https://raw.githubusercontent.com/microsoft/leprosy-skin-lesion-ai-analysis/main/LICENSE)
is **MIT**. No patient data or pretrained weights are supplied by the inspected
code listing; this does not grant rights to Fiocruz data or clinical use. Archive
date is not established by current status. The data repository now verifies
**CC BY-NC 4.0 with all files restricted/request-gated**; see the
[dataset survey](03-datasets.md). Learn to compare image-only,
metadata-only and fused models with patient separation. Keep a symptom-only
referral path even when an image model is present.

## WHO Skin NTDs App — distinguish public education and AI studies

WHO's initiative currently identifies public Android/iOS versions **without the
AI feature**, with AI in a non-public beta. Its AI library total of 5,693 photos is
explicitly dated October 2024. Public app availability grants no verified image,
code or weight reuse licence.
[WHO initiative page](https://www.who.int/initiatives/who-initiative-on-artificial-intelligence-for-skin-conditions).
This differs from the December 2024 news update's broad description of an updated
free app. Treat exact public AI distribution and offline AI capability as
**UNVERIFIED** rather than resolving the ambiguity in favour of availability.

The Kenya update reports two algorithms: UniversalDoctor's 12 skin-NTD algorithm
for WHO and Belle.ai's 24 common-condition algorithm. Forty primary-care workers
collected 605 images from 605 patients in five counties, June–October 2024.
Preliminary average sensitivity was about 80% against three board-certified
dermatologists' diagnoses.
[WHO Kenya study update, 4 December 2024](https://www.who.int/news/item/04-12-2024-the-who-skin-ntds-app-shows-encouraging-results-in-kenya-study).
**Limit:** a preliminary multi-condition average is not leprosy sensitivity;
class counts, uncertainty intervals, algorithm architecture, frozen version,
specificity and downloadable study-data licence are **UNVERIFIED** from this
update. Numbra should evaluate the worker workflow as well as the algorithm.

A separate Ghana/Kenya study of **version 3 as a training tool**, led by UOC
researchers, recruited 60 users (24 Ghana, 36 Kenya) by snowball sampling. uMARS
app-quality mean was 4.02/5 and subjective quality 3.82/5; English comprehension
was required. It was a usability/experience study, not AI diagnostic validation.
[Authors' JMIR 2024 study](https://www.jmir.org/2024/1/e51628).
Learn from the offline educational workflow, but validate Nepali wording and
non-English users separately. The paper's open-access status does not establish
rights to the app's source code, embedded photos or model.

## Independent WHO classifier evaluation — positive-case top-5 recall

Deps et al. evaluated the WHO desktop visual classifier on 439 confirmed leprosy
images collected in 1996–2024. Sixteen processing failures left 423 images:
367 classical and 56 reactional/atypical. Leprosy appeared in the **top five**
predictions for 84.9% overall, 87.2% classical, and 69.6% reactional/atypical images.
They reported inconsistent predictions between similar lesions in the same patient.
[Authors' PAHO journal abstract, 2026, DOI 10.26633/RPSP.2026.40](https://journal.paho.org/en/articles/independent-assessment-who-skin-neglected-tropical-diseases-application-leprosy-detection).

**Limit:** top-5 image recall is not top-1 accuracy, patient sensitivity, or referral
sensitivity. A positive-only cohort cannot establish specificity or AUC for
leprosy versus differentials. Excluding processing failures also affects the
denominator; unusable inputs need an explicit referral/abstention path. Algorithm
internals, patient count and data/weight reuse licence are **UNVERIFIED** here
(indexed primary abstract available; full-page/PMC access failed). Learn to audit
reactional/atypical cases, multiple views per patient and failures separately;
do not adopt the headline percentage as a deployment threshold.

## NLR SkinApp — structured knowledge and usability before ML

Mieras et al. describe NLR SkinApp's staged development: a Nigerian paper
algorithm, Mozambique mobile pilot in 2015, and implementation in 2017–2018.
It uses symptoms/body areas and clinical reference content with treatment/referral
advice; this is not reported as an image CNN. Field feedback requested a glossary
and reporting, and the pilots did not measure diagnostic performance.
[Authors' development study, 2018](https://pmc.ncbi.nlm.nih.gov/articles/PMC6160956/).
NLR reports integration into the WHO Skin NTDs App.
[Implementer's integration announcement](https://nlrinternational.org/nlrs-skinapp-embraced-by-world-health-organization/).

**Reuse:** learn the branching questions, broad skin-health presentation and
iterative worker feedback. Exact current code/content licences, export formats,
weights (if any), and permission to embed reference images are **UNVERIFIED**.
Do not confuse similarly named commercial apps with NLR's tool. Free access and
an open-access development paper are not permission to copy app content.

## LEARNS — expert teleconsultation and a service network

The Philippine LEprosy Alert and Response Network System was developed with DOH,
PCHRD, MetaHelix and Novartis partners. Implementer reporting describes health
workers sending lesion images and patient details to experts by SMS or app;
it reports expansion after an Iloilo pilot, reaching 29 provinces in nine regions
and over 6,000 trained providers by January 2019.
[Novartis Philippines implementer report, 28 January 2019](https://www.novartis.com/ph-en/news/media-releases/learns-countrys-first-mobile-phone-based-leprosy-teleconsultation-system).
The Philippine health-research portal also documents the initial Region 6 pilot.
[Government health-research portal](https://www.healthresearch.ph/index.php/news/11-events/213-referrals-using-mobile-phone-help-detect-leprosy).

**Limit:** those are dated implementation reports, not sensitivity/specificity,
current coverage or evidence of an autonomous classifier. A learned model is not
specified; no reusable code, weights or patient-data licence verified. Learn
referral acknowledgement, expert confirmation and follow-up. The online
teleconsultation component is outside this POC's no-server/no-upload scope.

## 2023 JMIR scoping review — useful map, limited evidence base

Frade and colleagues' review searched PubMed/Embase, found 416 records and included
three studies (2018–2021): SkinApp development, computerized Mitsuda-test reading,
and an AI screening app using Brazilian notification data. The authors emphasise
limited evidence and the need for controlled evaluation. The last is tabular
random-forest classification, not proof that smartphone photos diagnose leprosy.
[Authors' JMIR Dermatology review, 2023](https://derma.jmir.org/2023/1/e47142).

**Limit:** review inclusion does not license the reviewed tools, and this scope
does not cover all teleconsultation or later AI studies. Do not present metrics
quoted by a review as independently checked primary results. Its search omissions
are a reason to look further, not evidence that no other tool exists.

## Academic image work and newer candidate resources

| Work and primary evidence | Data, model and reported result | Validation/reuse limits and lesson |
| --- | --- | --- |
| [Baweja & Parhar, ICMLC/IEEE 2016; authors' CMU record](https://publications.ri.cmu.edu/leprosy-lesion-recognition-using-convolutional-neural-networks) | CNN; DermNet and web-scraped images; best accuracy 91.6%; 60/20/20 image split. | Patient separation, sample count and clinical confirmation UNVERIFIED in the accessible abstract; IEEE page blocked. No code/weight/data licence verified. Web scraping is excluded here; image split alone does not establish patient independence. |
| [Banerjee et al., arXiv:2004.04122, 2020](https://arxiv.org/abs/2004.04122) | Leprosy/tinea versicolor/vitiligo; LBP and Weber texture ensemble with SVM, accuracy 91.38%; ResNet-101 comparator 89%. | Sample size, confirmation, grouping, external testing and reusable artifact licences UNVERIFIED from the abstract. Relevant differential task, but headline accuracy does not choose a safe referral rule. |
| [Yotsu et al., PLOS NTD 2023](https://journals.plos.org/plosntds/article?id=10.1371/journal.pntd.0011230) | Côte d'Ivoire/Ghana, 1,709 images/506 patients, five skin NTDs; ResNet-50/VGG-16; overall predictions over 70%, poorer leprosy/mycetoma performance; no patient overlap between train/test. | Data explicitly non-public for privacy; requests go through Tulane IRB. Code/weight reuse licence UNVERIFIED. Overall result is not leprosy sensitivity. Its medRxiv pilot preprint was found, but the published paper is the cited record. Learn patient splits and confirmation provenance. |
| [Wang et al., eSkinHealth, arXiv:2508.18608, 2025](https://arxiv.org/abs/2508.18608), [authors' release status](https://github.com/janet-sw/eSkinHealth/blob/main/README.md) | 5,623 images/1,639 cases, 47 conditions in Côte d'Ivoire/Ghana; metadata and assisted masks/captions/concepts. | Authors' February 2026 notice says release delayed for ethical/privacy/legal review. No accessible licensed image release verified; downstream clinical metrics UNVERIFIED. Study multimodal provenance design; do not acquire data or mistake repository code licensing for image permission. |
| [Sanchez et al., CO2Wounds-V2, ICIP 2024](https://arxiv.org/html/2408.10827v1) | 764 smartphone chronic-wound images from 96 leprosy patients in Colombia; segmentation, not initial lesion triage. | Article says CC BY-NC-ND, while [Mendeley v2](https://data.mendeley.com/datasets/s2w7rjwz49/2) lists CC BY-NC 3.0. Hold for conflicting terms and task mismatch; segmentation scores cannot be interpreted as leprosy detection. Code licence and patient-independent released splits UNVERIFIED. |

This search did not verify a clinically validated, anonymously obtainable,
licensed model that can simply be embedded in Numbra. That is a finding about
this survey, not a universal absence claim. Additional academic dataset records
and the conservative acquisition disposition are in the [dataset survey](03-datasets.md).

## Related general dermatology and skin-tone evidence

Daneshjou et al. evaluated existing dermatology AI on DDI's 656 curated clinical
images. Performance fell on this external cohort, with worse results on darker
skin and uncommon diseases; diverse fine-tuning reduced the tone gap.
[Authors' DDI study](https://arxiv.org/abs/2203.08807).
**Inference:** inspect subgroup counts and uncertainty and keep an external
cohort separate. This is malignancy-oriented evidence, not evidence of leprosy
performance. DDI access requires an agreement; no acquisition is approved.

SCIN offers volunteer consumer photos with demographic/symptom information and
dermatologist differential assessments, estimated Fitzpatrick and Monk tone
labels. It documents duplicates and a bespoke data licence.
[Google/clinical collaborators' repository](https://github.com/google-research-datasets/scin/blob/main/README.md).
PAD-UFES-20 provides Brazilian smartphone lesion data, patient/lesion references
and six cancer/benign classes under the record's CC BY 4.0 licence.
[Authors' PAD v1 record](https://data.mendeley.com/datasets/zr7vgbcyr2/1).
**Inference:** these demonstrate metadata and smartphone-data design patterns,
but neither establishes a suitable leprosy positive/control cohort. SCIN's photo
assessments are not uniformly clinical/laboratory confirmation. All availability
and permission details remain governed by ADR-002; no weights or images reused.

## Comparison for Numbra's decision

This table compares roles and limits, not a leaderboard; its evidence is cited in
the corresponding records above. Percentages with different denominators cannot
be ranked as if they measure the same task.

| System/work | Main role | Evidence most relevant here | Proposed reuse boundary |
| --- | --- | --- | --- |
| AI4Leprosy | ResNet-50 close-up and metadata research | Internal patient results; Table 3/Supplement Fig. 6 description conflict | MIT code; CC BY-NC 4.0 restricted data; learn ablations, no data acquisition. |
| WHO Kenya AI beta | Broad skin-condition assistance | Preliminary aggregate sensitivity | Learn field workflow; no inferred leprosy accuracy or public offline weights. |
| WHO independent study | Leprosy top-5 retrieval | Positive-case, image-level recall; reaction gaps | Learn failure/presentation audits; cannot estimate specificity. |
| WHO training/NLR SkinApp | Education and structured knowledge | Usability and staged development | Learn language/glossary/referral design; no content copying permission assumed. |
| LEARNS | Worker-to-expert referral | Dated programme implementation reports | Learn referral closure; network service deferred. |
| Academic CNN/texture studies | Image classification | Often internal accuracy | Audit grouping and confirmation; no scraped image reuse. |
| eSkinHealth/CO2Wounds | Multimodal annotation/wound segmentation | Release governance/task-specific resources | Hold data; different clinical target and unresolved release/rights. |
| DDI/SCIN/PAD | Diversity and smartphone evidence | External shift, labels, provenance | Inform evaluation/schema; not leprosy validation. |

## Who should we contact before building?

**Recommendations for humans; no messages sent.** Building the synthetic
PLACEHOLDER POC may proceed after M0's gate; contact is essential before any real
data or field use.

1. Nepal EDCD's leprosy programme and a local receiving clinical service, FCHVs and
   people affected by leprosy: verify workflow, differential vocabulary, training,
   stigma, referral capacity and follow-up. [WHO Nepal's programme training report](https://www.who.int/nepal/news/detail/08-07-2026-strengthening-capacity-of-frontline-health-workers-for-leprosy-diagnosis-and-management)
   identifies existing institutional activity, not a partnership with Numbra.
2. WHO skin-NTD initiative, UniversalDoctor/UOC and NLR: clarify current AI access,
   offline operation, integration interfaces, content licences and whether extending
   existing education/referral tooling is preferable. Use [WHO's initiative contact route](https://www.who.int/initiatives/who-initiative-on-artificial-intelligence-for-skin-conditions).
3. AI4Leprosy authors/Fiocruz: consider access via the owner-contact route on the
   repository; review non-commercial data/weight obligations, group IDs,
   diagnostic confirmation and the Table 3/supplement evaluation discrepancy.
   Code licence is verified MIT; data permission is a separate request.
4. WHO independent-evaluation authors and Yotsu/eSkinHealth collaborators: discuss
   reactional/atypical test design, privacy-controlled external testing and the
   release-review status. Do not request or transfer patient data in autopilot.
5. Philippine DOH/PCHRD/LEARNS implementers: learn referral acknowledgement and
   programme maintenance rather than presuming a downloadable reusable classifier.

## Open questions

- Which WHO app version/AI algorithm is currently available, and under what offline and reuse terms?
- Can AI4's evaluation-caption discrepancy and restricted-data permission, and the independent study's patient counts/failure handling, be settled?
- Which systems offer reusable software interfaces rather than just free app access?
- Will prospective Nepal validation include early, reactional, atypical and non-classical presentations and track referral completion?
- Can a separately licensed external positive-and-differential cohort be obtained under the project's access limits?

## Confidence

Medium: primary abstracts, papers and implementer records establish useful
distinctions, but architecture, release rights and several validation details are
unverified. Low confidence that any surveyed system is ready to reuse clinically
in Nepal without further permissions and prospective evaluation.
