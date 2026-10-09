"""M2 acceptance: synthetic only, conflicts, component splits and held-out source."""

from collections import defaultdict
from dataclasses import replace
import hashlib

import numpy as np
from PIL import Image
import pytest

from numbra_ml.dataset import DataError, ManifestDataset
from numbra_ml.manifest import ManifestError, read_manifest, validate_manifest, write_manifest
from numbra_ml.preparation import PreparationConfig, prepare
from numbra_ml.prepare import main, prepare_run
from numbra_ml.synthetic import SOURCES, SyntheticConfig, generate
from numbra_ml.taxonomy import LabelFamily, unresolved_label


@pytest.fixture
def generated(tmp_path):
    root = tmp_path / "generated"
    return root, generate(root, SyntheticConfig(groups_per_source=16))


def _pixel_copy(root, row, record_id, *, delta=0, compression=0):
    rgb = np.asarray(Image.open(root / row.image_path)).copy()
    if delta:
        rgb[10:20, 10:20] = np.clip(rgb[10:20, 10:20].astype(int) + delta, 0, 255)
    path = root / "images" / f"{record_id}.png"
    Image.fromarray(rgb).save(path, compress_level=compression)
    return replace(row, record_id=record_id, image_path=path.relative_to(root).as_posix(),
                   sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                   group_id=f"group-{record_id}", patient_id=f"patient-{record_id}")


def test_component_splits_are_deterministic_and_isolate_held_out_source(generated):
    root, rows = generated
    output, report = prepare(root, rows)
    reverse, reverse_report = prepare(root, tuple(reversed(rows)))
    assert output == reverse and report == reverse_report
    assert all(row.licence.id == "Apache-2.0" and row.placeholder for row in output)
    assert {row.split for row in output} == {"train", "calibration", "threshold_validation", "test", "held_out"}
    by_patient, by_group = defaultdict(set), defaultdict(set)
    for row in output:
        by_patient[(row.source.id, row.patient_id)].add(row.split)
        by_group[row.group_key].add(row.split)
        assert (row.split == "held_out") == (row.source.id == SOURCES[2])
    assert all(len(splits) == 1 for splits in by_patient.values())
    assert all(len(splits) == 1 for splits in by_group.values())
    for split in report["rows_by_split"]:
        assert {row.label.binary_target for row in output if row.split == split} == {0, 1}
    lookup = {row.record_id: row for row in output}
    for pair in report["duplicates"]["near_visual"]:
        first, second = pair["records"]
        assert lookup[first].split == lookup[second].split
    assert "PLACEHOLDER" in report["notice"]


def test_exact_byte_opposing_labels_quarantine_entire_patient(generated):
    root, rows = generated
    original = rows[0]
    opposite = replace(original, record_id="conflicting-copy",
                       label=replace(original.label, family="leprosy", diagnosis="synthetic_leprosy"),
                       patient_id="copy-patient", group_id="copy-group")
    output, report = prepare(root, rows + (opposite,))
    affected = [row for row in output if row.record_id in {original.record_id, rows[1].record_id, opposite.record_id}]
    assert len(affected) == 3
    assert all(row.split == "quarantine" and row.label.binary_target is None for row in affected)
    component = report["components"][report["record_components"][opposite.record_id]]
    assert component["quarantine_reasons"] == ["conflicting_diagnoses"]
    assert report["duplicates"]["exact_bytes"]
    assert report["original_label_status"][opposite.record_id] == "synthetic"
    # Bypassing preparation cannot sneak contradictory active labels into a reader.
    active = [replace(original, split="train"), replace(opposite, split="train")]
    with pytest.raises(ManifestError, match="conflicting labels"):
        validate_manifest(active)
    assert validate_manifest([replace(row, split="unassigned") for row in active])


def test_transitive_patient_and_cross_source_duplicate_links(generated):
    root, rows = generated
    source_a = rows[0]
    source_b = rows[32]
    source_b_next = rows[36]  # another same-target patient/group
    bridge = replace(source_b_next, record_id="bridge", image_path=source_a.image_path,
                     sha256=source_a.sha256, patient_id=source_b.patient_id)
    output, report = prepare(root, rows + (bridge,))
    ids = {source_a.record_id, rows[1].record_id, source_b.record_id,
           rows[33].record_id, source_b_next.record_id, rows[37].record_id, "bridge"}
    component_ids = {report["record_components"][record] for record in ids}
    assert len(component_ids) == 1
    assert len({row.split for row in output if row.record_id in ids}) == 1
    component = report["components"][component_ids.pop()]
    assert component["sources"] == list(SOURCES[:2])
    assert component["quarantine_reasons"] == []


def test_cross_held_out_duplicate_quarantines_whole_connected_group(generated):
    root, rows = generated
    original, held = rows[0], rows[64]
    bridge = replace(held, record_id="held-bridge", image_path=original.image_path, sha256=original.sha256)
    output, report = prepare(root, rows + (bridge,))
    component = report["components"][report["record_components"]["held-bridge"]]
    assert component["quarantine_reasons"] == ["crosses_held_out_source_boundary"]
    affected = {original.record_id, rows[1].record_id, held.record_id, rows[65].record_id, "held-bridge"}
    assert all(row.split == "quarantine" for row in output if row.record_id in affected)
    assert {row.source.id for row in output if row.split == "held_out"} == {SOURCES[2]}


def test_reencoded_and_small_visual_edits_connect_distinct_groups(generated):
    root, rows = generated
    original = rows[0]
    reencoded = _pixel_copy(root, original, "reencoded")
    near = _pixel_copy(root, original, "near-copy", delta=1)
    assert original.sha256 != reencoded.sha256 != near.sha256
    output, report = prepare(root, rows + (reencoded, near))
    component_id = report["record_components"][original.record_id]
    assert report["record_components"][reencoded.record_id] == component_id
    assert report["record_components"][near.record_id] == component_id
    assert report["duplicates"]["decoded_pixels"]
    assert any(set(pair["records"]) == {original.record_id, "near-copy"}
               for pair in report["duplicates"]["near_visual"])
    assert len({row.split for row in output if row.record_id in {original.record_id, "near-copy", "reencoded"}}) == 1


def test_missing_groups_and_unresolved_labels_are_reported_not_imputed(generated):
    root, rows = generated
    missing = replace(rows[0], group_id=None)
    unknown = replace(rows[4], label=unresolved_label("SYNTHETIC:Unrecognised Name"))
    output, report = prepare(root, (missing,) + rows[1:4] + (unknown,) + rows[5:])
    assert all(row.split == "quarantine" for row in output if row.record_id in {
        missing.record_id, rows[1].record_id, unknown.record_id, rows[5].record_id})
    assert next(row for row in output if row.record_id == missing.record_id).group_id is None
    assert report["unresolved_by_source_label"] == [{
        "source": SOURCES[0], "original_label": "SYNTHETIC:Unrecognised Name", "count": 1}]
    selected, excluded = ManifestDataset(root, output).supervised_selection()
    assert len(excluded) == 4 and len(selected) == 92


def test_preparation_verifies_every_image_and_source_before_split(generated):
    root, rows = generated
    real = replace(rows[0], synthetic=False, label=replace(rows[0].label, status="provisional"))
    with pytest.raises(DataError, match="synthetic PLACEHOLDER"):
        prepare(root / "missing", (real,) + rows[1:])
    (root / rows[-1].image_path).write_bytes(b"changed")
    with pytest.raises(DataError, match="checksum"):
        prepare(root, rows)


@pytest.mark.parametrize("change", ["already_split", "missing_held", "too_few_classes", "one_source"])
def test_preparation_refuses_invalid_or_inadequate_cohorts(generated, change):
    root, rows = generated
    config = PreparationConfig()
    if change == "already_split":
        rows = (replace(rows[0], split="train"),) + rows[1:]
    elif change == "missing_held":
        config = PreparationConfig(held_out_source="synthetic-not-present")
    elif change == "too_few_classes":
        rows = tuple(row for row in rows if row.source.id == SOURCES[2] or row.label.binary_target == 0)
    else:
        rows = tuple(row for row in rows if row.source.id == SOURCES[2])
    with pytest.raises(ManifestError):
        prepare(root, rows, config)


def test_reproducible_full_run_and_manifest_round_trip(tmp_path):
    first, second = tmp_path / "first", tmp_path / "second"
    report1 = prepare_run(first, groups_per_source=16)
    report2 = prepare_run(second, groups_per_source=16)
    assert report1 == report2
    assert (first / "manifest.jsonl").read_bytes() == (second / "manifest.jsonl").read_bytes()
    assert (first / "preparation-report.json").read_bytes() == (second / "preparation-report.json").read_bytes()
    assert len(read_manifest(first / "manifest.jsonl")) == 96
    assert all(row.split == "unassigned" for row in read_manifest(first / "unassigned.jsonl"))
    assert {row.source.id for row in read_manifest(first / "manifest.jsonl")} == set(SOURCES)
    with pytest.raises(ManifestError, match="never overwrite"):
        prepare_run(first, groups_per_source=16)


def test_cli_rejects_output_outside_ignored_data(tmp_path):
    with pytest.raises(SystemExit) as error:
        main(["--output", str(tmp_path / "bad")])
    assert error.value.code == 2 and not (tmp_path / "bad").exists()


@pytest.mark.parametrize("kwargs", [{"groups_per_source": 15}, {"groups_per_source": 258},
                                     {"groups_per_source": True}, {"seed": True}])
def test_invalid_generator_config_rejected(kwargs):
    with pytest.raises(ManifestError):
        SyntheticConfig(**kwargs)


@pytest.mark.parametrize("kwargs", [{"near_rms": float("nan")}, {"near_rms": 6},
                                     {"seed": True}, {"held_out_source": "real-source"}])
def test_invalid_preparation_config_rejected(kwargs):
    with pytest.raises(ManifestError):
        PreparationConfig(**kwargs)


def test_explicit_fixture_row_limit_never_subsamples(generated):
    root, rows = generated
    with pytest.raises(ManifestError, match="1..2000 rows"):
        prepare(root, ())
    too_many = tuple(replace(rows[0], record_id=f"extra-{i}") for i in range(2001))
    with pytest.raises(ManifestError, match="1..2000 rows"):
        prepare(root, too_many)


def test_changed_seed_changes_development_assignment_only(generated):
    root, rows = generated
    first, _ = prepare(root, rows)
    second, _ = prepare(root, rows, PreparationConfig(seed=42))
    assert any(a.split != b.split for a, b in zip(first, second, strict=True))
    for a, b in zip(first, second, strict=True):
        assert a.sha256 == b.sha256 and a.label == b.label
        if a.source.id == SOURCES[2]:
            assert a.split == b.split == "held_out"


@pytest.mark.parametrize("status", ["provisional", "withdrawn"])
def test_ineligible_labels_quarantine_component_without_reviving_withdrawal(generated, status):
    root, rows = generated
    changed = replace(rows[0], label=replace(rows[0].label, status=status))
    output, report = prepare(root, (changed,) + rows[1:])
    lookup = {row.record_id: row for row in output}
    assert lookup[changed.record_id].split == lookup[rows[1].record_id].split == "quarantine"
    assert lookup[changed.record_id].label.binary_target is None
    assert lookup[rows[1].record_id].label.binary_target is None
    if status == "withdrawn":
        assert lookup[changed.record_id].label.status == "withdrawn"
    assert report["original_label_status"][changed.record_id] == status


def test_held_out_requires_both_classes_after_quarantine(generated):
    root, rows = generated
    rows = tuple(replace(row, label=replace(row.label, status="withdrawn"))
                 if row.source.id == SOURCES[2] and row.label.binary_target == 1 else row
                 for row in rows)
    with pytest.raises(ManifestError, match="held-out source needs both binary classes"):
        prepare(root, rows)
