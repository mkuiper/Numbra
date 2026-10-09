# Nepal ethics, privacy and medical-software questions

Evidence accessed **2026-10-09**. This is preliminary research, not legal clearance,
ethics approval or a clinical protocol. The present work uses synthetic fixtures
only. An unattended software gate permits the next POC milestone, not recruitment,
clinical use, image collection, publication or app distribution.

## Ethics authority and proposed approval route

Nepal Health Research Council (**NHRC**, not the National Human Rights Commission)
publishes National Ethical Guidelines for Health Research in Nepal 2022. Indexed
primary text describes submission to the NHRC Ethical Review Board (ERB) through
the online portal, with application documents and processing requirements in
Annex II/SOP. It also describes voluntary withdrawal without penalty.
[NHRC 2022 guidance](https://elibrary.nhrc.gov.np/bitstream/20.500.14356/2481/1/National-ethical-guidelines-October.pdf).
The NHRC-approved RAHS Institutional Review Committee describes reviewing research
within and affiliated to its institution under NHRC guidelines.
[RAHS committee scope](https://www.rahs.edu.np/research/institutional-review-committee).
This establishes an institutional route exists; it does not establish that any
IRC may approve Numbra or replace national review for a collaborative field pilot.

Full NHRC text opens failed on both the eLibrary and NHRC-hosted copies.
**Labelled research workaround: indexed official guidance plus an institution's
own scope statement.** Current ERB/IRC allocation for externally sponsored,
multisite or device research, exemptions, fees, timelines and required forms
remain **UNVERIFIED**. Search-result dates for other uploaded NHRC PDFs are not
evidence of a newer guideline edition. No portal account or submission was made.

**Proposed future process:** appoint a Nepal principal investigator/custodian and
clinical service partner; obtain written determination from NHRC and the relevant
institutional committee about review jurisdiction; submit protocol, consent and
translations, recruitment/assent plans, scientific design, safety monitoring,
data management and partner/funding agreements; obtain required site/programme
permissions and regulatory determinations before recruitment or clinical use.
These are planning deliverables, not a verified exhaustive application checklist.
Specify a receiving clinic and follow-up, incident reporting, stopping conditions,
compensation/redress and responsibilities. A clinical partner's enthusiasm or a
repository review is insufficient approval. Even usability sessions involving
people/images need a documented determination; no exemption is presumed here.

## Privacy law: verified text and unresolved application

The Nepal Law Commission page links the English text of **The Privacy Act, 2075
(2018)**. Section 3 concerns bodily/personal privacy; section 12 provides consent
and purpose limits for personal data and health-examination disclosure; section
19 addresses electronic privacy. Section 23(2)–(3) describes consent and purpose
information for research collection. Section 27 identifies physical/mental health
as sensitive information for public-body processing and contains health-service
exceptions. These are not a blanket AI-training permission.
Section **11(2)(b)** includes medical history and health-examination reports among
personal documents; section 11(4) describes exceptions including consent for
study/research. Section **16(1)** addresses non-consensual photography that damages
character/social prestige and defamatory composites/publication; **16(3)** restricts
dissemination/commercial use of non-consensual photographs with the specified
harmful/profit intentions. These provisions matter to lesion photos and stigma;
they are not paraphrased as a blanket prohibition of every photograph.
[Act, government-hosted English text](https://giwmscdnone.gov.np/media/app/public/275/posts/1721034328_44.pdf),
linked from [Law Commission](https://lawcommission.gov.np/content/12261/the-privacy-act-2075/).
Text inspected; the initial National Information Commission copy returned 404.

**Inference/proposal:** treat identifiable lesion photos, answers and linked labels
as confidential health records. Separate care, sharing and research consent;
minimise access and obtain local legal interpretation. Current amendments, rules,
actor-specific duties, lawful basis for secondary training, residency/cross-border
requirements, breach procedure and mandatory retention remain **UNVERIFIED**.
Consent and de-identification alone are not claimed to settle them. See the
[contribution design](06-data-contribution-platform.md) for proposed controls.

## Nepal device regulation and future markets

DDA's official catalogue lists the **Directive on Health Technology Product and
Equipment, 2074 (2017)**; its indexed English introduction concerns production,
export/import, sales/distribution and monitoring of health-technology products.
[DDA translated directive record](https://www.dda.gov.np/content/23/health-technology-product-and-equipment-directive--2074/),
[English directive](https://dda.gov.np/download/Health%20Technology%20Product%20and%20Equipment%20Directive%2C%202074%20%282017%29_Translated%20Final.pdf).
Direct DDA catalogue, record and PDF opens failed. **Labelled research workaround:
indexed official record/text only.** Standalone screening-software coverage,
current implementing process, classification and investigational permissions are
**UNVERIFIED**. Absence of accessible software detail is not absence of regulation.
Before a future pilot, seek a written jurisdiction/classification determination
from DDA/MoHP through the Nepal partner; do not assume “triage aid” creates exemption.

| Possible future market | Verified primary guidance | Bounded Numbra inference |
| --- | --- | --- |
| United States | [FDA policy navigator, step 6](https://www.fda.gov/medical-devices/digital-health-center-excellence/step-6-software-function-intended-provide-clinical-decision-support) includes dermatology photographs as medical images and says image-analysis functions fail the non-device CDS image criterion; a product may be a device. | Numbra's photo analysis should not assume a non-device CDS exclusion. Actual classification, pathway and investigational obligations need specialist determination; no FDA approval claimed. |
| European Union | [MDCG 2019-11 rev.1, June 2025](https://health.ec.europa.eu/document/download/b45335c5-1679-4c71-a91c-fc7a4d37f12b_en?filename=md_mdcg_2019_11_guidance_qualification_classification_software_en.pdf&prefLang=fr) discusses intended purpose and Rule 11. Diagnostic/therapeutic decision software is generally class IIa under that rule, with higher classes for specified potential harms. The guidance is nonbinding. | Screening/referral wording alone does not settle qualification or risk class. Evaluate the actual intended purpose, decision significance and harm; do not assign Numbra a definitive class here. |

These markets are illustrative comparison cases, not chosen expansion plans.
Their guidance does not establish Nepal law. Open-source licensing, offline
operation and a disclaimer do not constitute regulatory authorisation.

## Draft intended use and non-goals

**Current POC:** an offline Android engineering demonstrator, for developers and
reviewers using generated synthetic examples, of guided observations, local image
inference and transparent referral actions. Its model is **PLACEHOLDER — not
clinically validated**, and is not for decisions about a person's care.

**Future proposed intended use, contingent on approvals and validation:** help
trained and supervised Nepal community health volunteers record a consented
lesion photo and observations, and support referral to an agreed clinical service
for possible skin/nerve concerns. A clinician determines diagnosis and treatment.
The app cannot establish absence of leprosy from a low photo score; symptoms,
missingness and failures can independently require referral. Intended population,
age limits, excluded presentations, user competency and service geography must
be specified in the approved protocol before clinical use.

Non-goals: autonomous diagnosis or exclusion, PB/MB assignment from photos,
treatment/dosing, nerve palpation by untrained users, contact surveillance,
screening without consent, uncontrolled consumer self-diagnosis, automatic model
learning, research uploads or replacement of ordinary clinical assessment.

## Proposed risk controls and future evidence

WHO emphasises human control, accountability and equity in AI health governance.
[WHO principles](https://www.who.int/news/item/28-06-2021-who-issues-first-global-report-on-ai-in-health-and-six-guiding-principles-for-its-design-and-use).
The following is a project risk plan, **not evidence that controls are effective**.

| Risk | Proposed control | Evidence needed before field use |
| --- | --- | --- |
| False reassurance and delayed care | Symptom-first rules, no negative diagnosis, referral for incomplete sensation/failed input, explicit follow-up and trained supervision. | Representative prospective evaluation of missed cases, time to assessment and failure handling; synthetic sensitivity is insufficient. |
| Excess referral burden | Prespecified threshold, transparent reasons, clinic capacity planning and referral closure. | Actual workload, waiting times, completion, transport/cost and unintended delays for other conditions. |
| Stigma and disclosure | Neutral home/notification wording; private consent; encrypted minimum records; optional/previewed sharing, no photo by default. | Shared-device usability/security audit and affected-person feedback; encryption/neutral branding cannot eliminate disclosure. |
| Automation bias or misuse | PLACEHOLDER banner, explain action/reasons, no diagnosis percentage, independent symptom path and competency training. | Observed decisions with conflicting photo/symptom information, comprehension and supervision; exclusion of unsafe use cases. |
| Unequal performance/access | Preserve missing tone/provenance, assess subgroups, native Nepali/clinical review and accessible controls. | Adequate South Asian cohorts and subgroup counts/uncertainty; validated translation and low-literacy usability. |
| Data abuse or poisoning | Separate provisional/confirmed assertions, consent scope, quarantine, steward approval and human model-release gate. | Audited custodian/roles, provenance verification, withdrawal and security testing. |

Future pilot stopping conditions should include a serious suspected delay in care,
unmanaged privacy breach, missing receiving service, systematic misunderstanding
or material subgroup harm. Humans must set event definitions, independent review,
notification duties, thresholds and restart authority. The POC does not set a
clinical tolerance for harm or claim ethics approval by completing an ADR.

## Open questions

- What current NHRC/IRC jurisdiction and application requirements apply to this proposed collaborative software study?
- How do current privacy rules apply to the chosen custodian, secondary model training and transfer/retention?
- Does DDA classify the actual screening function as regulated software, and what is required for an investigational pilot?
- Who owns referral follow-up, safety incidents, complaints and stopping authority?
- Which population, local-language procedure and measured evidence could justify a supervised clinical pilot?

## Confidence

Medium for the identified authorities and inspected privacy/FDA/MDCG text; low for
Numbra-specific Nepal legal classification and approval procedures because full
NHRC/DDA access and institutional/regulatory determinations remain unavailable.
