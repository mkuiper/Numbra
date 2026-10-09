# Source register

Sources inspected on 2026-10-09 using web search/open after Firecrawl's credit
failures. Links identify documentation or publications, not scraped clinical
photos. No clinical images or task-data archives were acquired. Documentation,
file catalogues and metadata dictionaries were inspected. The Fitzpatrick17k
CSV was counted in memory only; no individual row/image URL was retained or used.
Search snippets are not permission to acquire a dataset. A repository page that
could not be opened is explicitly listed as unverified.

| ID | Primary source | What was checked |
| --- | --- | --- |
| WHO-LEPROSY | [WHO leprosy fact sheet, 23 January 2026](https://www.who.int/news-room/fact-sheets/detail/leprosy) | Cardinal signs, PB/MB, limits of a photo-only task. |
| AI4-PAPER | [Barbieri et al., Lancet Regional Health – Americas 9 (2022), 100192](https://pmc.ncbi.nlm.nih.gov/articles/PMC9903738/) | Web PMC still gives browser check; Review-1 direct full text via Europe PMC now verified. Abstract/result counts and Table 3/supplement descriptions differ; see 02. |
| AI4-ABSTRACT | [PubMed record, PMID 36776278](https://pubmed.ncbi.nlm.nih.gov/36776278/) | Independent bibliographic access to the authors' abstract; not an independent dataset verification. |
| AI4-REPOSITORY | [Repository DOI supplied by the paper](https://doi.org/10.35078/1PSIEL), [Fiocruz landing page](https://arcadados.fiocruz.br/dataset.xhtml?persistentId=doi:10.35078/1PSIEL), [catalogue API](https://arcadados.fiocruz.br/api/datasets/:persistentId/?persistentId=doi:10.35078/1PSIEL) | Supersedes failed-open note: direct HTML/API worked; CC BY-NC 4.0, v1.10 release 2024-05-16, all 1,456 files restricted, access-request/owner instructions. No request or data download. Generic guestbook UI is not proof of an active guestbook (API ID null). |
| FITZ-PAPER | [Groh et al., CVPR 2021 / arXiv:2104.09957](https://arxiv.org/abs/2104.09957) | Clinical image count, atlas provenance, condition count and skin-type imbalance. |
| FITZ-REPO | [Authors' Fitzpatrick17k README](https://github.com/mattgroh/fitzpatrick17k/blob/main/README.md) | Claimed CC BY-NC-SA 3.0, original atlas sources, broken image links and alternate access form. |
| DDI | [Stanford DDI dataset project and Research Use Agreement](https://ddi-dataset.github.io/index.html) | Size, pathology-based labels, skin-tone annotation and registration/agreement restrictions. |
| SCIN-REPO | [Google's SCIN README](https://github.com/google-research-datasets/scin/blob/main/README.md) | US volunteer smartphone contributions, label/skin-tone provenance, public bucket and known duplicates. |
| SCIN-LICENCE | [SCIN Data Use License](https://github.com/google-research-datasets/scin/blob/main/LICENSE) | Bespoke public licence, attribution and no re-identification/re-linking conditions; acceptance language. |
| PAD | [PAD-UFES-20, Mendeley Data v1, DOI 10.17632/zr7vgbcyr2.1](https://data.mendeley.com/datasets/zr7vgbcyr2/1) | CC BY 4.0, smartphones, patient/lesion references, diagnosis classes and confirmation. Download was not invoked. |
| DERMNET | [DermNet image licence](https://dermnetnz.org/image-licence) | Explicit prohibition of AI training/testing with freely available website images; paid separately licensed dataset distinguished. |
| ISIC | [Official ISIC challenge dataset page](https://challenge.isic-archive.com/data/) | Collection-specific licences, dermoscopic challenge data and later clinical-photo collections. |
| ISIC-TERMS | [ISIC gallery terms](https://gallery.isic-archive.com/) | Image contributor licences distinct from archive annotations, software and database rights. |
| WHO-AI | [WHO initiative on AI for skin conditions](https://www.who.int/initiatives/who-initiative-on-artificial-intelligence-for-skin-conditions) | Photo library progress and distinction between public app and AI beta; no reusable image dataset licence found on this page. |
| APACHE | [Official Apache-2.0 text](https://www.apache.org/licenses/LICENSE-2.0.txt) | Code licence, stored verbatim in LICENSE. |

## Clinical and prior-work additions

All accessed **2026-10-09**. Access limitations are part of the evidence record.
Only publication/documentation text was inspected; no image links were followed.

| ID | Primary source | What was checked / access limits |
| --- | --- | --- |
| ZAMBIA-CLINICAL | [Zambia Ministry of Health, Management of Leprosy, second edition March 2020, hosted by WHO](https://www.afro.who.int/sites/default/files/2020-09/Guidelines%20for%20Management%20of%20Leprosy.PRINT%20Veersion.pdf) | Text of presentations, differential list (section 5.5), reaction types; not a Nepal protocol. |
| WHO-REACTIONS | [WHO reaction/disability technical guidance, 2020](https://www.who.int/publications/i/item/9789290227595) | Clinical importance of reactions/nerve function and skilled assessment. |
| WHO-MONITOR | [WHO monitoring/evaluation guide, annex 3.3](https://espen.afro.who.int/system/files/content/resources/GUIDE%20FOR%20MONITORING%20EVLAUTION%20CM%20NTD%20PROGRAMMES.PDF) | Indexed text of the skin sensory-test explanation/open-eye/closed-eye sequence. Local FCHV authorisation and training remain UNVERIFIED. |
| NEPAL-REPORTS | [DoHS publication catalogue](https://dohs.gov.np/category/publications/) | Lists FY 2080/81 and 2081/82 reports. Full 2080/81 HMIS and government PDF opens failed. |
| BAGMATI-REPORT | [Bagmati government FY 2081/82 report](https://giwmscdnone.gov.np/media/pdf_upload/Annual%20Health%20Report-081-82_evub4er.pdf) | Indexed national-situation paragraph, printed page 128. Full open failed (25 MB exceeds tool limit). Numbers explicitly UNVERIFIED against full report; no current complete district list asserted. |
| EDCD-2019 | [EDCD leprosy/disability annual report FY 2076/77 (2019/20)](https://www.edcd.gov.np/uploads/resource/6162b6d5e3507.pdf) | Indexed government text on referral centres and Nawalparasi-West contact examination; dated context only. |
| FCHV-SARLAHI | [Singh et al., KUMJ 2019;17(65):40–45](https://www.kumj.com.np/issue/65/40-45.pdf) | Primary study's training, referral and detection results; historical local pathway, not current national policy. |
| WHO-NEPAL-2026 | [WHO Nepal training report, 8 July 2026](https://www.who.int/nepal/news/detail/08-07-2026-strengthening-capacity-of-frontline-health-workers-for-leprosy-diagnosis-and-management) | EDCD/basic-service staff training, Dhanusha and represented provinces; not a complete service directory. |
| WHO-KENYA-AI | [WHO Kenya AI field update, 4 December 2024](https://www.who.int/news/item/04-12-2024-the-who-skin-ntds-app-shows-encouraging-results-in-kenya-study) | Two algorithms, cohort and preliminary aggregate sensitivity; no verified leprosy-specific threshold result/data licence. |
| WHO-TRAINING-STUDY | [Authors' JMIR 2024;26:e51628](https://www.jmir.org/2024/1/e51628) | Version-3 training app, Ghana/Kenya users, uMARS quality versus subjective scores; not diagnostic validation. |
| WHO-INDEPENDENT | [Deps et al., PAHO journal 2026, DOI 10.26633/RPSP.2026.40](https://journal.paho.org/en/articles/independent-assessment-who-skin-neglected-tropical-diseases-application-leprosy-detection) | Indexed primary abstract: positive-case top-5 recall, failure exclusions and presentation groups. Full journal open failed and PMC gave browser check; artifact licence/patient count UNVERIFIED. |
| NLR-DEVELOPMENT | [Mieras et al. development study, 2018](https://pmc.ncbi.nlm.nih.gov/articles/PMC6160956/) | Indexed primary study: staged symptom/reference app development and pilot limitations. |
| NLR-INTEGRATION | [NLR integration announcement](https://nlrinternational.org/nlrs-skinapp-embraced-by-world-health-organization/) | Implementer's statement of integration with WHO; no source/content licence established. |
| LEARNS-IMPLEMENTER | [Novartis Philippines, 28 January 2019](https://www.novartis.com/ph-en/news/media-releases/learns-countrys-first-mobile-phone-based-leprosy-teleconsultation-system) | Dated expert teleconsultation/programme report; not independent diagnostic-effectiveness evidence. |
| LEARNS-GOV | [Philippine health-research portal initial pilot report](https://www.healthresearch.ph/index.php/news/11-events/213-referrals-using-mobile-phone-help-detect-leprosy) | Government programme description; no patient-data/weight/code licence verified. |
| JMIR-SCOPING | [JMIR Dermatology 2023;6:e47142](https://derma.jmir.org/2023/1/e47142) | Authors' review methodology and three included studies; a primary source for its own review findings, not independent verification of cited study metrics. |
| IEEE-BAWEJA | [Authors' CMU publication record, ICMLC 2016](https://publications.ri.cmu.edu/leprosy-lesion-recognition-using-convolutional-neural-networks) | CNN abstract, source images, image split and accuracy; IEEE Xplore page blocked. Patient separation/rights UNVERIFIED. |
| ARXIV-BANERJEE | [Authors' arXiv:2004.04122](https://arxiv.org/abs/2004.04122) | Three diagnoses, texture/SVM ensemble and CNN comparator abstract. Grouping/confirmation/rights UNVERIFIED. |
| YOTSU-PILOT | [Authors' published PLOS NTD 2023;17:e0011230](https://journals.plos.org/plosntds/article?id=10.1371/journal.pntd.0011230) | Models, cohort, patient split, diagnostic provenance and explicit non-public data statement. Published version used instead of the discovered medRxiv preprint. |
| ESKIN-PAPER | [Authors' arXiv:2508.18608](https://arxiv.org/abs/2508.18608) | Multimodal dataset counts and geography; not proof of current release/permission. |
| ESKIN-STATUS | [Authors' eSkinHealth README](https://github.com/janet-sw/eSkinHealth/blob/main/README.md) | February 2026 delay for ethical/privacy/legal review remains displayed. Code licence badge is separate from image-data rights. |
| CO2-PAPER | [Authors' CO2Wounds-V2 ICIP 2024 paper](https://arxiv.org/html/2408.10827v1) | Wound-segmentation purpose, cohort and stated CC BY-NC-ND licence. |
| CO2-RECORD | [Mendeley v2, DOI 10.17632/s2w7rjwz49.2](https://data.mendeley.com/datasets/s2w7rjwz49/2) | Labelled/unlabelled counts, smartphones/Colombia and **CC BY-NC 3.0**, conflicting with paper's stated terms; download not invoked. |
| DDI-STUDY | [Daneshjou et al., author manuscript arXiv:2203.08807](https://arxiv.org/abs/2203.08807) | External dermatology-model/tone performance findings; different clinical target from leprosy. |
| CLINICAL-TERMS | [Benedetti, Description of Skin Lesions, MSD Manual Professional, August 2026](https://www.msdmanuals.com/professional/dermatologic-disorders/approach-to-the-dermatologic-patient/description-of-skin-lesions) | Authored clinical reference for glossary morphology definitions, not a diagnostic-performance primary study. Text inspected; images not fetched. |

## Methods and deployment additions

All accessed **2026-10-09** using the previously labelled web-tool workaround;
Firecrawl status again showed zero credits. Documentation text only was inspected;
no model binaries, patient photos, registrations or terms acceptances.

| ID | Primary source | What was checked / access limits |
| --- | --- | --- |
| MOBILENET-V3 | [Howard et al., arXiv:1905.02244](https://arxiv.org/abs/1905.02244) | Mobile CPU architecture motivation and Small/Large variants; no Numbra performance inferred. |
| EFFICIENTNET | [Tan and Le, arXiv:1905.11946](https://arxiv.org/abs/1905.11946) | Compound scaling alternative; no particular Lite checkpoint approved. |
| TIMM-MNV3-CARD | [Publisher checkpoint README](https://huggingface.co/timm/mobilenetv3_small_100.lamb_in1k/raw/main/README.md) | Apache-2.0 declaration, ImageNet-1k provenance, small backbone and feature extraction. No binary retrieval. |
| TIMM-MNV3-FILES | [Publisher file listing](https://huggingface.co/timm/mobilenetv3_small_100.lamb_in1k/tree/main) | Public listing and safetensors option; anonymous binary access untested. |
| TIMM-MNV3-CONFIG | [Publisher preprocessing config](https://huggingface.co/timm/mobilenetv3_small_100.lamb_in1k/raw/main/config.json) | NCHW size, bicubic/centre crop, normalisation; Numbra's proposed letterbox differs explicitly. |
| TIMM-CODE | [timm repository licence](https://github.com/huggingface/pytorch-image-models/blob/main/LICENSE) | Apache-2.0 code licence; separately checked checkpoint declaration. |
| KERAS-MOBILE | [Keras MobileNet API](https://keras.io/api/applications/mobilenet/mobilenet_models/) | MobileNetV3Small initialisation options and model-specific preprocessing. Initial guessed subpage failed; followed official index link to this page. |
| KERAS-CODE | [Keras repository licence](https://github.com/keras-team/keras/blob/master/LICENSE) | Apache-2.0 code text, not a separately established checkpoint licence. |
| TORCHVISION-WEIGHTS | [Models and pretrained weights](https://docs.pytorch.org/vision/stable/models.html) | Explicit warning about dataset-derived weight terms and model-specific transforms. |
| DERM-FOUNDATION | [Google publisher model card](https://huggingface.co/google/derm-foundation) | Architecture/embedding details and login/HAI-DEF acceptance gating; no request for access made. |
| TEMPERATURE | [Guo et al., arXiv:1706.04599](https://arxiv.org/abs/1706.04599) | Calibration and temperature scaling research; not a Nepal validation source. |
| ORT-MOBILE | [ONNX Runtime mobile guide](https://onnxruntime.ai/docs/tutorials/mobile/) | Android bindings, CPU-first quantised inference, profiling dimensions and native-runtime footprint caveat. |
| ORT-QUANT | [ONNX Runtime quantisation guide](https://onnxruntime.ai/docs/performance/model-optimizations/quantization.html) | Static CNN quantisation, QDQ/default recommendations; actual Numbra graph not tested. |
| ORT-LICENCE | [ONNX Runtime licence](https://raw.githubusercontent.com/microsoft/onnxruntime/main/LICENSE) | MIT code licence; transitive notices still require audit. |
| LITERT-ANDROID | [LiteRT Android guide](https://developers.google.com/edge/litert/android) | API/version/minSdk matrix, last updated September 2026; version matrix and sample dependency differ. |
| LITERT-QUANT | [TensorFlow conversion/PTQ](https://developers.google.com/edge/litert/conversion/tensorflow/quantization/post_training_quantization) | Representative-data requirements and quantisation modes; original ai.google.dev link redirects here. |
| SAMSUNG-EXAMPLE | [Galaxy A04e Philippines 3/32 GB specification](https://www.samsung.com/ph/smartphones/galaxy-a/galaxy-a04e-black-32gb-sm-a042fzkdphl/) | Entry-level regional hardware example only; rural Nepal device distribution remains UNVERIFIED after Nepal manufacturer/NTA searches. |
| NTA-MIS | [Nepal telecom regulator MIS page](https://www.nta.gov.np/misreport) | Subscription categories; current values and field-visit connectivity not established from accessed text. |
| ODK-COLLECT | [ODK Collect introduction](https://docs.getodk.org/collect-intro/) | Android offline forms/media support; no project/account created. |
| ODK-ENCRYPTION | [ODK encrypted forms](https://docs.getodk.org/encrypted-forms/) | Finalisation encryption plus plaintext-draft/capture-copy limitations. |
| KOBO-COLLECT | [KoboCollect collection guide](https://support.kobotoolbox.org/data_collection_kobocollect.html) | Offline forms after setup and later submission; no account or upload. |
| DHIS2-ANDROID | [DHIS2 Android overview](https://dhis2.org/android/) | Offline aggregate/individual capture and synchronisation; no claim about Nepal programme configuration. |
| HMIS-LOGIN | [Nepal HMIS government login page](https://hmis.gov.np/dataportal/dhis-web-commons/security/login.action) | Indexed primary-page text identifies DHIS2/DoHS; direct open failed HTTP 502. Authenticated schemas/APIs/permissions UNVERIFIED and not accessed. |

## Contribution and ethics additions

All accessed **2026-10-09**, using the labelled web-tool workaround after Firecrawl
status again showed zero credits. Only document/metadata text was inspected.
Failed full opens are explicitly distinguished from indexed primary evidence.

| ID | Primary source | What was checked / access limits |
| --- | --- | --- |
| WHO-AI-ETHICS | [WHO six AI health principles, 28 June 2021](https://www.who.int/news/item/28-06-2021-who-issues-first-global-report-on-ai-in-health-and-six-guiding-principles-for-its-design-and-use) | Human control, consent, privacy, transparency, accountability and equity; governance guidance, not Nepal legal clearance. |
| NHRC-2022 | [NHRC National Ethical Guidelines for Health Research in Nepal 2022](https://elibrary.nhrc.gov.np/bitstream/20.500.14356/2481/1/National-ethical-guidelines-October.pdf) | Indexed official text: ERB online submission, Annex II/SOP and withdrawal without penalty. Full eLibrary open timed out; [NHRC-hosted copy](https://nhrc.gov.np/wp-content/uploads/2022/04/National-ethical-guidelines-October.pdf) also failed. Current jurisdiction, fees/forms/timelines UNVERIFIED. |
| RAHS-IRC | [RAHS Institutional Review Committee](https://www.rahs.edu.np/research/institutional-review-committee) | Indexed institution's statement of NHRC approval and internal/affiliated scope. Does not establish Numbra jurisdiction or replace national approval. |
| NEPAL-PRIVACY-INDEX | [Law Commission, Privacy Act 2075](https://lawcommission.gov.np/content/12261/the-privacy-act-2075/) | Opened official page and followed its English PDF link. |
| NEPAL-PRIVACY-TEXT | [Government-hosted English Act](https://giwmscdnone.gov.np/media/app/public/275/posts/1721034328_44.pdf) | Inspected sections 3, 11, 12, 16, 19, 23 and 27; Review-1 adds personal medical documents and qualified photography restrictions. Amendments/rules and Numbra-specific duties not established. Initial [NIC copy](https://nic.gov.np/files/new_files/the-privacy-act-2075-2018.pdf) returned 404. |
| DDA-DIRECTIVE | [Official translated directive record](https://www.dda.gov.np/content/23/health-technology-product-and-equipment-directive--2074/), [English directive](https://dda.gov.np/download/Health%20Technology%20Product%20and%20Equipment%20Directive%2C%202074%20%282017%29_Translated%20Final.pdf) | Indexed official existence/title/introduction. Record/PDF opens failed; [catalogue](https://www.dda.gov.np/content/act-policies) timed out. Software classification and current process UNVERIFIED. |
| FDA-CDS-NAV | [FDA policy navigator step 6](https://www.fda.gov/medical-devices/digital-health-center-excellence/step-6-software-function-intended-provide-clinical-decision-support) | Dermatology as medical images and image-analysis limit on non-device CDS criteria. Page contains a contradictory No/Yes sentence in explanatory text; conclusion uses the question, Yes branch and listed criteria, not that apparent typo. No Numbra classification/clearance established. |
| EU-MDCG-SOFTWARE | [MDCG 2019-11 rev.1, June 2025](https://health.ec.europa.eu/document/download/b45335c5-1679-4c71-a91c-fc7a4d37f12b_en?filename=md_mdcg_2019_11_guidance_qualification_classification_software_en.pdf&prefLang=fr) | Intended purpose, nonbinding guidance and Rule 11, section 4.2.1. Not a definitive Numbra class or Nepal rule. |
| FEDAVG | [McMahan et al., AISTATS 2017 / arXiv:1602.05629](https://arxiv.org/abs/1602.05629) | Original distributed-data/local-update aggregation proposal; not evidence of Nepal infrastructure, anonymity or clinical performance. |

## Review-1 corrections and additions

Accessed **2026-10-09**, using the labelled web-tool/direct-document workaround;
Firecrawl status confirmed zero credits. No account, terms submission, clinical
image, model or patient-table download. Publication PDFs/supplements are research
documents, not task datasets; only their text was inspected.

| ID | Primary source | What was checked / access limits |
| --- | --- | --- |
| AI4-FULLTEXT | [Europe PMC full-text XML](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9903738/fullTextXML) | Selected ResNet-50 close-up model; main Table 3 Model-2 outputs plus patient info SEN 89% / SP 91%. Abstract lacks SEN/SP. Full text's image/lesion counts differ from abstract. |
| AI4-SUPPLEMENT | [Europe PMC supplementary files](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9903738/supplementaryFiles) | Publication supplement mmc1.pdf inspected as text. Table 3 contains refit coefficients, not SEN/SP. Fig. 6's CV-average description conflicts with main Table 3's held-out caption. No alternative invented. |
| AI4-CODE | [Author-linked Microsoft repository](https://github.com/microsoft/leprosy-skin-lesion-ai-analysis), [README](https://raw.githubusercontent.com/microsoft/leprosy-skin-lesion-ai-analysis/main/README.md), [LICENSE](https://raw.githubusercontent.com/microsoft/leprosy-skin-lesion-ai-analysis/main/LICENSE) | README ResNet-50 and research-only purpose; MIT licence and currently archived status. No weights/data reused; exact archive date not asserted. |
| DERMACON-PAPER | [Authors' arXiv:2506.06099v2](https://arxiv.org/html/2506.06099v2) | Regional setting, reported counts, capture, dermatologist labels and tone annotations. Descriptor examples are not a released diagnosis enumeration. |
| DERMACON-RECORD | [Harvard landing page](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/W7OUZM), [JSON metadata export](https://dataverse.harvard.edu/api/datasets/export?exporter=dataverse_json&persistentId=doi%3A10.7910%2FDVN%2FW7OUZM) | Ordinary page/API access failed; export works anonymously: v4.0, 2026-01-11, CC BY-NC-SA 4.0, 17 unrestricted files, no extra terms/guestbook ID shown. Catalogues only; no data/weights. |
| DERMACON-DOCS | [README file 11394641](https://dataverse.harvard.edu/api/access/datafile/11394641), [schema file 11362259](https://dataverse.harvard.edu/api/access/datafile/11362259), [public DDI dictionary](https://dataverse.harvard.edu/api/access/datafile/13321639/metadata/ddi) | Anonymous HTTP 200 without registration/acceptance. Subject_ID and subject-wise split documented; dictionary confirms column, no diagnosis enumeration. Actual row linkage, target labels and image flow UNVERIFIED. |
| CC-NC-SA | [CC BY-NC-SA 4.0 legal text](https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode.en) | Non-commercial and adapted-material/share-alike conditions. Whether trained weights are adapted material not determined; queued for humans. |
| FITZ-LABELS | [Authors' CSV](https://raw.githubusercontent.com/mattgroh/fitzpatrick17k/main/fitzpatrick17k.csv) | In-memory label-only counts: 16,577 / 114; no leprosy, named relevant counts in 03. No image URL followed or patient rows retained; no patient/group column. |
| CURATED32 | [Mendeley pgd42j3h5c v2](https://data.mendeley.com/datasets/pgd42j3h5c/2) | 2026-05-05, contributor Kurnia Adi Cahyanto; CC BY 4.0 claim and Kaggle-compilation provenance. Leprosy subtype labels listed, upstream rights/grouping UNVERIFIED; excluded. |
| ILA-SENSATION | [Technical Forum diagnosis/classification, 2002, S23–S31](http://ila.ilsl.br/pdfs/v70n1s1a05.pdf) | HTTPS web/direct opens failed; direct HTTP PDF and pdftotext succeeded. S24–S25 warns MB patches can retain sensation; 30% concerns patients missed by the single criterion in a cited study, not all lesions. |
| PKDL-NEPAL | [Uranw et al., PLOS NTD 2011 / PMC3243697](https://pmc.ncbi.nlm.nih.gov/articles/PMC3243697/) | Macular/plaquelike PKDL and differential relevance in a historical south-eastern Nepal cohort; no current nationwide prevalence claim. |
| NIST-BINOMIAL | [NIST exact binomial confidence interval construction](https://www.itl.nist.gov/div898/handbook/prc/section2/prc241.htm) | Exact interval calculation; minimum group-count guardrails are Numbra proposals, not NIST recommendations. |
| JOURNAL-SEARCH | [Leprosy Review 2024 WHO-app commentary](https://leprosyreview.org/article/95/2/20-24030), [IJDVL AI review](https://ijdvl.com/?article=f95403cc7ddbe468fc249d9a2284fcb6kOH1AhQgusZg2Q%3D%3D&embedded=true&view-pdf=1), [IJL 2025 research editorial](https://www.ijl.org.in/published-articles/26032025110641/1_Editorial__VMK_Jan_March_2025_final_print_version.pdf) | Targeted domain searches found contextual reviews/commentaries; no new diagnostic metric or reuse licence asserted from them. Not systematic coverage. |

## Open questions

- Will humans seek AI4's restricted-data permission and resolve its evaluation-description discrepancy?
- Can DermaCon-IN's target labels, patient linkage, image access and derived-weight rights be audited?
- Can full Nepal burden tables, current district pathways and local sensory-test protocols be verified?
- Can anonymous checkpoint access and measured export/device budgets be verified during the implementation milestones?
- Which current NHRC/IRC jurisdiction, privacy rules and DDA classification apply to a future Numbra pilot?

## Confidence

Medium: AI4 repository terms are verified and DermaCon-IN documentation adds a
regional candidate, but real-data label/linkage details, Nepal field/device configuration and legal
determinations remain unverified; proposed methods and budgets are not measured
performance. Indexed NHRC/DDA evidence cannot establish full current procedures.
