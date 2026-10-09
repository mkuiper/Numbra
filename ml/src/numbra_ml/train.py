"""One reproducible CPU PLACEHOLDER training/evaluation command; no network."""

import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
from importlib.metadata import version
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
import time

from safetensors.torch import save_file
import torch

from . import PLACEHOLDER_NOTICE
from .evaluation import bootstrap_intervals, evaluation_report, read_component_index
from .prepare import repository_root
from .preprocessing import SPEC
from .pretrained import ignored_path, sha256, verify_checkpoint
from .training import Baseline, TrainingConfig, extract_features, fit_head, initialise, load_backbone, predict, tensor_hash


def json_text(value) -> str:
    return json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"


def environment(repo: Path) -> dict:
    """Refuse version drift from the platform-specific wheel lock."""
    lock = repo / "ml/requirements-cpu.lock"
    dependencies = {}
    for line in lock.read_text().splitlines():
        if not line or line.startswith(("#", "--")):
            continue
        name, pinned = line.split()[0].split("==")
        installed = version(name)
        if installed != pinned:
            raise ValueError(f"dependency drift: {name} expected {pinned}, got {installed}")
        dependencies[name] = installed
    if sys.version_info[:2] != (3, 12) or platform.system() != "Linux" or platform.machine() != "x86_64":
        raise ValueError("current dependency lock supports Python 3.12 Linux x86_64 only")
    source_files = sorted((repo / "ml/src/numbra_ml").glob("*.py"))
    code = {str(path.relative_to(repo)): sha256(path) for path in source_files}
    return {"python": platform.python_version(), "platform": platform.platform(),
            "machine": platform.machine(), "processor": platform.processor(),
            "logical_cpu_count": os.cpu_count(),
            "cpu_model": next((line.split(":", 1)[1].strip() for line in
                               Path("/proc/cpuinfo").read_text().splitlines()
                               if line.startswith("model name")), "unavailable"),
            "torch_cpu_capability": torch.backends.cpu.get_cpu_capability(),
            "torch_build": torch.__config__.show(), "dependencies": dependencies,
            "dependency_lock_sha256": sha256(lock), "source_files_sha256": code,
            "source_tree_sha256": hashlib.sha256(json_text(code).encode()).hexdigest(),
            "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip(),
            "git_dirty": bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=repo, text=True).strip()),
            "deterministic_algorithms": True, "device": "cpu",
            "reproduction_scope": "same pinned environment/hardware; other platforms unverified"}


def add_bootstrap(report: dict, predictions, *, seed: int, replicates: int) -> None:
    temp = report["calibration"]["temperature"]
    threshold = report["primary_operating_point"]["threshold"]
    for split in ("test", "held_out"):
        subset = tuple(item for item in predictions if item.split == split)
        cohorts = {"overall": subset}
        cohorts.update({f"source:{source}": tuple(item for item in subset if source in item.sources)
                        for source in sorted({source for item in subset for source in item.sources})})
        cohorts.update({f"colour:{colour}": tuple(item for item in subset if item.colour_stratum == colour)
                        for colour in sorted({item.colour_stratum for item in subset})})
        result = {}
        cached = {}
        for name, values in cohorts.items():
            ids = tuple(sorted(item.component_id for item in values))
            derived = int.from_bytes(hashlib.sha256(f"{seed}:{split}:{name}".encode()).digest()[:4], "big")
            if name != "overall" and min(sum(item.target == target for item in values) for target in (0, 1)) < 20:
                result[name] = {"notice": PLACEHOLDER_NOTICE, "status": "suppressed_small_cell",
                                "minimum_per_class": 20, "n": len(values), "metrics": None}
            elif ids in cached:
                result[name] = cached[ids]
                continue
            else:
                result[name] = bootstrap_intervals(values, temp, threshold, seed=derived, replicates=replicates)
                cached[ids] = result[name]
        report["splits"][split]["bootstrap"] = result
    report["bootstrap_protocol"] = {"seed": seed, "replicates": replicates,
                                    "cohort_seed": "first four SHA256 bytes of seed:split:cohort, big endian",
                                    "scope": "test and held_out, primary frozen endpoint, overlapping source/colour cohorts",
                                    "identical_cohorts": "reuse first cohort's result and seed",
                                    "subgroup_minimum_per_class": 20}


def model_card(report: dict, name: str) -> str:
    point = report["primary_operating_point"]
    train = report["training"]
    rows = []
    def number(value):
        return "unavailable" if value is None else f"{value:.4f}"
    def interval(value):
        return "unavailable" if value is None else f"[{number(value[0])}, {number(value[1])}]"
    fallback = point.get("fallback") or "none"
    below_target = []
    for split in ("test", "held_out"):
        m = report["splits"][split]["primary"]
        marker = "refer-all fallback" if point.get("fallback") else "frozen selected point"
        rows.append(f"| {split} ({marker}) | {m['n']} | {m['tp']}/{m['fn']}/{m['tn']}/{m['fp']} | "
                    f"{number(m['sensitivity'])} {interval(m['sensitivity_interval_95'])} | "
                    f"{number(m['specificity'])} {interval(m['specificity_interval_95'])} | {number(m['auc'])} | {number(m['brier'])} |")
        if m['sensitivity'] is not None and m['sensitivity'] < point['target']:
            below_target.append(split)
    target_note = (f"**Observed sensitivity below the illustrative target in: {', '.join(below_target)}.**"
                   if below_target else "Observed synthetic sensitivity does not guarantee the target on independent data.")
    return f"""# PLACEHOLDER model card — {name}

**{PLACEHOLDER_NOTICE}.** Intended use: software pipeline/offline integration
testing on generated pixels only. No clinical or volunteer screening use.

Frozen timm MobileNetV3Small ImageNet features, train-only standardisation and a
binary linear head, fixed full-batch AdamW. No metadata fusion. Target 0 is
**synthetic square**, target 1 is **synthetic circle**. These are artificial shape
targets, never disease labels. Report: [{name}.json]({name}.json).

Task data: shapes-v2 generated under ADR-002/008, source-dependent texture/channel
changes and intentional 0.10 group-level rendered-shape flips. One first-sorted
record-ID image per duplicate-connected component; excluded components are
counted in the JSON report. No patient data or ImageNet images acquired.
Training components: {train['components']}; scaling and head fitting use train
only. Calibration and threshold selection use separate frozen partitions.
No early stopping, hyperparameter search or test/source-C tuning.

Primary endpoint status: **{point['status']}**; evidence **{point['target_evidence']}**;
threshold {number(point['threshold'])} (full precision in JSON),
inclusive score >= threshold. Target sensitivity 0.95 is illustrative, never a
clinical promise. Fallback: {fallback}. {target_note} Calibration status:
{report['calibration']['status']}; temperature {number(report['calibration']['temperature'])},
boundary {report['calibration'].get('boundary') or 'none'}. Scores are not calibrated
clinical risk. JSON includes secondary specificity endpoint, exact binomial
intervals, reliability bins, ECE, Brier, pre-calibration metrics and component
bootstrap percentile intervals conditional on the fixed model/operating point.

| PLACEHOLDER partition | Components | TP/FN/TN/FP | Synthetic sensitivity [95% exact interval] | Synthetic specificity [95% exact interval] | AUC | Brier |
| --- | ---: | --- | --- | --- | ---: | ---: |
{chr(10).join(rows)}

**Single held-out source (one leave-one-source-out fold):**
{report['source_fold']['held_out_source']}. No source rotation or independent
clinical external validation. Per-source and **synthetic colour strata** results
are in JSON; they overlap and cannot establish skin-tone fairness. Human skin-tone
labels are absent. Source/colour cells below 20/class suppress AUC, calibration bins
and bootstrap; this is an engineering display guard, not a real-data privacy policy.
Small strata/single-class bootstrap draws have explicit valid
counts or unavailable metrics. Calibration-fit metrics are in-sample; threshold-
selection intervals are descriptive after search. Bootstrap excludes training,
calibration and threshold-fitting uncertainty.

Preprocessing: RGB 224-pixel bilinear letterbox with RGB-128 padding, explicit
half-pixel coordinates and half-up uint8 rounding, ImageNet normalisation;
differs from publisher centre-crop. M4/M6 must test exported/Android parity.
Model output is one uncalibrated logit; apply saved temperature/sigmoid once.
Weights live only under ignored data/; checksums and full run provenance are in
JSON. Publisher-declared Apache-2.0 pretrained licence is separate from code/data
and is not a warranty about all pretraining-image rights.

## Limitations and safeguards

No lesion, Nepal, clinical accuracy, diagnosis, calibration or field-safety evidence.
Photos cannot represent pure-neural disease without a skin lesion or establish
sensation loss. Synthetic scores cannot cancel symptom/contact/concern/quality or
missing-assessment referrals. The app must never infer disease absence. Every
downstream app surface must identify this model as **PLACEHOLDER**.
Independent licensed data, patient grouping/duplicate adjudication, prospective
clinical validation, clinical/ethics/legal approval and native Nepali review remain
human work. No export, on-device performance or APK is claimed by M3.

## Open questions

- Do humans approve ADR-005/008/009/010, training/preprocessing/fit choices and the one-fold scope?
- Which licensed independent clinical cohorts and evaluation protocol can replace synthetic targets?

## Confidence

Software verification only; **no confidence in clinical performance**.
"""


def write_reports(report: dict, directory: Path, name: str) -> None:
    if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_-]{0,63}", name):
        raise ValueError("invalid report name")
    directory.mkdir(parents=True, exist_ok=True)
    paths = [directory / f"{name}.json", directory / f"{name}-MODEL-CARD.md"]
    if any(path.exists() for path in paths):
        raise ValueError("refusing to overwrite existing report")
    paths[0].write_text(json_text(report), encoding="utf-8")
    paths[1].write_text(model_card(report, name), encoding="utf-8")


def verified_backbone(checkpoint: Path):
    return load_backbone(checkpoint), verify_checkpoint(checkpoint)


def train_run(repo: Path, prepared: Path, checkpoint: Path, output: Path, *,
              name: str, config: TrainingConfig, bootstrap_replicates: int = 1000,
              backbone_loader=verified_backbone) -> dict:
    started = time.monotonic()
    prepared, checkpoint, output = [ignored_path(repo, path) for path in (prepared, checkpoint, output)]
    reports = repo / "ml/reports"
    if reports.is_symlink() or reports.resolve() != reports:
        raise ValueError("reports directory must be local and not symlinked")
    if (not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_-]{0,63}", name)
            or any((reports / f"{name}{suffix}").exists() for suffix in (".json", "-MODEL-CARD.md"))):
        raise ValueError("invalid or existing report name")
    if output.exists() and (not output.is_dir() or any(output.iterdir())):
        raise ValueError("training output must be new/empty")
    if type(bootstrap_replicates) is not int or not 100 <= bootstrap_replicates <= 10000:
        raise ValueError("invalid bootstrap replicate count")
    manifest, preparation = prepared / "manifest.jsonl", prepared / "preparation-report.json"
    index = read_component_index(manifest, preparation)
    preparation_digest = sha256(preparation)
    env = environment(repo)
    initialise(config)
    backbone, weight_evidence = backbone_loader(checkpoint)
    backbone_digest = tensor_hash(backbone.state_dict())
    features = extract_features(index, prepared, backbone, batch_size=config.batch_size)
    head, training = fit_head(index, features, config)
    predictions = predict(index, features, head)
    report = evaluation_report(predictions, held_out_source=index.held_out_source)
    add_bootstrap(report, predictions, seed=config.seed, replicates=bootstrap_replicates)
    if sha256(manifest) != index.manifest_sha256 or sha256(preparation) != preparation_digest:
        raise ValueError("preparation inputs changed during training")
    if tensor_hash(backbone.state_dict()) != backbone_digest:
        raise ValueError("backbone changed during head training")
    output.mkdir(parents=True, exist_ok=True)
    model = Baseline(backbone, head).eval()
    save_file({key: val.contiguous() for key, val in model.state_dict().items()},
              str(output / "PLACEHOLDER-model.safetensors"), metadata={"notice": PLACEHOLDER_NOTICE})
    prediction_path = output / "PLACEHOLDER-predictions.json"
    prediction_path.write_text(json_text({"notice": PLACEHOLDER_NOTICE,
                                         "predictions": [asdict(item) for item in predictions]}))
    report.update(training=training, preprocessing=SPEC, pretrained=weight_evidence,
                  exclusions={"components": len(index.excluded), "reasons": {
                      reason: sum(reason in reasons for reasons in index.excluded.values())
                      for reason in sorted({r for reasons in index.excluded.values() for r in reasons})}},
                  provenance={**env, "created_utc": datetime.now(timezone.utc).isoformat(),
                              "elapsed_seconds": time.monotonic() - started,
                              "manifest_sha256": index.manifest_sha256,
                              "preparation_report_sha256": preparation_digest,
                              "preparation_config": json.loads(preparation.read_text())["config"],
                              "generator": json.loads(preparation.read_text())["generator"],
                              "frozen_backbone_sha256": backbone_digest,
                              "predictions_sha256": sha256(prediction_path),
                              "model_sha256": sha256(output / "PLACEHOLDER-model.safetensors"),
                              "model_bytes": (output / "PLACEHOLDER-model.safetensors").stat().st_size,
                              "output_directory": str(output.relative_to(repo))})
    (output / "PLACEHOLDER-run.json").write_text(json_text(report), encoding="utf-8")
    write_reports(report, reports, name)
    return report


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=PLACEHOLDER_NOTICE)
    parser.add_argument("--prepared", type=Path, default=Path("data/prepared/synthetic-v2-selection"))
    parser.add_argument("--checkpoint", type=Path, default=Path("data/pretrained/mobilenetv3-small"))
    parser.add_argument("--output", type=Path, default=Path("data/models/PLACEHOLDER-m3-baseline"))
    parser.add_argument("--report-name", default="PLACEHOLDER-m3-baseline")
    parser.add_argument("--seed", type=int, default=20261009)
    parser.add_argument("--epochs", type=int, default=300)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--threads", type=int, default=2)
    parser.add_argument("--learning-rate", type=float, default=0.03)
    parser.add_argument("--weight-decay", type=float, default=0.01)
    parser.add_argument("--bootstrap-replicates", type=int, default=1000)
    args = parser.parse_args(argv)
    try:
        config = TrainingConfig(seed=args.seed, epochs=args.epochs, batch_size=args.batch_size, threads=args.threads,
                                learning_rate=args.learning_rate, weight_decay=args.weight_decay)
        report = train_run(repository_root(), args.prepared, args.checkpoint, args.output,
                           name=args.report_name, config=config, bootstrap_replicates=args.bootstrap_replicates)
    except (ValueError, OSError, RuntimeError) as exc:
        print(f"PLACEHOLDER training failed: {exc}", file=sys.stderr)
        return 1
    print(PLACEHOLDER_NOTICE)
    print(json_text({"report": f"ml/reports/{args.report_name}.json", "training": report["training"],
                     "primary_operating_point": report["primary_operating_point"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
