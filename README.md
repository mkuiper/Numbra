# Numbra

Numbra is an open-source proof of concept for an offline Android skin-screening
and referral aid for community health volunteers, initially in Nepal. It combines
a lesion photo with guided questions and a transparent referral rule.

It is a triage aid, never a diagnosis. It must never reassure someone that they do
not have leprosy. There is no clinically validated model, deployable app, or field
pilot at this stage. Any model trained only on synthetic fixtures must display
**PLACEHOLDER** in its model card, reports, and app UI.

Current work: M1 Python data scaffold, after the harness closed M0's engineering
gate (human review pending). See [status](notes/STATUS.md), the
[phase-0 synthesis](docs/01-phase0-synthesis.md), the [roadmap](docs/ROADMAP.md),
and [human review queue](notes/HUMAN-QUEUE.md).
No patient data or model weights are committed. No server, upload service,
app-store release, or autonomous diagnosis is in scope.

Code is licensed under [Apache-2.0](LICENSE), with that autopilot decision recorded
in [ADR-003](decisions/ADR-003-code-licence.md). Dataset and pretrained-weight
permissions are separate; the code licence grants no rights to either.

Run `python3 -m unittest discover -s tests -v` for documentation
and repository-safety checks, and `bash scripts/check.sh` for the harness's
available-project checks. M1 now runs the synthetic ML suite; Android remains
skipped until M5. See [ML setup](ml/README.md); green checks at M1 are not a working APK.
