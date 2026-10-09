"""Generated-only ADR-024 PLACEHOLDER arithmetic/context regression evidence."""

import copy

import numpy as np
import onnx
from onnx import helper, numpy_helper
import onnxruntime as ort
import pytest
import timm
import torch

from numbra_ml.export import session_options
from numbra_ml.export_batchnorm import export_preserving_batchnorm
from numbra_ml.export_promoted_bn import substitute_batchnorm
from numbra_ml.export_remaining_arithmetic import (RECIPES, arithmetic_graph,
    audit_arithmetic_graph, complete_arithmetic_scope, eager_expression, expression_metrics)
from numbra_ml.export_remaining_native import same_bits
from numbra_ml.export_rounded_bn import RECIPE
from numbra_ml.training import Baseline, FeatureHead, tensor_hash
from test_export_remaining import graph_pair, operands_for


def source_for(op, shape=None):
    node, operands = operands_for(op)
    if shape is not None:
        operands = [np.zeros(shape, np.float32)]
    output = ([*operands[0].shape[:2], 1, 1] if op in ('ReduceMean', 'GlobalAveragePool')
              else [operands[0].shape[0], operands[1].shape[0]] if op == 'Gemm'
              else list(operands[0].shape))
    constants = []
    for name, array in zip(node.input[1:], operands[1:]):
        constants.append(numpy_helper.from_array(array, name))
    graph = helper.make_graph([node], 'PLACEHOLDER-fixture',
        [helper.make_tensor_value_info(node.input[0], onnx.TensorProto.FLOAT, operands[0].shape)],
        [helper.make_tensor_value_info(node.output[0], onnx.TensorProto.FLOAT, output)], constants)
    return helper.make_model(graph, opset_imports=[helper.make_opsetid('', 17)], ir_version=8), node, operands


def run_graph(tmp_path, graph, feed):
    path, runtime_path = tmp_path / 'PLACEHOLDER-source.onnx', tmp_path / 'PLACEHOLDER-runtime.onnx'
    onnx.save(graph, path)
    options = session_options('disabled')
    options.optimized_model_filepath = str(runtime_path)
    session = ort.InferenceSession(str(path), sess_options=options, providers=['CPUExecutionProvider'])
    actual, = session.run(None, feed)
    return actual, onnx.load(runtime_path)


@pytest.mark.parametrize('op,variant', [(op, variant) for op, variants in RECIPES.items() for variant in variants])
def test_every_fixed_recipe_runs_and_all_runtime_arithmetic_is_audited(tmp_path, op, variant):
    torch.set_num_threads(2)
    source, node, operands = source_for(op)
    before = source.SerializeToString(), [v.tobytes() for v in operands]
    graph = arithmetic_graph(source, node, variant)
    actual, runtime = run_graph(tmp_path, graph, {node.input[0]: operands[0]})
    assert audit_arithmetic_graph(source, node, variant, graph)['status'] == 'PASS'
    audit = audit_arithmetic_graph(source, node, variant, runtime, runtime=True)
    assert audit['all_expressions_constants_boundaries']
    assert audit['native_equivalence'] == audit['whole_model_parity'] == 'UNVERIFIED'
    expected = eager_expression(source, node, variant, operands)
    metrics = expression_metrics(source, node, variant, operands, actual)
    delta = actual.astype(np.float64) - expected.astype(np.float64)
    assert metrics['signed_min'] == float(delta.min())
    assert metrics['signed_max'] == float(delta.max())
    assert metrics['signed_mean'] == float(delta.mean())
    assert metrics['max_absolute_error'] == float(np.abs(delta).max())
    assert metrics['mean_absolute_error'] == float(np.abs(delta).mean())
    assert metrics['exact_bits'] == same_bits(actual, expected)
    if op == 'Gemm':
        # Constant-context isolation must preserve the original ONNX result.
        # ORT/native linear arithmetic need not agree: keep the observed drift.
        whole, _ = run_graph(tmp_path, source, {node.input[0]: operands[0]})
        assert same_bits(actual, whole)
        assert metrics['max_absolute_error'] > 0
    else:
        np.testing.assert_array_equal(actual, expected)
    assert (source.SerializeToString(), [v.tobytes() for v in operands]) == before
    assert len(graph.graph.input) == 1
    assert all('PLACEHOLDER' in p.value for p in graph.metadata_props if 'notice' in p.key)


@pytest.mark.parametrize('op', ['HardSwish', 'HardSigmoid'])
@pytest.mark.parametrize('variant', ['divide', 'reciprocal'])
def test_activation_float32_rounding_and_clamp_boundaries(tmp_path, op, variant):
    source, node, _ = source_for(op, [1, 1, 1, 18])
    x = np.array([-100., -3.000001, -3., -2.999999, -2.1, -0.1, -0., 0.,
                  0.1, 0.7, 1.1, 2.3, 2.999999, 3., 3.000001, 100., 1e-20, -1e-20], np.float32).reshape(1, 1, 1, -1)
    # NumPy specifies each rounding boundary independently of eager PyTorch.
    gate = np.clip(np.add(x, np.float32(3)), np.float32(0), np.float32(6))
    product = np.multiply(x, gate) if op == 'HardSwish' else gate
    expected = (np.divide(product, np.float32(6)) if variant == 'divide'
                else np.multiply(product, np.float32(1 / 6)))
    actual, _ = run_graph(tmp_path, arithmetic_graph(source, node, variant), {node.input[0]: x})
    assert same_bits(actual, expected)
    assert same_bits(eager_expression(source, node, variant, [x]), expected)


def test_division_and_reciprocal_are_distinct_experiments():
    source, node, _ = source_for('HardSigmoid', [1, 1, 1, 4096])
    x = np.random.default_rng(240).uniform(-3., 3., (1, 1, 1, 4096)).astype(np.float32)
    divide, reciprocal = [eager_expression(source, node, variant, [x]) for variant in RECIPES['HardSigmoid']]
    assert not same_bits(divide, reciprocal)
    assert len(RECIPES['HardSigmoid']) == 2


@pytest.mark.parametrize('op', ['ReduceMean', 'GlobalAveragePool'])
def test_double_reduction_retains_cancellation_and_float32_output(tmp_path, op):
    source, node, _ = source_for(op, [2, 3, 3, 5])
    x = np.tile(np.array([1e8, 1, -1e8, 3, -2], np.float32), 18).reshape(2, 3, 3, 5)
    graph = arithmetic_graph(source, node, 'double_mean')
    actual, runtime = run_graph(tmp_path, graph, {node.input[0]: x})
    expected = x.astype(np.float64).mean((2, 3), keepdims=True).astype(np.float32)
    assert same_bits(actual, expected)
    assert same_bits(eager_expression(source, node, 'double_mean', [x]), expected)
    assert audit_arithmetic_graph(source, node, 'double_mean', runtime, runtime=True)['status'] == 'PASS'
    assert [n.op_type for n in graph.graph.node] == ['Cast', 'ReduceMean', 'Cast']


def aliased_head():
    source, node, operands = source_for('Gemm')
    weight = source.graph.initializer[0]
    weight.name = 'original-weight'
    bias = operands[2].copy()
    bias[0] = -0.
    del source.graph.initializer[1]
    prefix = [helper.make_node('Identity', ['original-weight'], ['weight-alias'], name='alias-1'),
              helper.make_node('Identity', ['weight-alias'], [node.input[1]], name='alias-2'),
              helper.make_node('Constant', [], [node.input[2]], name='original-bias',
                               value=numpy_helper.from_array(bias))]
    for position, original in enumerate(prefix):
        source.graph.node.insert(position, original)
    operands[2] = bias
    return source, source.graph.node[-1], operands


def test_head_keeps_exact_constant_and_identity_context(tmp_path):
    source, node, operands = aliased_head()
    graph = arithmetic_graph(source, node, 'constant_parameters')
    assert [n.SerializeToString() for n in graph.graph.node] == [n.SerializeToString() for n in source.graph.node]
    assert [i.SerializeToString() for i in graph.graph.initializer] == [i.SerializeToString() for i in source.graph.initializer]
    assert [v.name for v in graph.graph.input] == [node.input[0]]
    assert np.signbit(numpy_helper.to_array(graph.graph.node[2].attribute[0].t)[0])
    actual, runtime = run_graph(tmp_path, graph, {node.input[0]: operands[0]})
    assert audit_arithmetic_graph(source, node, 'constant_parameters', runtime, runtime=True)['status'] == 'PASS'
    whole, _ = run_graph(tmp_path, source, {node.input[0]: operands[0]})
    assert same_bits(actual, whole)
    metrics = expression_metrics(source, node, 'constant_parameters', operands, actual)
    assert metrics['status'] == 'DIAGNOSTIC ONLY'
    assert metrics['reference'].endswith('not captured native saved output')


@pytest.mark.parametrize('runtime', [False, True])
@pytest.mark.parametrize('change', ['constant_bit', 'operand_order', 'extra_node', 'omit_node',
                                  'input_type', 'output_shape', 'recipe_change'])
def test_recipe_corruption_is_rejected(tmp_path, runtime, change):
    source, node, _ = source_for('HardSwish')
    graph = arithmetic_graph(source, node, 'divide')
    if runtime:
        _, graph = run_graph(tmp_path, graph, {node.input[0]: np.ones((1, 3, 2, 2), np.float32)})
    if change == 'constant_bit':
        item = next(i for i in graph.graph.initializer if i.name.endswith('six'))
        item.CopyFrom(numpy_helper.from_array(np.array(5., np.float32), item.name))
    elif change == 'operand_order':
        next(n for n in graph.graph.node if n.op_type == 'Div').input.reverse()
    elif change == 'extra_node':
        graph.graph.node.append(helper.make_node('Relu', [node.output[0]], ['unexpected'], name='extra'))
    elif change == 'omit_node':
        graph.graph.node.remove(graph.graph.node[0])
    elif change == 'input_type':
        graph.graph.input[0].type.tensor_type.elem_type = onnx.TensorProto.DOUBLE
    elif change == 'output_shape':
        graph.graph.output[0].type.tensor_type.shape.dim[-1].dim_value += 1
    else:
        next(n for n in graph.graph.node if n.op_type == 'Div').op_type = 'Mul'
    with pytest.raises((ValueError, onnx.checker.ValidationError, onnx.shape_inference.InferenceError)):
        audit_arithmetic_graph(source, node, 'divide', graph, runtime=runtime)


@pytest.mark.parametrize('runtime', [False, True])
@pytest.mark.parametrize('change', ['signed_zero', 'alias_fold', 'dynamic_weight', 'gemm_attribute'])
def test_head_context_corruption_is_rejected(tmp_path, runtime, change):
    source, node, operands = aliased_head()
    graph = arithmetic_graph(source, node, 'constant_parameters')
    if runtime:
        _, graph = run_graph(tmp_path, graph, {node.input[0]: operands[0]})
    if change == 'signed_zero':
        item = (next(i for i in graph.graph.initializer if i.name == node.input[2])
                if runtime else graph.graph.node[2].attribute[0].t)
        bias = numpy_helper.to_array(item).copy()
        bias[0] = 0.
        item.CopyFrom(numpy_helper.from_array(bias, item.name))
    elif change == 'alias_fold':
        graph.graph.node[1].input[0] = 'original-weight'
        graph.graph.node.remove(graph.graph.node[0])
    elif change == 'dynamic_weight':
        graph.graph.input.append(helper.make_tensor_value_info('original-weight', onnx.TensorProto.FLOAT, [2, 12]))
    else:
        gemm = next(n for n in graph.graph.node if n.op_type == 'Gemm')
        trans_a = next((a for a in gemm.attribute if a.name == 'transA'), None)
        if trans_a is None:
            gemm.attribute.append(helper.make_attribute('transA', 1))
        else:
            trans_a.i = 1
    with pytest.raises((ValueError, onnx.checker.ValidationError, onnx.shape_inference.InferenceError)):
        audit_arithmetic_graph(source, node, 'constant_parameters', graph, runtime=runtime)


@pytest.mark.parametrize('change', ['dtype', 'shape', 'nan', 'arity', 'head_bits'])
def test_eager_recipe_rejects_invalid_supplied_operands(change):
    source, node, operands = source_for('Gemm')
    if change == 'dtype':
        operands[0] = operands[0].astype(np.float64)
    elif change == 'shape':
        operands[0] = operands[0].reshape(2, 6)
    elif change == 'nan':
        operands[0].flat[0] = np.nan
    elif change == 'arity':
        operands.pop()
    else:
        operands[1].flat[0] += 1
    with pytest.raises(ValueError, match='operand|parameter bits'):
        eager_expression(source, node, 'constant_parameters', operands)


def test_overridable_head_parameter_is_forbidden():
    source, node, _ = source_for('Gemm')
    source.graph.input.append(helper.make_tensor_value_info(node.input[1], onnx.TensorProto.FLOAT, [2, 12]))
    with pytest.raises(ValueError, match='overridable'):
        arithmetic_graph(source, node, 'constant_parameters')


@pytest.mark.parametrize('change', ['dtype', 'shape', 'nan'])
def test_metrics_reject_invalid_runtime_output(change):
    source, node, operands = source_for('HardSwish')
    actual = eager_expression(source, node, 'divide', operands)
    if change == 'dtype':
        actual = actual.astype(np.float64)
    elif change == 'shape':
        actual = actual.reshape(1, -1)
    else:
        actual.flat[0] = np.nan
    with pytest.raises(ValueError, match='runtime output specification'):
        expression_metrics(source, node, 'divide', operands, actual)


def test_finite_operands_with_overflow_are_reported_as_invalid_output():
    source, node, _ = source_for('HardSwish')
    operands = [np.full((1, 3, 2, 2), np.finfo(np.float32).max, np.float32)]
    with pytest.raises(ValueError, match='nonfinite/invalid output'):
        eager_expression(source, node, 'divide', operands)


@pytest.mark.parametrize('change', ['recipe', 'unbound_node', 'attributes', 'dynamic', 'count'])
def test_unsupported_recipe_or_geometry_fails_before_execution(change):
    source, node, _ = source_for('ReduceMean')
    variant = 'sum_divide'
    if change == 'recipe':
        variant = 'adaptive'
    elif change == 'unbound_node':
        node = copy.deepcopy(node)
        node.name += '-different'
    elif change == 'attributes':
        next(a for a in node.attribute if a.name == 'keepdims').i = 0
    elif change == 'dynamic':
        source.graph.input[0].type.tensor_type.shape.dim[2].ClearField('dim_value')
        source.graph.input[0].type.tensor_type.shape.dim[2].dim_param = 'dynamic'
    else:
        source, node, _ = source_for('ReduceMean')
        source.graph.input[0].type.tensor_type.shape.dim[2].dim_value = 2**24 + 1
        source.graph.input[0].type.tensor_type.shape.dim[3].dim_value = 1
    with pytest.raises((ValueError, onnx.checker.ValidationError, onnx.shape_inference.InferenceError)):
        arithmetic_graph(source, node, variant)


def test_complete_scope_covers_full_random_mobile_architecture_without_inference(tmp_path, monkeypatch):
    torch.manual_seed(240)
    torch.set_num_threads(2)
    backbone = timm.create_model('mobilenetv3_small_100', pretrained=False, num_classes=0).eval()
    model = Baseline(backbone, FeatureHead(torch.zeros(1024), torch.ones(1024))).eval().requires_grad_(False)
    source_path, rounded_path = tmp_path / 'PLACEHOLDER-mobile.onnx', tmp_path / 'PLACEHOLDER-rounded.onnx'
    export_preserving_batchnorm(model, source_path)
    substitute_batchnorm(model, source_path, rounded_path, rounding_recipe=RECIPE)
    source, rounded = onnx.load(source_path), onnx.load(rounded_path)
    before = tensor_hash(model.state_dict())
    def forbidden(*a, **kw):
        pytest.fail('complete static scope must not infer, decode or construct a session')
    monkeypatch.setattr(model, 'forward', forbidden)
    monkeypatch.setattr(ort, 'InferenceSession', forbidden)
    monkeypatch.setattr('numbra_ml.dataset.load_rgb', forbidden)
    scope = complete_arithmetic_scope(model, source, rounded)
    assert scope['operator_counts'] == {'HardSwish': 19, 'HardSigmoid': 9, 'ReduceMean': 9,
                                       'GlobalAveragePool': 1, 'Gemm': 1}
    assert scope['graph_count'] == 77
    assert scope['unchanged_controls']['saved_conv_bn_control'] == 87
    assert scope['status'] == 'STATIC SCOPE ONLY'
    assert scope['training_observation_replay'] == 'UNIMPLEMENTED'
    assert scope['baseline_inference'] is scope['deployment_selection'] is False
    assert [r['position'] for r in scope['ordered_nodes']] == sorted(r['position'] for r in scope['ordered_nodes'])
    assert tensor_hash(model.state_dict()) == before
    # All target nodes are unchanged in both contexts; recipe graph bits agree.
    for record in scope['ordered_nodes']:
        node = next(n for n in rounded.graph.node if n.name == record['name'])
        for variant in RECIPES[node.op_type]:
            expected = arithmetic_graph(source, node, variant)
            actual = arithmetic_graph(rounded, node, variant)
            assert actual.SerializeToString() == expected.SerializeToString()


def test_complete_scope_rejects_changed_control_before_building_recipes(tmp_path):
    model, source, rounded = graph_pair(tmp_path)
    next(n for n in rounded.graph.node if n.op_type == 'HardSwish').op_type = 'Relu'
    with pytest.raises(ValueError, match='remaining/control node scope'):
        complete_arithmetic_scope(model, source, rounded)
