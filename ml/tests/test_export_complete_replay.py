"""PLACEHOLDER complete-layer scope, arithmetic accounting and isolation tests."""

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
from numbra_ml.export_complete_replay import (audit_affine_graph, audit_complete_report, audit_native_graph,
    complete_operators, signed_accounting)
from numbra_ml.export_precision import AFFINE_FORMULAS, promoted_affine_graph
from numbra_ml.export_replay import replay_diagnostics, replay_run
from numbra_ml.prepare import prepare_run, repository_root
from numbra_ml.pretrained import sha256
from numbra_ml.train import train_run
from numbra_ml.training import Baseline, FeatureHead, TrainingConfig, tensor_hash
from test_export_replay import toy_model
from test_export_precision import source_model


def complete_backbone():
    return nn.Sequential(nn.Conv2d(3, 4, 1, stride=224),
        BatchNormAct2d(4, act_layer='hard_swish', inplace=True),
        nn.Conv2d(4, 4, 1, groups=4), BatchNormAct2d(4, act_layer='relu', inplace=True),
        nn.Conv2d(4, 4, 1, groups=2, bias=False), nn.BatchNorm2d(4), nn.ReLU(inplace=True),
        nn.Conv2d(4, 4, 1), nn.Flatten()).requires_grad_(False).eval()


def complete_model():
    torch.manual_seed(149)
    torch.set_num_threads(2)
    return Baseline(complete_backbone(), FeatureHead(torch.zeros(4), torch.ones(4))).eval()


def test_complete_scope_includes_grouped_conv_and_conv_without_following_bn(tmp_path):
    model = complete_model()
    source = tmp_path / 'PLACEHOLDER-source.onnx'
    export_preserving_batchnorm(model, source)
    graph = onnx.load(source)
    chosen = complete_operators(model, graph)
    assert [name for name, _, _ in chosen] == [f'backbone.{i}' for i in (0, 1, 2, 3, 4, 5, 7)]
    assert [node.op_type for _, _, node in chosen].count('Conv') == 4
    node = onnx.NodeProto()
    node.CopyFrom(chosen[-1][2])
    node.output[0] = 'extra-conv'
    graph.graph.node.append(node)
    with pytest.raises(ValueError, match='one-to-one'):
        complete_operators(model, graph)


@pytest.mark.parametrize('corruption', ['weight', 'signed_zero', 'group', 'padding', 'epsilon', 'mode', 'duplicate'])
def test_complete_rejects_saved_parameter_geometry_and_ambiguity(tmp_path, corruption):
    model = toy_model()
    source = tmp_path / 'PLACEHOLDER-source.onnx'
    export_preserving_batchnorm(model, source)
    graph = onnx.load(source)
    if corruption in ('weight', 'signed_zero'):
        if corruption == 'signed_zero':
            with torch.no_grad():
                model.backbone[0].weight.flatten()[0] = 0.
            export_preserving_batchnorm(model, source)
            graph = onnx.load(source)
            with torch.no_grad():
                model.backbone[0].weight.flatten()[0] = -0.
        else:
            with torch.no_grad():
                model.backbone[0].weight.add_(1.)
        expected = 'parameter bits'
    else:
        node = next(n for n in graph.graph.node if n.op_type == ('BatchNormalization' if corruption in ('epsilon', 'mode') else 'Conv'))
        if corruption == 'duplicate':
            graph.graph.node.append(node)
            expected = 'one saved boundary'
        else:
            key, value = {'group': ('group', 2), 'padding': ('pads', [1, 1, 1, 1]),
                          'epsilon': ('epsilon', 0.2), 'mode': ('training_mode', 1)}[corruption]
            retained = [a for a in node.attribute if a.name != key]
            del node.attribute[:]
            node.attribute.extend(retained + [onnx.helper.make_attribute(key, value)])
            expected = 'geometry' if corruption in ('group', 'padding') else 'epsilon/mode'
    with pytest.raises(ValueError, match=expected):
        complete_operators(model, graph)


def test_complete_replay_all_layers_both_origins_accounting_and_cleanup(tmp_path):
    model = complete_model()
    before = tensor_hash(model.state_dict())
    source = tmp_path / 'PLACEHOLDER-source.onnx'
    export_preserving_batchnorm(model, source)
    summary, details = replay_diagnostics(model, source, tmp_path, stress_inputs()[:2], promoted=True, complete=True)
    assert summary['operator_counts'] == {'Conv': 4, 'BatchNormalization': 3}
    assert len(summary['operators']) == 7
    assert summary['instrumentation_absolute_logit_change']['max'] == 0
    for name, errors in summary['operators'].items():
        assert errors['python_replay_fidelity']['max_absolute_error']['max'] == 0
        assert errors['onnx_replay_fidelity']['max_absolute_error']['max'] == 0
        assert errors['signed_accounting']['telescoping_max_residual']['max'] == 0
        assert set(errors['signed_accounting']['terms']) == {'python_replay', 'propagation', 'kernel', 'extraction'}
        graphs = summary['operator_graphs'][name]
        assert all(a['status'] == 'PASS' for a in graphs['native_audits'].values())
        if graphs['original_operator'] == 'BatchNormalization':
            assert set(graphs['promoted_graphs']) == set(AFFINE_FORMULAS)
            assert set(errors['promoted']) == {'python_input', 'onnx_input'}
            for origin in errors['promoted'].values():
                for result in origin.values():
                    assert result['onnx_vs_python_promoted']['max_absolute_error']['max'] == 0
            for record in graphs['promoted_graphs'].values():
                assert all(a['status'] == 'PASS' for a in record['audits'].values())
        else:
            assert 'promoted' not in errors and 'promoted_graphs' not in graphs
    assert details['component_ids'] == [name for name, _ in stress_inputs()[:2]]
    assert tensor_hash(model.state_dict()) == before
    assert not any(m._forward_hooks or m._forward_pre_hooks for m in model.modules())
    def broken_inputs():
        raise RuntimeError('complete replay injected failure')
        yield
    with pytest.raises(RuntimeError, match='injected failure'):
        replay_diagnostics(model, source, tmp_path, broken_inputs(), promoted=True, complete=True)
    assert not any(m._forward_hooks or m._forward_pre_hooks for m in model.modules())
    assert tensor_hash(model.state_dict()) == before


def test_signed_accounting_keeps_separate_signed_terms_with_cancellation():
    arrays = [np.array(value, np.float32).reshape(1, 1, 1, 2) for value in
              ([1., 3.], [2., 1.], [3., -2.], [1., 4.], [2., 3.])]
    result = signed_accounting(*arrays)
    assert result['terms']['python_replay']['signed_min'] == -2
    assert result['terms']['kernel']['signed_min'] == -2
    assert result['terms']['kernel']['signed_max'] == 6
    assert result['terms']['propagation']['signed_mean'] == -1
    assert result['total']['max_absolute'] == 1
    assert sum(term['max_absolute'] for term in result['terms'].values()) > result['total']['max_absolute']
    assert result['telescoping_max_residual'] == 0
    with pytest.raises(ValueError, match='shape mismatch'):
        signed_accounting(arrays[0][..., :1], *arrays[1:])


def test_complete_replay_refuses_partial_recipe_protocol(tmp_path):
    with pytest.raises(ValueError, match='both promoted BN recipes'):
        replay_diagnostics(complete_model(), tmp_path / 'missing.onnx', tmp_path, [], complete=True)


@pytest.mark.parametrize('formula', AFFINE_FORMULAS)
@pytest.mark.parametrize('corruption', ['cast', 'coefficient', 'extra_node'])
def test_promoted_audit_rejects_runtime_arithmetic_and_coefficient_corruption(tmp_path, formula, corruption):
    module = toy_model().backbone[1]
    path = tmp_path / 'PLACEHOLDER-affine.onnx'
    promoted_affine_graph(module, [1, 4, 1, 1], formula, source_model(), path)
    assert audit_affine_graph(module, formula, path)['status'] == 'PASS'
    graph = onnx.load(path)
    if corruption == 'cast':
        graph.graph.node[0].attribute[0].i = onnx.TensorProto.FLOAT
        expected = 'arithmetic/cast'
    elif corruption == 'extra_node':
        graph.graph.node.append(onnx.helper.make_node('Identity', ['y'], ['extra']))
        expected = 'arithmetic/cast scope'
    else:
        array = onnx.numpy_helper.to_array(graph.graph.initializer[0]).copy()
        array.flat[0] += 1
        graph.graph.initializer[0].CopyFrom(onnx.numpy_helper.from_array(array, 'alpha'))
        expected = 'coefficient bits'
    onnx.save(graph, path)
    with pytest.raises(ValueError, match=expected):
        audit_affine_graph(module, formula, path)


def test_native_runtime_audit_rejects_extra_computation(tmp_path):
    model = complete_model()
    source = tmp_path / 'PLACEHOLDER-source.onnx'
    export_preserving_batchnorm(model, source)
    replay_diagnostics(model, source, tmp_path, stress_inputs()[:1], promoted=True, complete=True)
    path = tmp_path / 'PLACEHOLDER-operator-0-optimized.onnx'
    graph = onnx.load(path)
    graph.graph.node.append(onnx.helper.make_node('Relu', [graph.graph.output[0].name], ['extra']))
    onnx.save(graph, path)
    with pytest.raises(ValueError, match='scope/interface'):
        audit_native_graph(model.backbone[0], path)


def test_complete_pipeline_uses_only_training_and_preserves_evidence():
    repo = repository_root()
    parent = repo / 'data/test-runs'
    parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=parent) as temporary:
        root = Path(temporary)
        prepared, run = root / 'prepared', root / 'model'
        prepare_run(prepared, groups_per_source=16)
        name = f'PLACEHOLDER-complete-test-{root.name}'
        reports = [repo / 'ml/reports' / f'{name}{suffix}' for suffix in ('.json', '-MODEL-CARD.md')]
        try:
            train_run(repo, prepared, root / 'checkpoint', run, name=name,
                config=TrainingConfig(epochs=3), bootstrap_replicates=100,
                backbone_loader=lambda _: (complete_backbone(), {'notice': 'PLACEHOLDER toy; no pretraining'}))
            experiment, preserved = root / 'PLACEHOLDER-export', root / 'PLACEHOLDER-preserved'
            export_run(repo, prepared, run, experiment, backbone_factory=complete_backbone)
            batchnorm_run(repo, prepared, run, [experiment], preserved, backbone_factory=complete_backbone)
            hashes = {path: sha256(path) for folder in (run, experiment, preserved)
                      for path in folder.rglob('*') if path.is_file()}
            index = read_component_index(prepared / 'manifest.jsonl', prepared / 'preparation-report.json')
            for component in index.components:
                if component.split != 'train':
                    (prepared / component.row.image_path).write_bytes(b'unreadable frozen image')
            output = root / 'PLACEHOLDER-complete'
            result = replay_run(repo, prepared, run, [experiment], preserved, output,
                                backbone_factory=complete_backbone, promoted=True, complete=True)
            assert result['protocol']['decision'] == 'ADR-019'
            assert result['protocol']['promoted_strategies']['stem'] == 'none; native Conv replay only'
            assert not any(result['protocol'][key] for key in
                           ('frozen_evaluation_inputs_used', 'quantisation_fit', 'deployment_selection'))
            assert result['diagnostics']['operator_counts'] == {'Conv': 4, 'BatchNormalization': 3}
            detail = output / 'PLACEHOLDER-complete-replay-details.json'
            assert json.loads(detail.read_text())['component_ids'] == [item.id for item in index.components if item.split == 'train']
            assert sha256(detail) == result['diagnostic_details_sha256']
            assert {path: sha256(path) for path in hashes} == hashes
            assert result['model_state_before_sha256'] == result['model_state_after_sha256']
            assert json.loads((output / 'PLACEHOLDER-complete-replay-report.json').read_text()) == result
            audit = audit_complete_report(repo, output, result)
            assert audit['status'] == 'PASS' and audit['operators'] == 7
            assert audit['graph_records_checked'] == 47  # 3 taps + 14 native + 18 primitive + 12 promoted
            original_details = detail.read_text()
            detail.write_text('{}')
            with pytest.raises(ValueError, match='detail checksum'):
                audit_complete_report(repo, output, result)
            detail.write_text(original_details)
            altered = json.loads(json.dumps(result))
            altered['diagnostics']['operators']['backbone.0']['signed_accounting']['total']['max_absolute']['max'] += 1
            with pytest.raises(ValueError, match='aggregate reconstruction'):
                audit_complete_report(repo, output, altered)
            altered = json.loads(json.dumps(result))
            altered['environment']['source_tree_sha256'] = '0' * 64
            with pytest.raises(ValueError, match='source/dependency'):
                audit_complete_report(repo, output, altered)
            graph_path = output / 'PLACEHOLDER-operator-0-optimized.onnx'
            graph_bytes = graph_path.read_bytes()
            graph_path.write_bytes(b'invalid graph')
            with pytest.raises(ValueError, match='graph checksum/report'):
                audit_complete_report(repo, output, result)
            graph_path.write_bytes(graph_bytes)
            for private in ('component_ids"', 'python_logit"', 'rows"'):
                assert private not in json.dumps(result)
            report_path = preserved / 'PLACEHOLDER-batchnorm-report.json'
            stale = json.loads(report_path.read_text())
            stale['protocol']['temperature'] += 0.1
            report_path.write_text(json.dumps(stale))
            with pytest.raises(ValueError, match='provenance mismatch'):
                replay_run(repo, prepared, run, [experiment], preserved, root / 'PLACEHOLDER-stale',
                           backbone_factory=complete_backbone, promoted=True, complete=True)
            assert not (root / 'PLACEHOLDER-stale').exists()
        finally:
            for path in reports:
                path.unlink(missing_ok=True)
