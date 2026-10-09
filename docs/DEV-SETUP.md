# Development setup

Research stage, 2026-10-09: uses the existing system `python3`, git, bash, and web
tools. No toolchains were installed in this iteration. Run repository checks with:

```
python3 -m unittest discover -s tests -v
bash scripts/check.sh
```

check.sh currently skips ML and Android because neither project exists. It is not
an APK verification at M0. Later milestones must document actual venv, JDK, and
SDK installation commands and versions here. Python's venv belongs in `ml/.venv`;
Android command-line tools belong under `$HOME/Android/Sdk`.

Firecrawl CLI 1.14.8 is installed and authenticated, but status showed zero credits.
The setup scrape and a one-result search both failed with insufficient credits.
The research iteration used the available web search/open tool as a labelled
workaround; no new account, subscription, authentication, or licence acceptance
was performed. `.firecrawl/` is ignored and must never store tracked content.

## Open questions

- What exact dependency versions and Android device targets will later ADRs select?

## Confidence

High for commands and tooling observed in this iteration; future build setup is pending.
