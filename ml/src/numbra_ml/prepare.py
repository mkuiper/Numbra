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
from .synthetic import GENERATOR_VERSION, SyntheticConfig, generate


def prepare_run(output: Path, *, groups_per_source: int = 128, seed: int = 20261009) -> dict:
    rows = generate(output, SyntheticConfig(groups_per_source, seed))
    write_manifest(output / "unassigned.jsonl", rows)
    prepared, report = prepare(output, rows, PreparationConfig(seed=seed))
    write_manifest(output / "manifest.jsonl", prepared)
    report["generator"] = {"version": GENERATOR_VERSION, "groups_per_source": groups_per_source,
                           "views_per_group": 2, "seed": seed}
    report["manifest_sha256"] = hashlib.sha256((output / "manifest.jsonl").read_bytes()).hexdigest()
    (output / "preparation-report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    return report


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=PLACEHOLDER_NOTICE)
    parser.add_argument("--output", type=Path, default=Path("data/prepared/synthetic-v1"))
    parser.add_argument("--groups-per-source", type=int, default=128)
    parser.add_argument("--seed", type=int, default=20261009)
    args = parser.parse_args(argv)
    repo = Path(__file__).resolve().parents[3]
    output = args.output if args.output.is_absolute() else repo / args.output
    allowed = repo / "data"
    # Canonical resolution catches existing symlink parents even for a new run.
    if (allowed.is_symlink() or not output.resolve().is_relative_to(allowed)
            or output.resolve() == allowed):
        parser.error("output must be a new run below this repository's ignored data/ directory")
    try:
        report = prepare_run(output, groups_per_source=args.groups_per_source, seed=args.seed)
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
