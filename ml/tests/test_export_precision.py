"""PLACEHOLDER generated arithmetic, borders and one-rounding regression cases."""

import numpy as np
import onnx
import pytest
import torch
from torch import nn

from numbra_ml.export_batchnorm import export_preserving_batchnorm
from numbra_ml.export_precision import (AFFINE_FORMULAS, conv_geometry,
    promoted_affine_graph, promoted_conv_graph, python_promoted_affine, python_promoted_conv)
from numbra_ml.export_replay import operator_session, python_formula, replay_diagnostics, run_operator
from numbra_ml.training import tensor_hash
from test_export_replay import toy_model


def source_model():
    return onnx.helper.make_model(onnx.helper.make_graph([], 'PLACEHOLDER-source', [], []),
                                 opset_imports=[onnx.helper.make_opsetid('', 17)], ir_version=8)


@pytest.mark.parametrize('bias', [False, True])
@pytest.mark.parametrize('geometry', [((3, 3), (2, 2), (1, 1), (1, 1)),
                                     ((2, 3), (1, 2), (2, 1), (2, 2))])
def test_promoted_stem_patch_order_borders_dilation_stride(tmp_path, bias, geometry):
    kernel, stride, padding, dilation = geometry
    module = nn.Conv2d(3, 4, kernel, stride=stride, padding=padding, dilation=dilation, bias=bias).eval()
    with torch.no_grad():
        module.weight.copy_(torch.arange(module.weight.numel()).reshape_as(module.weight) % 11 - 5)
        if bias:
            module.bias.copy_(torch.tensor([1., -2., 3., -4.]))
    before = tensor_hash(module.state_dict())
    value = ((np.arange(2 * 3 * 7 * 9).reshape(2, 3, 7, 9) % 17) - 8).astype(np.float32)
    shape = conv_geometry(module, list(value.shape))
    # Direct scalar convolution independently checks patch/channel order and edge zeros.
    expected = np.zeros(shape, np.float32)
    weights = module.weight.detach().numpy()
    for n, o, y, x in np.ndindex(*shape):
        total = float(module.bias[o].detach()) if bias else 0.
        for c, ky, kx in np.ndindex(3, *kernel):
            iy, ix = y * stride[0] - padding[0] + ky * dilation[0], x * stride[1] - padding[1] + kx * dilation[1]
            if 0 <= iy < 7 and 0 <= ix < 9:
                total += float(value[n, c, iy, ix]) * float(weights[o, c, ky, kx])
        expected[n, o, y, x] = total
    path, optimized = [tmp_path / f'PLACEHOLDER-{tag}.onnx' for tag in ('conv', 'optimized')]
    promoted_conv_graph(module, list(value.shape), source_model(), path)
    actual = run_operator(operator_session(path, optimized), value)
    np.testing.assert_array_equal(actual, expected)
    np.testing.assert_array_equal(python_promoted_conv(module, value), expected)
    graph = onnx.load(optimized)
    assert 'Conv' not in {node.op_type for node in graph.graph.node}
    assert 'MatMul' in {node.op_type for node in graph.graph.node}
    saved_weight = next(item for item in onnx.load(path).graph.initializer if item.name == 'weights')
    np.testing.assert_array_equal(onnx.numpy_helper.to_array(saved_weight), weights.reshape(4, -1).T)
    assert saved_weight.data_type == onnx.TensorProto.FLOAT
    assert tensor_hash(module.state_dict()) == before


@pytest.mark.parametrize('formula', AFFINE_FORMULAS)
def test_promoted_affine_retains_product_before_float32_boundary(tmp_path, formula):
    module = nn.BatchNorm2d(1, eps=0).eval()
    with torch.no_grad():
        module.weight.fill_(1 - 2 ** -23)
        module.bias.fill_(-1)
    value = np.full((1, 1, 2, 3), 1 + 2 ** -23, dtype=np.float32)
    before = tensor_hash(module.state_dict())
    path, optimized = [tmp_path / f'PLACEHOLDER-{tag}.onnx' for tag in ('affine', 'optimized')]
    promoted_affine_graph(module, list(value.shape), formula, source_model(), path)
    actual = run_operator(operator_session(path, optimized), value)
    np.testing.assert_array_equal(actual, np.full_like(value, -2 ** -46))
    np.testing.assert_array_equal(actual, python_promoted_affine(module, value, formula))
    np.testing.assert_array_equal(python_formula(module, value, formula), np.zeros_like(value))
    assert tensor_hash(module.state_dict()) == before
    assert {node.op_type for node in onnx.load(optimized).graph.node} == {'Cast', 'Mul', 'Add'}


def test_promoted_rejects_unsupported_geometry_and_input():
    with pytest.raises(ValueError, match='ungrouped numeric zero padding'):
        conv_geometry(nn.Conv2d(3, 3, 3, groups=3), [1, 3, 7, 7])
    with pytest.raises(ValueError, match='ungrouped numeric zero padding'):
        conv_geometry(nn.Conv2d(3, 4, 3, padding='same'), [1, 3, 7, 7])
    with pytest.raises(ValueError, match='ungrouped numeric zero padding'):
        conv_geometry(nn.Conv2d(3, 4, 3, padding_mode='reflect'), [1, 3, 7, 7])
    with pytest.raises(ValueError, match='positive NCHW'):
        conv_geometry(nn.Conv2d(3, 4, 3), [1, 4, 7, 7])
    with pytest.raises(ValueError, match='empty output'):
        conv_geometry(nn.Conv2d(3, 4, 9), [1, 3, 7, 7])
    with pytest.raises(ValueError, match='saved float32'):
        conv_geometry(nn.Conv2d(3, 4, 3).double(), [1, 3, 7, 7])
    with pytest.raises(ValueError, match='finite float32'):
        python_promoted_conv(nn.Conv2d(3, 4, 3), np.full((1, 3, 7, 7), np.nan, np.float32))
    with pytest.raises(ValueError, match='unknown promoted'):
        python_promoted_affine(nn.BatchNorm2d(3), np.zeros((1, 3, 7, 7), np.float32), 'unplanned')


def test_promoted_replay_uses_both_origins_and_cleans_hooks(tmp_path):
    model = toy_model()
    source = tmp_path / 'PLACEHOLDER-source.onnx'
    export_preserving_batchnorm(model, source)
    value = np.random.default_rng(413).normal(size=(1, 3, 224, 224)).astype(np.float32)
    before = tensor_hash(model.state_dict())
    summary, details = replay_diagnostics(model, source, tmp_path, [('generated', value)], promoted=True)
    assert len(details['rows']) == 1
    assert summary['instrumentation_absolute_logit_change']['max'] == 0
    for name, stats in summary['operators'].items():
        if name == 'backbone.2':
            assert 'promoted' not in stats  # Only first stem, never all/depthwise Conv.
            continue
        assert set(stats['promoted']) == {'python_input', 'onnx_input'}
        for origin in stats['promoted'].values():
            for errors in origin.values():
                assert errors['onnx_vs_python_promoted']['max_absolute_error']['max'] == 0
    def bad_inputs():
        raise RuntimeError('promoted input failure')
        yield
    with pytest.raises(RuntimeError, match='promoted input failure'):
        replay_diagnostics(model, source, tmp_path, bad_inputs(), promoted=True)
    assert tensor_hash(model.state_dict()) == before
    assert not any(m._forward_hooks or m._forward_pre_hooks for m in model.modules())
    for path in tmp_path.glob('*.onnx'):
        assert {item.key: item.value for item in onnx.load(path).metadata_props}['diagnostic_notice'].endswith('never bundle')
