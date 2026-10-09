"""PLACEHOLDER diagnostics on generated training images and toy weights only."""

import json
from pathlib import Path
import tempfile

import numpy as np
import onnx
import pytest
import torch
from torch import nn

from numbra_ml.evaluation import read_component_index
from numbra_ml.export import OPTIMISATION_LEVELS, export_float, export_run, runtime, session_options
from numbra_ml.export_diagnostics import diagnose_run, feature_drift, head_sensitivity, tap_features
from numbra_ml.prepare import prepare_run, repository_root
from numbra_ml.pretrained import sha256
from numbra_ml.train import train_run
from numbra_ml.training import Baseline, FeatureHead, TrainingConfig


def toy_backbone():
    return nn.Sequential(nn.Conv2d(3, 4, 1, stride=224), nn.Flatten()).requires_grad_(False).eval()


@pytest.mark.parametrize('profile', OPTIMISATION_LEVELS)
def test_runtime_profiles_are_explicit_and_preserve_interface(tmp_path, profile):
    torch.manual_seed(42)
    model = Baseline(toy_backbone(), FeatureHead(torch.zeros(4), torch.ones(4))).eval()
    path = tmp_path / 'PLACEHOLDER-float.onnx'
    export_float(model, path)
    options = session_options(profile)
    assert options.graph_optimization_level == OPTIMISATION_LEVELS[profile]
    assert options.intra_op_num_threads == 2 and options.inter_op_num_threads == 1
    assert runtime(path, optimisation=profile).get_inputs()[0].shape == [1, 3, 224, 224]


def test_unknown_optimisation_does_not_silently_use_default():
    with pytest.raises(ValueError, match='unknown predeclared'):
        session_options('tuned')


def test_affine_attribution_uses_original_scale_and_separates_head_error():
    head = FeatureHead(torch.tensor([1., 2.]), torch.tensor([0.5, 2.])).eval()
    with torch.no_grad():
        head.linear.weight.copy_(torch.tensor([[2., -4.]]))
        head.linear.bias.zero_()
    before = np.array([[1., 2.]], dtype=np.float32)
    after = np.array([[1.5, 3.]], dtype=np.float32)
    # Effects cancel in the signed logit; bound remains conservative and nonzero.
    result = feature_drift(head, before, after, 0., 1.)
    assert result['max_feature_absolute_error'] == 1.
    assert result['mean_feature_absolute_error'] == 0.75
    assert result['affine_feature_error_bound'] == 4.
    assert result['affine_signed_feature_effect'] == 0.
    assert result['induced_python_head_absolute_error'] == 0.
    assert result['tapped_runtime_vs_python_head_absolute_error'] == 1.
    assert head_sensitivity(head)['effective_coefficient_l1'] == 6.
    assert head_sensitivity(head)['maximum_absolute_effective_coefficient'] == 4.
    for invalid in (after.astype(np.float64), after[0], np.full(after.shape, np.nan, np.float32)):
        with pytest.raises(ValueError, match='invalid diagnostic'):
            feature_drift(head, before, invalid, 0., 1.)
    with pytest.raises(ValueError, match='invalid diagnostic'):
        feature_drift(head, before, after, 0., float('inf'))


def test_feature_tap_is_separate_and_rejects_ambiguous_boundaries(tmp_path):
    model = Baseline(toy_backbone(), FeatureHead(torch.zeros(4), torch.ones(4))).eval()
    source, target = [tmp_path / name for name in ('PLACEHOLDER-original.onnx', 'PLACEHOLDER-tap.onnx')]
    export_float(model, source)
    before = sha256(source)
    name = tap_features(source, target, 4)
    assert sha256(source) == before
    graph = onnx.load(target)
    assert len(graph.graph.output) == 2
    assert graph.graph.output[1].name == name
    assert 'never bundle' in {item.key: item.value for item in graph.metadata_props}['diagnostic_notice']
    # Strict deployment interface must reject instrumented graphs.
    with pytest.raises(ValueError, match='interface mismatch'):
        runtime(target)
    graph = onnx.load(source)
    boundary = next(node for node in graph.graph.node if node.op_type == 'Sub')
    boundary.input[1] = 'head.scale'
    onnx.save(graph, source)
    with pytest.raises(ValueError, match='feature boundary'):
        tap_features(source, target, 4)


def test_complete_diagnostics_never_read_nontraining_images_and_verify_provenance():
    repo = repository_root()
    parent = repo / 'data/test-runs'
    parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=parent) as temporary:
        root = Path(temporary)
        prepared = root / 'prepared'
        prepare_run(prepared, groups_per_source=16)
        name = f'PLACEHOLDER-diagnostic-test-{root.name}'
        paths = [repo / 'ml/reports' / f'{name}{suffix}' for suffix in ('.json', '-MODEL-CARD.md')]
        try:
            train_run(repo, prepared, root / 'checkpoint', root / 'model', name=name,
                      config=TrainingConfig(epochs=3), bootstrap_replicates=100,
                      backbone_loader=lambda _: (toy_backbone(), {'notice': 'PLACEHOLDER toy; no pretraining'}))
            experiment = root / 'PLACEHOLDER-export'
            exported = export_run(repo, prepared, root / 'model', experiment, backbone_factory=toy_backbone)
            graph_paths = list(experiment.glob('*.onnx'))
            hashes = {path: sha256(path) for path in graph_paths}
            index = read_component_index(prepared / 'manifest.jsonl', prepared / 'preparation-report.json')
            # If the diagnostic opens even one non-training image, decode/hash fails.
            for component in index.components:
                if component.split != 'train':
                    (prepared / component.row.image_path).write_bytes(b'invalid nontraining image')
            output = root / 'PLACEHOLDER-diagnostic'
            result = diagnose_run(repo, prepared, root / 'model', [experiment, experiment], output,
                                  backbone_factory=toy_backbone)
            assert result['status'] == 'DIAGNOSTIC ONLY'
            assert result['protocol']['split'] == 'train'
            assert not result['protocol']['frozen_evaluation_inputs_used']
            assert len(result['artifacts']) == 2  # same original graphs deduplicated
            assert {path: sha256(path) for path in graph_paths} == hashes
            details_path = output / 'PLACEHOLDER-diagnostic-details.json'
            detail = json.loads(details_path.read_text())
            assert sha256(details_path) == result['diagnostic_details_sha256']
            train_ids = [c.id for c in index.components if c.split == 'train']
            for digest, artifact in result['artifacts'].items():
                assert len(artifact['source_experiments']) == 2
                assert set(artifact['profiles']) == set(OPTIMISATION_LEVELS)
                for profile, values in artifact['profiles'].items():
                    assert values['original_graph_training_parity']['n'] == len(train_ids)
                    assert detail['artifacts'][digest][profile]['component_ids'] == train_ids
                    assert len(detail['artifacts'][digest][profile]['feature_attribution']) == len(train_ids)
                    assert values['instrumented_attribution']['instrumentation_absolute_logit_change']['max'] >= 0
            # No per-component diagnostics leak into the tracked-safe aggregate.
            assert 'failure_cases' not in json.dumps(result)
            assert 'component_ids"' not in json.dumps(result)
            assert 'python_logits' not in json.dumps(result)
            assert json.loads((output / 'PLACEHOLDER-diagnostic-report.json').read_text()) == result
            with pytest.raises(ValueError, match='new and named'):
                diagnose_run(repo, prepared, root / 'model', [experiment], output, backbone_factory=toy_backbone)
            with pytest.raises(ValueError, match='ignored data'):
                diagnose_run(repo, prepared, root / 'model', [experiment], repo / 'docs/unsafe', backbone_factory=toy_backbone)
            with pytest.raises(ValueError, match='retained export'):
                diagnose_run(repo, prepared, root / 'model', [], root / 'PLACEHOLDER-empty', backbone_factory=toy_backbone)
            report_path = experiment / 'PLACEHOLDER-export-report.json'
            altered = json.loads(report_path.read_text())
            altered['interface']['threshold'] += 0.01
            report_path.write_text(json.dumps(altered))
            with pytest.raises(ValueError, match='provenance mismatch'):
                diagnose_run(repo, prepared, root / 'model', [experiment], root / 'PLACEHOLDER-bad-fit', backbone_factory=toy_backbone)
            assert not (root / 'PLACEHOLDER-bad-fit').exists()
            report_path.write_text(json.dumps(exported))
            graph = onnx.load(experiment / 'PLACEHOLDER-int8.onnx')
            onnx.helper.set_model_props(graph, {'notice': 'PLACEHOLDER tampered'})
            onnx.save(graph, experiment / 'PLACEHOLDER-int8.onnx')
            with pytest.raises(ValueError, match='checksum/report mismatch'):
                diagnose_run(repo, prepared, root / 'model', [experiment], root / 'PLACEHOLDER-bad-graph', backbone_factory=toy_backbone)
            assert not (root / 'PLACEHOLDER-bad-graph').exists()
        finally:
            for path in paths:
                path.unlink(missing_ok=True)
