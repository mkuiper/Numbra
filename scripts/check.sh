#!/usr/bin/env bash
# Numbra — tests of record. Protected: the autopilot harness runs this itself, so test
# results don't depend on the Builder's word. Discovers what exists and runs it.
#
#   ml/   → pytest           (uses ml/.venv if present)
#   app/  → Gradle unit tests + assembleDebug, then checks a debug APK exists
#
# Exit 0 only if everything that exists passes.
# Env: CHECK_REQUIRE_APP=1 makes a missing app/ a failure (used for the final check).

set -uo pipefail
ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

status=0
summary=()
note() { summary+=("$1"); echo "== $1"; }

# --- ML ---------------------------------------------------------------------------
if [[ -f ml/pyproject.toml || -d ml/tests ]]; then
  PY="$(command -v python3)"
  [[ -x ml/.venv/bin/python ]] && PY="$ROOT/ml/.venv/bin/python"
  echo "### ml: $PY -m pytest"
  if (cd ml && "$PY" -m pytest -q); then
    note "ml tests: PASS"
  else
    note "ml tests: FAIL"; status=1
  fi
else
  note "ml tests: SKIPPED (no ml/ project yet)"
fi

# --- Android ------------------------------------------------------------------------
if [[ -x app/gradlew ]]; then
  echo "### app: ./gradlew testDebugUnitTest assembleDebug"
  if (cd app && ./gradlew --no-daemon --console=plain testDebugUnitTest assembleDebug); then
    apk="$(find app -path '*build/outputs/apk/debug/*.apk' -print -quit)"
    if [[ -n "$apk" ]]; then
      note "app build+tests: PASS ($apk, $(du -h "$apk" | cut -f1))"
    else
      note "app build+tests: FAIL (no debug APK found)"; status=1
    fi
  else
    note "app build+tests: FAIL"; status=1
  fi
elif [[ "${CHECK_REQUIRE_APP:-0}" == 1 ]]; then
  note "app: FAIL (required but app/gradlew not found)"; status=1
else
  note "app: SKIPPED (no app/gradlew yet)"
fi

echo
echo "===== CHECK SUMMARY ====="
printf '%s\n' "${summary[@]}"
echo "RESULT: $([[ $status == 0 ]] && echo PASS || echo FAIL)"
exit $status
