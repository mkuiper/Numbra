"""ADR-018 joint training-only PLACEHOLDER stem/BN arithmetic; never bundle."""

from collections import Counter
import hashlib

import numpy as np
import onnx
from onnx import helper, numpy_helper

from .export_batchnorm import mark_diagnostic
from .export_precision import promoted_conv_graph
from .export_promoted_bn import constant_array, coefficient_hash
from .export_replay import selected_operators
from .training import tensor_hash

PREFIX = 'PLACEHOLDER-promoted-stem-'


def substitute_stem(model, source, target):
    """Embed the already tested ADR-016 expression at the saved stem boundary."""
    if any(module.training for module in model.modules()):
        raise ValueError('joint substitution requires every module in eval mode')
    graph = onnx.load(source, load_external_data=False)
    name, module, stem = selected_operators(model, graph)[0]
    if (len(graph.graph.input) != 1 or stem.input[0] != graph.graph.input[0].name
            or len(stem.output) != 1 or stem.domain):
        raise ValueError('saved stem must connect directly to the single graph input')
    shape = [dim.dim_value for dim in graph.graph.input[0].type.tensor_type.shape.dim]
    if graph.graph.input[0].type.tensor_type.elem_type != onnx.TensorProto.FLOAT:
        raise ValueError('saved stem requires float32 graph input')
    expected_attributes = {'kernel_shape': list(module.kernel_size), 'strides': list(module.stride),
        'dilations': list(module.dilation), 'pads': list(module.padding) * 2, 'group': module.groups}
    actual = {attr.name: helper.get_attribute_value(attr) for attr in stem.attribute}
    if actual.pop('auto_pad', b'NOTSET') != b'NOTSET' or actual != expected_attributes:
        raise ValueError('saved stem geometry mismatch')
    parameters = [module.weight] + ([] if module.bias is None else [module.bias])
    if len(stem.input) != len(parameters) + 1:
        raise ValueError('saved stem parameter count mismatch')
    for key, parameter in zip(stem.input[1:], parameters):
        array = constant_array(graph, key)
        expected = parameter.detach().numpy()
        if (array.dtype != np.float32 or expected.dtype != np.float32
                or array.shape != expected.shape or not np.array_equal(array, expected)
                or not np.isfinite(array).all()):
            raise ValueError('saved stem parameter mismatch or non-finite value')
    names = [item.name for item in graph.graph.initializer]
    names += [value.name for value in (*graph.graph.input, *graph.graph.output, *graph.graph.value_info)]
    names += [value for node in graph.graph.node for value in (*node.input, *node.output, node.name)]
    if any(value.startswith(PREFIX) for value in names):
        raise ValueError('promoted stem namespace collision')
    before = tensor_hash(model.state_dict())
    # Kept as a labelled private artifact, with the exact previously tested recipe.
    isolated = target.with_name(target.stem + '-isolated.onnx')
    promoted_conv_graph(module, shape, graph, isolated)
    expression = onnx.load(isolated, load_external_data=False)
    def rename(value):
        return stem.input[0] if value == 'x' else stem.output[0] if value == 'y' else PREFIX + value
    for position, node in enumerate(expression.graph.node):
        # ORT serializes this opset-17 default even with optimisation disabled.
        # Declare it explicitly so the audit still compares exact node bytes.
        if node.op_type == 'Reshape':
            node.attribute.append(helper.make_attribute('allowzero', 0))
        node.name = PREFIX + str(position)
        node.input[:] = [rename(value) for value in node.input]
        node.output[:] = [rename(value) for value in node.output]
    for item in expression.graph.initializer:
        item.name = rename(item.name)
    record = {'module': name, 'original_node': stem.name, 'input': stem.input[0],
        'output': stem.output[0], 'input_shape': shape,
        'expression_node_sha256': {node.name: hashlib.sha256(node.SerializeToString()).hexdigest()
                                   for node in expression.graph.node},
        'constants': {item.name: {'dtype': str(numpy_helper.to_array(item).dtype),
            'shape': list(numpy_helper.to_array(item).shape),
            'sha256': coefficient_hash(numpy_helper.to_array(item))}
            for item in expression.graph.initializer}}
    replaced = [list(expression.graph.node) if node == stem else [node] for node in graph.graph.node]
    del graph.graph.node[:]
    graph.graph.node.extend(node for group in replaced for node in group)
    graph.graph.initializer.extend(expression.graph.initializer)
    mark_diagnostic(graph)
    onnx.checker.check_model(graph, full_check=True)
    if tensor_hash(model.state_dict()) != before:
        raise ValueError('stem substitution changed saved model state')
    onnx.save(graph, target)
    audit_stem_graph(target, source, record, serialized=True)
    return record


def audit_stem_graph(path, source, record, *, serialized=False):
    """Audit actual expression nodes, geometry/weight bits and original counts."""
    graph, original = [onnx.load(item, load_external_data=False) for item in (path, source)]
    nodes = [node for node in graph.graph.node if node.name.startswith(PREFIX)]
    actual = {node.name: hashlib.sha256(node.SerializeToString()).hexdigest() for node in nodes}
    if len(nodes) != len(actual) or actual != record['expression_node_sha256']:
        raise ValueError('promoted stem arithmetic/cast audit mismatch')
    for name, expected in record['constants'].items():
        array = constant_array(graph, name)
        if {'dtype': str(array.dtype), 'shape': list(array.shape),
                'sha256': coefficient_hash(array)} != expected:
            raise ValueError('promoted stem constant audit mismatch')
    original_ops = Counter(node.op_type for node in original.graph.node)
    actual_ops = Counter(node.op_type for node in graph.graph.node)
    if any(actual_ops[op] != original_ops[op] + offset
           for op, offset in (('Conv', -1), ('MatMul', 1), ('Gemm', 0))):
        raise ValueError('promoted stem Conv/head operator count mismatch')
    if serialized:
        retained = [node.SerializeToString() for node in graph.graph.node if not node.name.startswith(PREFIX)]
        expected = [node.SerializeToString() for node in original.graph.node if node.name != record['original_node']]
        constants = [item.SerializeToString() for item in original.graph.initializer]
        if (retained != expected
                or [item.SerializeToString() for item in graph.graph.initializer
                    if not item.name.startswith(PREFIX)] != constants
                or graph.graph.input != original.graph.input or graph.graph.output != original.graph.output):
            raise ValueError('stem substitution changed retained nodes/constants/interface')
    return {'notice': 'PLACEHOLDER diagnostic graph; never bundle', 'status': 'PASS',
        'expression_nodes': len(nodes), 'constants': len(record['constants']),
        'one_conv_replaced_by_matmul': True, 'saved_float32_bits_and_boundary': True,
        'other_serialized_nodes_constants_interface_retained': serialized}


def main(argv=None):
    from .export_promoted_bn import main as bn_main
    return bn_main(argv, joint_stem=True)


if __name__ == '__main__':
    raise SystemExit(main())
