"""Reproducible M2 CLI: generate and prepare local PLACEHOLDER fixtures only."""

import argparse
import hashlib
import json
from pathlib import Path
import sys

from . import PLACEHOLDER_NOTICE
from .dataset import DataError
from .manifest import ManifestError, write_manifest
from .preparation import PreparationConfig, prepare
from .synthetic import GENERATOR_VERSION, LABEL_NOISE_RATE, TARGET_NAMES, SyntheticConfig, generate


def prepare_run(output: Path, *, groups_per_source: int = 128, seed: int = 20261009,
                split_profile: str = "default", held_out_source: str = "synthetic-source-c") -> dict:
    config = PreparationConfig(seed=seed, split_profile=split_profile, held_out_source=held_out_source)
    rows = generate(output, SyntheticConfig(groups_per_source, seed))
    write_manifest(output / "unassigned.jsonl", rows)
    prepared, report = prepare(output, rows, config)
    write_manifest(output / "manifest.jsonl", prepared)
    report["generator"] = {"version": GENERATOR_VERSION, "groups_per_source": groups_per_source,
                           "views_per_group": 2, "seed": seed, "label_noise_rate": LABEL_NOISE_RATE,
                           "target_names": TARGET_NAMES,
                           "colour_strata": "generated background luminance <85, 85..<170, >=170"}
    report["manifest_sha256"] = hashlib.sha256((output / "manifest.jsonl").read_bytes()).hexdigest()
    (output / "preparation-report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    return report


def repository_root(start: Path | None = None) -> Path:
    """Find the checkout from the invocation directory, including normal installs.

    Do not guess relative to site-packages or create data outside a checkout.
    A roadmap marker supports a checkout with a .git file (git worktree).
    """
    start = (Path.cwd() if start is None else Path(start)).resolve()
    for candidate in (start, *start.parents):
        if (candidate / "docs" / "ROADMAP.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise ManifestError("run inside the Numbra repository; no checkout root found")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=PLACEHOLDER_NOTICE)
    parser.add_argument("--output", type=Path, default=Path("data/prepared/synthetic-v2"))
    parser.add_argument("--groups-per-source", type=int, default=128)
    parser.add_argument("--seed", type=int, default=20261009)
    parser.add_argument("--split-profile", choices=("default", "selection_exercise"), default="default")
    parser.add_argument("--held-out-source", default="synthetic-source-c")
    args = parser.parse_args(argv)
    try:
        repo = repository_root()
    except ManifestError as exc:
        parser.error(str(exc))
    output = args.output if args.output.is_absolute() else repo / args.output
    allowed = repo / "data"
    # Canonical resolution catches existing symlink parents even for a new run.
    if (allowed.is_symlink() or not output.resolve().is_relative_to(allowed)
            or output.resolve() == allowed):
        parser.error("output must be a new run below this repository's ignored data/ directory")
    try:
        report = prepare_run(output, groups_per_source=args.groups_per_source, seed=args.seed,
                             split_profile=args.split_profile, held_out_source=args.held_out_source)
    except (ManifestError, DataError, OSError) as exc:
        print(f"PLACEHOLDER preparation failed: {exc}", file=sys.stderr)
        return 1
    print(PLACEHOLDER_NOTICE)
    print(json.dumps({"rows_by_split": report["rows_by_split"],
                      "components_by_split": report["components_by_split"],
                      "manifest_sha256": report["manifest_sha256"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
