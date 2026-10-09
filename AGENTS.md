# Working in Numbra

## Roles and authority

- **Builder (Codex):** implements and documents one roadmap milestone at a time,
  runs checks, commits logical steps, and writes HANDOFF and RESPONSE files.
- **Reviewer (Claude):** critically evaluates evidence and implementation. The
  review is saved in `reviews/<milestone>/REVIEW-<n>.md` by the review tooling.
- **Humans (Mike and the clinical partner):** review scientific, clinical, ethical,
  and legal choices; approve attended gates and review autopilot ADRs afterwards.
- **Harness:** runs tests of record and reviews between unattended iterations,
  writes CHECK logs and GATE files, and handles pushes to the current autopilot branch.

Read `docs/ROADMAP.md`, `notes/STATUS.md`, `notes/HARNESS.md`, the current milestone's
review folder, then this file and relevant ADRs, in that order every iteration.
The roadmap defines acceptance; review folders are `reviews/M0/`, `reviews/M1/`, etc.

## Review and handoff

Builder produces → writes HANDOFF → reviewer evaluates → Builder answers each
numbered issue in RESPONSE as accepted, rejected with evidence, or deferred to
humans → revises → repeat until PASS, PASS WITH CHANGES, or the three-round limit.

In **attended** mode the Builder may run `scripts/review.sh <milestone>` and humans
approve GATE.md. In **autopilot** mode, as in the current run, the Builder must
never run review.sh or write REVIEW, CHECK, or GATE files. The harness runs
`scripts/check.sh` and review.sh, then closes gates itself. Humans review
`notes/HUMAN-QUEUE.md` afterwards. See [autopilot instructions](prompts/autopilot.md)
and [harness documentation](docs/AUTOPILOT.md).

Review exit codes: 0 PASS; 10 PASS WITH CHANGES; 20 REVISE; 30 round limit reached;
1 error. A review request is a single `REVIEW M<n>` line in `notes/NEXT_ACTION`.
Otherwise write CONTINUE, or DONE only after every gate exists and check.sh is green.
Overwrite STATUS, append a UTC iteration JOURNAL entry, and commit before ending.

## Evidence and safeguards

- Research only in M0: no training or app implementation before its gate.
- Cite primary sources for factual research claims; use **UNVERIFIED** for claims
  that cannot be checked. Record access dates and distinguish proposals from facts.
- Each research document ends with Open questions and Confidence sections.
- No patient data in git, including public data. `data/` stays fully ignored.
  Describe its layout in tracked documentation rather than forcing a README into it.
- Only use public datasets permitted without registration, signed agreements, or
  accepting terms on another person's behalf. Do not scrape clinical photos.
- Keep secrets and weights out of git. Do not publish, send messages, or push;
  the harness owns the allowed push to the current `autopilot/*` branch.
- Protected: `prompts/`, `scripts/`, `docs/ROADMAP.md`, and
  `reviews/**/{REVIEW-*,CHECK-*,GATE.md}`. Never edit these.
- Add tests for built functionality. Never weaken or skip a failing test; fix
  the code or document the disputed test in JOURNAL and HUMAN-QUEUE.
- Make unattended decisions as ADRs with status
  `Accepted (autopilot) — pending human review`; queue each for humans and proceed.
  This overrides the attended phase-0 prompt's requirement to await decisions.
- After two genuine attempts at a blocker, use and document a labelled workaround.
  Synthetic models must say **PLACEHOLDER** everywhere they surface.
- The app must never output “no leprosy” or an equivalent negative diagnosis.

Install toolchains only in the permitted home locations and record commands in
`docs/DEV-SETUP.md`. Do not touch unrelated files outside this repository.
