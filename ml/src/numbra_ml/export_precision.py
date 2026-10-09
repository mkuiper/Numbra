"""ADR-016 PLACEHOLDER promoted operator arithmetic; never bundle graphs."""

import numpy as np
import onnx
from onnx import helper, numpy_helper
import torch
from torch import nn
from torch.nn import functional as F

from .export_batchnorm import mark_diagnostic
from .export_replay import bn_constants, validate_array

AFFINE_FORMULAS = ('affine_rsqrt', 'affine_divide')


def conv_geometry(module, shape):
    if (not isinstance(module, nn.Conv2d) or module.groups != 1
            or module.padding_mode != 'zeros' or isinstance(module.padding, str)):
        raise ValueError('promoted stem requires ungrouped numeric zero padding')
    if (len(shape) != 4 or any(type(size) is not int or size <= 0 for size in shape)
            or shape[1] != module.in_channels):
        raise ValueError('promoted stem requires fixed positive NCHW shape')
    if module.weight.dtype != torch.float32 or (module.bias is not None and module.bias.dtype != torch.float32):
        raise ValueError('promoted stem requires saved float32 parameters')
    height, width = [(size + 2 * pad - dilation * (kernel - 1) - 1) // stride + 1
        for size, pad, dilation, kernel, stride in zip(shape[2:], module.padding,
            module.dilation, module.kernel_size, module.stride)]
    if height <= 0 or width <= 0:
        raise ValueError('promoted stem has empty output')
    return [shape[0], module.out_channels, height, width]


def python_promoted_conv(module, value):
    conv_geometry(module, list(validate_array(value).shape))
    with torch.inference_mode():
        tensor = torch.from_numpy(value.copy()).double()
        patches = F.unfold(tensor, module.kernel_size, dilation=module.dilation,
                           padding=module.padding, stride=module.stride)
        weights = module.weight.detach().double().reshape(module.out_channels, -1)
        result = torch.matmul(patches.transpose(1, 2), weights.T).transpose(1, 2)
        if module.bias is not None:
            result = result + module.bias.detach().double().reshape(1, -1, 1)
        return result.reshape(conv_geometry(module, list(value.shape))).float().numpy().copy()


def python_promoted_affine(module, value, formula):
    if formula not in AFFINE_FORMULAS:
        raise ValueError('unknown promoted affine formula')
    constants = bn_constants(module, formula)
    with torch.inference_mode():
        tensor = torch.from_numpy(validate_array(value).copy()).double()
        alpha, beta = [torch.from_numpy(constants[key]).double() for key in ('alpha', 'beta')]
        return (tensor * alpha + beta).float().numpy().copy()


def save_graph(nodes, constants, shape, out_shape, source, path, name):
    graph = helper.make_graph(nodes, f'PLACEHOLDER-{name}',
        [helper.make_tensor_value_info('x', onnx.TensorProto.FLOAT, shape)],
        [helper.make_tensor_value_info('y', onnx.TensorProto.FLOAT, out_shape)],
        [numpy_helper.from_array(array, key) for key, array in constants.items()])
    model = helper.make_model(graph, opset_imports=list(source.opset_import), ir_version=source.ir_version)
    mark_diagnostic(model)
    onnx.checker.check_model(model, full_check=True)
    if path is not None:
        onnx.save(model, path)
    return model


def promoted_conv_graph(module, shape, source, path):
    out_shape = conv_geometry(module, shape)
    _, channels, height, width = out_shape
    nodes, constants = [], {}
    def constant(name, value, dtype=np.int64):
        constants[name] = np.asarray(value, dtype=dtype)
        return name
    def node(op, inputs, output, **attributes):
        nodes.append(helper.make_node(op, inputs, [output], **attributes))
    py, px = module.padding
    node('Pad', ['x', constant('pads', [0, 0, py, px, 0, 0, py, px]),
                 constant('zero', 0, np.float32)], 'padded', mode='constant')
    node('Cast', ['padded'], 'promoted', to=onnx.TensorProto.DOUBLE)
    slices = []
    for ky in range(module.kernel_size[0]):
        for kx in range(module.kernel_size[1]):
            tag = f'patch-{ky}-{kx}'
            start = [ky * module.dilation[0], kx * module.dilation[1]]
            end = [start[0] + (height - 1) * module.stride[0] + 1,
                   start[1] + (width - 1) * module.stride[1] + 1]
            node('Slice', ['promoted', constant(f'{tag}-starts', start),
                constant(f'{tag}-ends', end), constant(f'{tag}-axes', [2, 3]),
                constant(f'{tag}-steps', module.stride)], tag)
            expanded = f'{tag}-expanded'
            node('Unsqueeze', [tag, constant(f'{tag}-expand', [2])], expanded)
            slices.append(expanded)
    node('Concat', slices, 'patches', axis=2)
    node('Reshape', ['patches', constant('patch-shape', [shape[0],
        module.in_channels * module.kernel_size[0] * module.kernel_size[1], height * width])], 'matrix')
    node('Transpose', ['matrix'], 'positions', perm=[0, 2, 1])
    # Serialize saved float32 bits, promote at runtime; do not store refitted weights.
    constant('weights', module.weight.detach().numpy().reshape(channels, -1).T.copy(), np.float32)
    node('Cast', ['weights'], 'double-weights', to=onnx.TensorProto.DOUBLE)
    node('MatMul', ['positions', 'double-weights'], 'products')
    last = 'products'
    if module.bias is not None:
        constant('bias', module.bias.detach().numpy().copy(), np.float32)
        node('Cast', ['bias'], 'double-bias', to=onnx.TensorProto.DOUBLE)
        node('Add', ['products', 'double-bias'], 'biased')
        last = 'biased'
    node('Transpose', [last], 'channel-first', perm=[0, 2, 1])
    node('Reshape', ['channel-first', constant('out-shape', out_shape)], 'double-result')
    node('Cast', ['double-result'], 'y', to=onnx.TensorProto.FLOAT)
    save_graph(nodes, constants, shape, out_shape, source, path, 'promoted-stem-conv')


def promoted_affine_graph(module, shape, formula, source, path=None):
    if formula not in AFFINE_FORMULAS:
        raise ValueError('unknown promoted affine formula')
    constants = bn_constants(module, formula)
    nodes = [helper.make_node('Cast', [name], [f'double-{name}'], to=onnx.TensorProto.DOUBLE)
             for name in ('x', 'alpha', 'beta')]
    nodes.extend([helper.make_node('Mul', ['double-x', 'double-alpha'], ['product']),
                  helper.make_node('Add', ['product', 'double-beta'], ['sum']),
                  helper.make_node('Cast', ['sum'], ['y'], to=onnx.TensorProto.FLOAT)])
    return save_graph(nodes, constants, shape, shape, source, path, f'promoted-{formula}')


def main(argv=None):
    # Same provenance/input isolation and output handling as ADR-015.
    from .export_replay import main as replay_main
    return replay_main(argv, promoted=True)


if __name__ == '__main__':
    raise SystemExit(main())
