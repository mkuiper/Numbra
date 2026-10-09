"""Component-level PLACEHOLDER evaluation; no clinical probability claims.

All fit functions accept only their named split. Test/held-out scores never enter
calibration or threshold fitting. NumPy plus the standard library suffice.
"""

from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
from typing import Iterable, Mapping

import numpy as np

from . import PLACEHOLDER_NOTICE
from .dataset import require_approved_source
from .manifest import ManifestError, ManifestRow, read_manifest, validate_manifest
from .synthetic import TARGET_NAMES

EVALUATION_VERSION = "1.0.0"
ACTIVE_SPLITS = ("train", "calibration", "threshold_validation", "test", "held_out")


@dataclass(frozen=True)
class Component:
    id: str
    row: ManifestRow
    sources: tuple[str, ...]
    colour_stratum: str

    @property
    def split(self) -> str:
        return self.row.split

    @property
    def target(self) -> int:
        return self.row.label.binary_target


@dataclass(frozen=True)
class ComponentIndex:
    components: tuple[Component, ...]
    excluded: dict[str, tuple[str, ...]]
    manifest_sha256: str
    held_out_source: str


def index_components(rows: Iterable[ManifestRow], report: dict) -> ComponentIndex:
    """Choose lexicographically first record ID, before inspecting any scores.

    Validate the complete preparation partition, including exclusions; never
    reconstruct independent units from original group IDs or image paths.
    """
    rows = validate_manifest(rows)
    for row in rows:
        require_approved_source(row)
    by_id = {row.record_id: row for row in rows}
    try:
        held = report["config"]["held_out_source"]
        if not isinstance(held, str) or not held.startswith("synthetic-"):
            raise ManifestError("invalid held-out source")
        components, excluded, mapping, linked = [], {}, {}, {}
        for key, info in sorted(report["components"].items()):
            ids = info["records"]
            if not isinstance(key, str) or not ids or len(ids) != len(set(ids)):
                raise ManifestError("invalid component membership")
            if any(record not in by_id or record in mapping for record in ids):
                raise ManifestError("unknown or multiply assigned component record")
            members = [by_id[record] for record in sorted(ids)]
            mapping.update({record: key for record in ids})
            for row in members:
                links = [("hash", row.sha256)]
                if row.group_id is not None:
                    links.append(("group", row.source.id, row.group_id))
                if row.patient_id is not None:
                    links.append(("patient", row.source.id, row.patient_id))
                for link in links:
                    if linked.setdefault(link, key) != key:
                        raise ManifestError("known linked records span multiple components")
            sources = tuple(sorted({row.source.id for row in members}))
            split = info["split"]
            if list(sources) != info["sources"] or {row.split for row in members} != {split}:
                raise ManifestError("component source/split disagrees with manifest")
            if split == "quarantine":
                if info["target"] is not None or not info["quarantine_reasons"]:
                    raise ManifestError("quarantined component needs null target and reasons")
                excluded[key] = tuple(info["quarantine_reasons"])
                continue
            if split not in ACTIVE_SPLITS or info["quarantine_reasons"]:
                raise ManifestError("component has invalid active split/reasons")
            if (held in sources) != (split == "held_out") or (held in sources and len(sources) != 1):
                raise ManifestError("held-out source boundary violation")
            targets = {row.label.binary_target for row in members}
            if targets not in ({0}, {1}) or info["target"] != next(iter(targets)):
                raise ManifestError("component target disagrees with manifest")
            for row in members:
                expected = "synthetic_circle" if row.label.binary_target else "synthetic_square"
                if row.group_id is None or row.label.diagnosis != expected:
                    raise ManifestError("evaluation requires grouped shapes-v2 circle/square targets")
            tones = {None if row.skin_tone is None else row.skin_tone.value for row in members}
            colour = "missing" if tones == {None} else (
                next(iter(tones)) if len(tones) == 1 else "conflicting_or_partial")
            components.append(Component(key, members[0], sources, colour))
        if set(mapping) != set(by_id) or mapping != report["record_components"]:
            raise ManifestError("preparation report does not cover the manifest exactly")
        if not components or not any(item.split == "held_out" for item in components):
            raise ManifestError("no active components or held-out source")
        digest = report["manifest_sha256"]
        if not isinstance(digest, str) or len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            raise ManifestError("invalid manifest checksum")
        return ComponentIndex(tuple(components), excluded, digest, held)
    except (KeyError, TypeError, AttributeError) as exc:
        raise ManifestError("malformed preparation report") from exc


def read_component_index(manifest: Path, preparation_report: Path) -> ComponentIndex:
    report = json.loads(Path(preparation_report).read_text(encoding="utf-8"))
    digest = hashlib.sha256(Path(manifest).read_bytes()).hexdigest()
    if report.get("manifest_sha256") != digest:
        raise ManifestError("preparation report manifest checksum mismatch")
    return index_components(read_manifest(manifest), report)


@dataclass(frozen=True)
class Prediction:
    component_id: str
    split: str
    target: int
    logit: float
    sources: tuple[str, ...] = ()
    colour_stratum: str = "missing"


def component_predictions(index: ComponentIndex, logits: Mapping[str, float]) -> tuple[Prediction, ...]:
    if set(logits) != {item.id for item in index.components}:
        raise ValueError("logits must cover every active component exactly once")
    values = tuple(Prediction(item.id, item.split, item.target, float(logits[item.id]),
                              item.sources, item.colour_stratum) for item in index.components)
    _validate(values)
    return values


def _validate(values: Iterable[Prediction], split: str | None = None) -> tuple[Prediction, ...]:
    values = tuple(values)
    if len({item.component_id for item in values}) != len(values):
        raise ValueError("duplicate component ID or split leakage")
    for item in values:
        if (not item.component_id or item.split not in ACTIVE_SPLITS or item.target not in (0, 1)
                or not math.isfinite(item.logit)):
            raise ValueError("invalid component prediction")
        if split is not None and item.split != split:
            raise ValueError(f"fit requires {split} components only")
    return values


def _arrays(values: tuple[Prediction, ...], temperature: float = 1.0):
    if not math.isfinite(temperature) or not 0.05 <= temperature <= 20:
        raise ValueError("temperature must be finite in [0.05, 20]")
    labels = np.array([item.target for item in values], dtype=np.int64)
    logits = np.array([item.logit for item in values], dtype=np.float64) / temperature
    if not np.isfinite(logits).all():
        raise ValueError("scaled logits overflow")
    probabilities = np.exp(-np.logaddexp(0, -logits))
    return labels, logits, probabilities


def _counts(values):
    return {str(label): sum(item.target == label for item in values) for label in (0, 1)}


def _hash(values):
    payload = [(item.component_id, item.target, item.logit) for item in sorted(values, key=lambda v: v.component_id)]
    return hashlib.sha256(json.dumps(payload, allow_nan=False).encode()).hexdigest()


def fit_temperature(values: Iterable[Prediction]) -> dict:
    """Minimise logistic NLL in inverse-temperature by convex derivative bisection."""
    values = _validate(values, "calibration")
    counts = _counts(values)
    result = {"notice": PLACEHOLDER_NOTICE, "counts": counts, "fit_split": "calibration",
              "fit_sha256": _hash(values), "temperature": 1.0,
              "bounds": [0.05, 20.0], "method": "inverse-temperature derivative bisection"}
    if min(counts.values()) < 20:
        return {**result, "status": "unavailable_insufficient_groups"}
    labels, logits, _ = _arrays(values)

    def derivative(beta):
        scaled = logits * beta
        if not np.isfinite(scaled).all():
            raise ValueError("scaled logits overflow")
        probabilities = np.exp(-np.logaddexp(0, -scaled))
        return float(np.mean(logits * (probabilities - labels)))

    low, high = 0.05, 20.0
    boundary = None
    if derivative(low) >= 0:
        beta, boundary = low, "maximum_temperature"
    elif derivative(high) <= 0:
        beta, boundary = high, "minimum_temperature"
    else:
        for _ in range(80):
            middle = (low + high) / 2
            if derivative(middle) < 0:
                low = middle
            else:
                high = middle
        beta = (low + high) / 2
    return {**result, "temperature": 1 / beta, "status": "fitted", "boundary": boundary}


def _binomial_sum(n: int, p: float, first: int, last: int) -> float:
    if p <= 0:
        return float(first == 0)
    if p >= 1:
        return float(last == n)
    terms = [math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)
             + k * math.log(p) + (n - k) * math.log1p(-p) for k in range(first, last + 1)]
    maximum = max(terms)
    return min(1.0, math.exp(maximum) * math.fsum(math.exp(term - maximum) for term in terms))


def exact_interval(successes: int, total: int) -> list[float] | None:
    """Two-sided 95% Clopper–Pearson interval via binomial-tail inversion."""
    if not isinstance(successes, int) or not isinstance(total, int) or not 0 <= successes <= total:
        raise ValueError("invalid binomial counts")
    if total == 0:
        return None
    endpoints = []
    for lower in (True, False):
        if lower and successes == 0:
            endpoints.append(0.0)
            continue
        if not lower and successes == total:
            endpoints.append(1.0)
            continue
        low, high = 0.0, 1.0
        for _ in range(70):
            middle = (low + high) / 2
            tail = (_binomial_sum(total, middle, successes, total) if lower
                    else _binomial_sum(total, middle, 0, successes))
            if (tail < 0.025) == lower:
                low = middle
            else:
                high = middle
        endpoints.append((low + high) / 2)
    return endpoints


def metrics(values: Iterable[Prediction], temperature: float, threshold: float, *, bins: int = 10) -> dict:
    values = _validate(values)
    if not math.isfinite(threshold) or threshold < 0 or threshold > math.nextafter(1.0, math.inf):
        raise ValueError("invalid threshold")
    if not isinstance(bins, int) or not 1 <= bins <= 100:
        raise ValueError("invalid reliability bin count")
    labels, logits, scores = _arrays(values, temperature)
    positive = scores >= threshold
    tp = int(np.sum(positive & (labels == 1)))
    fn = int(np.sum(~positive & (labels == 1)))
    tn = int(np.sum(~positive & (labels == 0)))
    fp = int(np.sum(positive & (labels == 0)))
    npos, nneg = tp + fn, tn + fp
    # Rank-sum AUC; tied scores receive their mean rank, including sigmoid saturation.
    rank_sum, offset = 0.0, 0
    for score in np.unique(scores):
        tied = scores == score
        count = int(tied.sum())
        rank_sum += float(labels[tied].sum()) * (offset + (count + 1) / 2)
        offset += count
    auc = (rank_sum - npos * (npos + 1) / 2) / (npos * nneg) if npos and nneg else None
    reliability, ece = [], 0.0
    assignments = np.minimum((scores * bins).astype(int), bins - 1)
    for bin_id in range(bins):
        mask = assignments == bin_id
        count = int(mask.sum())
        mean = float(scores[mask].mean()) if count else None
        rate = float(labels[mask].mean()) if count else None
        reliability.append({"lower": bin_id / bins, "upper": (bin_id + 1) / bins,
                            "count": count, "mean_score": mean, "positive_fraction": rate})
        if count:
            ece += count / len(values) * abs(mean - rate)
    return {"notice": PLACEHOLDER_NOTICE, "n": len(values), "counts": _counts(values),
            "tp": tp, "fn": fn, "tn": tn, "fp": fp,
            "sensitivity": tp / npos if npos else None,
            "sensitivity_interval_95": exact_interval(tp, npos),
            "specificity": tn / nneg if nneg else None,
            "specificity_interval_95": exact_interval(tn, nneg), "auc": auc,
            "unavailable_auc_reason": None if npos and nneg else "requires_both_classes",
            "brier": float(np.mean((scores - labels) ** 2)) if len(values) else None,
            "log_loss": float(np.mean(np.logaddexp(0, logits) - labels * logits)) if len(values) else None,
            "ece": ece if len(values) else None, "reliability_bins": reliability,
            "bin_definition": "equal width [lower, upper), final bin includes 1",
            "warning": "synthetic component intervals only; small strata are unstable"}


def select_threshold(values: Iterable[Prediction], calibration: dict, *, endpoint: str = "sensitivity") -> dict:
    values = _validate(values, "threshold_validation")
    if endpoint not in {"sensitivity", "specificity"}:
        raise ValueError("unknown endpoint")
    counts = _counts(values)
    temperature = calibration["temperature"]
    target = 0.95 if endpoint == "sensitivity" else 0.80
    result = {"notice": PLACEHOLDER_NOTICE, "fit_split": "threshold_validation",
              "fit_sha256": _hash(values), "counts": counts, "target": target,
              "endpoint": endpoint, "threshold": 0.0, "comparison": "score >= threshold"}
    if (min(counts.values()) < 100 or calibration.get("status") != "fitted"
            or min(calibration["counts"].values()) < 20):
        return {**result, "status": "unavailable_insufficient_groups",
                "fallback": "unselected refer-all", "target_evidence": "unavailable"}
    labels, _, scores = _arrays(values, temperature)
    candidates = np.unique(scores).tolist()
    if endpoint == "sensitivity":
        qualifying = [point for point in candidates if float(np.mean(scores[labels == 1] >= point)) >= target]
        threshold = max(qualifying)
        successes, total = int(np.sum(scores[labels == 1] >= threshold)), counts["1"]
    else:
        candidates.append(math.nextafter(1.0, math.inf))
        qualifying = [point for point in candidates if float(np.mean(scores[labels == 0] < point)) >= target]
        threshold = min(qualifying)
        successes, total = int(np.sum(scores[labels == 0] < threshold)), counts["0"]
    interval = exact_interval(successes, total)
    evidence = "empirical_target_only" if interval[0] < target else "fixture_interval_lower_bound_meets_target"
    return {**result, "threshold": threshold, "status": "selected", "fallback": None,
            "target_evidence": evidence, "selection_interval_95": interval,
            "selection_interval_note": "descriptive after threshold search, not independent evidence",
            "degenerate": "all_negative" if threshold > 1 else ("refer_all" if np.all(scores >= threshold) else None),
            "selection_rule": "highest observed qualifying threshold" if endpoint == "sensitivity"
                              else "lowest observed qualifying threshold or above-one sentinel"}


def evaluation_report(values: Iterable[Prediction], *, held_out_source: str) -> dict:
    """Freeze calibration/thresholds, then compute test and one external fold."""
    values = _validate(values)
    if not held_out_source or any((held_out_source in item.sources) != (item.split == "held_out")
                                 or (item.split == "held_out" and item.sources != (held_out_source,))
                                 for item in values):
        raise ValueError("held-out source boundary violation")
    partitions = {split: tuple(item for item in values if item.split == split) for split in ACTIVE_SPLITS}
    calibration = fit_temperature(partitions["calibration"])
    primary = select_threshold(partitions["threshold_validation"], calibration)
    secondary = select_threshold(partitions["threshold_validation"], calibration, endpoint="specificity")
    temperature, threshold = calibration["temperature"], primary["threshold"]
    reports = {}
    for split in ACTIVE_SPLITS[1:]:
        subset = partitions[split]
        sources = sorted({source for item in subset for source in item.sources})
        colours = sorted({item.colour_stratum for item in subset})
        missing = sum(item.colour_stratum in {"missing", "conflicting_or_partial"} for item in subset)
        reports[split] = {"score_sha256": _hash(subset),
                         "primary": metrics(subset, temperature, threshold),
                         "secondary": metrics(subset, temperature, secondary["threshold"]),
                         "before_calibration": metrics(subset, 1.0, threshold),
                         "by_source": {source: metrics([item for item in subset if source in item.sources],
                                                       temperature, threshold) for source in sources},
                         "synthetic_colour_strata": {colour: metrics([item for item in subset if item.colour_stratum == colour],
                                                                      temperature, threshold) for colour in colours},
                         "missing_or_conflicting_colour_fraction": missing / len(subset) if subset else None}
    return {"notice": PLACEHOLDER_NOTICE, "evaluation_version": EVALUATION_VERSION,
            "target_names": {str(key): name for key, name in TARGET_NAMES.items()}, "unit": "duplicate-connected component, first sorted record ID",
            "calibration": calibration, "primary_operating_point": primary,
            "secondary_operating_point": secondary, "splits": reports,
            "source_fold": {"description": "single held-out source (one leave-one-source-out fold)",
                            "held_out_source": held_out_source},
            "limitations": ["generated circle/square targets, not clinical performance",
                            "synthetic colour strata are not human skin-tone/fairness evidence",
                            "temperature-scaled scores are not clinically calibrated probabilities",
                            "before-calibration threshold metrics are descriptive; thresholds were fitted after scaling",
                            "selection intervals are descriptive after search; test threshold is frozen",
                            "calibration-split summaries are in-sample after temperature fitting",
                            "multi-source components count once per represented source; strata overlap"]}


def bootstrap_intervals(values: Iterable[Prediction], temperature: float, threshold: float,
                        *, seed: int, replicates: int = 1000) -> dict:
    """Frozen-score, ordinary component bootstrap; no re-fitting within replicas.

    A component's single index image is drawn as a whole unit. Single-class draws
    contribute only available metrics; valid counts accompany every interval.
    Conditional on the fitted model/operating point, not total training uncertainty.
    """
    values = _validate(values)
    if (type(seed) is not int or not 0 <= seed < 2**32 or type(replicates) is not int
            or not 100 <= replicates <= 10000):
        raise ValueError("invalid bootstrap seed or replicate count")
    if any(item.split not in {"test", "held_out"} for item in values):
        raise ValueError("bootstrap requires frozen test/held_out scores")
    if len({item.split for item in values}) > 1:
        raise ValueError("bootstrap cannot pool independent evaluation splits")
    metrics(values, temperature, threshold)  # Reuse public parameter validation.
    labels, _, scores = _arrays(values, temperature)
    samples = {key: [] for key in ("sensitivity", "specificity", "auc", "brier", "ece")}
    rng = np.random.default_rng(seed)
    for _ in range(replicates if values else 0):
        draw = rng.integers(0, len(values), size=len(values))
        y, p = labels[draw], scores[draw]
        positive = p >= threshold
        npos, nneg = int(y.sum()), int((1 - y).sum())
        if npos:
            samples["sensitivity"].append(float(positive[y == 1].mean()))
        if nneg:
            samples["specificity"].append(float((~positive[y == 0]).mean()))
        if npos and nneg:
            # Tied-group positive × preceding negative counts; half credit for ties.
            order = np.argsort(p, kind="stable")
            _, starts = np.unique(p[order], return_index=True)
            positives = np.add.reduceat(y[order], starts)
            totals = np.diff(np.append(starts, len(y)))
            negatives = totals - positives
            precede = np.cumsum(negatives) - negatives
            samples["auc"].append(float(np.sum(positives * (precede + 0.5 * negatives)) / (npos * nneg)))
        samples["brier"].append(float(np.mean((p - y) ** 2)))
        assignments = np.minimum((p * 10).astype(int), 9)
        counts = np.bincount(assignments, minlength=10)
        score_sums = np.bincount(assignments, weights=p, minlength=10)
        target_sums = np.bincount(assignments, weights=y, minlength=10)
        samples["ece"].append(float(np.abs(score_sums[counts > 0] - target_sums[counts > 0]).sum() / len(y)))
    return {"notice": PLACEHOLDER_NOTICE, "seed": seed, "replicates": replicates,
            "unit": "duplicate-connected component; one index image",
            "method": "ordinary bootstrap, percentile 95%, linear quantiles",
            "conditioning": "fixed model, temperature and threshold; no fitting uncertainty",
            "n": len(values), "score_sha256": _hash(values),
            "metrics": {key: {"interval_95": np.quantile(sample, [0.025, 0.975]).tolist() if sample else None,
                              "valid_replicates": len(sample),
                              "unavailable_reason": None if sample else "empty_or_single_class"}
                        for key, sample in samples.items()}}
