"""PLACEHOLDER preparation: duplicate components, quarantine and frozen splits.

No source downloads or real-data bypass. Visual similarity is a conservative
engineering heuristic on resized RGB, not proof of clinical identity.
"""

from collections import Counter, defaultdict
from dataclasses import dataclass, replace
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image

from . import PLACEHOLDER_NOTICE
from .dataset import load_rgb, require_approved_source
from .manifest import ManifestError, ManifestRow, validate_manifest
from .taxonomy import LabelFamily, LabelStatus

PREPARATION_VERSION = "1.0.0"
ACTIVE_SPLITS = ("train", "calibration", "threshold_validation", "test")
FRACTIONS = (0.60, 0.15, 0.15, 0.10)
MAX_ROWS = 2000  # Explicit quadratic-fixture scope, never silently sample rows.


@dataclass(frozen=True)
class PreparationConfig:
    held_out_source: str = "synthetic-source-c"
    seed: int = 20261009
    near_rms: float = 2.0  # uint8 units, fixed before splitting; not a clinical metric.

    def __post_init__(self):
        if not isinstance(self.seed, int) or isinstance(self.seed, bool):
            raise ManifestError("seed must be an integer")
        if not isinstance(self.held_out_source, str) or not self.held_out_source.startswith("synthetic-"):
            raise ManifestError("held-out source must be synthetic")
        if not np.isfinite(self.near_rms) or not 0 <= self.near_rms <= 5:
            raise ManifestError("near_rms must be finite and in [0, 5]")


class _Components:
    def __init__(self, size):
        self.parent = list(range(size))

    def find(self, index):
        while index != self.parent[index]:
            self.parent[index] = self.parent[self.parent[index]]
            index = self.parent[index]
        return index

    def join(self, first, second):
        first, second = self.find(first), self.find(second)
        self.parent[max(first, second)] = min(first, second)


def _allocations(count: int) -> list[int]:
    # Guarantee all four partitions when at least four components/class exist.
    if count < len(ACTIVE_SPLITS):
        raise ManifestError("need at least four eligible development components per binary class")
    remaining = count - len(ACTIVE_SPLITS)
    raw = [remaining * fraction for fraction in FRACTIONS]
    sizes = [1 + int(value) for value in raw]
    order = sorted(range(4), key=lambda i: (-(raw[i] - int(raw[i])), i))
    for i in order[:count - sum(sizes)]:
        sizes[i] += 1
    return sizes


def prepare(root: Path, rows: tuple[ManifestRow, ...], config: PreparationConfig = PreparationConfig()
            ) -> tuple[tuple[ManifestRow, ...], dict]:
    """Verify every input, merge all links, quarantine whole components, then split.

    Requires an unassigned manifest. Never re-split a frozen run or infer patients.
    Held-out source is selected in config before loading and used only for testing.
    """
    rows = tuple(sorted(rows, key=lambda row: row.record_id))
    if not rows or len(rows) > MAX_ROWS:
        raise ManifestError(f"preparation requires 1..{MAX_ROWS} rows")
    for row in rows:
        require_approved_source(row)
    rows = validate_manifest(rows)
    if any(row.split != "unassigned" for row in rows):
        raise ManifestError("prepare only unassigned rows; regenerate rather than re-split")
    sources = {row.source.id for row in rows}
    if config.held_out_source not in sources or len(sources) < 2:
        raise ManifestError("held-out source and at least one development source required")

    links = _Components(len(rows))
    seen = {}
    duplicates = {"exact_bytes": [], "decoded_pixels": [], "near_visual": []}
    signatures = []
    unresolved = Counter()
    for i, row in enumerate(rows):
        rgb = load_rgb(root, row)  # safe paths, policy, byte checksum and decode
        pixel_hash = hashlib.sha256(str(rgb.shape).encode() + rgb.tobytes()).hexdigest()
        signature = np.asarray(Image.fromarray(rgb).resize((16, 16), Image.Resampling.BILINEAR),
                               dtype=np.float32).reshape(-1)
        signatures.append(signature)
        keys = [("exact_bytes", row.sha256), ("decoded_pixels", pixel_hash)]
        if row.group_id is not None:
            keys.append(("group", row.source.id, row.group_id))
        if row.patient_id is not None:
            keys.append(("patient", row.source.id, row.patient_id))
        for key in keys:
            if key in seen:
                other = seen[key]
                links.join(i, other)
                if key[0] in duplicates:
                    duplicates[key[0]].append([rows[other].record_id, row.record_id])
            else:
                seen[key] = i
        if row.label.family == LabelFamily.UNRESOLVED:
            unresolved[(row.source.id, row.label.original_label)] += 1

    # All candidate pairs, including already-linked ones, are audited. No silent
    # subsampling and no split-dependent duplicate search.
    signatures = np.stack(signatures)
    for i in range(len(rows)):
        distance = np.sqrt(np.mean((signatures[i + 1:] - signatures[i]) ** 2, axis=1))
        for offset in np.flatnonzero(distance <= config.near_rms):
            j = i + 1 + int(offset)
            links.join(i, j)
            duplicates["near_visual"].append({
                "records": [rows[i].record_id, rows[j].record_id],
                "rms_uint8": round(float(distance[offset]), 6),
            })

    members = defaultdict(list)
    for i, row in enumerate(rows):
        members[links.find(i)].append(row)
    components = {}
    for group in members.values():
        ids = [row.record_id for row in group]
        component_id = "component-" + hashlib.sha256(json.dumps(ids).encode()).hexdigest()[:24]
        diagnoses = {(str(row.label.family), row.label.diagnosis) for row in group
                     if row.label.family != LabelFamily.UNRESOLVED}
        group_sources = {row.source.id for row in group}
        reasons = []
        if len(diagnoses) > 1:
            reasons.append("conflicting_diagnoses")
        if any(row.group_id is None for row in group):
            reasons.append("missing_group_id")
        if any(row.label.binary_target is None for row in group):
            reasons.append("unresolved_or_unconfirmed_label")
        if config.held_out_source in group_sources and len(group_sources) > 1:
            reasons.append("crosses_held_out_source_boundary")
        components[component_id] = {
            "records": ids, "sources": sorted(group_sources), "quarantine_reasons": reasons,
            "target": None if reasons else group[0].label.binary_target,
            "split": "quarantine" if reasons else (
                "held_out" if config.held_out_source in group_sources else "unassigned"),
        }

    for target in (0, 1):
        candidates = [key for key, value in components.items()
                      if value["split"] == "unassigned" and value["target"] == target]
        candidates.sort(key=lambda key: (hashlib.sha256(f"{config.seed}:{key}".encode()).hexdigest(), key))
        offset = 0
        for split, count in zip(ACTIVE_SPLITS, _allocations(len(candidates)), strict=True):
            for key in candidates[offset:offset + count]:
                components[key]["split"] = split
            offset += count
    if {value["target"] for value in components.values() if value["split"] == "held_out"} != {0, 1}:
        raise ManifestError("held-out source needs both binary classes after quarantine")

    record_components = {record: key for key, value in components.items() for record in value["records"]}
    output = []
    for row in rows:
        component = components[record_components[row.record_id]]
        label = row.label
        if component["split"] == "quarantine" and label.status != LabelStatus.WITHDRAWN:
            label = replace(label, status=LabelStatus.QUARANTINED)
        output.append(replace(row, split=component["split"], label=label))
    output = validate_manifest(output)
    report = {
        "notice": PLACEHOLDER_NOTICE,
        "preparation_version": PREPARATION_VERSION,
        "config": {"seed": config.seed, "held_out_source": config.held_out_source,
                   "near_rms_uint8": config.near_rms, "thumbnail": "16x16 RGB bilinear"},
        "split_fractions": dict(zip(ACTIVE_SPLITS, FRACTIONS, strict=True)),
        "split_method": "binary-class component stratification; one/class/split minimum then largest remainder",
        "components": dict(sorted(components.items())),
        "record_components": record_components,
        "duplicates": duplicates,
        "rows_by_split": dict(sorted(Counter(row.split for row in output).items())),
        "components_by_split": dict(sorted(Counter(value["split"] for value in components.values()).items())),
        "unresolved_by_source_label": [
            {"source": source, "original_label": label, "count": count}
            for (source, label), count in sorted(unresolved.items())
        ],
        "original_label_status": {row.record_id: str(row.label.status) for row in rows},
        "limitations": ["synthetic metrics are not clinical performance",
                        "visual heuristic can miss duplicates or merge unrelated images",
                        "source-scoped IDs do not prove patient independence",
                        "quadratic pair search limited to 2000 fixture rows"],
    }
    return output, report
