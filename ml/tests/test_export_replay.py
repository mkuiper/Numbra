"""Generated PLACEHOLDER stem/depthwise kernels; no external images or weights."""

import json
from pathlib import Path
import tempfile

import numpy as np
import onnx
import pytest
import torch
from torch import nn
from timm.layers import BatchNormAct2d

from numbra_ml.evaluation import read_component_index
from numbra_ml.export import export_run, stress_inputs
from numbra_ml.export_batchnorm import batchnorm_run, export_preserving_batchnorm
from numbra_ml.export_replay import (FORMULAS, bn_constants, difference,
    double_formula, formula_graph, operator_session, python_formula,
    python_operator, replay_diagnostics, replay_run, run_operator, selected_operators)
from numbra_ml.prepare import prepare_run, repository_root
from numbra_ml.pretrained import sha256
from numbra_ml.train import train_run
from numbra_ml.training import Baseline, FeatureHead, TrainingConfig, tensor_hash


def toy_backbone():
    return nn.Sequential(nn.Conv2d(3, 4, 1, stride=224),
        BatchNormAct2d(4, act_layer='hard_swish', inplace=True),
        nn.Conv2d(4, 4, 1, groups=4), BatchNormAct2d(4, act_layer='relu', inplace=True),
        nn.Flatten()).requires_grad_(False).eval()


def toy_model():
    torch.manual_seed(931)
    torch.set_num_threads(2)
    model = Baseline(toy_backbone(), FeatureHead(torch.zeros(4), torch.ones(4))).eval()
    with torch.no_grad():
        for module in model.modules():
            if isinstance(module, nn.BatchNorm2d):
                module.running_mean.copy_(torch.tensor([0.5, -1., 2., -3.]))
                module.running_var.copy_(torch.tensor([0.2, 0.5, 2., 3.]))
                module.weight.copy_(torch.tensor([0.3, 0.7, 1.1, 1.3]))
                module.bias.copy_(torch.tensor([-1., 2., -3., 0.7]))
    return model


def test_selection_by_order_and_immediate_connectivity(tmp_path):
    model = toy_model()
    source = tmp_path / 'PLACEHOLDER-preserved.onnx'
    export_preserving_batchnorm(model, source)
    graph = onnx.load(source)
    chosen = selected_operators(model, graph)
    assert [name for name, _, _ in chosen] == ['backbone.0', 'backbone.1', 'backbone.2', 'backbone.3']
    assert [node.op_type for _, _, node in chosen] == ['Conv', 'BatchNormalization'] * 2
    chosen[-1][2].input[0] = 'wrong.connection'
    with pytest.raises(ValueError, match='immediately following'):
        selected_operators(model, graph)
    model.backbone[2].groups = 1
    with pytest.raises(ValueError, match='distinct first stem and depthwise'):
        selected_operators(model, onnx.load(source))


def test_same_inputs_replay_fidelity_pre_activation_and_cleanup(tmp_path):
    model = toy_model()
    before = tensor_hash(model.state_dict())
    source = tmp_path / 'PLACEHOLDER-preserved.onnx'
    export_preserving_batchnorm(model, source)
    summary, details = replay_diagnostics(model, source, tmp_path, stress_inputs()[:3])
    assert summary['components'] == 3
    assert details['component_ids'] == [name for name, _ in stress_inputs()[:3]]
    assert summary['instrumentation_absolute_logit_change']['max'] == 0
    for name, stats in summary['operators'].items():
        assert stats['python_replay_fidelity']['max_absolute_error']['max'] == 0
        assert stats['onnx_replay_fidelity']['max_absolute_error']['max'] == 0
        assert stats['telescoping_max_residual']['max'] == 0
        assert stats['local_kernel_on_python_input']['max_absolute_error']['max'] < 1e-5
        assert summary['operator_graphs'][name]['input_shape'][0] == 1
        if 'formulas' in stats:
            assert set(stats['formulas']) == {'python_input', 'onnx_input'}
            assert set(stats['formulas']['python_input']) == set(FORMULAS) | {'float64_rounded_vs_native'}
            assert summary['operator_graphs'][name]['graph']['operators']['BatchNormalization'] == 1
        else:
            assert summary['operator_graphs'][name]['graph']['operators']['Conv'] == 1
    assert tensor_hash(model.state_dict()) == before
    assert not any(m._forward_hooks or m._forward_pre_hooks for m in model.modules())
    for path in tmp_path.glob('*.onnx'):
        metadata = {item.key: item.value for item in onnx.load(path).metadata_props}
        assert metadata['diagnostic_notice'].endswith('never bundle')
    def bad_inputs():
        raise RuntimeError('injected replay input failure')
        yield
    with pytest.raises(RuntimeError, match='injected replay'):
        replay_diagnostics(model, source, tmp_path, bad_inputs())
    assert not any(m._forward_hooks or m._forward_pre_hooks for m in model.modules())
    assert tensor_hash(model.state_dict()) == before


@pytest.mark.parametrize('formula', FORMULAS)
def test_primitive_bn_graphs_use_saved_buffers_and_match_python(tmp_path, formula):
    module = toy_model().backbone[1]
    before = tensor_hash(module.state_dict())
    value = np.array([-7., -2., 1., 9.], np.float32).reshape(1, 4, 1, 1)
    source_path = tmp_path / 'PLACEHOLDER-source.onnx'
    export_preserving_batchnorm(toy_model(), source_path)
    path, optimized = [tmp_path / f'PLACEHOLDER-{name}.onnx' for name in ('formula', 'optimized')]
    formula_graph(module, list(value.shape), formula, onnx.load(source_path), path)
    candidate = run_operator(operator_session(path, optimized), value)
    np.testing.assert_array_equal(candidate, python_formula(module, value, formula))
    assert 'BatchNormalization' not in {node.op_type for node in onnx.load(optimized).graph.node}
    assert difference(python_operator(module, value), candidate)['max_absolute_error'] < 1e-5
    assert double_formula(module, value).dtype == np.float32
    assert tensor_hash(module.state_dict()) == before
    with pytest.raises(ValueError, match='unknown declared'):
        bn_constants(module, 'unplanned')
    with pytest.raises(ValueError, match='finite float32'):
        python_operator(module, value.astype(np.float64))
    with pytest.raises(ValueError, match='shape mismatch'):
        difference(value, value[..., :0])


def test_replay_pipeline_training_only_and_rejects_stale_provenance():
    repo = repository_root()
    parent = repo / 'data/test-runs'
    parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=parent) as temporary:
        root = Path(temporary)
        prepared, run = root / 'prepared', root / 'model'
        prepare_run(prepared, groups_per_source=16)
        name = f'PLACEHOLDER-replay-test-{root.name}'
        reports = [repo / 'ml/reports' / f'{name}{suffix}' for suffix in ('.json', '-MODEL-CARD.md')]
        try:
            train_run(repo, prepared, root / 'checkpoint', run, name=name,
                config=TrainingConfig(epochs=3), bootstrap_replicates=100,
                backbone_loader=lambda _: (toy_backbone(), {'notice': 'PLACEHOLDER toy; no pretraining'}))
            experiment, preserved = root / 'PLACEHOLDER-export', root / 'PLACEHOLDER-preserved'
            export_run(repo, prepared, run, experiment, backbone_factory=toy_backbone)
            batchnorm_run(repo, prepared, run, [experiment], preserved, backbone_factory=toy_backbone)
            protected = list(run.iterdir()) + list(experiment.iterdir()) + list(preserved.rglob('*.onnx'))
            hashes = {path: sha256(path) for path in protected if path.is_file()}
            index = read_component_index(prepared / 'manifest.jsonl', prepared / 'preparation-report.json')
            for component in index.components:
                if component.split != 'train':
                    (prepared / component.row.image_path).write_bytes(b'bad nontraining pixels')
            output = root / 'PLACEHOLDER-replay'
            result = replay_run(repo, prepared, run, [experiment], preserved, output, backbone_factory=toy_backbone)
            train_ids = [item.id for item in index.components if item.split == 'train']
            assert result['status'] == 'DIAGNOSTIC ONLY'
            assert result['protocol']['components'] == len(train_ids)
            assert not result['protocol']['frozen_evaluation_inputs_used']
            assert not result['protocol']['quantisation_fit'] and not result['protocol']['deployment_selection']
            assert result['model_state_before_sha256'] == result['model_state_after_sha256']
            detail = output / 'PLACEHOLDER-replay-details.json'
            assert json.loads(detail.read_text())['component_ids'] == train_ids
            assert sha256(detail) == result['diagnostic_details_sha256']
            assert {path: sha256(path) for path in hashes} == hashes
            assert json.loads((output / 'PLACEHOLDER-replay-report.json').read_text()) == result
            for private in ('component_ids"', 'python_logit"', 'rows"'):
                assert private not in json.dumps(result)
            with pytest.raises(ValueError, match='new and named'):
                replay_run(repo, prepared, run, [experiment], preserved, output, backbone_factory=toy_backbone)
            with pytest.raises(ValueError, match='ignored data'):
                replay_run(repo, prepared, run, [experiment], preserved, repo / 'docs/unsafe', backbone_factory=toy_backbone)
            with pytest.raises(ValueError, match='retained export'):
                replay_run(repo, prepared, run, [], preserved, root / 'PLACEHOLDER-empty', backbone_factory=toy_backbone)
            report_path = preserved / 'PLACEHOLDER-batchnorm-report.json'
            original_report = report_path.read_text()
            altered = json.loads(original_report)
            altered['protocol']['temperature'] += 0.1
            report_path.write_text(json.dumps(altered))
            with pytest.raises(ValueError, match='provenance mismatch'):
                replay_run(repo, prepared, run, [experiment], preserved, root / 'PLACEHOLDER-stale', backbone_factory=toy_backbone)
            assert not (root / 'PLACEHOLDER-stale').exists()
            report_path.write_text(original_report)
            altered = json.loads(original_report)
            altered['boundary_diagnostics'] = {'status': 'INVALID'}
            report_path.write_text(json.dumps(altered))
            with pytest.raises(ValueError, match='valid boundary evidence'):
                replay_run(repo, prepared, run, [experiment], preserved, root / 'PLACEHOLDER-invalid-boundary', backbone_factory=toy_backbone)
            assert not (root / 'PLACEHOLDER-invalid-boundary').exists()
            report_path.write_text(original_report)
            graph_path = preserved / 'PLACEHOLDER-preserved.onnx'
            original_graph = graph_path.read_bytes()
            changed = onnx.load(graph_path)
            onnx.helper.set_model_props(changed, {'notice': 'PLACEHOLDER changed graph'})
            onnx.save(changed, graph_path)
            with pytest.raises(ValueError, match='checksum/report mismatch'):
                replay_run(repo, prepared, run, [experiment], preserved, root / 'PLACEHOLDER-bad-graph', backbone_factory=toy_backbone)
            assert not (root / 'PLACEHOLDER-bad-graph').exists()
            graph_path.write_bytes(original_graph)
            (preserved / 'PLACEHOLDER-batchnorm-details.json').write_text('{}')
            with pytest.raises(ValueError, match='checksum/report mismatch'):
                replay_run(repo, prepared, run, [experiment], preserved, root / 'PLACEHOLDER-bad-detail', backbone_factory=toy_backbone)
            assert not (root / 'PLACEHOLDER-bad-detail').exists()
        finally:
            for path in reports:
                path.unlink(missing_ok=True)
