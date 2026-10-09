"""Local RGB loading interfaces. No downloads, implicit resizes or training yet."""

from dataclasses import dataclass
import hashlib
from io import BytesIO
from pathlib import Path
from typing import Callable, Iterator

import numpy as np
from PIL import Image, ImageOps, UnidentifiedImageError

from . import PLACEHOLDER_NOTICE
from .manifest import ManifestError, ManifestRow, read_manifest, validate_manifest
from .schema import SPLITS


class DataError(ValueError):
    """Disallowed source, unsafe path, invalid image or hash mismatch."""


def require_approved_source(row: ManifestRow) -> None:
    """ADR-002 currently approves only generated fixtures, never real sources."""
    if not row.synthetic or not row.placeholder or not row.source.id.startswith("synthetic-"):
        raise DataError("ADR-002 permits synthetic PLACEHOLDER sources only")
    if row.source.url != "urn:numbra:synthetic" or row.licence.id != "Apache-2.0":
        raise DataError("synthetic source must use generator provenance and project-code licence")


def load_rgb(root: Path, row: ManifestRow) -> np.ndarray:
    """Return oriented uint8 HWC RGB; verify bytes before decoding, reject escapes."""
    # Validate even if caller bypasses read_manifest and constructs a row directly.
    try:
        row = ManifestRow.from_dict(row.to_dict())
    except ManifestError as exc:
        raise DataError(str(exc)) from exc
    require_approved_source(row)
    try:
        root = Path(root).resolve(strict=True)
        if not root.is_dir():
            raise DataError("data root must be a directory")
        path = (root / row.image_path).resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise DataError(f"image path unavailable: {row.record_id}") from exc
    if not path.is_relative_to(root):
        raise DataError("image symlink escapes the data root")
    if not path.is_file():
        raise DataError("image_path must identify a file")
    try:
        content = path.read_bytes()
    except OSError as exc:
        raise DataError(f"image unreadable: {row.record_id}") from exc
    if hashlib.sha256(content).hexdigest() != row.sha256:
        raise DataError(f"image checksum mismatch: {row.record_id}")
    try:
        with Image.open(BytesIO(content)) as image:
            if getattr(image, "n_frames", 1) != 1:
                raise DataError("multi-frame images are unsupported")
            if image.mode not in {"RGB", "L"}:
                raise DataError(f"unsupported image mode: {image.mode}; RGB or grayscale required")
            rgb = ImageOps.exif_transpose(image).convert("RGB")
            return np.array(rgb, dtype=np.uint8, copy=True)
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as exc:
        raise DataError(f"undecodable image: {row.record_id}") from exc


@dataclass(frozen=True)
class Sample:
    row: ManifestRow
    image: np.ndarray
    binary_target: int | None
    notice: str = PLACEHOLDER_NOTICE


class ManifestDataset:
    """Sequence-style interface; transforms are supplied explicitly by later stages."""

    def __init__(
        self, root: Path, rows: tuple[ManifestRow, ...], *, split: str | None = None,
        transform: Callable[[np.ndarray], np.ndarray] | None = None,
    ) -> None:
        all_rows = validate_manifest(rows)
        for row in all_rows:
            require_approved_source(row)
        if split is not None and split not in SPLITS:
            raise DataError(f"unknown split: {split}")
        self.root = Path(root)
        self.rows = tuple(row for row in all_rows if split is None or row.split == split)
        self.transform = transform

    @classmethod
    def from_manifest(cls, root: Path, path: Path, **kwargs) -> "ManifestDataset":
        return cls(root, read_manifest(path), **kwargs)

    def __len__(self) -> int:
        return len(self.rows)

    def __getitem__(self, index: int) -> Sample:
        row = self.rows[index]
        image = load_rgb(self.root, row)
        if self.transform is not None:
            image = self.transform(image)
        return Sample(row, image, row.label.binary_target)

    def __iter__(self) -> Iterator[Sample]:
        for index in range(len(self)):
            yield self[index]

    def supervised_selection(self) -> tuple[tuple[ManifestRow, ...], dict[str, str]]:
        """Eligibility only: retain exclusion reasons, never impute missing groups."""
        included, excluded = [], {}
        for row in self.rows:
            reason = None
            if row.label.binary_target is None:
                reason = "unresolved_or_unconfirmed_label"
            elif row.group_key is None:
                reason = "missing_group_id"
            elif row.split in {"quarantine", "unassigned"}:
                reason = "ineligible_split"
            if reason:
                excluded[row.record_id] = reason
            else:
                included.append(row)
        return tuple(included), excluded
