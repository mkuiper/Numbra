# Offline deployment constraints and interoperability

Evidence accessed **2026-10-09**. This is a design proposal for a synthetic
**PLACEHOLDER** Android POC; there is no APK, model conversion or device benchmark
yet. The selected baseline/runtime is recorded in
[ADR-005](../decisions/ADR-005-baseline-runtime.md). No server or upload is in scope.

## Target devices: verified examples versus unknown local distribution

The exact phones used by rural Nepal FCHVs, their RAM/OS/ABI distribution and
available storage are **UNVERIFIED**. Searches of Nepal manufacturer pages and
NTA material did not establish a representative rural volunteer device inventory.
**Labelled research workaround:** use explicit conservative test profiles, with
manufacturer specifications from a regional example; do not describe them as
measured Nepal norms. Humans need a small consented device/workflow survey before
procurement or pilot design. No hardware purchase is authorised here.

Samsung's [Galaxy A04e Philippines specification](https://www.samsung.com/ph/smartphones/galaxy-a/galaxy-a04e-black-32gb-sm-a042fzkdphl/)
lists 3 GB RAM, 32 GB storage, a 720×1600 display, an octa-core processor,
13 MP rear camera and 5,000 mAh typical battery. This is a documented **example**,
not evidence of Nepal ownership, sustained inference speed or usable battery life.

Proposed test profiles: a 2 GB RAM/limited-storage stress profile, a physical
3 GB entry-level phone, and a newer reference phone. Record actual OS, SoC, ABI,
patch level and thermal state when tested. Emulation can check lifecycle and
layout but cannot establish real camera quality, battery cost or thermal latency.
Android minSdk belongs in a later ADR backed by the resolved libraries and device
survey; compatibility with an old OS is not evidence of security maintenance.

## Format and runtime comparison

| Option | Verified primary documentation | Fit and unresolved constraints |
| --- | --- | --- |
| LiteRT/TFLite | [Android guidance](https://developers.google.com/edge/litert/android) distinguishes CompiledModel and Interpreter, with version-dependent minimum SDKs. [TensorFlow quantisation guide](https://developers.google.com/edge/litert/conversion/tensorflow/quantization/post_training_quantization) explains representative-data calibration for full integer conversion. | Viable alternative, especially with TensorFlow/Keras. Must bundle a standalone runtime for deterministic offline use. Current docs' version matrix and sample dependency differ; pin/test the actual artifact rather than copy a sample blindly. |
| ONNX Runtime Mobile | [Mobile guide](https://onnxruntime.ai/docs/tutorials/mobile/) supplies Android Java/C/C++ bindings, CPU execution and optional accelerators. [Quantisation guide](https://onnxruntime.ai/docs/performance/model-optimizations/quantization.html) recommends static CNN quantisation. | Selected for the PyTorch/timm baseline. Verify exported operators, CPU kernels, Android artifact and actual size in M4–M6; do not assume NNAPI is faster. |

For ONNX, start with a float export for debugging, then static INT8 QDQ for
supported convolution/linear operators. Use only training synthetic inputs to
estimate activation ranges; held-out-source/test data must not shape conversion.
Record quantised and remaining float operators. Probability calibration and
activation-range calibration are different operations. Neither validates a
synthetic model clinically. Graph export must preserve inference/evaluation mode.

## Proposed preprocessing contract and parity checks

The publisher's [checkpoint config](https://huggingface.co/timm/mobilenetv3_small_100.lamb_in1k/raw/main/config.json)
uses RGB 3×224×224, bicubic/centre-crop settings and ImageNet channel means/stds.
**Numbra proposal intentionally differs in geometry:** preserve the whole patch
using a deterministic bilinear letterbox instead of centre crop. Use the same
transform for synthetic task training, evaluation and Android inference; evaluate
this change separately before any future clinical use. Pretraining is not a claim
that the proposed geometry is optimal. This is a proposed contract to finalise and
test in M4, not an already tested export specification.

1. Decode bounded-size input, apply all EXIF orientation variants once, composite
   alpha on RGB `(128,128,128)`, and convert to 8-bit RGB. Reject undecodable or
   excessive-dimension images rather than allocating unbounded buffers. Strip
   identifying metadata from retained/exported derivatives; orientation correction
   must precede stripping. No raw GPS/EXIF in summaries or logs.
2. Letterbox to 224×224: scale by `min(224/width,224/height)`; round scaled dimensions
   half-up, clamp each to 1…224, resize bilinearly and centre on RGB-128 padding.
   Put any odd extra padding on the right/bottom. Specify pixel-centre coordinate
   mapping and edge handling in the actual implementation; two libraries' default
   interpolation names alone do not guarantee parity.
3. Convert channels to `[0,1]`; normalise with mean `(0.485,0.456,0.406)` and std
   `(0.229,0.224,0.225)`; NCHW float32 input `[1,3,224,224]`. For this ONNX proposal,
   retain float input/output around quantised internal operators. If switching to
   integer tensors, record scale/zero point and explicit clipping/rounding.
4. Export an uncalibrated binary logit; apply saved temperature and sigmoid once
   in the versioned scoring layer. Save output semantics, threshold and transforms
   together with checksums. Reject non-finite outputs; never convert failure to
   qualified low concern.

M4 tests must cover generated RGB/channel fixtures, wide/tall images, odd padding,
orientation, alpha, malformed and oversized input. Compare Python and Android
preprocessing on generated fixtures in M6, in addition to Python-vs-export graph
parity on exactly the same input tensors in M4.

**Proposed fixed tolerances:** normalised preprocessing tensor max absolute error
≤0.02 across implementations; float ONNX probability error ≤0.0001; quantised
probability error ≤0.02. Use generated inputs covering colour/exposure/shape
variation and separate parity fixtures from quantisation calibration data. Report
max/mean errors, all failing cases and threshold crossings; close probabilities
can still change actions. A sample within 0.02 of the referral threshold is treated
conservatively as refer by the exported-score integration, while symptom overrides
remain active. Compare this margin rule against the Python workflow and report
added referrals. Tolerances and safety margin are engineering choices pending
review; never widen a failing test silently. Re-evaluate held-out results on the
quantised artifact rather than assuming unchanged performance.

## Proposed budgets and offline behaviour

These are **unmeasured engineering targets**, not device facts or clinical gates.
The roadmap's artifact cap is required; other targets guide later profiling.

| Dimension | Proposed target | Verification later |
| --- | --- | --- |
| Model artifact | ≤20 MB; aim <5 MB quantised | Measure actual file bytes and operators, not parameter-count arithmetic alone. |
| Installed/demo package | Aim debug APK <100 MB including native runtime/ABIs | Measure assembled APK separately from model size; trim unused ABIs only with evidence. |
| Peak process memory | Aim <256 MB on stress profile | Profile capture, bounded decode, preprocessing, interpreter and records together. |
| Latency | Aim warm inference p95 <2 s, cold complete scoring <5 s on entry-level physical device | Record device/threads, at least 30 warm trials and cold starts; include decode separately. No UI-thread inference. |
| Power | One inference per accepted capture; no background/repeated analysis | Measure a scripted session on real hardware, log thermal throttling and charging state. No battery-runtime estimate from mAh alone. |

Bundle the PLACEHOLDER model, runtime, question instructions and both language
resources. No login, connectivity check, analytics, cloud inference, update fetch
or remote model download may be required for screening. No internet permission is
needed for this POC's core flow. Test first launch and a complete screening in
airplane mode. Preserve drafts and encrypted records through process death; a
model/load/storage error must leave symptom referral available and state the error.

NTA's [MIS dashboard](https://www.nta.gov.np/misreport) reports subscription
categories; the accessed page did not expose current numbers. Local field
connectivity/outage/charging constraints remain **UNVERIFIED**. Aggregate
subscriptions would not establish connectivity at a particular volunteer visit.
Design for no connectivity throughout the encounter. Future store-and-forward
needs separate consent, residency, access, retry/idempotency and deletion design;
this POC provides deliberate local export only, with no automatic synchronisation.

## Language, literacy and privacy proposals

The Sarlahi [FCHV study, Table 2](https://www.kumj.com.np/issue/65/40-45.pdf)
reports 31.8% of its participants as illiterate, and its introduction describes
18 days of basic training. Incentives did not establish successful referral;
the authors discuss concealment/stigma. This is historical local evidence, not
today's national volunteer profile. **Design inference:** supervised demonstrations,
comprehension checks, symbols with text and optional bundled audio deserve testing;
Nepali text alone cannot establish accessibility.

Ship English and Nepali string resources, with every Nepali clinical instruction
flagged for **native-language and clinical review**. Do not claim translation is
validated. Keep one question per screen, visible unknown/declined answers, large
touch targets and labels that work with screen readers. Use text and symbols,
not colour alone. Demonstrate sensory-test steps with non-patient illustrations
if later approved; no scraped clinical photos. Audio prompts are a future local
usability question and must be bundled if implemented.

Use neutral home/notification wording, explicit PLACEHOLDER banners, qualified
referral wording and an obvious route to the next clinical service. Shared-device
threats require app-private encrypted storage, controlled summary export, minimal
identifiers and suppression of sensitive logs/backups/previews. A permission
refusal should retain the guided symptom flow. These safeguards require M7 tests;
neither encryption nor a neutral name eliminates stigma or device-compromise risk.

## Existing platforms and Nepal interoperability

| Platform | Verified capability | Proposed role and limits |
| --- | --- | --- |
| ODK Collect/Central | [Collect documentation](https://docs.getodk.org/collect-intro/) describes offline Android forms and media/questions; [encryption documentation](https://docs.getodk.org/encrypted-forms/) says finalised forms are encrypted, while drafts can remain plaintext and camera copies may survive. | Strong candidate for later clinician collection instead of building a new submission server. Not proof of always-encrypted drafts or integrated local inference; review identity/consent/permissions and integration before adoption. |
| KoboToolbox/KoboCollect | [Implementer's guide](https://support.kobotoolbox.org/data_collection_kobocollect.html) describes offline collection after form download and later server submission. | Candidate for multilingual collection workflows; no account creation or upload in autopilot. Hosting/residency and security configuration require human decisions. |
| DHIS2 Android Capture | [Implementer's overview](https://dhis2.org/android/) describes offline aggregate and Tracker/Event capture with synchronisation to a DHIS2 instance. | Potential future referral closure/aggregate interoperability; not permission to send clinical photos to a government system. Must map local metadata and access policies. |

The government [HMIS login page](https://hmis.gov.np/dataportal/dhis-web-commons/security/login.action)
is indexed as powered by DHIS2 and managed by the DoHS information-management
branch; direct open failed with HTTP 502. This is **indexed primary-page evidence**,
not inspection of authenticated configuration. Current Nepal leprosy Tracker
schemas, image support, FCHV accounts, approved APIs and receiving-service workflows
are **UNVERIFIED**. No authenticated access or integration was attempted.

**Selected POC boundary:** a small standalone screening app for local inference
and encrypted records; design its contribution schema for later export/mapping
rather than implement ODK/Kobo/DHIS2 sync. Reconsider a collection-platform extension
after humans choose a data custodian and workflow. Future mappings should retain
local opaque record ID, consent version/scope, provisional/confirmed status,
diagnostic method, referral outcome, model/rule versions and timestamps; use
versioned vocabulary crosswalks, never guess official programme codes. Clinical
confirmation is an externally supplied assessment, not a model-score update.

## Open questions

- What devices, OS/ABIs, patch levels, charging and network conditions do intended volunteers actually have?
- Can measured ONNX size, parity, memory and latency meet these proposed budgets?
- Which Nepali wording, sensory illustrations and low-literacy interactions work in supervised usability testing?
- Which institution controls HMIS/referral mappings, data residency, consent and any later platform integration?

## Confidence

High for the documented platform/runtime capabilities; medium for the proposed
offline design; low for rural Nepal hardware, latency, translation and HMIS fitness
because no representative device survey, build, benchmark or authorised integration
has been completed.
