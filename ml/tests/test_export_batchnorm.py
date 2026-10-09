"""Generated PLACEHOLDER data/weights; preserve BN and audit actual ORT graphs."""

import json
from pathlib import Path
import tempfile

import onnx
import pytest
import torch
from torch import nn
from timm.layers import BatchNormAct2d

from numbra_ml.evaluation import read_component_index
from numbra_ml.export import export_float, export_run, graph_report, runtime, stress_inputs
from numbra_ml.export_batchnorm import (assert_batchnorm, batchnorm_run, boundaries,
    boundary_diagnostics, export_preserving_batchnorm)
from numbra_ml.prepare import prepare_run, repository_root
from numbra_ml.pretrained import sha256
from numbra_ml.train import train_run
from numbra_ml.training import Baseline, FeatureHead, TrainingConfig, tensor_hash


def toy_backbone():
    return nn.Sequential(nn.Conv2d(3, 4, 1, stride=224), nn.BatchNorm2d(4),
                         nn.Flatten()).requires_grad_(False).eval()


def toy_model():
    torch.manual_seed(42)
    model = Baseline(toy_backbone(), FeatureHead(torch.zeros(4), torch.ones(4))).eval()
    # Non-identity BN so the test does not rely on removal of a no-op transform.
    with torch.no_grad():
        model.backbone[1].running_mean.copy_(torch.tensor([0.5, -1., 2., -3.]))
        model.backbone[1].running_var.copy_(torch.tensor([0.2, 0.5, 2., 3.]))
        model.backbone[1].weight.copy_(torch.tensor([0.3, 0.7, 1.1, 1.3]))
    return model


def test_preserved_export_keeps_eval_state_and_disabled_runtime_bn(tmp_path):
    model = toy_model()
    before = tensor_hash(model.state_dict())
    folded, preserved = [tmp_path / f'PLACEHOLDER-{name}.onnx' for name in ('folded', 'preserved')]
    export_float(model, folded)
    count = export_preserving_batchnorm(model, preserved)
    assert count == 1 and tensor_hash(model.state_dict()) == before
    assert all(not module.training for module in model.modules())
    assert graph_report(folded)['operators'].get('BatchNormalization', 0) == 0
    assert graph_report(preserved)['operators']['BatchNormalization'] == 1
    assert_batchnorm(onnx.load(preserved), 1)
    assert {item.key: item.value for item in onnx.load(preserved).metadata_props}['diagnostic_notice'].endswith('never bundle')
    for profile, expected in (('disabled', 1), ('all', 0)):
        optimized = tmp_path / f'PLACEHOLDER-{profile}-optimized.onnx'
        session = runtime(preserved, optimisation=profile, optimized_path=optimized)
        assert len(session.get_outputs()) == 1
        assert graph_report(optimized)['operators'].get('BatchNormalization', 0) == expected
    graph = onnx.load(preserved)
    bn = next(node for node in graph.graph.node if node.op_type == 'BatchNormalization')
    bn.attribute.append(onnx.helper.make_attribute('training_mode', 1))
    with pytest.raises(ValueError, match='inference mode'):
        assert_batchnorm(graph, 1)
    with pytest.raises(ValueError, match='node count'):
        assert_batchnorm(onnx.load(folded), 1)


def test_preserved_export_refuses_training_mode_or_absent_bn(tmp_path):
    path = tmp_path / 'PLACEHOLDER-preserved.onnx'
    model = toy_model()
    model.backbone[1].train()
    with pytest.raises(ValueError, match='every module in eval'):
        export_preserving_batchnorm(model, path)
    assert not path.exists()
    model.backbone = nn.Sequential(nn.Conv2d(3, 4, 1, stride=224), nn.Flatten()).eval()
    with pytest.raises(ValueError, match='requires saved BatchNorm'):
        export_preserving_batchnorm(model, path)


def test_all_boundary_taps_match_saved_weights_and_cleanup_hooks(tmp_path):
    model = toy_model()
    before = tensor_hash(model.state_dict())
    path = tmp_path / 'PLACEHOLDER-preserved.onnx'
    export_preserving_batchnorm(model, path)
    summary, details = boundary_diagnostics(model, path, tmp_path, stress_inputs()[:3])
    assert list(summary['boundaries']) == ['backbone.0', 'backbone.1']
    assert summary['boundaries']['backbone.0']['operator'] == 'Conv'
    assert summary['boundaries']['backbone.1']['operator'] == 'BatchNormalization'
    assert summary['runtime_graph']['operators']['BatchNormalization'] == 1
    assert summary['components'] == 3 and len(details['rows']) == 3
    for name in summary['boundaries']:
        assert summary['boundaries'][name]['max_absolute_error'] >= 0
        assert summary['boundaries'][name]['shape'] == [1, 4, 1, 1]
    assert not any(module._forward_hooks for module in model.modules())
    assert tensor_hash(model.state_dict()) == before
    graph = onnx.load(path)
    next(node for node in graph.graph.node if node.op_type == 'Conv').input[1] = 'swapped.weight'
    with pytest.raises(ValueError, match='expected one saved boundary'):
        boundaries(model, graph)
    def bad_inputs():
        raise RuntimeError('injected input failure')
        yield  # keeps the failure inside the iteration, after hooks are installed
    with pytest.raises(RuntimeError, match='injected input failure'):
        boundary_diagnostics(model, path, tmp_path, bad_inputs())
    assert not any(module._forward_hooks for module in model.modules())
    assert tensor_hash(model.state_dict()) == before


@pytest.mark.parametrize('activation', ['relu', 'hard_swish'])
def test_combined_batchnorm_activation_taps_raw_norm_before_inplace_activation(tmp_path, activation):
    model = toy_model()
    model.backbone[1] = BatchNormAct2d(4, act_layer=activation, inplace=True).eval()
    with torch.no_grad():
        model.backbone[0].weight.zero_()
        model.backbone[0].bias.fill_(-2.)
    before = tensor_hash(model.state_dict())
    path = tmp_path / 'PLACEHOLDER-combined.onnx'
    export_preserving_batchnorm(model, path)
    summary, details = boundary_diagnostics(model, path, tmp_path, stress_inputs()[:1])
    norm = summary['boundaries']['backbone.1']
    assert norm['python_capture'] == 'BatchNormAct2d.drop input before activation'
    # Raw norm is nearly -2; post-ReLU is 0 (post-HardSwish about -1/3).
    # A module-output hook produces a huge false difference here.
    assert norm['max_absolute_error'] < 1e-5
    assert details['rows'][0]['boundaries']['backbone.1']['max_absolute_error'] < 1e-5
    assert summary['instrumentation_absolute_logit_change']['max'] == 0
    assert tensor_hash(model.state_dict()) == before
    assert not any(m._forward_hooks or m._forward_pre_hooks for m in model.modules())


def test_complete_training_only_batchnorm_provenance_and_no_pixel_leakage():
    repo = repository_root()
    parent = repo / 'data/test-runs'
    parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=parent) as temporary:
        root = Path(temporary)
        prepared = root / 'prepared'
        prepare_run(prepared, groups_per_source=16)
        name = f'PLACEHOLDER-batchnorm-test-{root.name}'
        paths = [repo / 'ml/reports' / f'{name}{suffix}' for suffix in ('.json', '-MODEL-CARD.md')]
        try:
            train_run(repo, prepared, root / 'checkpoint', root / 'model', name=name,
                config=TrainingConfig(epochs=3), bootstrap_replicates=100,
                backbone_loader=lambda _: (toy_backbone(), {'notice': 'PLACEHOLDER toy; no pretraining'}))
            experiment = root / 'PLACEHOLDER-export'
            exported = export_run(repo, prepared, root / 'model', experiment, backbone_factory=toy_backbone)
            original_paths = list(experiment.glob('*.onnx')) + list((root / 'model').iterdir())
            hashes = {path: sha256(path) for path in original_paths}
            index = read_component_index(prepared / 'manifest.jsonl', prepared / 'preparation-report.json')
            for component in index.components:
                if component.split != 'train':
                    (prepared / component.row.image_path).write_bytes(b'bad nontraining pixels')
            output = root / 'PLACEHOLDER-batchnorm'
            result = batchnorm_run(repo, prepared, root / 'model', [experiment], output,
                                   backbone_factory=toy_backbone)
            assert result['status'] == 'DIAGNOSTIC ONLY'
            assert result['protocol']['expected_batchnorm_nodes'] == 1
            assert not result['protocol']['frozen_evaluation_inputs_used']
            assert not result['protocol']['quantisation_fit']
            assert result['folded_control_matches_retained_float']
            assert result['model_state_before_sha256'] == result['model_state_after_sha256']
            assert {path: sha256(path) for path in original_paths} == hashes
            detail_path = output / 'PLACEHOLDER-batchnorm-details.json'
            details = json.loads(detail_path.read_text())
            assert sha256(detail_path) == result['diagnostic_details_sha256']
            train_ids = [c.id for c in index.components if c.split == 'train']
            for name, artifact in result['artifacts'].items():
                assert set(artifact['profiles']) == {'disabled', 'all'}
                for profile, evidence in artifact['profiles'].items():
                    assert evidence['original_graph_training_parity']['n'] == len(train_ids)
                    assert details['artifacts'][name][profile]['component_ids'] == train_ids
                    for graph in evidence['runtime_graphs'].values():
                        expected = 1 if name == 'batchnorm_preserved' and profile == 'disabled' else 0
                        assert graph['operators'].get('BatchNormalization', 0) == expected
            for private_key in ('failure_cases', 'component_ids"', 'python_logits', 'rows"'):
                assert private_key not in json.dumps(result)
            assert json.loads((output / 'PLACEHOLDER-batchnorm-report.json').read_text()) == result
            with pytest.raises(ValueError, match='new and named'):
                batchnorm_run(repo, prepared, root / 'model', [experiment], output, backbone_factory=toy_backbone)
            with pytest.raises(ValueError, match='ignored data'):
                batchnorm_run(repo, prepared, root / 'model', [experiment], repo / 'docs/unsafe', backbone_factory=toy_backbone)
            with pytest.raises(ValueError, match='retained export'):
                batchnorm_run(repo, prepared, root / 'model', [], root / 'PLACEHOLDER-empty', backbone_factory=toy_backbone)
            report_path = experiment / 'PLACEHOLDER-export-report.json'
            altered = json.loads(report_path.read_text())
            altered['interface']['temperature'] += 0.1
            report_path.write_text(json.dumps(altered))
            with pytest.raises(ValueError, match='provenance mismatch'):
                batchnorm_run(repo, prepared, root / 'model', [experiment], root / 'PLACEHOLDER-bad-fit', backbone_factory=toy_backbone)
            assert not (root / 'PLACEHOLDER-bad-fit').exists()
            report_path.write_text(json.dumps(exported))
            altered_graph = onnx.load(experiment / 'PLACEHOLDER-float.onnx')
            onnx.helper.set_model_props(altered_graph, {'notice': 'PLACEHOLDER tampered'})
            onnx.save(altered_graph, experiment / 'PLACEHOLDER-float.onnx')
            with pytest.raises(ValueError, match='checksum/report mismatch'):
                batchnorm_run(repo, prepared, root / 'model', [experiment], root / 'PLACEHOLDER-bad-graph', backbone_factory=toy_backbone)
            assert not (root / 'PLACEHOLDER-bad-graph').exists()
        finally:
            for path in paths:
                path.unlink(missing_ok=True)
