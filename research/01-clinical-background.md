# Clinical background and proposed volunteer workflow

Evidence accessed **2026-10-09**. This is research for a **PLACEHOLDER** POC,
not a validated field protocol. Clinical facts and Numbra design proposals are
separated below. No clinical photos or patient records were acquired.

## Diagnosis and the limits of photography

WHO describes clinical diagnosis using at least one cardinal sign:

- Definite sensory loss in a pale or reddish skin patch.
- An enlarged peripheral nerve together with sensory loss or weakness in its distribution.
- Bacilli identified microscopically in a slit-skin smear.

WHO's treatment classification is PB for 1–5 lesions without bacilli demonstrated
in a smear; MB includes more than five lesions, nerve involvement, or a positive
smear regardless of lesion count. These are clinical classifications, not image
classes that Numbra can assign. Leprosy is curable; prolonged close contact with
an untreated case is relevant, while ordinary casual contact does not spread it.
[WHO fact sheet, 23 January 2026](https://www.who.int/news-room/fact-sheets/detail/leprosy).

**Inference for Numbra:** a photo cannot test sensation, palpate a nerve, assess its
function, or perform microscopy. A low image score cannot exclude leprosy,
including disease with little visible skin involvement. Preserve PB/MB only when
an external clinical source explicitly supplies it. A missing smear or unknown
nerve status is not a negative result. The later rule engine must not diagnose,
assign treatment, or reassure a person that leprosy is absent.

**Intact patch sensation does not exclude leprosy, especially MB disease.** The
ILA Technical Forum report (2002, sections 2.1–2.2, S24–S25) warns that using an
anaesthetic patch as the sole diagnostic criterion misses MB cases. It describes
an Ethiopian study in which that criterion missed about 30% of **patients**,
most smear-positive; this is not a universal proportion of lesions or a measured
Numbra miss rate. [ILA report](http://ila.ilsl.br/pdfs/v70n1s1a05.pdf).
HTTPS opens failed; direct HTTP retrieved the publication PDF and its text was
inspected. A volunteer-administered gentle-touch test has **UNVERIFIED sensitivity**
in this setting; recording “present” must never amount to diagnostic clearance.

## Presentations and differential diagnoses

The Zambia Ministry of Health's 2020 guideline describes hypopigmented patches,
plaques, nodules and skin thickening. Its section 5.5 (printed page 10; PDF page 16)
lists differentials by appearance, rather than a single mutually exclusive
photo taxonomy. It is a primary national clinical guideline hosted by WHO;
**it is not a Nepal guideline**.
[Zambia guideline](https://www.afro.who.int/sites/default/files/2020-09/Guidelines%20for%20Management%20of%20Leprosy.PRINT%20Veersion.pdf).

| Presentation | Examples named in that guideline | Proposed Numbra implication |
| --- | --- | --- |
| Pale/macule-like lesions | Vitiligo, pityriasis alba, pityriasis rotunda, tinea versicolor, post-inflammatory hypopigmentation | Include clinically confirmed examples and preserve the named diagnosis; colour alone is insufficient. |
| Other macular/plaque-like lesions | Tinea corporis, psoriasis, morphea, lupus vulgaris, discoid lupus erythematosus | Treat this as a challenge vocabulary, not an exhaustive classifier label set. |
| Nodular lesions | Post-kala-azar dermal leishmaniasis, cutaneous leishmaniasis, Kaposi sarcoma, neurofibromatosis | An alternative diagnosis may itself require referral; it is not a “don't refer” control. |

| Additional pale-lesion candidate | Primary evidence beyond the Zambia table | Proposed implication |
| --- | --- | --- |
| Macular PKDL | Nepal cohort cited below describes hypopigmented macules/plaques. | Include macular as well as nodular PKDL for local clinical ranking. |

The table is a subset of the guideline, **not a claim about prevalence in Nepal**.
Add **macular PKDL** to the pale-lesion challenge vocabulary, alongside nodular
PKDL. A south-eastern Nepal cohort describes hypopigmented macules/plaques as the
commonest presentation in its 16 probable/confirmed PKDL cases, and the potential
confusion with leprosy. [Uranw et al., 2011 Nepal cohort](https://pmc.ncbi.nlm.nih.gov/articles/PMC3243697/).
This supports local clinical ranking, not a claim of current national prevalence.
Eczema/dermatitis remains a **proposed** additional common-condition challenge
class from the brief; its priority as a leprosy differential in the intended Nepal
setting is **UNVERIFIED**. Local clinicians must rank the vocabulary. Use
`pityriasis_versicolor` as a proposed canonical label for the source name “tinea
versicolor”, with an explicit mapping rather than two accidentally separate
classes. Retain source names and do not infer subtype or reaction from appearance.

## Reactions, neuritis and referral urgency

WHO's 2020 technical guidance describes reactions as inflammatory episodes that
can occur before, during or after treatment and affect skin, nerves, eyes or limbs.
Nerve injury and disability make recognition and skilled assessment important.
Diagnosis and treatment of reactions require clinical judgement.
[WHO reaction guidance](https://www.who.int/publications/i/item/9789290227595).
The Zambia guideline distinguishes type 1 (reversal) and type 2 (erythema nodosum
leprosum, ENL) reactions in section 6.4.
[Zambia guideline](https://www.afro.who.int/sites/default/files/2020-09/Guidelines%20for%20Management%20of%20Leprosy.PRINT%20Veersion.pdf).

**Proposed safeguards:** record new weakness, worsening sensory loss, painful
nerves, eye pain or difficulty closing an eye, and rapidly inflamed lesions as
reasons for prompt clinical assessment, independent of image score. A future
urgent-referral rule is a conservative POC design requiring clinical approval,
not a validated urgency scale or a treatment instruction. Reaction status remains
orthogonal to PB/MB in the manifest. An existing diagnosis or treatment does not
disable referral for deterioration.

## Information beyond the photo

The following table proposes capture fields and limits, not diagnostic criteria.
The WHO monitoring guide's annex 3.3 describes explaining a skin sensory test,
demonstrating it with eyes open, then testing with eyes closed without verbal cues.
[WHO monitoring guide, annex 3.3](https://espen.afro.who.int/system/files/content/resources/GUIDE%20FOR%20MONITORING%20EVLAUTION%20CM%20NTD%20PROGRAMMES.PDF).
Exact Nepal training competency, materials, translated wording and supervision
for FCHVs are **UNVERIFIED**; demonstration alone is not training certification.

| Information | Proposed collection by a trained volunteer | Limits and action |
| --- | --- | --- |
| Patch sensation | Explain and demonstrate gentle touch on unaffected skin; after consent, test the patch with eyes closed without cueing; record present/reduced/absent/uncertain/not tested plus assessor and method. | Only a clinically reviewed skin-touch procedure belongs in the POC. No needles, heat, or eye sensation testing. Reduced/absent or uncertain sensation must not be overridden by an image score. |
| Nerve symptoms/function | Ask about numbness, tingling, new weakness or pain in hands/feet and difficulty closing eyes. | Do not ask untrained users to palpate or diagnose thickened nerves. Record reported symptoms separately from professional examination. |
| Patch count/distribution | Ask about all patches, not just the photographed one; allow unknown and an approximate count or many/widespread. | Proposed referral for >5 patches or many/widespread patches with unknown count, even when sensation is present. Count never assigns PB/MB in the app. Respect privacy. |
| Other skin/functional concerns | Ask about raised/nodular/thickened skin or earlobes, loss of eyebrows, and painless wounds/burns on hands/feet; allow uncertain. | Proposed independent referral triggers; do not ask volunteers to diagnose morphology or palpate nerves. Uncertain required assessment goes to clinical review. |
| Duration and change | Approximate onset in days/weeks/months, change and prior treatment, with unknown allowed. | Recall is uncertain; no duration threshold may rule out disease. |
| Contact history | Private, optional question about close contact with a diagnosed person in a screening for a presenting skin concern; allow declined/unknown. | Yes means refer under canonical rule 2; unknown/declined is neither a trigger nor rule-3 missingness. No can never lower the outcome. Do not record another person's name. |
| Volunteer concern | Explicit required question: “Are you concerned that this person needs clinical assessment despite the other answers?” yes/no/uncertain. | Yes means refer; uncertain/declined/missing routes to incomplete-assessment review. This is a proposed assessment question, not an implicit flag attached to every screening. |
| Photo and quality | Record capture/pick provenance and blur/exposure results; allow retake. | Quality checks measure image usability, not disease absence. Symptoms can trigger referral without a usable photo. |

**Proposed precedence:** urgent symptoms → urgent assessment; sensory/nerve concern,
more than five patches, many/widespread patches with unknown count, raised/nodular/thickened
skin or earlobes, eyebrow loss, painless wounds/burns, reported close contact with
the presenting skin concern, or volunteer concern → referral regardless of photo
score or intact sensation. Unusable photo or incomplete required concern assessment
→ clinical review, with retake offered; otherwise a high score → referral. Only a
completed assessment with no triggers permits qualified low-photo wording and
follow-up. These **proposed** answer-based triggers require clinical review and
do not guarantee detection of every MB case. The Zambia guideline's sections 5.1
and 10.1 support skin thickening/nodules and painless injuries as assessment
concerns; the [AI4 study](https://pmc.ncbi.nlm.nih.gov/articles/PMC9903738/)
records eyebrow loss. None validates this combined volunteer rule set.
The methods document and ADR-001 must make this precedence testable. For the
synthetic POC, every result also says **PLACEHOLDER — not clinically validated**.

## Nepal burden and referral context

The government publishes Annual Health Reports, including FY 2080/81 and 2081/82.
[DoHS publications catalogue](https://dohs.gov.np/category/publications/).
Full national-report opens failed on both the HMIS and government-hosted PDF
copies. **Labelled workaround: indexed primary-document text only.** The Bagmati
government FY 2081/82 report's indexed national-situation paragraph (printed page
128) gives national registered prevalence 0.88 per 10,000 and 14 districts above
1 per 10,000; the full file exceeded the web tool's size limit. Those numbers
remain **UNVERIFIED against the full report**, and are not app configuration.
[Bagmati FY 2081/82 report](https://giwmscdnone.gov.np/media/pdf_upload/Annual%20Health%20Report-081-82_evub4er.pdf).
Registered prevalence is not all infections, incidence, or proof of interrupted
transmission. Do not label Nepal “leprosy-free”.

Older EDCD reporting documents contact examination in Nawalparasi-West and
secondary/tertiary care through partner-supported referral centres.
[EDCD FY 2019/20 report](https://www.edcd.gov.np/uploads/resource/6162b6d5e3507.pdf).
More recent WHO Nepal reporting describes July 2026 staff training in Dhanusha
with workers from 10 districts in Koshi, Madhesh and Bagmati, covering diagnosis,
contact tracing, referral of complications and recording.
[WHO Nepal, 8 July 2026](https://www.who.int/nepal/news/detail/08-07-2026-strengthening-capacity-of-frontline-health-workers-for-leprosy-diagnosis-and-management).
These establish continuing programme activity, **not a current complete list of
endemic districts or available clinics**. That list and current district-specific
referral pathways are **UNVERIFIED**. Sarlahi and Nawalparasi-West are documented
historical examples, not a proposed pilot selection.

In Sarlahi, Singh et al. trained 151 FCHVs to detect and refer suspected cases to
the district hospital. They reported no cases detected through FCHV active
referral, although household screening identified two leprosy cases. The paper
also describes leprosy treatment available down to health-post level at that time.
[Primary study, KUMJ 2019](https://www.kumj.com.np/issue/65/40-45.pdf).
Table 2 reports 48/151 (**31.8%**) participants as illiterate; the prose's “majority”
wording conflicts with that table, so use the table. The introduction describes
18 days of basic FCHV training, distinct from the study's one-day orientation.
The district recorded 36 leprosy cases through passive detection during the
same period. Incentives supported training participation, with referral incentives
offered. The authors attribute failure to refer to stigma/concealment; this is
their interpretation, not a causal effect established by the design.
**Inference:** training knowledge and app availability do not establish case
detection or successful referral. A future pilot must measure referral completion,
time to qualified assessment, missed cases and stigma, not just app accuracy.

**Proposed pathway:** volunteer records concern → locally designated basic health
facility assesses → experienced clinician/referral centre confirms difficult cases
or manages complications → consented follow-up records the actual assessment.
The receiving clinic, transport, hours, cost and referral closure mechanism must
be agreed locally before field use. Numbra cannot create that service pathway.

## Open questions

- Which current national and district protocols specify FCHV sensory testing and referral competency?
- Can humans verify the current district burden tables and choose a receiving service, without relying on historical or indexed figures?
- Which local differentials, reaction signs and urgency rules should clinical partners approve?
- How will privacy, refusal, workload, transport and referral completion be evaluated with affected people and FCHVs?

## Confidence

High for WHO cardinal signs and photo limitations; medium for the sourced
clinical challenge vocabulary; low for current Nepal district mapping and field
fitness because local protocols and full current national tables remain unverified.
