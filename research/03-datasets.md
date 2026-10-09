# Dataset survey and combination plan

Evidence checked 2026-10-09. **This is a documentation survey, not acquisition.**
No clinical photos or task-data archives were acquired. Documentation and file
catalogues were inspected; Fitzpatrick17k's public CSV was read in memory only
to count labels, without following image URLs or retaining individual rows.
“Public” and a paper's “open-source” description do not establish a usable licence.
The [source register](sources.md) records which pages were accessible.

The selected unattended baseline is **synthetic only**, under
[ADR-002](../decisions/ADR-002-dataset-selection.md). No suitable openly licensed
leprosy-positive training set has been verified in this survey. This is a limit of
the evidence collected, not a claim that no such set exists. A real-data classifier
needs positives, clinically relevant differentials, usable provenance/group IDs,
and an independent validation source; negative-only public data do not suffice.

## Candidate records

### AI4Leprosy — excluded: verified licence, request-gated files

- **Owner/link:** Fiocruz investigators with Microsoft and Novartis Foundation;
  [authors' paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC9903738/).
- **Size:** abstract reports 222 participants, 1,229 images and 585 metadata sets;
  the full results text instead reports 1,226 images and 582 lesions. Keep these
  source discrepancies visible. Repository v1.10 lists 1,456 files, all restricted;
  1,231 JPEG and 225 JSON files; repository totals are not analytical cohort size.
- **Modality/geography:** high-resolution clinical images from a Brazilian leprosy
  referral centre. Exact camera mix and public-file mapping: **UNVERIFIED**.
- **Taxonomy/confirmation:** study compares leprosy and other dermatological
  conditions. Row-level confirmation methods and PB/MB/reaction availability in
  released files: **UNVERIFIED**.
- **Skin tone:** paper describes diverse skin types; public distribution and
  annotation method: **UNVERIFIED**.
- **Licence/access:** [repository DOI](https://doi.org/10.35078/1PSIEL),
  [Fiocruz page](https://arcadados.fiocruz.br/dataset.xhtml?persistentId=doi:10.35078/1PSIEL)
  and [public catalogue API](https://arcadados.fiocruz.br/api/datasets/:persistentId/?persistentId=doi:10.35078/1PSIEL)
  inspected directly after web-tool opens failed. API declares **CC BY-NC 4.0**,
  v1.10 released **2024-05-16**, all files restricted, access requests enabled and
  owner-contact instructions. This supersedes the earlier failed-open uncertainty.
  No access requested. HTML contains guestbook UI, but the API reports no
  guestbook ID; an actual download guestbook requirement is **UNVERIFIED** and
  irrelevant to exclusion because the files already require permission.
- **Relevance:** contains the positive class needed by the proposed task. Do not
  acquire or infer permissions from mirrors. Revisit only on verifiable primary
  repository terms and provenance. Humans may consider contacting the owner via
  the page, and must assess non-commercial use and future weight redistribution
  separately from MIT-licensed code. Released row/group schema remains UNVERIFIED.

### DermaCon-IN — relevant South Asian candidate, held pending audit

- **Owner/link:** Madarkar et al.; [paper v2](https://arxiv.org/html/2506.06099v2),
  [Harvard record](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/W7OUZM)
  and [catalogue export](https://dataverse.harvard.edu/api/datasets/export?exporter=dataverse_json&persistentId=doi%3A10.7910%2FDVN%2FW7OUZM).
- **Size/modality/geography:** paper reports 5,450 clinical images, 3,002 patients,
  South Indian outpatient clinics and smartphone/camera capture. A closer regional
  candidate than Brazilian/US cohorts, **not a Nepal validation cohort**.
- **Taxonomy/confirmation:** paper reports 245 dermatologist-assigned diagnoses.
  [README](https://dataverse.harvard.edu/api/access/datafile/11394641) and
  [schema](https://dataverse.harvard.edu/api/access/datafile/11362259) describe
  hierarchical labels and confidence but do not enumerate `Disease_label` values.
  **Leprosy, PB/MB and exact differential coverage/counts remain UNVERIFIED**.
  The paper's descriptor examples name vitiligo, pityriasis alba and tinea
  versicolor; examples do not prove released disease labels. Do not call this a
  negatives-only source or infer laboratory confirmation for individual cases.
- **Tone/grouping:** schema documents Fitzpatrick and Monk annotations and
  **`Subject_ID` as a patient identifier**, with a stratified subject-wise 80:20
  split. The [public data dictionary](https://dataverse.harvard.edu/api/access/datafile/13321639/metadata/ddi)
  also lists that column. The paper's privacy wording does not prove linkage is
  absent. Completeness, uniqueness across visits and actual split disjointness
  remain UNVERIFIED without an authorised row audit; image IDs cannot substitute.
- **Licence/access:** export v4.0 (released 2026-01-11) declares **CC BY-NC-SA 4.0**;
  17 catalogue files are unrestricted, no extra terms or guestbook ID shown.
  Anonymous GETs of README/schema returned HTTP 200 with no account or acceptance
  step. Metadata export worked after two failing ordinary API/page paths.
  **Image/weight retrieval was not attempted**; their download flow is UNVERIFIED.
  No patient-row tables, archives or weights downloaded.
- **Licence fitness (bounded inference):** NC restricts permitted uses; SA applies
  when sharing qualifying adapted material, under the
  [licence text](https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode.en).
  An Apache-2.0 code licence cannot replace these terms. Whether trained weights
  qualify as adapted material, whether later redistribution is non-commercial,
  and which notices/licences apply need human legal review. No blanket weight
  redistribution clearance is claimed.
- **Disposition:** hold under ADR-002. This promising candidate changes the survey,
  but unverified target labels, unaudited patient linkage, NC-SA weight obligations
  and lack of an approved independent positive/control cohort prevent promotion.
  If eventually used only as controls, cross-source class shortcuts need testing.

### Fitzpatrick17k — hold, atlas rights unresolved

- **Owner/link:** Groh et al.; [paper](https://arxiv.org/abs/2104.09957) and
  [authors' repository](https://github.com/mattgroh/fitzpatrick17k/blob/main/README.md).
- **Size/modality:** 16,577 clinical images, 114 conditions, sourced from two
  online atlases. This is not a prospective smartphone screening cohort.
- **Taxonomy/confirmation:** atlas disease labels; independent confirmation is
  **UNVERIFIED**. An in-memory count of the authors' [CSV label column](https://raw.githubusercontent.com/mattgroh/fitzpatrick17k/main/fitzpatrick17k.csv)
  confirms 16,577 rows / 114 labels, **no leprosy label**; vitiligo 166, psoriasis
  653, eczema 204, dyshidrotic eczema 83, allergic contact dermatitis 430.
  No exact tinea corporis/versicolor, pityriasis alba/rotunda, morphea, lupus
  vulgaris or PKDL label appears. Other pityriasis/lupus labels are not synonyms.
  These are row counts, not confirmed independent patients.
- **Skin tone/geography:** human Fitzpatrick annotations; authors report light
  skin types overrepresented. Patient geography and per-patient IDs: **UNVERIFIED**.
- **Licence/access:** README declares CC BY-NC-SA 3.0 and identifies Atlas
  Dermatologico and DermaAmin as image sources. It reports broken original links
  and offers an alternative access form/contact. Permission to use every original
  atlas image under that licence is **UNVERIFIED**. Annotation licensing alone
  must not be treated as settled image rights.
- **Relevance:** broad clinical differentials may help after rights and labels are
  audited; no automatic scraping or form completion in autopilot.

### DDI — excluded by unattended access limits

- **Owner/link:** Stanford School of Medicine;
  [project and agreement](https://ddi-dataset.github.io/index.html).
- **Size/modality/geography:** 656 clinical images, 570 patients; retrospective
  Stanford clinic collection from 2010–2020.
- **Taxonomy/confirmation:** pathology-based diagnoses curated by experts.
  Exact leprosy and target differential coverage: **UNVERIFIED**; do not relabel
  benign/malignant as leprosy/non-leprosy without original diagnosis evidence.
- **Skin tone:** in-person assessment cross-referenced with clinical/demographic
  photos and two dermatologists' review; diverse skin tones. Exact distribution
  was not extracted in this iteration.
- **Licence/access:** individual registration and Research Use Agreement;
  personal, noncommercial research only, with redistribution and derivative-work
  restrictions and a non-clinical-use limit. The agreement is not accepted.
- **Relevance:** could inform later independent fairness research if humans obtain
  permission; prohibited for this unattended acquisition irrespective of utility.

### SCIN — hold, custom licence and label fitness

- **Owner/link:** Google Research with dermatologist collaborators;
  [official README](https://github.com/google-research-datasets/scin/blob/main/README.md).
- **Size/modality/geography:** 5,000+ volunteer contributions, 10,000+ images,
  volunteered by US Google Search users; consumer clinical photos with symptoms.
- **Taxonomy/confirmation:** dermatologist condition assessments, rather than
  uniform biopsy/smear confirmation. Exact leprosy/differential counts and
  repeat-contributor identity availability: **UNVERIFIED**.
- **Skin tone:** self-reported and estimated Fitzpatrick types, plus estimated
  Monk tones; full distributions not extracted. README documents known duplicates.
- **Licence/access:** public Cloud Storage bucket documented; a bespoke
  [SCIN Data Use License](https://github.com/google-research-datasets/scin/blob/main/LICENSE),
  not CC BY 4.0. It grants reuse/adaptation subject to attribution, prohibits
  re-identification/re-linking, and contains acceptance language. No bucket
  download or use of licensed data was performed.
- **Relevance:** potential differential source, but unsuitable as confirmed
  leprosy evidence. Conservatively hold custom-terms data for human review under
  the no-accepting-terms-on-behalf constraint; this is an autopilot policy choice,
  not a legal conclusion that the licence forbids all research.

### PAD-UFES-20 — verified licence, excluded from selected baseline

- **Owner/link:** UFES-Brazil PAD investigators;
  [Mendeley v1 record](https://data.mendeley.com/datasets/zr7vgbcyr2/1).
- **Size/modality/geography:** 2,298 smartphone images, 1,641 lesions, 1,373
  patients, collected in Brazil; metadata references patients and lesions.
- **Taxonomy/confirmation:** BCC, SCC (including Bowen's disease), melanoma,
  actinic keratosis, seborrheic keratosis, nevus. Cancer labels biopsy-proven;
  other labels can be dermatologist-consensus diagnoses; about 58% biopsy-proven
  overall. No leprosy class among these six.
- **Skin tone:** Fitzpatrick metadata exists; exact distribution not checked.
- **Licence/access:** record lists CC BY 4.0 and a Download All control.
  Anonymous binary retrieval was not attempted or verified; a visible Sign In
  link does not establish that login is required to download.
- **Relevance:** smartphone modality and IDs are useful, but it cannot supply the
  leprosy positives or key inflammatory/infectious differentials needed here.
  Mixing it only as negatives risks a source shortcut. Do not download under
  the current synthetic-only decision. Future use needs a separately approved
  scientific role, anonymous access check and retained attribution.

### DermNet — excluded for AI use of free website images

- **Owner/link:** DermNet New Zealand Trust;
  [official image licence](https://dermnetnz.org/image-licence).
- **Size/modality/taxonomy:** broad clinical-image reference website; dataset size,
  target-class counts and camera distribution **UNVERIFIED** here.
- **Confirmation/skin tone/geography:** per-image confirmation, skin-tone metadata,
  patient group IDs and patient geography **UNVERIFIED**.
- **Licence/access:** current licence explicitly prohibits AI training and testing
  with freely available website images. Educational use of watermarked images
  must not be interpreted as permission for ML. A paid licensable AI dataset is
  a separate offering; buying/licensing it is outside this unattended task.
- **Relevance:** references may inform clinical research, but no image acquisition,
  scraping or third-party mirror is authorised.

### 32 Curated Categories of Skin Disease Images — excluded: upstream rights

- **Owner/link:** depositor Kurnia Adi Cahyanto;
  [Mendeley v2 record](https://data.mendeley.com/datasets/pgd42j3h5c/2), May 2026.
- **Labels/modality:** record lists borderline, lepromatous and tuberculoid
  leprosy, plus tinea corporis, psoriasis and other clinical-image categories.
  Exact image/patient counts, independent clinical confirmation, tone, camera,
  geography and patient grouping are **UNVERIFIED**.
- **Rights/access:** landing page lists CC BY 4.0 but describes compilation from
  websites and Kaggle. Individual upstream rights/consent are **UNVERIFIED**;
  a depositor's blanket licence does not establish permission over every original
  image. Anonymous binary access untested; no files or linked images acquired.
- **Disposition:** exclude. Do not use this collection or mirrors as a shortcut
  around DermNet/atlas permissions, grouping or diagnostic-provenance requirements.

### ISIC — collection-specific, task mismatch

- **Owner/link:** International Skin Imaging Collaboration;
  [official challenge data](https://challenge.isic-archive.com/data/).
- **Size/modality:** varies by release; older challenges include dermoscopy,
  while SLICE-3D includes later clinical-photo data. It is inaccurate to call
  the entire evolving archive dermoscopic only. No combined count asserted.
- **Taxonomy/confirmation:** skin-cancer-oriented tasks; target leprosy and
  infectious/inflammatory differential labels **UNVERIFIED** for any selected
  collection. Confirmation methods must be checked per collection.
- **Skin tone/geography:** multi-institution contributions; exact target-cohort
  distribution and group fields **UNVERIFIED** here.
- **Licence/access:** challenge licences vary (e.g. CC0, CC BY-NC, and a permissive
  SLICE-3D CC BY subset). [Archive terms](https://gallery.isic-archive.com/) separate
  contributor image licences from annotation/database/software rights. Never
  infer a blanket licence for all images. Anonymous retrieval not tested.
- **Relevance:** not selected; different modality/clinical task would create poor
  leprosy controls even when a specific collection has suitable permissions.

### WHO Skin NTDs photo library and study datasets — hold

- **Owner/link:** WHO and collaborating institutions;
  [official AI initiative](https://www.who.int/initiatives/who-initiative-on-artificial-intelligence-for-skin-conditions).
- **Size/modality:** page reports 5,693 library photographs as of October 2024;
  that is a dated library total, not an accessible training release or current
  patient count. Exact cameras **UNVERIFIED**.
- **Taxonomy/confirmation:** skin NTDs and common conditions; source-specific
  diagnostic adjudication and leprosy class counts **UNVERIFIED**.
- **Skin tone/geography:** source-level composition and group IDs **UNVERIFIED**.
- **Licence/access:** no downloadable image-data licence verified on that page.
  Free app access is not a licence to extract its library or weights. Do not
  generalise WHO's statistical-dataset licences to clinical photographs.
- **Relevance:** potential collaboration for relevant positives and differentials;
  no extraction or contact is authorised. Individual studies are compared in
  [prior work](02-prior-work.md); records below retain their acquisition limits.

### Additional published-study candidates — no new acquisition approval

Accessed 2026-10-09 during the prior-work search. These supplement, rather than
replace, the synthetic-only recommendation. A paper's publication licence is not
a licence for the patient images used in its experiments.

| Candidate / primary source | Owner, size, modality, labels and geography | Confirmation, tone and grouping | Licence/access and disposition |
| --- | --- | --- | --- |
| [WHO independent leprosy evaluation, Deps et al. 2026](https://journal.paho.org/en/articles/independent-assessment-who-skin-neglected-tropical-diseases-application-leprosy-detection) | Authors' retrospective clinical-image cohort; 439 images, 423 processed; classical/reactional/atypical leprosy. Specific cohort geography and camera mix UNVERIFIED here. | Confirmed cases per abstract; exact confirmation methods, patient count/IDs and skin-tone distribution UNVERIFIED. | No image-release licence or anonymous endpoint verified. Positive-only evaluation cannot supply specificity controls. **Hold**. |
| [Yotsu et al. 2023 pilot](https://journals.plos.org/plosntds/article?id=10.1371/journal.pntd.0011230) | Tulane/local collaborators; clinical tablet photographs from Côte d'Ivoire/Ghana; leprosy, Buruli ulcer, mycetoma, scabies, yaws. | Dermatologist adjudication with some disease-specific laboratory tests; Fitzpatrick IV+ described. Patient-independent study splits; released group schema unavailable. | Authors explicitly state images are **not public** for privacy and direct requests to Tulane IRB. No unattended download licence; **excluded**. |
| [eSkinHealth, Wang et al. 2025](https://arxiv.org/abs/2508.18608), [authors' release notice](https://github.com/janet-sw/eSkinHealth/blob/main/README.md) | Author consortium; West African clinical images with metadata, masks/captions/concepts. Full disease counts, camera mix and confirmed leprosy subset UNVERIFIED here. | Diagnostic confirmation, skin-tone distribution, cross-release duplicates and whether case IDs establish patient independence UNVERIFIED without a release audit. | February 2026 notice still says delayed under ethical/privacy/legal review. No usable image release or data licence verified. Repository MIT badge does not license unreleased photos. **Hold**. |
| [CO2Wounds-V2 paper](https://arxiv.org/html/2408.10827v1), [Mendeley v2](https://data.mendeley.com/datasets/s2w7rjwz49/2) | Sanchez/Hinojosa et al.; 607 labelled plus 157 unlabelled smartphone wound images; Colombian wound-care cohort. Wound/background segmentation, not initial leprosy diagnosis or PB/MB. | Medical staff capture; diagnostic confirmation, tone and patient-independent released split IDs UNVERIFIED. | Paper states CC BY-NC-ND; record lists CC BY-NC 3.0. Anonymous binary retrieval untested. **Hold** for conflicting terms and clinical task mismatch; no download authorised. |
| [Baweja/Parhar 2016 authors' abstract](https://publications.ri.cmu.edu/leprosy-lesion-recognition-using-convolutional-neural-networks), [Banerjee et al. 2020 abstract](https://arxiv.org/abs/2004.04122) | Academic image studies. Former uses DermNet/web-scraped images; latter includes leprosy, tinea versicolor and vitiligo. Cohort size, geography/camera mix UNVERIFIED from inspected abstracts. | Confirmation, tone and defensible patient/group identifiers UNVERIFIED. | No separately licensed patient-data release verified. DermNet's current prohibition still applies; study reuse does not override source rights. **Hold/exclude scraped sources**. |

These sources add no currently approved positive-and-differential cohort. The
synthetic generator should cover `reaction_status=unknown` and missing
confirmation/tone/group fields to test software safeguards, without pretending
that invented labels represent these study populations.

## Proposed unified taxonomy and mappings

This is a **project design**, pending human clinical scrutiny under ADR-001/002.
Keep the original source label and confirmation provenance alongside the mapping:

| Field | Proposed values and rules |
| --- | --- |
| `label_family` | `leprosy`, `leprosy_differential`, `other`, `unresolved` |
| `diagnosis` | Named source diagnosis; versioned exact-name mapping. The [clinical document](01-clinical-background.md) verifies tinea corporis/versicolor, vitiligo, psoriasis and further challenge diagnoses from a national clinical guideline. Eczema is still a proposed local challenge class requiring review; this is not an exhaustive differential list. |
| `leprosy_classification` | `PB`, `MB`, `unknown`; only explicit clinical labels, never inferred from image count. |
| `reaction_status` | `type_1`, `type_2`, `none`, `unknown`; orthogonal to PB/MB, retained only when explicitly provided. |
| `label_status` / `confirmed_by` | Provisional or confirmed; named method/provenance, never fabricated. Missing confirmation remains missing. |
| `refer_for_review` | A workflow flag for uncertainty or poor quality, not a disease class and not a confirmed negative. |

| Source label | Proposed family mapping | Availability caveat |
| --- | --- | --- |
| AI4 study's leprosy label | `leprosy`; classification/reaction unknown unless explicit | Released label schema UNVERIFIED |
| AI4 other condition | Named differential only if exact source diagnosis matches verified vocabulary; otherwise `other`/`unresolved` | Must not presume all controls are one disease |
| Fitzpatrick17k disease name | Exact, versioned name-to-diagnosis mapping after rights audit | No leprosy label; documented differential row counts above; not approved |
| DermaCon-IN / SCIN disease name | Exact mapping only after permitted label audit | DermaCon-IN schema has patient IDs; target diagnoses remain UNVERIFIED; neither approved |
| DDI pathology diagnosis | Preserve name; usually outside current target vocabulary | Do not collapse benign into “safe”; acquisition prohibited |
| PAD's six labels | `other`, with exact disease name retained | Verified record taxonomy; cancer may still require clinical referral |
| ISIC cancer label | `other` or `unresolved` with original name | Collection must be verified; data not selected |
| WHO disease name | No executable mapping until licensed release is inspected | Library label schema UNVERIFIED |
| CO2Wounds wound/background mask | No mapping to a diagnostic label | Wound segmentation is not leprosy triage ground truth |
| Other study diagnosis | Preserve original; no executable mapping until a permitted release and confirmation audit | No additional real source approved |
| Synthetic fixtures | Explicit synthetic labels across all families and missingness cases | Invented fixture labels, never evidence of disease |

A model may later estimate a confirmed leprosy-vs-labelled-control score. It must
not learn “don't refer” from controls: skin cancers and other conditions can need
referral too. The transparent symptom/quality rules determine the action. Selected
task framing and operating-point proposals are in ADR-001 and the methods document.

## Combination risks and required controls

These are proposed checks, not measured findings on downloaded data:

1. **Rights:** retain source version, licence identifier/link and attribution per
   row. No pooled Apache-2.0 dataset; reject unknown permissions and mirrors.
2. **Labels:** record method of confirmation and retain uncertain labels separately.
   Dermatologist photo assessment is not equivalent to biopsy or smear. Missing
   subtype/tone information remains unknown rather than inferred.
3. **Duplicates:** exact content hashes and perceptual-hash review across sources;
   merge duplicate-connected groups before splitting. Conflicting labels quarantine
   the group rather than silently choosing a label.
4. **Leakage:** namespace IDs by source; all patient images, encounters, lesions and
   duplicate-linked records stay together. A lesion/case ID alone does not establish
   patient independence. Without patient linkage, use conservative groups and
   report that patient-level independence cannot be established.
5. **Domain shift:** track camera/modality, acquisition site, rulers, watermarks and
   backgrounds. A positive-only source versus negative-only source can let a model
   identify the hospital instead of disease. Such pooling is not a sound baseline.
6. **Evaluation:** validation selects thresholds; frozen test and leave-one-source-out
   evaluation remain untouched. A held-out set with one class cannot estimate both
   sensitivity and specificity or AUC. Mark unavailable metrics explicitly.
7. **Representation:** per-tone/presentation reports need counts, missingness and
   uncertainty intervals; tiny cells and absent labels cannot support fairness claims.
   DermaCon-IN is a verified South Asian clinical smartphone/camera candidate;
   its task-label fitness and permitted image access remain UNVERIFIED. No Nepal
   validation cohort is established. Do not infer geography from atlas names.

## Recommendation and next acquisition gate

Generate multiple named **synthetic** sources and patient groups for pipeline,
duplicate/split tests and a held-out synthetic source. Every model, metric report,
model card and app result identifies **PLACEHOLDER — synthetic demonstration**.
Synthetic leave-one-source-out exercises software only, with no external-validity
claim. Grouping synthetic records can be known exactly because the generator
assigns IDs, without representing an actual person.

Revisit real data only when a primary licence allows unattended access, target
positives and clinically relevant controls are documented, confirmation and
patient grouping are auditable, and a second suitable validation source exists.
Human-reviewed local collection/ethics is a later phase, not an overnight workaround.

## Open questions

- Will humans seek AI4Leprosy owner permission and accept its non-commercial obligations?
- Does DermaCon-IN include confirmed leprosy and key differentials, and do its patient IDs prevent leakage?
- Do DermaCon-IN's anonymous image flow and NC-SA terms permit the intended use and possible weight redistribution?
- Can any compatible second source support independent, patient-grouped evaluation?
- What clinically reviewed differential vocabulary and reaction schema should be final?
- What patient-linkage, tone and confirmation fields actually exist in candidate files?
- How should future human-approved releases handle custom licence obligations?

## Confidence

Medium for the primary-documentation survey and conservative acquisition decision;
low for real-data feasibility: AI4 rights are documented but access is restricted;
DermaCon-IN documentation is anonymously readable but target coverage is unknown.
No patient-row or image audit establishes a suitable independent real-data cohort.
