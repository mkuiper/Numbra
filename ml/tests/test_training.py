"""Generated fixtures/invented features only; no network or pretrained weights needed."""
from dataclasses import replace
import json
from pathlib import Path
import numpy as np
import pytest
from safetensors.torch import load_file, save_file
import torch
from torch import nn
from numbra_ml.dataset import DataError
from numbra_ml.evaluation import evaluation_report, read_component_index
from numbra_ml.prepare import prepare_run, repository_root
from numbra_ml.preprocessing import SPEC, preprocess
from numbra_ml.pretrained import FILES, acquire, ignored_path, verify_checkpoint
from numbra_ml.train import add_bootstrap, environment, main, write_reports
from numbra_ml.training import Baseline, FeatureHead, TrainingConfig, extract_features, fit_head, initialise, predict, tensor_hash

@pytest.fixture
def fixture(tmp_path):
    root = tmp_path / "prepared"
    prepare_run(root, groups_per_source=16)
    return root, read_component_index(root / "manifest.jsonl", root / "preparation-report.json")

def invented_features(index):
    features = np.random.default_rng(20).normal(size=(len(index.components), 4)).astype(np.float32)
    features[:, 0] = [2 * item.target - 1 for item in index.components]
    features[:, 3] = 7
    return torch.from_numpy(features)

def test_head_learns_reproduces_and_standardises_train_only(fixture):
    _, index = fixture
    features = invented_features(index)
    config = TrainingConfig(epochs=100)
    head, report = fit_head(index, features, config)
    repeated, repeated_report = fit_head(index, features, config)
    assert tensor_hash(head.state_dict()) == tensor_hash(repeated.state_dict())
    assert report == repeated_report
    assert report["loss_after_updates"] < report["loss_before_updates"] * 0.2
    selected = features[[i for i, item in enumerate(index.components) if item.split == "train"]]
    assert torch.equal(head.mean, selected.mean(0))
    assert head.scale[-1] == 1
    assert report["fit_split"] == "train" and report["components"] == len(selected)
    assert "PLACEHOLDER" in report["notice"]
    predictions = predict(index, features, head)
    assert len(predictions) == len(index.components)
    assert len({p.component_id for p in predictions}) == len(predictions)
    assert all((p.logit >= 0) == bool(p.target) for p in predictions if p.split == "train")

@pytest.mark.parametrize("split", ["calibration", "threshold_validation", "test", "held_out"])
def test_other_split_pixels_and_labels_cannot_change_fitted_head(fixture, split):
    _, index = fixture
    features = invented_features(index)
    config = TrainingConfig(epochs=10)
    head, report = fit_head(index, features, config)
    changed_features = features.clone()
    changed_components = []
    for i, item in enumerate(index.components):
        if item.split == split:
            changed_features[i] = 1000
            # Use an opposite known family's binary target; this is an in-memory
            # isolation probe, never a persisted manifest or disease label.
            opposite = next(c.row.label for c in index.components if c.target != item.target)
            item = replace(item, row=replace(item.row, label=opposite))
        changed_components.append(item)
    changed_index = replace(index, components=tuple(changed_components))
    changed_head, changed_report = fit_head(changed_index, changed_features, config)
    assert tensor_hash(head.state_dict()) == tensor_hash(changed_head.state_dict())
    assert report == changed_report

def test_head_rejects_invalid_features_and_single_class(fixture):
    _, index = fixture
    config = TrainingConfig(epochs=1)
    features = invented_features(index)
    for invalid in [features[:-1], features.double(), features[:, :0], features * float("nan")]:
        with pytest.raises(ValueError, match="feature"):
            fit_head(index, invalid, config)
    subset = tuple(item for item in index.components if item.split != "train" or item.target == 0)
    changed = replace(index, components=subset)
    with pytest.raises(ValueError, match="both"):
        fit_head(changed, invented_features(changed), config)

@pytest.mark.parametrize("change", [{"epochs": 0}, {"epochs": True}, {"seed": -1}, {"batch_size": 0},
                                   {"threads": 17}, {"learning_rate": float("nan")}, {"weight_decay": -1}])
def test_invalid_training_config(change):
    with pytest.raises(ValueError):
        TrainingConfig(**change)

def toy_backbone():
    return nn.Sequential(nn.Conv2d(3, 4, 1), nn.BatchNorm2d(4), nn.Dropout(0.5),
                         nn.AdaptiveAvgPool2d(1), nn.Flatten()).requires_grad_(False)

def test_frozen_feature_extraction_is_indexed_batch_invariant_and_nonmutating(fixture):
    root, index = fixture
    initialise(TrainingConfig(epochs=1))
    backbone = toy_backbone().train()
    before = tensor_hash(backbone.state_dict())
    single = extract_features(index, root, backbone, batch_size=1)
    batched = extract_features(index, root, backbone, batch_size=7)
    assert single.shape == (48, 4)
    assert torch.allclose(single, batched, atol=1e-6)
    assert tensor_hash(backbone.state_dict()) == before
    assert not backbone.training
    fit_head(index, batched, TrainingConfig(epochs=2))

def test_feature_extraction_rejects_unfrozen_or_changed_image(fixture):
    root, index = fixture
    initialise(TrainingConfig(epochs=1))
    backbone = toy_backbone().requires_grad_(True)
    with pytest.raises(ValueError, match="frozen"):
        extract_features(index, root, backbone, batch_size=16)
    backbone.requires_grad_(False)
    (root / index.components[0].row.image_path).write_bytes(b"corrupt")
    with pytest.raises(DataError, match="checksum"):
        extract_features(index, root, backbone, batch_size=16)

def test_serialised_baseline_roundtrip_is_raw_logit(tmp_path):
    initialise(TrainingConfig(epochs=1))
    first = Baseline(toy_backbone().eval(), FeatureHead(torch.zeros(4), torch.ones(4))).eval()
    inputs = torch.randn(3, 3, 224, 224)
    with torch.inference_mode():
        expected = first(inputs)
        assert expected.shape == (3,)
        assert torch.equal(expected, first.head(first.backbone(inputs)))
    path = tmp_path / "PLACEHOLDER-model.safetensors"
    save_file(first.state_dict(), str(path))
    other = Baseline(toy_backbone().eval(), FeatureHead(torch.ones(4), torch.ones(4))).eval()
    other.load_state_dict(load_file(str(path)), strict=True)
    with torch.inference_mode():
        assert torch.equal(other(inputs), expected)

def unnormalise(tensor):
    return (tensor.transpose(1, 2, 0) * np.array(SPEC["std"], dtype=np.float32)
            + np.array(SPEC["mean"], dtype=np.float32)) * 255

@pytest.mark.parametrize("colour", [[0, 0, 0], [255, 0, 0], [0, 255, 0], [0, 0, 255], [128, 128, 128]])
def test_preprocessing_channel_order_constants(colour):
    rgb = np.full((224, 224, 3), colour, dtype=np.uint8)
    output = preprocess(rgb)
    assert output.shape == (3, 224, 224)
    assert output.dtype == np.float32 and output.flags.c_contiguous
    np.testing.assert_allclose(unnormalise(output), rgb, atol=3e-5)

@pytest.mark.parametrize("shape,upper,left", [((1, 2), 56, 0), ((2, 1), 0, 56), ((1, 3), 74, 0)])
def test_letterbox_wide_tall_odd_padding(shape, upper, left):
    output = unnormalise(preprocess(np.full((*shape, 3), 255, dtype=np.uint8))).round().astype(int)
    mask = output[:, :, 0] == 255
    yy, xx = np.where(mask)
    assert yy.min() == upper and xx.min() == left
    assert (224 - yy.max() - 1) - upper in (0, 1)
    assert (224 - xx.max() - 1) - left in (0, 1)
    assert np.all(output[~mask] == 128)

def test_preprocessing_half_pixel_bilinear_edge_and_half_up_rounding():
    rgb = np.array([[[0, 10, 100], [255, 30, 0]]], dtype=np.uint8)
    output = unnormalise(preprocess(rgb)).round().astype(int)
    assert output[56, 0].tolist() == [0, 10, 100]
    assert output[56, -1].tolist() == [255, 30, 0]
    expected = np.floor(rgb[0, 0] * (1 - 0.5044642857142857)
                        + rgb[0, 1] * 0.5044642857142857 + 0.5).astype(int)
    assert output[56, 112].tolist() == expected.tolist()

@pytest.mark.parametrize("image", [np.zeros((0, 1, 3), np.uint8), np.zeros((1, 1, 4), np.uint8),
                                  np.zeros((1, 1, 3), np.float32), np.zeros((4097, 1, 3), np.uint8)])
def test_preprocessing_rejects_invalid_or_excessive_input(image):
    with pytest.raises(ValueError, match="bounded"):
        preprocess(image)

def test_missing_and_corrupt_pretrained_files_fail_before_any_download(tmp_path):
    with pytest.raises(ValueError, match="checksum"):
        verify_checkpoint(tmp_path)
    (tmp_path / "README.md").write_bytes(b"bad")
    with pytest.raises(ValueError, match="checksum"):
        acquire(tmp_path)
    assert not (tmp_path / "model.safetensors").exists()
    assert all(len(digest) == 64 for _, digest in FILES.values())

def test_ignored_path_rejects_escape_and_symlink_parent(tmp_path):
    repo = tmp_path / "repo"
    (repo / "data").mkdir(parents=True)
    outside = tmp_path / "outside"
    outside.mkdir()
    (repo / "data/link").symlink_to(outside, target_is_directory=True)
    for path in [repo / "data", repo / "data/../../escape", repo / "data/link/run"]:
        with pytest.raises(ValueError, match="ignored"):
            ignored_path(repo, path)
    assert ignored_path(repo, Path("data/run")) == repo / "data/run"

def test_environment_matches_full_hashed_platform_lock():
    repo = repository_root()
    evidence = environment(repo)
    assert len(evidence["dependencies"]) == 35
    assert evidence["dependencies"]["torch"] == "2.8.0+cpu"
    assert evidence["device"] == "cpu"
    assert len(evidence["dependency_lock_sha256"]) == 64
    assert "ml/src/numbra_ml/training.py" in evidence["source_files_sha256"]
    for line in (repo / "ml/requirements-cpu.lock").read_text().splitlines():
        if line and not line.startswith(("#", "--")):
            assert "--hash=sha256:" in line and len(line.split("sha256:")[1]) == 64

def test_cli_invalid_output_refuses_before_model_load():
    assert main(["--output", "ml/reports/forbidden"]) == 1

def test_report_writer_name_and_overwrite_guard(tmp_path):
    with pytest.raises(ValueError, match="name"):
        write_reports({}, tmp_path, "../escape")
    (tmp_path / "run.json").write_text("existing")
    with pytest.raises(ValueError, match="overwrite"):
        write_reports({}, tmp_path, "run")
    assert (tmp_path / "run.json").read_text() == "existing"


def test_generated_fixture_to_head_to_evaluation_to_written_model_card(fixture, tmp_path):
    _, index = fixture
    features = invented_features(index)
    head, training = fit_head(index, features, TrainingConfig(epochs=3))
    predictions = predict(index, features, head)
    report = evaluation_report(predictions, held_out_source=index.held_out_source)
    add_bootstrap(report, predictions, seed=20, replicates=100)
    report["training"] = training
    directory = tmp_path / "reports"
    write_reports(report, directory, "PLACEHOLDER-test")
    written = json.loads((directory / "PLACEHOLDER-test.json").read_text())
    assert written == report
    assert written["primary_operating_point"]["status"] == "unavailable_insufficient_groups"
    assert written["primary_operating_point"]["threshold"] == 0
    assert written["splits"]["test"]["bootstrap"]["overall"]["replicates"] == 100
    card = (directory / "PLACEHOLDER-test-MODEL-CARD.md").read_text()
    for phrase in ("PLACEHOLDER", "synthetic square", "synthetic circle", "pure-neural",
                   "single-class", "Single held-out source", "not calibrated", "clinical"):
        assert phrase in card
    assert "synthetic colour strata" in card
    assert "leprosy" not in json.dumps(written["target_names"])
    assert "predictions" not in written
