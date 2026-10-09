"""PLACEHOLDER fixture acquisition: procedural pixels, no clinical photos."""

from dataclasses import dataclass
import hashlib
from pathlib import Path

import numpy as np
from PIL import Image

from .manifest import Capture, Licence, ManifestError, ManifestRow, Observations, SkinTone, Source
from .taxonomy import Label, LabelFamily, LabelStatus

GENERATOR_VERSION = "shapes-v2"
SOURCES = ("synthetic-source-a", "synthetic-source-b", "synthetic-source-c")
LABEL_NOISE_RATE = 0.10
TARGET_NAMES = {0: "synthetic square", 1: "synthetic circle"}


def colour_stratum(background: np.ndarray) -> str:
    """Fixed luminance bands of the generated background, never human skin tone."""
    luminance = float(np.dot(background, [0.2126, 0.7152, 0.0722]))
    return f"background-stratum-{int(luminance >= 85) + int(luminance >= 170)}"


def shape_mask(x: np.ndarray, y: np.ndarray, cx: int, cy: int, area: int, target: int) -> np.ndarray:
    """Match the exact raster area; target selects radial versus square ordering."""
    distance = ((x - cx) ** 2 + (y - cy) ** 2) if target else (
        np.maximum(np.abs(x - cx), np.abs(y - cy)))
    mask = np.zeros(x.size, dtype=bool)
    mask[np.argsort(distance.ravel(), kind="stable")[:area]] = True
    return mask.reshape(x.shape)


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
            background = rng.integers(25, 220, size=3)
            texture = rng.normal(0, 22 + 7 * source_index, size=(64, 64, 3))
            cx, cy = rng.integers(22, 42, size=2)
            # Deliberate group-level label noise exercises imperfect evaluation.
            rendered_target = 1 - target if rng.random() < LABEL_NOISE_RATE else target
            area = int(rng.integers(250, 750))  # Same area distribution for both targets.
            mask = shape_mask(x, y, cx, cy, area, rendered_target)
            # Source-dependent illumination/noise acts on both classes. Shape and
            # background share intensity ranges; neither mean nor area is a target.
            gradient = (source_index + 1) * 18 * np.sin((x + y) / (4 + source_index))
            gains = np.roll(np.array([0.75, 1.0, 1.25]), source_index)
            background = np.clip(background * gains, 0, 255)
            base = background + texture + gradient[..., None]
            contrast = rng.uniform(12, 65) * rng.choice([-1, 1])
            base[mask] += contrast
            base = np.clip(base, 0, 255)
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
                    label=Label(f"SYNTHETIC:{'circle' if target else 'square'}",
                                f"synthetic_{'circle' if target else 'square'}",
                                family, LabelStatus.SYNTHETIC),
                    confirmed_by=None, patient_id=f"invented-patient-{group:04d}",
                    group_id=f"invented-group-{group:04d}", split="unassigned",
                    synthetic=True, placeholder=True,
                    skin_tone=SkinTone("synthetic_colour", colour_stratum(background)),
                    observations=Observations(),
                    capture=Capture(f"invented-site-{source_index}", "procedural_generator", "not_applicable"),
                ))
    return tuple(rows)
