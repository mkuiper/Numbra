"""Generated-only PLACEHOLDER complete native capture; no saved-baseline inference."""

import copy
from functools import partial

import numpy as np
import onnx
import onnxruntime as ort
import pytest
import timm
import torch
from torch import nn
from timm.layers import BatchNormAct2d
from timm.models._efficientnet_blocks import InvertedResidual, SqueezeExcite

from numbra_ml.export import session_options
from numbra_ml.export_batchnorm import export_preserving_batchnorm
from numbra_ml.export_complete_replay import complete_operators
from numbra_ml.export_promoted_bn import substitute_batchnorm
from numbra_ml.export_remaining_native import (capture_native, native_fidelity, native_plan,
    same_bits, tap_complete_graph)
from numbra_ml.export_replay import python_operator
from numbra_ml.export_rounded_bn import RECIPE
from numbra_ml.training import Baseline, FeatureHead, tensor_hash


@pytest.fixture
def generated_pair(tmp_path):
    torch.manual_seed(231)
    torch.set_num_threads(2)
    backbone = nn.Sequential(nn.Conv2d(3, 4, 1, stride=56),
        BatchNormAct2d(4, act_layer='hard_swish', inplace=True),
        InvertedResidual(4, 4, stride=1, exp_ratio=2, act_layer=nn.Hardswish,
            se_layer=partial(SqueezeExcite, gate_layer=nn.Hardsigmoid, force_act_layer=nn.ReLU)),
        nn.AdaptiveAvgPool2d(1), nn.Flatten())
    model = Baseline(backbone, FeatureHead(torch.zeros(4), torch.ones(4))).requires_grad_(False).eval()
    source, rounded = tmp_path / 'PLACEHOLDER-source.onnx', tmp_path / 'PLACEHOLDER-rounded.onnx'
    export_preserving_batchnorm(model, source)
    substitute_batchnorm(model, source, rounded, rounding_recipe=RECIPE)
    value = np.random.default_rng(231).uniform(-4, 4, (1, 3, 224, 224)).astype(np.float32)
    return model, onnx.load(source), onnx.load(rounded), value


def assert_clean(model):
    assert not any(m._forward_pre_hooks or m._forward_hooks for m in model.modules())


def test_static_mapping_and_taps_need_no_image_decode_forward_or_session(generated_pair, monkeypatch):
    model, source, rounded, _ = generated_pair
    before = tensor_hash(model.state_dict())
    def forbidden(*args, **kwargs):
        raise AssertionError('static mapping must not perform inference or decode')
    monkeypatch.setattr(nn.Module, '_call_impl', forbidden)
    monkeypatch.setattr(ort, 'InferenceSession', forbidden)
    monkeypatch.setattr('numbra_ml.dataset.load_rgb', forbidden)
    plan = native_plan(model, source, rounded)
    assert plan['baseline_inference'] is False
    for graph in (source, rounded):
        tapped, names = tap_complete_graph(graph, plan)
        assert names
        assert len(tapped.graph.output) > 1
    assert tensor_hash(model.state_dict()) == before
    assert_clean(model)


def test_complete_native_capture_preserves_multi_operands_inplace_controls_and_logits(generated_pair):
    model, source, rounded, value = generated_pair
    before = tensor_hash(model.state_dict())
    original = value.copy()
    with torch.inference_mode():
        reference = model(torch.from_numpy(value.copy())).numpy().copy()
    capture = capture_native(model, source, rounded, value)
    assert same_bits(reference, capture['logit'])
    assert len(capture['events']) == len([n for n in source.graph.node if n.op_type not in ('Constant', 'Identity')])
    assert {'Add', 'Mul', 'ReduceMean', 'HardSigmoid', 'HardSwish', 'Relu'} <= set(capture['plan']['operator_counts'])
    metrics = native_fidelity(source, capture)['remaining_operators']
    assert len(metrics) == sum(r['category'] == 'remaining_replay' for r in capture['plan']['nodes'])
    assert all(m['exact_bits'] and m['max_absolute_error'] == 0 for m in metrics.values())
    by_name = {e['name']: e for e in capture['events']}
    for name, module, node in complete_operators(model, source):
        e = by_name[node.name]
        assert same_bits(python_operator(module, e['operands'][0]), e['output'])
    for e in capture['events']:
        if e['operator'] == 'HardSwish':
            assert not same_bits(e['operands'][0], e['output'])
        if e['operator'] in ('Mul', 'Add'):
            assert len(e['operands']) == 2
            assert not same_bits(*e['operands'])
        assert not any(np.shares_memory(e['output'], operand) for operand in e['operands'])
    assert tensor_hash(model.state_dict()) == before
    assert same_bits(original, value)
    assert_clean(model)


def test_native_capture_full_random_mobile_architecture_generated_tensor_only(tmp_path):
    # Same architecture, new random weights and a generated input: never saved M3 data/model.
    torch.manual_seed(232)
    torch.set_num_threads(2)
    backbone = timm.create_model('mobilenetv3_small_100.lamb_in1k', pretrained=False)
    backbone.reset_classifier(0)
    model = Baseline(backbone, FeatureHead(torch.zeros(1024), torch.ones(1024))).requires_grad_(False).eval()
    source, rounded = tmp_path / 'PLACEHOLDER-generated.onnx', tmp_path / 'PLACEHOLDER-generated-rounded.onnx'
    export_preserving_batchnorm(model, source)
    substitute_batchnorm(model, source, rounded, rounding_recipe=RECIPE)
    source, rounded = onnx.load(source), onnx.load(rounded)
    value = np.random.default_rng(232).uniform(-3, 3, (1, 3, 224, 224)).astype(np.float32)
    with torch.inference_mode():
        reference = model(torch.from_numpy(value.copy())).numpy().copy()
    capture = capture_native(model, source, rounded, value)
    assert capture['plan']['operator_counts'] == {'Conv': 53, 'BatchNormalization': 34,
        'HardSwish': 19, 'Relu': 14, 'ReduceMean': 9, 'HardSigmoid': 9, 'Mul': 9,
        'Add': 6, 'GlobalAveragePool': 1, 'Flatten': 1, 'Sub': 1, 'Div': 1, 'Gemm': 1, 'Squeeze': 1}
    assert len(capture['events']) == 159
    assert same_bits(reference, capture['logit'])
    metrics = native_fidelity(source, capture)['remaining_operators']
    assert len(metrics) == 72
    assert all(m['exact_bits'] for m in metrics.values())
    assert_clean(model)


@pytest.mark.parametrize('which', ['source', 'rounded'])
def test_complete_taps_preserve_all_operand_bits_and_whole_logits(generated_pair, tmp_path, which):
    model, source, rounded, value = generated_pair
    plan = native_plan(model, source, rounded)
    original = source if which == 'source' else rounded
    tapped, names = tap_complete_graph(original, plan)
    assert [n.SerializeToString() for n in tapped.graph.node] == [n.SerializeToString() for n in original.graph.node]
    assert [n.SerializeToString() for n in tapped.graph.initializer] == [n.SerializeToString() for n in original.graph.initializer]
    assert names == list(dict.fromkeys(name for r in plan['nodes'] for name in (*r['inputs'], *r['outputs'])))
    one = ort.InferenceSession(original.SerializeToString(), session_options('disabled'), providers=['CPUExecutionProvider'])
    all_outputs = ort.InferenceSession(tapped.SerializeToString(), session_options('disabled'), providers=['CPUExecutionProvider'])
    expected, = one.run(None, {'rgb': value})
    values = dict(zip([o.name for o in tapped.graph.output], all_outputs.run(None, {'rgb': value})))
    assert same_bits(expected, values['raw_logit'])
    for record in plan['nodes']:
        for name in (*record['inputs'], *record['outputs']):
            assert name in values
        if record['operator'] in ('Mul', 'Add'):
            assert len(record['inputs']) == 2


@pytest.mark.parametrize('change', ['scope', 'subclass', 'alias', 'flatten', 'pool', 'no_skip', 'training'])
def test_native_mapping_rejects_ambiguous_or_changed_owner_semantics(generated_pair, change):
    model, source, rounded, _ = generated_pair
    if change == 'scope':
        for graph in (source, rounded):
            next(n for n in graph.graph.node if n.op_type == 'HardSwish').name = '/missing/HardSwish'
    elif change == 'subclass':
        class Unknown(nn.Hardswish):
            pass
        model.backbone[1].act = Unknown(inplace=True)
    elif change == 'alias':
        model.alias = model.backbone[1].act
    elif change == 'flatten':
        model.backbone[4].start_dim = 0
    elif change == 'pool':
        model.backbone[3].output_size = 2
    elif change == 'no_skip':
        model.backbone[2].has_skip = False
    else:
        model.backbone[1].train()
    with pytest.raises(ValueError):
        native_plan(model, source, rounded)
    assert_clean(model)


@pytest.mark.parametrize('change', ['dim', 'keepdim', 'missing', 'extra', 'order', 'operand', 'failure'])
def test_actual_native_calls_fail_closed_and_remove_hooks(generated_pair, change):
    model, source, rounded, value = generated_pair
    before = tensor_hash(model.state_dict())
    se = model.backbone[2].se
    original_forward = se.forward
    if change in ('dim', 'keepdim'):
        def bad_forward(x):
            return x.mean((1, 3) if change == 'dim' else (2, 3), keepdim=change != 'keepdim')
        se.forward = bad_forward
    elif change == 'missing':
        se.forward = lambda x: x
    elif change == 'extra':
        se.forward = lambda x: original_forward(x) * x
    elif change == 'order':
        se.forward = lambda x: x * original_forward(x)
    elif change == 'operand':
        # Preserve event scope/count but substitute a different tensor before reduction.
        se.forward = lambda x: original_forward(x.clone().fill_(0))
    else:
        def failure(x):
            raise RuntimeError('injected native failure')
        se.forward = failure
    with pytest.raises((ValueError, RuntimeError)):
        capture_native(model, source, rounded, value)
    assert tensor_hash(model.state_dict()) == before
    assert_clean(model)


@pytest.mark.parametrize('change', ['dtype', 'shape', 'nonfinite'])
def test_capture_rejects_invalid_input_before_forward(generated_pair, change):
    model, source, rounded, value = generated_pair
    if change == 'dtype':
        value = value.astype(np.float64)
    elif change == 'shape':
        value = value[:, :, :1, :1]
    else:
        value.flat[0] = np.nan
    model.forward = lambda *a: pytest.fail('invalid input must fail before inference')
    with pytest.raises(ValueError, match='input specification'):
        capture_native(model, source, rounded, value)
    assert_clean(model)


def test_fidelity_retains_drift_and_signed_zero(generated_pair):
    model, source, rounded, value = generated_pair
    capture = capture_native(model, source, rounded, value)
    event = next(e for e in capture['events'] if e['operator'] == 'Mul')
    event['output'].flat[0] += np.float32(0.01)
    metric = native_fidelity(source, capture)['remaining_operators'][event['name']]
    assert not metric['exact_bits']
    assert metric['signed_min'] < 0
    assert metric['max_absolute_error'] > 0
    assert not same_bits(np.array([0.], np.float32), np.array([-0.], np.float32))


def test_existing_hooks_are_preserved_and_refused(generated_pair):
    model, source, rounded, value = generated_pair
    handle = model.backbone[0].register_forward_hook(lambda *a: None)
    try:
        with pytest.raises(ValueError, match='pre-existing'):
            capture_native(model, source, rounded, value)
        assert len(model.backbone[0]._forward_hooks) == 1
    finally:
        handle.remove()
    assert_clean(model)


@pytest.mark.parametrize('change', ['omit', 'omit_bn', 'reorder', 'duplicate', 'empty', 'operand_bits', 'boundary', 'extra_boundary'])
def test_complete_taps_reject_changed_or_partial_plans(generated_pair, change):
    model, source, rounded, _ = generated_pair
    plan = native_plan(model, source, rounded)
    if change == 'omit':
        plan['nodes'].pop(2)
    elif change == 'omit_bn':
        plan['nodes'].remove(next(r for r in plan['nodes'] if r['operator'] == 'BatchNormalization'))
    elif change == 'reorder':
        plan['nodes'].reverse()
    elif change == 'duplicate':
        plan['nodes'].append(copy.deepcopy(plan['nodes'][0]))
    elif change == 'empty':
        plan['nodes'].clear()
    elif change == 'operand_bits':
        for graph in (source, rounded):
            next(n for n in graph.graph.node if n.op_type == 'Mul').input.reverse()
    elif change == 'boundary':
        first = plan['nodes'][0]
        first['boundaries'][first['inputs'][0]]['dtype'] = 'float64'
    else:
        plan['nodes'][0]['boundaries']['undeclared'] = {'dtype': 'float32', 'shape': [1]}
    for graph in (source, rounded):
        with pytest.raises(ValueError, match='complete tap'):
            tap_complete_graph(graph, plan)


@pytest.mark.parametrize('change', ['omit', 'reorder', 'duplicate', 'operator', 'nonfinite', 'dtype'])
def test_native_fidelity_refuses_partial_and_invalid_captured_scope(generated_pair, change):
    model, source, rounded, value = generated_pair
    capture = capture_native(model, source, rounded, value)
    event = next(e for e in capture['events'] if e['operator'] == 'Mul')
    if change == 'omit':
        capture['events'].remove(event)
    elif change == 'reorder':
        capture['events'].reverse()
    elif change == 'duplicate':
        capture['events'].append(event)
    elif change == 'operator':
        event['operator'] = 'Conv'
    elif change == 'nonfinite':
        event['output'].flat[0] = np.nan
    else:
        event['output'] = event['output'].astype(np.float64)
    with pytest.raises(ValueError, match='native recipe fidelity'):
        native_fidelity(source, capture)


def test_capture_state_mutation_is_detected_and_failed_mode_can_be_reused(generated_pair):
    model, source, rounded, value = generated_pair
    original_forward = model.backbone[2].se.forward
    def failed(x):
        raise RuntimeError('injected reuse failure')
    model.backbone[2].se.forward = failed
    with pytest.raises(RuntimeError, match='reuse failure'):
        capture_native(model, source, rounded, value)
    assert_clean(model)
    model.backbone[2].se.forward = original_forward
    capture_native(model, source, rounded, value)
    assert_clean(model)
    original_head = model.head.forward
    def mutate(x):
        model.head.mean.add_(1.)
        return original_head(x)
    model.head.forward = mutate
    with pytest.raises(ValueError, match='changed saved state'):
        capture_native(model, source, rounded, value)
    assert_clean(model)
