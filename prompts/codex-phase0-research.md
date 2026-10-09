# Numbra — Phase 0 Kickoff Prompt (Codex research team)

Before starting: copy `prompts/` and `scripts/` from this kit into the root of a fresh clone
of https://github.com/mkuiper/Numbra.git, run `chmod +x scripts/review.sh`, and check
`claude auth status` succeeds. Codex needs network access when it runs `scripts/review.sh`,
because the script calls Claude. Then paste everything below the line into Codex.

---

You are the lead of a small agentic research team working on **Numbra**, an open-source
proof-of-concept tool to help **community health volunteers** (initially Female Community
Health Volunteers in Nepal) screen skin lesions for possible **leprosy (Hansen's disease)**
and refer suspected cases to a clinic. Numbra is a **triage and referral aid, not a
diagnostic device**. Its name refers to the key clinical sign an image cannot show:
numbness (loss of sensation) in a skin patch.

This is **Phase 0: research only**. Do not write model training code or app code yet.
Your output is a set of evidence-backed documents that a second AI (Claude, acting as
critical reviewer) and the human leads will review before Phase 1 begins.

## Working rules

1. **Evidence over memory.** Every factual claim about a dataset, paper, model, licence,
   metric or law must carry a source link. If you could not verify something, mark it
   `UNVERIFIED` rather than stating it. Never invent citations, dataset sizes or licences.
2. **Write for review.** Each document ends with an `## Open questions` section and a
   `## Confidence` line (high / medium / low, with one sentence of justification).
3. **Small commits, clear messages.** One logical change per commit, prefixed with the
   phase, for example `phase0: add dataset survey`.
4. **No patient data in the repo, ever.** No images, no links to scraped clinical photos,
   no identifiable information. Datasets are described and linked, never vendored.
5. **Flag, don't decide, on ethics and law.** Where a choice has ethical, consent or legal
   implications, lay out the options in `decisions/` and leave the decision to the humans.
6. **Run the review loop at the gate.** When the deliverables below are done, follow
   "Step 4 — Review loop with Claude". Never edit `prompts/claude-reviewer.md`,
   `scripts/review.sh` or any `REVIEW-*.md` file; those belong to the reviewer and humans.

## Step 1 — Scaffold the repository

Create this structure (empty folders get a short `README.md` explaining their purpose):

```
Numbra/
├── README.md                  # project purpose, scope, non-goals, status, disclaimer
├── LICENSE                    # Apache-2.0 for code (flag in decisions/ if unsure)
├── AGENTS.md                  # how agents work in this repo: roles, rules above, handoff protocol
├── docs/
│   ├── 00-project-brief.md    # problem, users, context, success criteria for the POC
│   └── glossary.md            # clinical + ML terms (PB/MB, reactions, macule, sensitivity…)
├── research/
│   ├── 01-clinical-background.md
│   ├── 02-prior-work.md
│   ├── 03-datasets.md
│   ├── 04-models-and-methods.md
│   ├── 05-deployment-constraints.md
│   ├── 06-data-contribution-platform.md
│   ├── 07-ethics-regulatory-nepal.md
│   └── sources.bib            # or sources.md — every source cited anywhere
├── prompts/                   # ALREADY PRESENT — reviewer prompt; do not edit
├── scripts/
│   └── review.sh              # ALREADY PRESENT — launches the Claude reviewer; do not edit
├── decisions/
│   └── ADR-template.md        # Architecture/Decision Record template
├── reviews/
│   └── M0/                    # reviewer writes here; you write HANDOFF.md here
├── data/                      # README only: data is NEVER committed; describe layout + .gitignore
├── ml/                        # README only for now (Phase 1+)
├── app/                       # README only for now (Phase 3+)
└── .gitignore                 # ignore data/, model weights, secrets, notebooks' outputs
```

`AGENTS.md` must define three roles: **Builder** (Codex, produces work), **Reviewer**
(Claude, critiques work and writes to `reviews/<milestone>/`), and **Humans** (Mike and the
clinical partner, who approve gates and decide ADRs). It must define the loop:
Builder produces → Builder writes HANDOFF → `scripts/review.sh <milestone>` launches
Claude and saves `REVIEW-<n>.md` → Builder writes `RESPONSE-<n>.md` addressing each point
(accept / reject with reason / defer) and revises → repeat until the verdict is `PASS` or
`PASS WITH CHANGES`, or the round limit (3) is reached. Describe both ways of running it:
**attended** (the Builder runs review.sh and humans approve GATE.md) and **autopilot**
(`scripts/autopilot.sh` runs check.sh and review.sh between Builder iterations, writes
GATE.md itself, and humans review `notes/HUMAN-QUEUE.md` afterwards; see
`prompts/autopilot.md`). Document review.sh's exit codes: 0 PASS, 10 PASS WITH CHANGES,
20 REVISE, 30 round limit reached, 1 error. Review folders are named by roadmap milestone
(`reviews/M0/`, `reviews/M1/`, …).

## Step 2 — Research deliverables

### 01-clinical-background.md
- How leprosy is diagnosed clinically (WHO cardinal signs), PB vs MB classification,
  common lesion presentations, leprosy reactions, and the main **differential diagnoses**
  a classifier must not confuse with leprosy (e.g. tinea, pityriasis versicolor, vitiligo,
  eczema, psoriasis — verify and complete this list from WHO/clinical sources).
- What information besides a photo is diagnostically important (sensation testing, nerve
  thickening, lesion count, duration, contact history) and how a volunteer could collect
  each item in the field.
- Nepal context: burden, endemic districts, existing referral pathways, the role of FCHVs.

### 02-prior-work.md
For each tool or study: what it does, who built it, data used, model, reported metrics,
validation setting, whether code/model/data are available and under what licence, and
**what Numbra could reuse or learn**. Must cover at minimum:
- AI4Leprosy (Fiocruz / Microsoft / Novartis Foundation, Lancet Regional Health – Americas 2022)
- WHO Skin NTDs App (UniversalDoctor / UOC), its AI visual classifier, the Kenya field
  study, and the independent leprosy evaluation (PAHO journal)
- NLR SkinApp; LEARNS (Philippines); the 2023 JMIR Dermatology scoping review of leprosy apps
- Academic leprosy image-classification papers (search IEEE, PubMed, arXiv, medRxiv)
- Closely related general dermatology AI work on diverse skin tones and smartphone images
End with a table comparing them and a section: **"Who should we contact before building?"**

### 03-datasets.md
A survey of every candidate dataset. For each: name, link, owner, size, image modality
(clinical smartphone / clinical camera / dermoscopy), label taxonomy, how labels were
confirmed (biopsy / smear / expert / crowd), skin-tone distribution (Fitzpatrick or
Monk if reported), geography, **licence and permitted use**, access process, and whether
it contains leprosy or its key differentials.
Candidates to verify (do not assume any of these are suitable):
- AI4Leprosy open dataset
- General dermatology sets that may supply differentials or leprosy classes:
  Fitzpatrick17k, DDI (Diverse Dermatology Images), SCIN (Google), PAD-UFES-20,
  DermNet, ISIC (likely irrelevant — dermoscopic, melanoma-focused; say so if true)
- Any dataset associated with the WHO Skin NTDs App or published leprosy studies
Then produce a **dataset-combination analysis**:
- A proposed unified label taxonomy (likely hierarchical: `leprosy (PB/MB/reaction)` /
  `leprosy-differential (named)` / `other` / `refer-for-review`) and a mapping table
  from each source's labels into it.
- Risks of combining: licence incompatibility, label-definition mismatch, duplicate
  images across sets, patient-level leakage between train/test, modality and camera
  domain shift, skin-tone imbalance, site/hospital shortcut features (rulers, markers,
  backgrounds).
- A recommendation: which combination is legally usable **and** scientifically sound
  for a Phase 1 baseline, and what is missing (expect: South Asian smartphone images).

### 04-models-and-methods.md
- Recommended baseline approaches given small data: transfer learning from ImageNet or
  dermatology foundation models (identify which exist, their licences, and whether they
  can run on-device), image + tabular metadata fusion (as AI4Leprosy did).
- **Task framing.** Argue for/against: binary `refer / don't refer` with a fixed
  high-sensitivity operating point vs multi-class differential vs top-k. Recommend one.
- Evaluation protocol: patient-level splits, **leave-one-dataset/site-out** testing,
  sensitivity at fixed specificity, calibration, per-skin-tone and per-presentation
  (classical vs reactional vs atypical) breakdowns, confidence/abstention behaviour.
- How the sensation test and other non-image inputs should combine with the model
  output into a referral recommendation (a transparent rule, not a black box).

### 05-deployment-constraints.md
- Target devices: low-end Android phones common in rural Nepal (verify typical specs).
- **Offline-first** inference: on-device model formats (TFLite/LiteRT, ONNX Runtime
  Mobile), model size and latency budgets, quantisation.
- Connectivity, store-and-forward sync, battery, Nepali language and low-literacy UI.
- Existing open-source platforms worth building on rather than reinventing (e.g. ODK /
  Kobo / DHIS2 Android capture — verify fitness), and how Numbra could interoperate
  with Nepal's health information systems.

### 06-data-contribution-platform.md
Design (not build) a framework for practitioners to submit new labelled images that
improve future models. Cover:
- Who can submit (credentialed clinicians vs volunteers) and how labels are confirmed:
  provisional label at capture → **confirmed label** only after clinical diagnosis /
  smear / expert adjudication, with label-provenance fields.
- Consent flow, de-identification (faces, tattoos, jewellery, EXIF/GPS stripping),
  secure storage, data residency, retention and withdrawal of consent.
- Quality control: image-quality checks at capture, duplicate detection, inter-rater
  agreement, adversarial or erroneous submission handling.
- **Model governance:** submissions never flow straight into a deployed model. Define a
  versioned dataset → retrain → evaluate on a frozen held-out set → human sign-off →
  release cycle, plus a model card per release.
- Options for data that cannot leave a site (e.g. federated learning) — note
  feasibility for a POC honestly, probably "later".
- Data-sovereignty and benefit-sharing questions for Nepal; who owns the dataset.

### 07-ethics-regulatory-nepal.md
- Ethics approval route for collecting images and running a field pilot in Nepal
  (identify the relevant national body and process — verify), privacy law applicable
  to health images in Nepal, and whether a screening aid like this is regulated as a
  medical device there or in likely future markets.
- Risks and mitigations: false negatives delaying care, stigma from a phone holding
  "leprosy" data (consider app naming, neutral UI wording, data on device), automation
  bias in volunteers, misuse.
- A draft "intended use" statement and list of non-goals.

## Step 3 — Synthesis

Write `docs/01-phase0-synthesis.md`:
- The recommended Phase 1 plan (datasets, taxonomy, baseline model, evaluation) in one page.
- The 3–5 decisions humans must make, each drafted as an ADR in `decisions/`
  (e.g. ADR-001 task framing, ADR-002 dataset selection & licensing, ADR-003 code licence,
  ADR-004 data contribution governance).
- A proposed phase plan with gates:
  Phase 0 research → Phase 1 baseline classifier on public data →
  Phase 2 local data collection protocol + ethics →
  Phase 3 offline Android prototype → Phase 4 supervised field pilot.

## Step 4 — Review loop with Claude (attended runs only)

If you are running under the autopilot (`prompts/autopilot.md`), skip this step: write
HANDOFF.md and request review as that file describes.

1. Write `reviews/M0/HANDOFF.md`: what you produced (with file list), your top five
   uncertainties, and what you want the reviewer to scrutinise hardest. Commit it.
2. Run `scripts/review.sh M0`. It can take several minutes; do not interrupt it.
   It writes `reviews/M0/REVIEW-<n>.md` and exits with the verdict code.
3. Read the review in full, then act on the exit code:
   - **20 (REVISE) or 10 (PASS WITH CHANGES):** write `reviews/M0/RESPONSE-<n>.md`
     answering every numbered issue as **accepted** (with what you changed and where),
     **rejected** (with evidence, not opinion), or **deferred to humans**. Make the
     accepted changes, update HANDOFF.md, commit, and for exit code 20 run the script
     again. For exit code 10, fix the issues and continue to step 4 without another review.
   - **0 (PASS):** continue to step 4.
   - **30 (round limit):** do not run the script again. Go to step 4 and list the
     unresolved disagreements.
   - **1 (error):** report the error message and stop. Do not write a review yourself
     or skip the review.
4. Write `reviews/M0/GATE.md`: final verdict, rounds taken, issues resolved,
   issues rejected or deferred (with reasons), and the questions for the humans
   collected from every review. Commit, then **stop and wait for the humans**.
   Phase 1 starts only when a human adds an approval line to GATE.md.
