# Running Numbra on autopilot

Codex builds and Claude reviews, unattended, working through `docs/ROADMAP.md` from
research (M0) to a debug APK (M8). You read the results in the morning.

## Who does what

| Role | Who | Can edit the repo? |
|---|---|---|
| Builder | Codex (`codex exec`, one iteration at a time) | Yes, except protected files |
| Reviewer | Claude Code (`claude -p`, read-only tools + web) | No; the harness saves its review |
| Harness | `scripts/autopilot.sh` | Runs tests of record, reviews, gates; reverts protected edits; pushes |
| Humans | You | Edit the roadmap between runs; work through `notes/HUMAN-QUEUE.md` |

Protected files: `prompts/`, `scripts/`, `docs/ROADMAP.md`, and every
`reviews/**/REVIEW-*`, `CHECK-*` and `GATE.md`. If Codex edits them, the harness
reverts the change and tells it so in `notes/HARNESS.md`.

## One-time setup (laptop)

```bash
git clone git@github.com:mkuiper/Numbra.git && cd Numbra
unzip ~/Downloads/numbra-agent-kit.zip          # adds prompts/ scripts/ docs/
chmod +x scripts/*.sh
git add -A && git commit -m "Add autopilot agent kit" && git push

codex --version && claude auth status            # both installed and signed in
claude update                                    # review.sh needs Claude Code ≥ 2.1.259
```

Also needed: Python 3.10+, git, and `timeout` (coreutils). Codex installs the JDK and
Android SDK itself during M5 and records the steps in `docs/DEV-SETUP.md`. Allow about
10 GB of disk for the SDK, Gradle and datasets.

## Start an overnight run

```bash
cd Numbra
tmux new -s numbra
systemd-inhibit --what=sleep:idle --why="Numbra autopilot" scripts/autopilot.sh
#   macOS: caffeinate -i scripts/autopilot.sh
# detach with Ctrl-b d ; re-attach later with: tmux attach -t numbra
```

Useful settings (environment variables):

```bash
AUTOPILOT_HOURS=10          # wall-clock budget
AUTOPILOT_MAX_ITER=40       # iteration cap
AUTOPILOT_ITER_TIMEOUT=90m  # max length of one Codex iteration
NUMBRA_REVIEW_MAX_ROUNDS=3  # review rounds per milestone before auto-closing
NUMBRA_REVIEW_BUDGET_USD=5  # cap per review (API-key billing only)
CODEX_MODEL=...             # override Codex's default model
```

Stop gracefully at any time: `touch STOP` in the repo root (the run halts before the
next iteration). Hard stop: Ctrl-C in the tmux pane.

## In the morning

Work happens on a branch named `autopilot/<date-time>` and is pushed after every
iteration, so you can also follow along on GitHub. Read, in order:

1. `notes/STATUS.md`: where it got to.
2. `notes/HUMAN-QUEUE.md`: decisions made without you, blockers, placeholders.
3. `reviews/M*/GATE.md`: which milestones closed, and on what verdict.
4. `notes/JOURNAL.md` and `notes/HARNESS.md`: the story of the night.
5. `runs/<timestamp>/`: raw Codex transcripts and the harness log (not committed).

Merge to `main` only after you've reviewed the work. To continue from where the run
stopped, check out the branch and start the autopilot again; it picks up from the notes.

## Safety notes

- By default Codex runs with `--sandbox danger-full-access --ask-for-approval never`,
  because builds need network access and write outside the repo (Gradle and SDK caches).
  That means it can do anything your user account can. Prefer a **separate Linux user
  or a VM** with its own Codex/Claude sign-ins and a GitHub **deploy key** scoped to this
  repo only, rather than your main account and SSH keys.
- The guardrails (protected files, independent test runs, read-only reviewer) catch
  accidents and shortcuts. They do not stop a Builder with full machine access that is
  determined to get around them, which is another reason to isolate the run.
- Hard limits for the Builder (in `prompts/autopilot.md`): no real patient data beyond
  openly licensed public datasets, no accepting licence agreements or creating accounts,
  no publishing or releases, no secrets in the repo, and the app must never tell anyone
  they don't have leprosy.
