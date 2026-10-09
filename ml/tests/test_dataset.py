from dataclasses import replace
import hashlib

import numpy as np
from PIL import Image
import pytest

from numbra_ml import PLACEHOLDER_NOTICE
from numbra_ml.dataset import DataError, ManifestDataset, load_rgb
from numbra_ml.manifest import ManifestError, write_manifest


def test_loading_and_explicit_transform_preserve_row_target_and_notice(tmp_path, tiny_fixture):
    manifest = tmp_path / "fixture.jsonl"
    write_manifest(manifest, tiny_fixture)
    dataset = ManifestDataset.from_manifest(tmp_path, manifest, split="train")
    assert len(dataset) == 4
    sample = dataset[0]
    assert sample.image.shape == (12, 16, 3)
    assert sample.image.dtype == np.uint8
    np.testing.assert_array_equal(sample.image[0, 0], [30, 60, 90])
    assert sample.binary_target == 1
    assert sample.notice == PLACEHOLDER_NOTICE and "PLACEHOLDER" in sample.notice
    assert [item.binary_target for item in dataset] == [1, 0, 0, None]
    transformed = ManifestDataset(tmp_path, tiny_fixture, transform=lambda rgb: rgb.astype(np.float32) / 255)
    assert transformed[0].image.dtype == np.float32
    np.testing.assert_allclose(transformed[0].image[0, 0], np.array([30, 60, 90]) / 255)


def test_supervised_selection_reports_every_exclusion(tmp_path, row_factory):
    rows = [row_factory(0), row_factory(1, family="unresolved"), row_factory(2),
            row_factory(3, split="quarantine"), row_factory(4, split="unassigned"), row_factory(5)]
    rows[2] = replace(rows[2], group_id=None)
    rows[5] = replace(rows[5], label=replace(rows[5].label, status="provisional"))
    selected, excluded = ManifestDataset(tmp_path, tuple(rows)).supervised_selection()
    assert selected == (rows[0],)
    assert excluded == {
        "synthetic-1": "unresolved_or_unconfirmed_label", "synthetic-2": "missing_group_id",
        "synthetic-3": "ineligible_split", "synthetic-4": "ineligible_split",
        "synthetic-5": "unresolved_or_unconfirmed_label",
    }


def test_non_synthetic_source_blocked_before_image_access(tmp_path, row_factory):
    row = row_factory()
    row = replace(row, synthetic=False, source=replace(row.source, id="dermacon-in"),
                  label=replace(row.label, status="provisional"), image_path="does-not-exist.png")
    with pytest.raises(DataError, match="synthetic PLACEHOLDER"):
        ManifestDataset(tmp_path, (row,))
    with pytest.raises(DataError, match="synthetic PLACEHOLDER"):
        load_rgb(tmp_path, row)


@pytest.mark.parametrize("change", ["id", "url", "licence"])
def test_synthetic_flag_alone_does_not_approve_other_sources(tmp_path, row_factory, change):
    row = row_factory()
    if change == "id":
        row = replace(row, source=replace(row.source, id="arbitrary-source"))
    elif change == "url":
        row = replace(row, source=replace(row.source, url="https://unapproved.invalid"))
    else:
        row = replace(row, licence=replace(row.licence, id="UNVERIFIED"))
    with pytest.raises(DataError):
        ManifestDataset(tmp_path, (row,))


def test_hash_integrity_failure_is_not_a_low_target(tmp_path, row_factory):
    row = row_factory()
    (tmp_path / row.image_path).write_bytes(b"changed bytes")
    with pytest.raises(DataError, match="checksum"):
        load_rgb(tmp_path, row)


def test_undecodable_image_is_explicit_failure(tmp_path, row_factory):
    row = row_factory()
    content = b"synthetic non-image bytes"
    (tmp_path / row.image_path).write_bytes(content)
    row = replace(row, sha256=hashlib.sha256(content).hexdigest())
    with pytest.raises(DataError, match="undecodable"):
        load_rgb(tmp_path, row)


def test_missing_image_is_explicit_failure(tmp_path, row_factory):
    row = replace(row_factory(), image_path="missing.png")
    with pytest.raises(DataError, match="unavailable"):
        load_rgb(tmp_path, row)


def test_exif_orientation_is_applied_before_returning_pixels(tmp_path, row_factory):
    row = row_factory()
    path = tmp_path / row.image_path
    pixels = np.zeros((3, 7, 3), dtype=np.uint8)
    pixels[0, 0] = [255, 0, 0]
    image = Image.fromarray(pixels)
    exif = Image.Exif()
    exif[274] = 6  # 90 degrees clockwise, generated metadata only.
    image.save(path, exif=exif)
    row = replace(row, sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    output = load_rgb(tmp_path, row)
    np.testing.assert_array_equal(output, np.rot90(pixels, k=3))


def test_multiframe_image_is_explicit_failure(tmp_path, row_factory):
    row = row_factory()
    path = tmp_path / "frames.gif"
    images = [Image.new("RGB", (4, 4), colour) for colour in ["red", "blue"]]
    images[0].save(path, save_all=True, append_images=images[1:])
    row = replace(row, image_path=path.name, sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    with pytest.raises(DataError, match="multi-frame"):
        load_rgb(tmp_path, row)


def test_symlink_escape_and_direct_traversal_are_rejected(tmp_path, row_factory):
    row = row_factory()
    root = tmp_path / "data-root"
    root.mkdir()
    (root / "escape.png").symlink_to(tmp_path / row.image_path)
    with pytest.raises(DataError, match="symlink escapes"):
        load_rgb(root, replace(row, image_path="escape.png"))
    with pytest.raises(DataError, match="relative"):
        load_rgb(root, replace(row, image_path="../shape-0.png"))


def test_grayscale_is_explicitly_expanded_to_rgb(tmp_path, row_factory):
    row = row_factory()
    image_path = tmp_path / row.image_path
    Image.fromarray(np.full((5, 7), 50, dtype=np.uint8)).save(image_path)
    row = replace(row, sha256=hashlib.sha256(image_path.read_bytes()).hexdigest())
    image = load_rgb(tmp_path, row)
    assert image.shape == (5, 7, 3)
    assert np.all(image == 50)


def test_transparent_images_rejected_until_background_policy_exists(tmp_path, row_factory):
    row = row_factory()
    path = tmp_path / row.image_path
    Image.fromarray(np.zeros((4, 4, 4), dtype=np.uint8)).save(path)
    row = replace(row, sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    with pytest.raises(DataError, match="unsupported image mode"):
        load_rgb(tmp_path, row)


def test_full_manifest_leakage_is_checked_before_filtering(tmp_path, row_factory):
    first, second = row_factory(1), row_factory(2, split="test")
    second = replace(second, patient_id=first.patient_id)
    with pytest.raises(ManifestError, match="split leakage"):
        ManifestDataset(tmp_path, (first, second), split="train")


def test_invalid_split_and_empty_selection(tmp_path, tiny_fixture):
    with pytest.raises(DataError, match="unknown split"):
        ManifestDataset(tmp_path, tiny_fixture, split="typo")
    dataset = ManifestDataset(tmp_path, tiny_fixture, split="held_out")
    assert len(dataset) == 0 and dataset.supervised_selection() == ((), {})
    with pytest.raises(IndexError):
        dataset[0]
