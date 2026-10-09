"""PLACEHOLDER fixture acquisition: procedural pixels, no clinical photos."""

from dataclasses import dataclass
import hashlib
from pathlib import Path

import numpy as np
from PIL import Image

from .manifest import Capture, Licence, ManifestError, ManifestRow, Observations, SkinTone, Source
from .taxonomy import Label, LabelFamily, LabelStatus

GENERATOR_VERSION = "shapes-v1"
SOURCES = ("synthetic-source-a", "synthetic-source-b", "synthetic-source-c")


@dataclass(frozen=True)
class SyntheticConfig:
    groups_per_source: int = 128
    seed: int = 20261009

    def __post_init__(self):
        if (not isinstance(self.groups_per_source, int) or isinstance(self.groups_per_source, bool)
                or not 16 <= self.groups_per_source <= 256 or self.groups_per_source % 2):
            raise ManifestError("groups_per_source must be an even integer in [16, 256]")
        if not isinstance(self.seed, int) or isinstance(self.seed, bool):
            raise ManifestError("seed must be an integer")


def generate(root: Path, config: SyntheticConfig = SyntheticConfig()) -> tuple[ManifestRow, ...]:
    """Write two generated views per invented group for each of three sources.

    Caller must provide a new/empty directory. Group IDs are generated identities,
    never claims of real patient independence. Sources differ only procedurally.
    """
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    if any(root.iterdir()):
        raise ManifestError("synthetic generation requires an empty directory; never overwrite data")
    image_root = root / "images"
    image_root.mkdir()
    rows = []
    y, x = np.mgrid[:64, :64]
    for source_index, source_id in enumerate(SOURCES):
        for group in range(config.groups_per_source):
            key = f"{GENERATOR_VERSION}:{config.seed}:{source_id}:{group}"
            rng = np.random.default_rng(int.from_bytes(hashlib.sha256(key.encode()).digest()[:8]))
            target = group % 2
            background = rng.integers(25, 130, size=3)
            texture = rng.normal(0, 22, size=(64, 64, 3))
            cx, cy = rng.integers(22, 42, size=2)
            radius = int(rng.integers(9, 16))
            mask = ((x - cx) ** 2 + (y - cy) ** 2 <= radius ** 2) if target else (
                (np.abs(x - cx) <= radius) & (np.abs(y - cy) <= radius))
            base = np.clip(background + texture, 0, 255)
            base[mask] = np.clip(rng.integers(170, 240, size=3) + texture[mask], 0, 255)
            # Source style affects both labels; no positive-only/negative-only source.
            base[::(source_index + 5)] = np.clip(base[::(source_index + 5)] + 12, 0, 255)
            family = LabelFamily.LEPROSY if target else LabelFamily.DIFFERENTIAL
            for view in range(2):
                record = f"{source_id}-g{group:04d}-v{view}"
                pixels = np.clip(base + rng.normal(0, 1.5, size=base.shape), 0, 255).astype(np.uint8)
                path = image_root / f"{record}.png"
                Image.fromarray(pixels).save(path)
                rows.append(ManifestRow(
                    record_id=record, image_path=path.relative_to(root).as_posix(),
                    sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                    source=Source(source_id, GENERATOR_VERSION, "urn:numbra:synthetic"),
                    licence=Licence("Apache-2.0", "urn:numbra:project-code-licence",
                                    "Numbra procedural PLACEHOLDER fixture; no patient data"),
                    label=Label(f"SYNTHETIC:{'circle' if target else 'square'}", f"synthetic_{family}",
                                family, LabelStatus.SYNTHETIC),
                    confirmed_by=None, patient_id=f"invented-patient-{group:04d}",
                    group_id=f"invented-group-{group:04d}", split="unassigned",
                    synthetic=True, placeholder=True,
                    skin_tone=SkinTone("synthetic_colour", f"background-stratum-{(group // 2) % 3}"),
                    observations=Observations(),
                    capture=Capture(f"invented-site-{source_index}", "procedural_generator", "not_applicable"),
                ))
    return tuple(rows)
