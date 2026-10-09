# Project brief

## Problem and proposed users

Numbra's POC is intended to help community health volunteers, initially Nepal's
Female Community Health Volunteers, collect a lesion photo and structured symptoms
and recommend clinic referral. This is a proposed workflow, not an established
Nepal referral protocol or a validated medical device.

WHO identifies loss of sensation in a pale or reddish patch as a cardinal sign;
the other signs involve peripheral nerve findings or bacilli in a slit-skin smear.
A photograph cannot measure sensation. This motivates collecting answers alongside
the image and retaining clinical referral authority.
[WHO leprosy fact sheet, 23 January 2026](https://www.who.int/news-room/fact-sheets/detail/leprosy)
(accessed 2026-10-09).

## POC success and boundaries

The [roadmap](ROADMAP.md) defines completion: evidence review, synthetic-capable ML
pipeline, reproducible evaluation, quantised model with parity checks, offline
Android flow, encrypted records, referral summary, and a synthetic end-to-end test
through a debug APK. Model metrics on synthetic data demonstrate software behaviour
only. No deployment claims or clinical accuracy claims follow from them.

The intended outputs are referral advice, including urgent referral where rules
require it, or qualified low concern from the photo with explicit follow-up advice.
Never provide a negative diagnosis. Guided questions cover sensation, patch count,
duration, nerve symptoms, and contact history; local clinical partners must review
the wording and procedures before any use with people.

No clinical pilot, real-data collection, server, automatic training from submissions,
treatment recommendation, or publication is authorised by this POC. English and
Nepali resources are planned; Nepali needs native review. Home-screen wording will
be neutral. Contributions are a local record model and export format only.

## Open questions

- Which Nepal clinical partner will validate volunteer procedures and referral routes?
- What supported device inventory and native-language wording fit the target sites?
- Which ethics and regulatory approvals would a future pilot require?

## Confidence

High on POC boundaries specified by the roadmap; low on field fitness until Nepal
partners validate the proposed workflow.
