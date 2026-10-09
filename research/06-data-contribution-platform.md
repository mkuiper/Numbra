# Contribution governance: local records now, governed research later

Evidence accessed **2026-10-09**. This is a design, not a submission service or
permission to collect images. M7 builds only a local record model and deliberate
export format, tested with synthetic records. No server, account, upload or real
patient collection is authorised. All models remain **PLACEHOLDER** under
[ADR-002](../decisions/ADR-002-dataset-selection.md). The selected governance is
[ADR-004](../decisions/ADR-004-contribution-governance.md).

## Evidence and scope

WHO's AI governance principles call for human control, informed consent, privacy,
transparency, accountability and equity. These support the safeguards below, but
do not establish that Numbra complies with Nepal law.
[WHO principles, 2021](https://www.who.int/news/item/28-06-2021-who-issues-first-global-report-on-ai-in-health-and-six-guiding-principles-for-its-design-and-use).
Nepal's NHRC 2022 guidance has indexed text describing voluntary withdrawal without
penalty; full document access failed on two official endpoints. **Labelled research
workaround: indexed primary text**, with current procedural details UNVERIFIED.
[NHRC guidance](https://elibrary.nhrc.gov.np/bitstream/20.500.14356/2481/1/National-ethical-guidelines-October.pdf).
The [ethics document](07-ethics-regulatory-nepal.md) records legal evidence and gaps.
Every workflow below is a **Numbra proposal**, requiring institutional approval
before use with people; it is not presented as a statutory requirement.

## Roles and label lifecycle

Trained volunteers may capture consented observations and a provisional suspected
condition. A future participating clinic verifies clinicians' credentials and
scope, with revocation and periodic checks; an app-entered role is not proof of
credentials. Clinicians record an assessment and its method. A designated expert
adjudicates disputed cases. Data stewards check permission, consent and linkage;
model developers receive approved research derivatives, not identity registers.
The POC records these roles as provenance without claiming credential verification.

Proposed state progression: `captured_provisional` → `awaiting_confirmation` →
`confirmed` or `unresolved`; `quarantined` and `withdrawn` block research eligibility.
Confirmation is a separate dated assertion with assessor, institution, clinical
examination/smear/biopsy/expert-adjudication method and an opaque evidence reference.
Do not require biopsy for every diagnosis or imply all confirmation methods are
equally reliable. An app prediction, referral action, repeat photo, treatment
response or volunteer suspicion cannot automatically create a confirmed label.
Record diagnostic disagreement and superseding assertions; never erase provenance.
Missing follow-up remains unresolved, including for referred and low-score cases.

| Proposed record group | Minimum fields / constraints |
| --- | --- |
| Identity and grouping | Random record/encounter IDs, site-scoped patient/group token, lesion/view IDs, source and capture/import origin. The clinic alone holds any re-identification key separately. Never hash a name/phone number as an allegedly anonymous ID. |
| Observations | Sensation status/method/assessor, patch count, distribution/widespread, duration, nerve symptoms, urgent weakness/eye symptoms, raised/nodular/thickened skin or earlobes, eyebrow loss, painless hand/foot wounds/burns, explicit volunteer concern, and optional contact history. Preserve unknown/uncertain/declined/not-tested values; no other person's name. Every answer-based referral reason must remain reconstructable from the stored answers. |
| Label assertions | Original diagnosis, versioned mapped family/diagnosis, explicit PB/MB/reaction if supplied, provisional/confirmed status, confirmation method, confirmer role/reference, dates, disagreement and supersession reason. |
| Consent | Information-sheet version/language, separate scope decisions, how comprehension was checked, date, collector role, participant/guardian/assent status where applicable, withdrawal token/state. No default research opt-in. |
| Image and security | Derivative ID/hash, quality findings, orientation/redaction/metadata-removal version, access and export events, retention policy/due date. Hashes and tokens remain sensitive local metadata. |
| Reproducibility | App/model/rule/preprocessing/schema/taxonomy versions, PLACEHOLDER flag, referral reasons and externally recorded referral outcome. Prediction remains separate from ground truth. |

## Consent, minimisation, retention and withdrawal

Explain capture and local care records first, in reviewed Nepali or the person's
preferred supported language. Use teach-back and private conversation. Obtain
separate choices for local storage, clinic-summary sharing, future research/model
development, and any future cross-border transfer/public release. A general care
consent does not authorise research. Refusal must preserve ordinary care/referral;
offer symptom-only assessment without taking a photo. Minor/guardian/assent and
impaired-capacity procedures need local ethics review; the POC uses synthetic
examples only. Avoid storing signature photographs or identity documents.

Frame only the lesion where feasible. Flag faces, tattoos, jewellery, household
details, identifying marks and embedded text for trained human review. Correct
orientation, create a re-encoded derivative without EXIF/GPS or other metadata,
then review pixels and filenames. If identifiers cannot be safely removed without
destroying utility, quarantine or exclude the image. A crop, automated detector
or absent EXIF is not an anonymity certificate. Linkable longitudinal records
remain pseudonymous. Keep the original only if a separately approved purpose and
retention policy require it; do not place capture copies in a shared gallery.

Propose app-private authenticated encryption, device-bound key management, no
sensitive logs/notifications/previews/backups and controlled temporary exports.
Test corruption, lost keys, process death, deletion, file-provider scope and
temporary-file expiry in M7/M8. Encryption does not protect an unlocked shared
phone or an authorised recipient's copy. Loss of keys must yield an explicit
unavailable-record state, not plaintext recovery. Refer without relying on storage.

Before real collection, the Nepal custodian must set separate numeric retention
periods for care, source images, research derivatives, audit records and backups,
with legal/ethics reasons. **No real-data retention period is approved here.**
The POC demonstrates explicit deletion and policy fields; it must not imply that
an unset policy authorises indefinite real storage. Residency starts on the local
device; this is a design choice, not a verified legal localisation requirement.
Future hosting, processor contracts and cross-border conditions remain UNVERIFIED.

Provide a receipt/withdrawal token and a reachable local custodian in a future
protocol. Withdrawal stops new exports and dataset inclusion, marks linked records,
and schedules approved deletion of active copies/backups and recipient requests.
Retain only the minimal authorised tombstone needed to prevent re-ingestion.
Explain limits: a copied referral summary cannot be remotely recalled, and deletion
from source data does not automatically undo influence on a trained model. Track
affected versions and obtain a human decision on retraining/retirement; never
promise immediate model unlearning. Care-record obligations must be explained
separately and resolved by the custodian, not guessed by this app.

## Local export and future quality control

M7 should define versioned JSON for contribution metadata with explicit consent,
label provenance and schema version; validate before export, reject unknown consent
states, and omit direct identifiers. A separate clinic summary contains minimum
care information and the person's sharing choice; exclude photos by default.
Preview exactly what will be shared, identify the chosen recipient and record the
event. Android sharing is an explicit user action, not an upload service. The
recipient app may transmit or retain it; Numbra cannot guarantee downstream
residency, encryption or withdrawal. Research image transfer is a later governed
process, not implied by exporting metadata. Nothing is sent in autopilot.

For a future service, authenticate authorised contributors, quarantine all new
submissions, enforce file/decode limits and check blur/exposure, metadata, rights
and consent. Exact hashes and reviewed perceptual matches link duplicates across
sources before patient/group splits. Quarantine conflicting labels and suspicious
repeated/adversarial submissions; keep an appeal and correction trail. Sample
labels for blinded independent assessment, record raw agreement, a prespecified
agreement statistic, class counts and disagreement resolution. No measured
inter-rater reliability or automated identity-redaction performance is claimed.

## Model promotion, sovereignty and site-bound alternatives

Proposed future cycle: steward approves a versioned consent/licence/provenance
snapshot → researcher retrains with patient/duplicate isolation → independent
evaluation uses a frozen held-out cohort and source/tone/presentation breakdowns →
clinicians and ethics/data governors sign off → a separately authorised release.
Record exclusions, threshold/rule versions, hashes, model card, software/parity
evidence, intended use, monitoring and rollback. No continuous on-device learning
or automatic promotion. Repeatedly tuning on the frozen holdout invalidates its
independence; register a replacement cohort for later development cycles.
Synthetic checks demonstrate mechanics and cannot satisfy clinical promotion.

Propose a Nepal institution as accountable custodian, with affected people/FCHVs
represented in access and benefit-sharing decisions. Legal ownership, licence,
authorship, funding terms, commercial use and authority to transfer are **UNVERIFIED**
and must be agreed; open-source code does not mean open patient images. Budget
local annotation/training, share accessible findings and useful services, and
support complaints/redress without conditioning care on contribution.

Federated learning aggregates locally computed model updates while training data
remain distributed in the original method.
[McMahan et al., AISTATS 2017](https://arxiv.org/abs/1602.05629).
**Proposal: later**, after institutions, connectivity, threat assessment and update
governance exist. Do not infer that keeping images local establishes anonymity or
legal permission for exchanging updates. For site-bound data, start instead with
approved local evaluation and disclosure-controlled aggregate findings. Neither
federation nor a research backend belongs in this offline POC.

## Open questions

- Which Nepal institution will be custodian, credential verifier and withdrawal contact?
- Which consent/guardian/assent wording, retention periods and evidence methods will local reviewers approve?
- Who may authorise secondary use, cross-border transfer or a dataset licence, and how will communities share benefits?
- What independent cohort and human release board could assess a future clinically trained model?

## Confidence

Medium for the proposed provenance and separation-of-duty design; low for legal,
operational and consent fitness until Nepal institutions and affected people review
it. No contribution system, security control or clinical release has been built.
