"""Generated PLACEHOLDER preflight scope and same-input primitive regressions."""

import copy
import json
from pathlib import Path

import numpy as np
import onnx
from onnx import helper, numpy_helper
import pytest
import torch
from torch import nn

from numbra_ml.export_batchnorm import export_preserving_batchnorm
from numbra_ml.export_promoted_bn import substitute_batchnorm
from numbra_ml.export_remaining import (REMAINING, REPORT, audit_isolated, audit_preflight,
    constant, isolated_graph, main, preflight_evidence, recipe, remaining_plan, replay_isolated, validate_node)
from numbra_ml.export_rounded_bn import RECIPE
from numbra_ml.training import Baseline, FeatureHead, tensor_hash
from test_export_precision import source_model
from test_export_runtime_profiles import profile_evidence
from test_export_replay import toy_backbone


def graph_pair(tmp_path):
    torch.manual_seed(230)
    model = Baseline(nn.Sequential(nn.Conv2d(3, 4, 1, stride=224), nn.BatchNorm2d(4),
        nn.Hardswish(inplace=True), nn.AdaptiveAvgPool2d(1), nn.Flatten()),
        FeatureHead(torch.zeros(4), torch.ones(4))).requires_grad_(False).eval()
    source, rounded = tmp_path / 'PLACEHOLDER-source.onnx', tmp_path / 'PLACEHOLDER-rounded.onnx'
    export_preserving_batchnorm(model, source)
    substitute_batchnorm(model, source, rounded, rounding_recipe=RECIPE)
    return model, onnx.load(source), onnx.load(rounded)


def operands_for(op):
    x = np.array([-8., -3., -2.99, -1., -0., 0., 0.1, 2.99, 3., 8., 1e-6, -1e-6], np.float32).reshape(1, 3, 2, 2)
    kwargs = {}
    if op in ('Add', 'Sub', 'Mul', 'Div'):
        values = [x, np.array([0.1, 2., -3.], np.float32).reshape(1, 3, 1, 1)]
    elif op == 'Gemm':
        values = [x.reshape(1, -1), np.arange(24, dtype=np.float32).reshape(2, 12) / 7,
                  np.array([2., -3.], np.float32)]
        kwargs = {'transB': 1, 'alpha': 1., 'beta': 1.}
    elif op == 'Squeeze':
        values = [np.array([[2.]], np.float32), np.array([1], np.int64)]
    else:
        values = [x]
        if op == 'HardSigmoid':
            kwargs = {'alpha': float(np.float32(1 / 6))}
        elif op == 'ReduceMean':
            kwargs = {'axes': [2, 3], 'keepdims': 1}
        elif op == 'Flatten':
            kwargs = {'axis': 1}
    node = helper.make_node(op, [f'x{i}' for i in range(len(values))], ['y'], name='PLACEHOLDER-' + op, **kwargs)
    return node, values


def test_remaining_plan_covers_every_node_and_constant_without_inference(tmp_path):
    model, source, rounded = graph_pair(tmp_path)
    before = tensor_hash(model.state_dict())
    def no_forward(*args):
        raise AssertionError('baseline inference forbidden in preflight')
    model.forward = no_forward
    plan = remaining_plan(model, source, rounded)
    assert sum(plan['node_counts'].values()) == len(source.graph.node)
    assert plan['node_counts']['saved_conv_bn_control'] == 2
    assert plan['remaining_operator_counts'] == {'HardSwish': 1, 'GlobalAveragePool': 1,
        'Flatten': 1, 'Sub': 1, 'Div': 1, 'Gemm': 1, 'Squeeze': 1}
    assert [r['position'] for r in plan['nodes']] == list(range(len(source.graph.node)))
    assert len(plan['initializers']) == len(source.graph.initializer)
    assert plan['status'] == 'STATIC SCOPE ONLY'
    assert plan['remaining_native_mapping'].startswith('UNIMPLEMENTED')
    assert tensor_hash(model.state_dict()) == before


@pytest.mark.parametrize('change', ['missing', 'extra', 'order', 'attribute', 'operand', 'head_bits', 'signed_zero', 'constant_bits'])
def test_remaining_plan_rejects_changed_rounded_nodes_and_constants(tmp_path, change):
    model, source, rounded = graph_pair(tmp_path)
    node = next(n for n in rounded.graph.node if n.op_type == 'HardSwish')
    if change == 'missing':
        rounded.graph.node.remove(node)
    elif change == 'extra':
        rounded.graph.node.append(helper.make_node('Relu', [node.output[0]], ['extra'], name='extra'))
    elif change == 'order':
        # Topologically valid extra movement is still a changed ordered scope.
        constant_node = next(n for n in rounded.graph.node if n.op_type == 'Constant')
        rounded.graph.node.remove(constant_node)
        rounded.graph.node.insert(0, constant_node)
    elif change == 'attribute':
        next(n for n in rounded.graph.node if n.op_type == 'Flatten').attribute[0].i = 0
    elif change == 'operand':
        mul = next(n for n in rounded.graph.node if n.op_type == 'Div')
        mul.input.reverse()
    else:
        name = 'head.mean' if change in ('head_bits', 'signed_zero') else 'backbone.0.weight'
        producers = {output: n for n in rounded.graph.node for output in n.output}
        while name in producers and producers[name].op_type == 'Identity':
            name = producers[name].input[0]
        initializer = next(t for t in rounded.graph.initializer if t.name == name)
        array = numpy_helper.to_array(initializer).copy()
        array.flat[0] = -0. if change == 'signed_zero' else array.flat[0] + 1
        initializer.CopyFrom(numpy_helper.from_array(array, name))
    with pytest.raises((ValueError, onnx.checker.ValidationError, onnx.onnx_cpp2py_export.shape_inference.InferenceError)):
        remaining_plan(model, source, rounded)


def test_remaining_plan_binds_original_head_bits(tmp_path):
    model, source, rounded = graph_pair(tmp_path)
    with torch.no_grad():
        model.head.mean[0] = -0.
    with pytest.raises(ValueError, match='head parameter bits'):
        remaining_plan(model, source, rounded)


@pytest.mark.parametrize('change', ['unsupported', 'custom_domain', 'dead_node', 'duplicate_name', 'axes', 'head_geometry'])
def test_remaining_plan_rejects_incomplete_or_unsupported_source(tmp_path, change):
    model, source, rounded = graph_pair(tmp_path)
    node = next(n for n in source.graph.node if n.op_type == 'HardSwish')
    if change == 'unsupported':
        node.op_type = 'Sigmoid'
    elif change == 'custom_domain':
        node.domain = 'untrusted'
        source.opset_import.append(helper.make_opsetid('untrusted', 1))
    elif change == 'dead_node':
        source.graph.node.append(helper.make_node('Relu', [node.output[0]], ['dead'], name='dead'))
    elif change == 'duplicate_name':
        node.name = source.graph.node[0].name
    elif change == 'axes':
        axis = next(n for n in source.graph.node if n.op_type == 'Constant')
        axis.attribute[0].t.CopyFrom(numpy_helper.from_array(np.array([0], np.int64)))
    else:
        gemm = next(n for n in source.graph.node if n.op_type == 'Gemm')
        gemm.attribute.append(helper.make_attribute('transA', 1))
    with pytest.raises((ValueError, onnx.checker.ValidationError, onnx.onnx_cpp2py_export.shape_inference.InferenceError)):
        remaining_plan(model, source, rounded)


@pytest.mark.parametrize('op', REMAINING)
def test_every_remaining_primitive_isolates_exact_inputs_and_reports_signed_drift(tmp_path, op):
    torch.set_num_threads(2)
    node, values = operands_for(op)
    originals = [v.copy() for v in values]
    path, runtime_path = tmp_path / 'PLACEHOLDER-local.onnx', tmp_path / 'PLACEHOLDER-runtime.onnx'
    expected = recipe(node, values)
    result, actual = replay_isolated(node, values, source_model(), path, runtime_path)
    assert result['serialized_audit']['status'] == result['runtime_audit']['status'] == 'PASS'
    assert result['status'] == 'DIAGNOSTIC ONLY'
    delta = actual.astype(np.float64) - expected.astype(np.float64)
    assert result['signed_min'] == float(delta.min())
    assert result['signed_max'] == float(delta.max())
    assert result['max_absolute_error'] == float(np.abs(delta).max())
    assert result['mean_absolute_error'] == float(np.abs(delta).mean())
    for before, after in zip(originals, values):
        assert before.tobytes() == after.tobytes()
    # Structural operations and simple binary float32 arithmetic are exact on this fixture.
    if op in ('Relu', 'Add', 'Sub', 'Mul', 'Div', 'Flatten', 'Squeeze'):
        assert actual.tobytes() == expected.tobytes()


def test_native_hardswish_rounding_difference_is_retained(tmp_path):
    node, _ = operands_for('HardSwish')
    rng = np.random.default_rng(230)
    values = [rng.uniform(-3., 3., (1, 3, 16, 16)).astype(np.float32)]
    result, _ = replay_isolated(node, values, source_model(), tmp_path / 'PLACEHOLDER-local.onnx',
                               tmp_path / 'PLACEHOLDER-runtime.onnx')
    assert result['max_absolute_error'] > 0
    assert result['status'] == 'DIAGNOSTIC ONLY'


@pytest.mark.parametrize('change', ['attribute', 'order', 'boundary_dtype', 'boundary_shape', 'extra_node', 'constant_fold'])
def test_isolated_audit_refuses_runtime_arithmetic_and_boundary_changes(tmp_path, change):
    node, values = operands_for('Sub')
    path = tmp_path / 'PLACEHOLDER-local.onnx'
    isolated_graph(node, values, source_model(), path)
    graph = onnx.load(path)
    if change == 'attribute':
        graph.graph.node[0].attribute.append(helper.make_attribute('unexpected', 1))
    elif change == 'order':
        graph.graph.node[0].input.reverse()
    elif change == 'boundary_dtype':
        graph.graph.input[0].type.tensor_type.elem_type = onnx.TensorProto.DOUBLE
    elif change == 'boundary_shape':
        graph.graph.input[0].type.tensor_type.shape.dim[0].dim_value = 2
    elif change == 'extra_node':
        graph.graph.node.append(helper.make_node('Identity', ['y'], ['extra']))
    else:
        graph.graph.initializer.append(numpy_helper.from_array(values[1], node.input[1]))
        del graph.graph.input[1]
    onnx.save(graph, path)
    with pytest.raises((ValueError, onnx.onnx_cpp2py_export.shape_inference.InferenceError)):
        audit_isolated(node, values, path)


def test_repeated_operand_and_negative_squeeze_axes_are_preserved(tmp_path):
    value = np.array([[2., -3.]], np.float32)
    node = helper.make_node('Mul', ['x', 'x'], ['y'], name='PLACEHOLDER-square')
    path, runtime_path = tmp_path / 'PLACEHOLDER-local.onnx', tmp_path / 'PLACEHOLDER-runtime.onnx'
    _, actual = replay_isolated(node, [value, value.copy()], source_model(), path, runtime_path)
    np.testing.assert_array_equal(actual, value * value)
    with pytest.raises(ValueError, match='repeated remaining operand'):
        isolated_graph(node, [value, value + 1], source_model(), path)
    squeeze = helper.make_node('Squeeze', ['x', 'axes'], ['y'], name='PLACEHOLDER-squeeze')
    np.testing.assert_array_equal(recipe(squeeze, [value[:, :, None], np.array([-1], np.int64)]), value)
    with pytest.raises(ValueError, match='axes/shape'):
        recipe(squeeze, [value[:, :, None], np.array([-1, 2], np.int64)])


@pytest.mark.parametrize('op,kwargs', [('HardSigmoid', {}), ('HardSigmoid', {'alpha': 0.2}),
    ('ReduceMean', {'axes': [1, 2]}), ('ReduceMean', {'axes': [2, 3], 'keepdims': 0}),
    ('Flatten', {'axis': 0}), ('Gemm', {'transB': 0}), ('Gemm', {'transB': 1, 'alpha': 2.}),
    ('Squeeze', {'axes': [1]})])
def test_recipe_rejects_unmapped_semantics(op, kwargs):
    node, _ = operands_for(op)
    del node.attribute[:]
    node.attribute.extend(helper.make_attribute(key, value) for key, value in kwargs.items())
    with pytest.raises(ValueError, match='attributes'):
        validate_node(node)


@pytest.mark.parametrize('change', ['dtype', 'nonfinite', 'count', 'divide_zero', 'pool_rank', 'squeeze_dim'])
def test_recipe_refuses_invalid_actual_operands(change):
    node, values = operands_for('Div' if change == 'divide_zero' else 'GlobalAveragePool' if change == 'pool_rank'
                                else 'Squeeze' if change == 'squeeze_dim' else 'Relu')
    if change == 'dtype':
        values[0] = values[0].astype(np.float64)
    elif change == 'nonfinite':
        values[0].flat[0] = np.nan
    elif change == 'count':
        values.append(values[0])
    elif change == 'divide_zero':
        values[1].fill(0)
    elif change == 'pool_rank':
        values[0] = values[0].reshape(1, -1)
    else:
        values[1] = np.array([0, 1, 2], np.int64)
    with pytest.raises(ValueError):
        recipe(node, values)


def test_constant_resolution_rejects_cycles_external_data_and_invalid_types():
    g = source_model()
    g.graph.node.extend([helper.make_node('Identity', ['b'], ['a']), helper.make_node('Identity', ['a'], ['b'])])
    with pytest.raises(ValueError, match='cycle'):
        constant(g, 'a')
    g.graph.initializer.append(numpy_helper.from_array(np.array([1.], np.float64), 'bad'))
    with pytest.raises(ValueError, match='type/value'):
        constant(g, 'bad')
    g.graph.initializer[0].data_location = onnx.TensorProto.EXTERNAL
    with pytest.raises(ValueError, match='external'):
        constant(g, 'bad')


@pytest.mark.parametrize('change', ['omitted_node', 'reordered_nodes', 'extra_node', 'fit', 'scope', 'environment'])
def test_no_inference_report_reconstruction_rejects_rehashed_partial_evidence(tmp_path, monkeypatch, change):
    # A report checksum alone is insufficient: complete expected evidence is rebuilt.
    from numbra_ml import export_remaining as module
    expected = {'status': 'PREFLIGHT ONLY; NO INFERENCE', 'plan': {'nodes': [1, 2]},
                'fit': 19.15, 'scope': 'train', 'environment': 'original'}
    monkeypatch.setattr(module, 'preflight_evidence', lambda *a, **k: copy.deepcopy(expected))
    report = copy.deepcopy(expected)
    if change == 'omitted_node':
        report['plan']['nodes'].pop()
    elif change == 'reordered_nodes':
        report['plan']['nodes'].reverse()
    elif change == 'extra_node':
        report['plan']['nodes'].append(3)
    else:
        report[change] = 'changed'
    (tmp_path / REPORT).write_text(json.dumps(report))
    with pytest.raises(ValueError, match='complete reconstruction'):
        audit_preflight(None, tmp_path, None, None, None, None, None)
    (tmp_path / REPORT).write_text(json.dumps(expected))
    assert audit_preflight(None, tmp_path, None, None, None, None, None)['baseline_inference'] is False


def test_cli_refuses_existing_output_before_preflight(tmp_path, monkeypatch):
    from numbra_ml import export_remaining as module
    root = tmp_path / 'repo'
    output = root / 'data/PLACEHOLDER-existing'
    output.mkdir(parents=True)
    monkeypatch.setattr(module, 'repository_root', lambda: root)
    monkeypatch.setattr(module, 'preflight_evidence', lambda *a, **k: pytest.fail('must reject before loading'))
    assert main(['--output', str(output)]) == 1
    assert not list(output.iterdir())


@pytest.mark.parametrize('change', ['alpha', 'beta', 'order', 'domain', 'extra_node', 'gate_shape', 'input'])
def test_runtime_hardswish_expansion_is_audited_exactly(tmp_path, change):
    node, values = operands_for('HardSwish')
    path, runtime_path = tmp_path / 'PLACEHOLDER-local.onnx', tmp_path / 'PLACEHOLDER-runtime.onnx'
    replay_isolated(node, values, source_model(), path, runtime_path)
    graph = onnx.load(runtime_path)
    gate, mul = graph.graph.node
    if change in ('alpha', 'beta'):
        next(a for a in gate.attribute if a.name == change).f += 0.1
    elif change == 'order':
        mul.input.reverse()
    elif change == 'domain':
        gate.domain = 'com.microsoft'
    elif change == 'extra_node':
        graph.graph.node.append(helper.make_node('Identity', ['y'], ['unused']))
    elif change == 'gate_shape':
        graph.graph.value_info.append(helper.make_tensor_value_info(gate.output[0], onnx.TensorProto.FLOAT, [2, 3, 2, 2]))
    else:
        gate.input[0] = gate.output[0]
    onnx.save(graph, runtime_path)
    with pytest.raises((ValueError, onnx.onnx_cpp2py_export.shape_inference.InferenceError)):
        audit_isolated(node, values, runtime_path, runtime=True)


def test_full_preflight_reconstructs_provenance_without_any_image_or_inference(profile_evidence, monkeypatch):
    repo, prepared, run, experiments, source, prior, old_output, _, index = profile_evidence
    for component in index.components:
        (prepared / component.row.image_path).write_bytes(b'undecodable image; preflight may not open')
    from numbra_ml.pretrained import sha256
    paths = [p for directory in (run, source, prior, *experiments)
             for p in directory.rglob('*') if p.is_file()]
    retained = {p: sha256(p) for p in paths}
    def no_inference(*args, **kwargs):
        raise AssertionError('preflight must perform no image decode or inference')
    monkeypatch.setattr(nn.Module, '_call_impl', no_inference)
    monkeypatch.setattr('onnxruntime.InferenceSession', no_inference)
    monkeypatch.setattr('numbra_ml.dataset.load_rgb', no_inference)
    report = preflight_evidence(repo, prepared, run, experiments, source, prior, backbone_factory=toy_backbone)
    assert report['status'] == 'PREFLIGHT ONLY; NO INFERENCE'
    assert report['protocol']['components'] == len([c for c in index.components if c.split == 'train'])
    assert not any(report['protocol'][key] for key in
        ('baseline_inference', 'frozen_evaluation_inputs_used', 'quantisation_fit', 'deployment_selection'))
    assert report['plan']['remaining_native_mapping'].startswith('UNIMPLEMENTED')
    assert 'component_ids"' not in json.dumps(report)
    output = old_output.parent / 'PLACEHOLDER-preflight'
    output.mkdir()
    path = output / REPORT
    path.write_text(json.dumps(report))
    assert audit_preflight(repo, output, prepared, run, experiments, source, prior,
                          backbone_factory=toy_backbone)['status'] == 'PASS'
    for bad in ('nodes', 'environment', 'components', 'model'):
        changed = copy.deepcopy(report)
        if bad == 'nodes':
            changed['plan']['nodes'].pop()
        elif bad == 'environment':
            changed['environment']['source_tree_sha256'] = 'bad'
        elif bad == 'components':
            changed['protocol']['components'] -= 1
        else:
            changed['model_state_sha256'] = 'bad'
        path.write_text(json.dumps(changed))
        with pytest.raises(ValueError, match='complete reconstruction'):
            audit_preflight(repo, output, prepared, run, experiments, source, prior, backbone_factory=toy_backbone)
    for bad in ('fit', 'details', 'graph', 'empty-experiments'):
        previous_path = prior / 'PLACEHOLDER-promoted-bn-report.json'
        original = previous_path.read_text()
        changed = json.loads(original)
        if bad == 'fit':
            changed['protocol']['threshold'] += 0.1
        elif bad == 'details':
            changed['diagnostic_details_sha256'] = 'bad'
        elif bad == 'graph':
            changed['artifacts']['complete_promoted_bn']['graph']['sha256'] = 'bad'
        try:
            previous_path.write_text(json.dumps(changed))
            with pytest.raises(ValueError):
                preflight_evidence(repo, prepared, run, [] if bad == 'empty-experiments' else experiments,
                                   source, prior, backbone_factory=toy_backbone)
        finally:
            previous_path.write_text(original)
    assert {p: sha256(p) for p in paths} == retained
