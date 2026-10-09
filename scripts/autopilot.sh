#!/usr/bin/env bash
# Numbra autopilot — runs Codex (Builder) and Claude (Reviewer) unattended, e.g. overnight.
#
# Usage (from the repo root, ideally inside tmux):
#   scripts/autopilot.sh
#
# Each loop:
#   1. Runs one Codex iteration (`codex exec`) with prompts/autopilot.md.
#   2. Commits anything left uncommitted, then reverts edits to protected files
#      (prompts/, scripts/, docs/ROADMAP.md, review/check/gate files) and reports them.
#   3. Reads notes/NEXT_ACTION:
#        CONTINUE     → next iteration
#        REVIEW <M>   → runs scripts/check.sh (saved as CHECK-n.log), then
#                       scripts/review.sh <M>; on PASS / PASS WITH CHANGES / round
#                       limit it writes reviews/<M>/GATE.md (auto-approval)
#        DONE         → runs the final check (app required); stops if it passes
#   4. Pushes the autopilot branch.
#
# Stops on: DONE verified, deadline, iteration cap, a STOP file in the repo root
# (`touch STOP`), or two consecutive iterations that change nothing.
#
# Env (all optional):
#   AUTOPILOT_HOURS          wall-clock budget, default 10
#   AUTOPILOT_MAX_ITER       iteration cap, default 40
#   AUTOPILOT_ITER_TIMEOUT   per-Codex-iteration timeout, default 90m
#   AUTOPILOT_BRANCH         default autopilot/<YYYYMMDD-HHMM>
#   AUTOPILOT_PUSH           1 to push after each iteration (default 1)
#   CODEX_MODEL              passed to codex as -m if set
#   CODEX_FLAGS              default: --sandbox danger-full-access
#                            (codex exec is non-interactive, so it never asks for approval)
#   plus NUMBRA_REVIEW_* (see scripts/review.sh)

set -uo pipefail

ROOT="$(git rev-parse --show-toplevel)" || { echo "Run inside the Numbra git repo" >&2; exit 1; }
cd "$ROOT"

HOURS="${AUTOPILOT_HOURS:-10}"
MAX_ITER="${AUTOPILOT_MAX_ITER:-40}"
ITER_TIMEOUT="${AUTOPILOT_ITER_TIMEOUT:-90m}"
BRANCH="${AUTOPILOT_BRANCH:-autopilot/$(date +%Y%m%d-%H%M)}"
PUSH="${AUTOPILOT_PUSH:-1}"
read -r -a CODEX_ARGS <<< "${CODEX_FLAGS:---sandbox danger-full-access}"
[[ -n "${CODEX_MODEL:-}" ]] && CODEX_ARGS+=(-m "$CODEX_MODEL")

DEADLINE=$(( $(date +%s) + ${HOURS%.*} * 3600 ))
RUN_DIR="runs/$(date +%Y%m%d-%H%M%S)"
PROTECTED=(prompts scripts docs/ROADMAP.md)
GIT_ID=(-c user.name="Numbra autopilot" -c user.email="autopilot@numbra.invalid")

for cmd in codex claude git timeout; do
  command -v "$cmd" >/dev/null || { echo "ERROR: '$cmd' not found on PATH" >&2; exit 1; }
done
for f in prompts/autopilot.md prompts/claude-reviewer.md docs/ROADMAP.md scripts/check.sh scripts/review.sh; do
  [[ -f "$f" ]] || { echo "ERROR: missing $f — copy the agent kit into the repo first" >&2; exit 1; }
done
claude auth status >/dev/null 2>&1 || { echo "ERROR: Claude Code not signed in (claude auth status)" >&2; exit 1; }
[[ -n "$(git status --porcelain)" ]] && { echo "ERROR: working tree not clean; commit or stash first" >&2; exit 1; }

mkdir -p "$RUN_DIR" notes
LOG="$RUN_DIR/autopilot.log"
log()     { echo "[$(date '+%F %T')] $*" | tee -a "$LOG"; }
harness() { echo "- $(date -u '+%FT%TZ') — $*" >> notes/HARNESS.md; log "HARNESS: $*"; }
commit()  { git add -A && git "${GIT_ID[@]}" commit -q -m "$1" >/dev/null 2>&1 || true; }

# One-time setup on the branch.
git checkout -q -B "$BRANCH"
grep -qxF 'runs/' .gitignore 2>/dev/null || echo 'runs/' >> .gitignore
grep -qxF 'STOP'  .gitignore 2>/dev/null || echo 'STOP'  >> .gitignore
grep -qxF 'data/' .gitignore 2>/dev/null || echo 'data/' >> .gitignore
[[ -f notes/HARNESS.md ]]     || printf '# Harness messages\n\nWritten by scripts/autopilot.sh. The Builder reads this first each iteration.\n\n' > notes/HARNESS.md
[[ -f notes/JOURNAL.md ]]     || printf '# Journal\n\nAppend-only log of Builder iterations.\n\n' > notes/JOURNAL.md
[[ -f notes/HUMAN-QUEUE.md ]] || printf '# For the humans\n\nDecisions made autonomously, blockers, and anything needing human review.\n\n' > notes/HUMAN-QUEUE.md
[[ -f notes/STATUS.md ]]      || printf '# Status\n\nNot started. Begin with M0 in docs/ROADMAP.md.\n' > notes/STATUS.md
echo CONTINUE > notes/NEXT_ACTION
harness "Autopilot run started on branch $BRANCH (budget ${HOURS}h, max $MAX_ITER iterations)."
commit "harness: start autopilot run $BRANCH"

push() { [[ "$PUSH" == 1 ]] && { git push -q -u origin "$BRANCH" >>"$LOG" 2>&1 || log "push failed (will retry next iteration)"; }; }

# Revert any change to protected paths between $1 and HEAD.
guard_protected() {
  local base="$1" changed=()
  mapfile -t changed < <(
    git diff --name-only "$base" HEAD -- "${PROTECTED[@]}"
    git diff --name-only "$base" HEAD -- 'reviews/' | grep -E '/(REVIEW-[0-9]+\.md|CHECK-[0-9]+\.log|GATE\.md)$'
  )
  (( ${#changed[@]} )) || return 0
  for f in "${changed[@]}"; do
    if git cat-file -e "$base:$f" 2>/dev/null; then git checkout -q "$base" -- "$f"; else git rm -q -f "$f"; fi
  done
  commit "harness: revert edits to protected files"
  harness "Reverted Builder edits to protected files: ${changed[*]}. Do not edit these."
}

# Runs check + review for milestone $1, writes GATE.md on acceptance.
do_review() {
  local m="$1" dir="reviews/$1" n=1 rc verdict
  [[ -f "$dir/HANDOFF.md" ]] || { harness "REVIEW $m requested but $dir/HANDOFF.md is missing."; return; }
  [[ -f "$dir/GATE.md" ]]    && { harness "REVIEW $m requested but $m already has GATE.md; move to the next milestone."; return; }
  while [[ -f "$dir/REVIEW-$n.md" ]]; do n=$((n + 1)); done

  log "Running check.sh for $m (round $n)"
  scripts/check.sh > "$dir/CHECK-$n.log" 2>&1; local check_rc=$?
  log "check.sh exit $check_rc"

  log "Running Claude review for $m (round $n)"
  scripts/review.sh "$m" >>"$LOG" 2>&1; rc=$?
  case $rc in
    0)  verdict="PASS" ;;
    10) verdict="PASS WITH CHANGES" ;;
    20) verdict="REVISE" ;;
    30) verdict="ROUND LIMIT" ;;
    *)  rm -f "$dir/CHECK-$n.log"
        harness "Review of $m failed to run (exit $rc; see $LOG). Check RESPONSE-$((n-1)).md exists if this is a later round, then request review again."
        commit "harness: review $m could not run"; return ;;
  esac
  log "Review verdict for $m: $verdict"

  if [[ $rc != 20 ]]; then
    if [[ $rc == 30 ]]; then rm -f "$dir/CHECK-$n.log"; fi
    {
      echo "# Gate $m — closed by autopilot"
      echo
      echo "- Closed: $(date -u '+%FT%TZ')"
      echo "- Verdict: $verdict after $((rc == 30 ? n - 1 : n)) review round(s)"
      echo "- Last test run: check.sh exit $check_rc"
      echo "- Human approval: **pending** — review this gate and notes/HUMAN-QUEUE.md"
    } > "$dir/GATE.md"
    [[ $rc == 30 ]] && echo "- Gate $m closed at the review round limit with unresolved reviewer issues; see reviews/$m/." >> notes/HUMAN-QUEUE.md
    harness "Milestone $m closed ($verdict). Address cheap non-blocking items, then start the next milestone."
  else
    harness "Review $n of $m: REVISE. Read reviews/$m/REVIEW-$n.md, write RESPONSE-$n.md, fix, and request review again."
  fi
  commit "harness: review $m round $n — $verdict"
}

# ------------------------------------------------------------------------------------
iter=0; idle=0
while :; do
  [[ -f STOP ]]                       && { log "STOP file found — stopping."; break; }
  (( $(date +%s) >= DEADLINE ))       && { log "Time budget reached — stopping."; break; }
  (( iter >= MAX_ITER ))              && { log "Iteration cap reached — stopping."; break; }
  iter=$((iter + 1))
  base="$(git rev-parse HEAD)"

  log "=== Iteration $iter: Codex ==="
  timeout "$ITER_TIMEOUT" codex exec "${CODEX_ARGS[@]}" -C "$ROOT" "$(cat prompts/autopilot.md)" \
    > "$RUN_DIR/iter-$(printf %03d "$iter").log" 2>&1
  rc=$?
  (( rc == 124 )) && harness "Iteration $iter hit the ${ITER_TIMEOUT} timeout; uncommitted work was committed. Work in smaller steps."
  ITER_LOG="$RUN_DIR/iter-$(printf %03d "$iter").log"
  if (( rc != 0 && rc != 124 )); then
    log "codex exited $rc (see $ITER_LOG)"
    if [[ -z "$(git status --porcelain)" && "$(git rev-parse HEAD)" == "$base" ]]; then
      fails=$(( ${fails:-0} + 1 ))
      log "Codex failed without doing any work. Last lines of its output:"
      tail -n 15 "$ITER_LOG" | sed 's/^/    | /' | tee -a "$LOG"
      (( fails >= 2 )) && { log "Codex failed twice in a row — stopping. Fix the error above (often CODEX_FLAGS or sign-in) and rerun."; break; }
      continue
    fi
  fi
  fails=0

  commit "autopilot: iteration $iter (uncommitted work captured by harness)"
  guard_protected "$base"

  if [[ "$(git rev-parse HEAD)" == "$base" ]]; then
    idle=$((idle + 1)); log "No changes this iteration ($idle in a row)."
    (( idle >= 2 )) && { log "Two idle iterations — stopping."; break; }
  else
    idle=0
  fi

  action="$(head -n1 notes/NEXT_ACTION 2>/dev/null | tr -d '\r' | xargs)"
  log "NEXT_ACTION: ${action:-<none>}"
  case "$action" in
    REVIEW\ M[0-9]*) do_review "${action#REVIEW }"; echo CONTINUE > notes/NEXT_ACTION; commit "harness: reset NEXT_ACTION" ;;
    DONE)
      log "Builder reports DONE — running final check (app required)."
      if CHECK_REQUIRE_APP=1 scripts/check.sh > "$RUN_DIR/final-check.log" 2>&1; then
        missing=$(grep -oE '^## M[0-9]+' docs/ROADMAP.md | cut -c4- | while read -r m; do [[ -f "reviews/$m/GATE.md" ]] || echo "$m"; done | xargs)
        if [[ -z "$missing" ]]; then
          harness "DONE verified: all milestones gated and final check passed."
          commit "harness: run complete"; push; log "ALL DONE."; break
        fi
        harness "DONE rejected: milestones without GATE.md: $missing."
      else
        harness "DONE rejected: final check failed (see $RUN_DIR/final-check.log; summary: $(tail -4 "$RUN_DIR/final-check.log" | xargs))."
      fi
      echo CONTINUE > notes/NEXT_ACTION; commit "harness: DONE rejected" ;;
    *) : ;;
  esac
  push
done

log "Autopilot finished after $iter iteration(s). Branch: $BRANCH. Logs: $RUN_DIR/"
push
