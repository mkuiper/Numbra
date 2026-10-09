"""Tiny generated shapes, never clinical photographs or patient metadata."""

import hashlib
from pathlib import Path

import numpy as np
from PIL import Image
import pytest

from numbra_ml.manifest import ManifestRow
from numbra_ml.schema import SCHEMA_VERSION


def make_row(root: Path, index: int = 0, *, source: str = "synthetic-shapes",
             family: str = "leprosy", split: str = "train") -> ManifestRow:
    path = root / f"shape-{index}.png"
    # Pixels are invented RGB blocks; labels are invented engineering targets.
    pixels = np.zeros((12, 16, 3), dtype=np.uint8)
    pixels[:] = (30 + index % 50, 60, 90)
    pixels[3:9, 4:12] = (180, 100 + index % 50, 40)
    Image.fromarray(pixels).save(path)
    return ManifestRow.from_dict({
        "schema_version": SCHEMA_VERSION, "taxonomy_version": "1.0.0",
        "record_id": f"synthetic-{index}", "image_path": path.name,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "source": {"id": source, "version": "fixture-v1", "url": "urn:numbra:synthetic"},
        "licence": {"id": "Apache-2.0", "url": "urn:numbra:project-code-licence",
                    "attribution": "Numbra generated fixture; no patient data"},
        "label": {
            "original_label": f"SYNTHETIC:{family}",
            "diagnosis": None if family == "unresolved" else f"synthetic_{family}",
            "family": family, "status": "synthetic",
            "leprosy_classification": "unknown", "reaction_status": "unknown",
        },
        "confirmed_by": None, "patient_id": f"invented-patient-{index}",
        "group_id": f"invented-group-{index}", "split": split,
        "synthetic": True, "placeholder": True, "skin_tone": None,
        "observations": {},
    })


@pytest.fixture
def row_factory(tmp_path):
    return lambda index=0, **kwargs: make_row(tmp_path, index, **kwargs)


@pytest.fixture
def tiny_fixture(row_factory):
    families = ("leprosy", "leprosy_differential", "other", "unresolved")
    return tuple(row_factory(index, source="synthetic-shapes" if index < 4 else "synthetic-colours",
                             family=families[index % 4], split="train" if index < 4 else "test")
                 for index in range(8))
