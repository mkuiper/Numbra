"""ADR-024 supplied-graph PLACEHOLDER primitives; diagnostic only, never bundle.

No saved model, dataset, retained observations or baseline inference entry point.
Complete guarded training integration and evidence persistence remain unfinished.
"""

from collections import Counter
import copy
import hashlib
import math

import numpy as np
import onnx
from onnx import helper, numpy_helper
import torch

from .export_batchnorm import mark_diagnostic
from .export_remaining import constant, remaining_plan, validate_node
from .export_remaining_native import same_bits
from .export_remaining_runtime import audit_complete_runtime, specs

NOTICE = 'PLACEHOLDER bounded arithmetic diagnostic only; never bundle'
PREFIX = 'PLACEHOLDER-arithmetic/'
RECIPES = {
    'HardSwish': ('divide', 'reciprocal'),
    'HardSigmoid': ('divide', 'reciprocal'),
    'ReduceMean': ('sum_divide', 'double_mean'),
    'GlobalAveragePool': ('sum_divide', 'double_mean'),
    'Gemm': ('constant_parameters',),
}


def geometry(source, node, variant):
    """Bind a declared expression to one exact original node and static geometry."""
    if ([(o.domain, o.version) for o in source.opset_import] != [('', 17)]
            or source.functions or source.training_info or source.graph.sparse_initializer):
        raise ValueError('bounded arithmetic requires plain opset 17 inference')
    onnx.checker.check_model(source, full_check=True)
    validate_node(node)
    if (node.op_type not in RECIPES or variant not in RECIPES[node.op_type]
            or sum(n.SerializeToString() == node.SerializeToString() for n in source.graph.node) != 1):
        raise ValueError('bounded arithmetic node/recipe scope mismatch')
    boundaries = specs(source)
    names = [*node.input, *node.output]
    if (len(set(names)) != len(names) or any(name.startswith(PREFIX) for name in names)
            or any(boundaries[name]['dtype'] != 'float32' for name in names)):
        raise ValueError('bounded arithmetic requires distinct float32 boundaries')
    shapes = [boundaries[name]['shape'] for name in names]
    x, y = shapes[0], shapes[-1]
    if not x or not y or any(size <= 0 for shape in shapes for size in shape):
        raise ValueError('bounded arithmetic requires positive nonscalar geometry')
    if node.op_type in ('HardSwish', 'HardSigmoid'):
        valid = x == y
    elif node.op_type in ('ReduceMean', 'GlobalAveragePool'):
        valid = len(x) == 4 and y == [x[0], x[1], 1, 1]
        count = math.prod(x[2:])
        # The divisor itself must preserve the exact integer count in float32.
        if count > 2**24 or int(np.float32(count)) != count:
            raise ValueError('bounded reduction count is not exact float32')
    else:
        weight, bias = shapes[1:3]
        valid = (len(x) == len(weight) == 2 and bias == [weight[0]]
                 and x[1] == weight[1] and y == [x[0], weight[0]])
        for name in node.input[1:]:
            constant(source, name)
    if not valid:
        raise ValueError('bounded arithmetic unsupported geometry')
    return x, y


def constant_closure(source, names):
    """Copy the original ordered initializer/Constant/Identity dependency closure."""
    needed, selected = set(), set()
    producers = {name: node for node in source.graph.node for name in node.output}
    initializers = {item.name: item for item in source.graph.initializer}
    inputs = {value.name for value in source.graph.input}

    def visit(name):
        constant(source, name)  # Reject ambiguity, cycles, external and nonfinite data.
        if name in inputs:
            raise ValueError('head parameter cannot be an overridable graph input')
        if name in needed:
            return
        needed.add(name)
        if name in initializers:
            return
        node = producers[name]
        selected.add(node.output[0])
        for operand in node.input:
            visit(operand)

    for name in names:
        visit(name)
    return ([copy.deepcopy(n) for n in source.graph.node if n.output[0] in selected],
            [copy.deepcopy(i) for i in source.graph.initializer if i.name in needed])


def arithmetic_graph(source, node, variant):
    """Build one fixed recipe without executing it or reading any observations."""
    x_shape, y_shape = geometry(source, node, variant)
    x, y = node.input[0], node.output[0]
    nodes, constants = [], []

    def value(name, scalar, dtype=np.float32):
        name = PREFIX + name
        constants.append(numpy_helper.from_array(np.asarray(scalar, dtype=dtype), name))
        return name

    def operation(op, operands, output, **attributes):
        nodes.append(helper.make_node(op, operands, [output], name=PREFIX + output,
                                      **attributes))
        return output

    def intermediate(name):
        return PREFIX + name

    if node.op_type == 'Gemm':
        nodes, constants = constant_closure(source, node.input[1:])
        if x in {name for n in nodes for name in (*n.input, *n.output)} | {i.name for i in constants}:
            raise ValueError('head activation aliases parameter closure')
        nodes.append(copy.deepcopy(node))
    elif node.op_type in ('HardSwish', 'HardSigmoid'):
        three, zero, six = [value(name, scalar) for name, scalar in
                            (('three', 3), ('zero', 0), ('six', 6))]
        shifted = operation('Add', [x, three], intermediate('shifted'))
        gate = operation('Clip', [shifted, zero, six], intermediate('clamped'))
        if node.op_type == 'HardSwish':
            gate = operation('Mul', [x, gate], intermediate('product'))
        if variant == 'divide':
            operation('Div', [gate, six], y)
        else:
            reciprocal = value('reciprocal', np.float32(1 / 6))
            operation('Mul', [gate, reciprocal], y)
    elif variant == 'sum_divide':
        axes = value('axes', [2, 3], np.int64)
        total = operation('ReduceSum', [x, axes], intermediate('sum'), keepdims=1)
        count = value('count', math.prod(x_shape[2:]))
        operation('Div', [total, count], y)
    else:
        promoted = operation('Cast', [x], intermediate('double-input'), to=onnx.TensorProto.DOUBLE)
        mean = operation('ReduceMean', [promoted], intermediate('double-mean'), axes=[2, 3], keepdims=1)
        operation('Cast', [mean], y, to=onnx.TensorProto.FLOAT)
    graph = helper.make_graph(nodes, 'PLACEHOLDER-bounded-' + node.op_type + '-' + variant,
        [helper.make_tensor_value_info(x, onnx.TensorProto.FLOAT, x_shape)],
        [helper.make_tensor_value_info(y, onnx.TensorProto.FLOAT, y_shape)], constants)
    result = helper.make_model(graph, opset_imports=list(source.opset_import), ir_version=source.ir_version)
    mark_diagnostic(result)
    onnx.checker.check_model(result, full_check=True)
    return result


def eager_expression(source, node, variant, operands):
    """Independent eager recipe on supplied operands; never captured native output."""
    _, shape = geometry(source, node, variant)
    if len(operands) != len(node.input):
        raise ValueError('bounded expression operand count mismatch')
    boundaries = specs(source)
    for name, array in zip(node.input, operands):
        if (not isinstance(array, np.ndarray) or array.dtype != np.float32
                or list(array.shape) != boundaries[name]['shape'] or not np.isfinite(array).all()):
            raise ValueError('bounded expression operand specification mismatch')
    if node.op_type == 'Gemm' and any(not same_bits(array, constant(source, name))
                                     for name, array in zip(node.input[1:], operands[1:])):
        raise ValueError('bounded expression changed head parameter bits')
    with torch.inference_mode():
        x, *rest = [torch.from_numpy(array.copy()) for array in operands]
        if node.op_type == 'Gemm':
            result = torch.nn.functional.linear(x, *rest)
        elif node.op_type in ('HardSwish', 'HardSigmoid'):
            gate = torch.clamp(x + torch.tensor(3., dtype=torch.float32), 0., 6.)
            if node.op_type == 'HardSwish':
                gate = x * gate
            result = gate / 6. if variant == 'divide' else gate * torch.tensor(np.float32(1 / 6))
        elif variant == 'sum_divide':
            result = x.sum((2, 3), keepdim=True) / torch.tensor(np.float32(math.prod(x.shape[2:])))
        else:
            result = x.double().mean((2, 3), keepdim=True).float()
    array = result.numpy().copy()
    if array.dtype != np.float32 or list(array.shape) != shape or not np.isfinite(array).all():
        raise ValueError('bounded expression nonfinite/invalid output')
    return array


def audit_arithmetic_graph(source, node, variant, actual, *, runtime=False):
    """Rebuild all declared arithmetic/constants/interfaces before checking runtime."""
    expected = arithmetic_graph(source, node, variant)
    if runtime:
        result = audit_complete_runtime(expected, actual)
    else:
        if actual.SerializeToString() != expected.SerializeToString():
            raise ValueError('bounded serialized arithmetic reconstruction mismatch')
        result = {'status': 'PASS', 'complete_serialized_reconstruction': True}
    return {**result, 'notice': NOTICE, 'native_equivalence': 'UNVERIFIED',
            'whole_model_parity': 'UNVERIFIED'}


def expression_metrics(source, node, variant, operands, actual):
    """Retain signed runtime/eager drift without an equality claim or suppression."""
    expected = eager_expression(source, node, variant, operands)
    if (not isinstance(actual, np.ndarray) or actual.dtype != np.float32
            or actual.shape != expected.shape or not np.isfinite(actual).all()):
        raise ValueError('bounded runtime output specification mismatch')
    delta = actual.astype(np.float64) - expected.astype(np.float64)
    return {'notice': NOTICE, 'status': 'DIAGNOSTIC ONLY',
        'signed_min': float(delta.min()), 'signed_max': float(delta.max()),
        'signed_mean': float(delta.mean()), 'max_absolute_error': float(np.abs(delta).max()),
        'mean_absolute_error': float(np.abs(delta).mean()), 'exact_bits': same_bits(actual, expected),
        'reference': 'independent eager recipe; not captured native saved output'}


def complete_arithmetic_scope(model, preserved, rounded):
    """Mandatory complete ordered scope, with no configurable layer/input subset.

    Existing source/control/head/state validation runs before building any recipe.
    This does not load prior observations or establish provenance for a training run.
    """
    plan = remaining_plan(model, preserved, rounded)
    scope = []
    for record, node in zip(plan['nodes'], preserved.graph.node):
        if node.op_type not in RECIPES:
            continue
        graphs = [arithmetic_graph(preserved, node, variant) for variant in RECIPES[node.op_type]]
        scope.append({'position': record['position'], 'name': node.name,
            'operator': node.op_type, 'inputs': list(node.input), 'outputs': list(node.output),
            'node_sha256': record['node_sha256'],
            'recipes': [{'name': variant,
                'graph_sha256': hashlib.sha256(graph.SerializeToString()).hexdigest()}
                for variant, graph in zip(RECIPES[node.op_type], graphs)]})
    if sum(r['operator'] == 'Gemm' for r in scope) != 1:
        raise ValueError('bounded complete scope requires unique saved head')
    return {'notice': NOTICE, 'status': 'STATIC SCOPE ONLY', 'decision': 'ADR-024',
        'ordered_nodes': scope, 'operator_counts': dict(Counter(r['operator'] for r in scope)),
        'graph_count': sum(len(r['recipes']) for r in scope),
        'unchanged_controls': plan['node_counts'], 'baseline_inference': False,
        'training_observation_replay': 'UNIMPLEMENTED', 'deployment_selection': False}
