"""M2 acceptance: synthetic only, conflicts, component splits and held-out source."""

from collections import defaultdict
from dataclasses import replace
import hashlib
from pathlib import Path
import uuid

import numpy as np
from PIL import Image
import pytest

from numbra_ml.dataset import DataError, ManifestDataset
from numbra_ml.manifest import ManifestError, read_manifest, validate_manifest, write_manifest
from numbra_ml.preparation import PreparationConfig, prepare
from numbra_ml.prepare import main, prepare_run, repository_root
from numbra_ml.synthetic import GENERATOR_VERSION, SOURCES, SyntheticConfig, colour_stratum, generate, shape_mask
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
    assert len(report["components"]) == 48  # Distinct invented groups must stay separate.
    assert report["nearest_unlinked_pair"]["rms_uint8"] > 2
    for split in ("train", "calibration", "threshold_validation", "test"):
        counts = report["components_by_split_source_class"][split]
        assert counts[SOURCES[0]] == counts[SOURCES[1]]
        assert set(counts[SOURCES[0]]) == {"0", "1"}
        assert all(count > 0 for count in counts[SOURCES[0]].values())
        assert counts[SOURCES[2]] == {"0": 0, "1": 0}


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


def test_cli_rejects_symlink_parent_escape(tmp_path):
    repo = repository_root()
    link = repo / "data" / f".tmp-symlink-{uuid.uuid4().hex}"
    link.parent.mkdir(exist_ok=True)
    link.symlink_to(tmp_path, target_is_directory=True)
    try:
        with pytest.raises(SystemExit) as error:
            main(["--output", str(link / "escaped")])
        assert error.value.code == 2
        assert not (tmp_path / "escaped").exists()
    finally:
        link.unlink()


def test_root_discovery_works_from_site_packages_and_worktree_marker(tmp_path):
    checkout = tmp_path / "checkout"
    (checkout / "docs").mkdir(parents=True)
    (checkout / "docs" / "ROADMAP.md").write_text("test checkout marker")
    (checkout / ".git").write_text("gitdir: worktree-marker")
    installed = checkout / "ml" / ".venv" / "lib" / "python3.12" / "site-packages"
    installed.mkdir(parents=True)
    assert repository_root(installed) == checkout
    assert repository_root(checkout / "docs") == checkout
    (checkout / ".git").unlink()
    assert repository_root(installed) == repository_root()  # The outer checkout still exists.
    with pytest.raises(ManifestError, match="no checkout root"):
        repository_root(Path("/"))


@pytest.mark.parametrize("boundary_pixel", [129, 130, 131])
def test_visual_rms_boundary_and_nearest_final_unlinked_pair(generated, boundary_pixel):
    root, rows = generated
    changed = list(rows)
    for index in (0, 1, 4, 5):  # Two independent same-class source-A groups.
        pixels = np.full((16, 16, 3), 128 if index < 4 else 130, dtype=np.uint8)
        if index >= 4:
            pixels[0, 0, 0] = boundary_pixel
        path = root / rows[index].image_path
        Image.fromarray(pixels).save(path)
        changed[index] = replace(rows[index], sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    _, report = prepare(root, tuple(changed))
    first = report["record_components"][rows[0].record_id]
    second = report["record_components"][rows[4].record_id]
    assert (first != second) == (boundary_pixel > 130)
    if boundary_pixel > 130:
        assert report["nearest_unlinked_pair"]["rms_uint8"] == pytest.approx(2.001627, abs=1e-6)
        assert set(report["nearest_unlinked_pair"]["records"]) <= {
            rows[i].record_id for i in (0, 1, 4, 5)}
    else:
        assert any(1.998 < pair["rms_uint8"] <= 2 for pair in report["duplicates"]["near_visual"])
        assert report["nearest_unlinked_pair"]["rms_uint8"] > 2


@pytest.mark.parametrize("area", [250, 513, 749])
def test_circle_and_square_have_matching_exact_pixel_areas(area):
    y, x = np.mgrid[:64, :64]
    square = shape_mask(x, y, 32, 32, area, 0)
    circle = shape_mask(x, y, 32, 32, area, 1)
    assert square.sum() == circle.sum() == area
    assert np.any(square != circle)


def test_v2_fixture_is_not_separable_by_mean_intensity(tmp_path):
    root = tmp_path / "difficulty"
    rows = generate(root, SyntheticConfig(groups_per_source=128))[::2]
    means = np.array([np.asarray(Image.open(root / row.image_path)).mean() for row in rows])
    target = np.array([row.label.binary_target for row in rows])
    best = 0.0
    for threshold in means:
        positive = means >= threshold
        accuracy = (positive[target == 1].mean() + (~positive[target == 0]).mean()) / 2
        best = max(best, accuracy, 1 - accuracy)
    assert best < 0.65  # Regression on fixed procedural seed, no clinical meaning.


def test_synthetic_colour_bands_and_shape_diagnoses(generated):
    root, rows = generated
    assert colour_stratum(np.array([84, 84, 84])) == "background-stratum-0"
    assert colour_stratum(np.array([85, 85, 85])) == "background-stratum-1"
    assert colour_stratum(np.array([169, 169, 169])) == "background-stratum-1"
    assert colour_stratum(np.array([170, 170, 170])) == "background-stratum-2"
    for row in rows[::2]:
        source_index = SOURCES.index(row.source.id)
        group = int(row.group_id.rsplit("-", 1)[1])
        key = f"{GENERATOR_VERSION}:20261009:{row.source.id}:{group}"
        rng = np.random.default_rng(int.from_bytes(hashlib.sha256(key.encode()).digest()[:8]))
        background = np.clip(rng.integers(25, 220, size=3) *
                             np.roll([0.75, 1.0, 1.25], source_index), 0, 255)
        assert row.skin_tone.value == colour_stratum(background)
        assert row.label.diagnosis == ("synthetic_circle" if row.label.binary_target else "synthetic_square")


def test_selection_exercise_reaches_count_guard_without_raising_row_cap(tmp_path):
    report = prepare_run(tmp_path / "selection", groups_per_source=256,
                         split_profile="selection_exercise")
    assert len(report["components"]) == 768
    assert sum(report["rows_by_split"].values()) == 1536
    counts = report["components_by_split_source_class"]
    for target in ("0", "1"):
        assert sum(counts["threshold_validation"][source][target] for source in SOURCES) == 102
        assert sum(counts["calibration"][source][target] for source in SOURCES) == 52
    assert report["generator"]["target_names"] == {0: "synthetic square", 1: "synthetic circle"}
    assert report["config"]["split_profile"] == "selection_exercise"


@pytest.mark.parametrize("source", SOURCES[:2])
def test_other_predeclared_source_holdouts_preserve_components(generated, source):
    root, rows = generated
    output, report = prepare(root, rows, PreparationConfig(held_out_source=source))
    assert len(report["components"]) == 48
    assert {row.source.id for row in output if row.split == "held_out"} == {source}
    assert all(row.split == "held_out" for row in output if row.source.id == source)


@pytest.mark.parametrize("kwargs", [{"groups_per_source": 15}, {"groups_per_source": 258},
                                     {"groups_per_source": True}, {"seed": True}])
def test_invalid_generator_config_rejected(kwargs):
    with pytest.raises(ManifestError):
        SyntheticConfig(**kwargs)


@pytest.mark.parametrize("kwargs", [{"near_rms": float("nan")}, {"near_rms": 6},
                                     {"seed": True}, {"held_out_source": "real-source"},
                                     {"split_profile": "invented"}])
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
