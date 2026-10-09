"""ADR-023 native PLACEHOLDER boundary capture primitives; never bundle.

This module has no baseline replay CLI. It binds the complete saved graph before
inference and observes actual native calls without replacing the saved forward.
Training-only two-graph replay and independent row auditing remain separate work.
"""

from collections import Counter
import copy
import hashlib

import numpy as np
import onnx
from onnx import helper
import torch
from torch import nn
from torch.nn import functional as F
from torch.overrides import TorchFunctionMode
from timm.models._efficientnet_blocks import DepthwiseSeparableConv, InvertedResidual, SqueezeExcite

from .export_batchnorm import mark_diagnostic
from .export_complete_replay import complete_operators
from .export_remaining import constant, recipe, remaining_plan, tensor_specs
from .training import FeatureHead, tensor_hash

NOTICE = 'PLACEHOLDER native capture diagnostic only; never bundle'


def exporter_scope(name):
    """Exact legacy exporter module scopes, including nested Sequential keys."""
    parts, last = [], ''
    for key in name.split('.'):
        last = last + '.' + key if key.isdecimal() else key
        parts.append(last)
    return '/' + '/'.join(parts)


def native_plan(model, source, rounded):
    """One-to-one native owner/operator mapping for every computational node."""
    static = remaining_plan(model, source, rounded)
    modules = list(model.named_modules(remove_duplicate=False))
    if (any(m.training for _, m in modules)
            or len({id(m) for _, m in modules}) != len(modules)):
        raise ValueError('native capture requires unshared eval modules')
    owners = {exporter_scope(name): (name, m) for name, m in modules if name}
    if len(owners) != len(modules) - 1:
        raise ValueError('ambiguous native exporter scopes')
    controls = {node.name: (name, module) for name, module, node in complete_operators(model, source)}
    classes = {'Relu': (nn.ReLU,), 'HardSwish': (nn.Hardswish,), 'HardSigmoid': (nn.Hardsigmoid,),
               'ReduceMean': (SqueezeExcite,), 'Mul': (SqueezeExcite,),
               'Add': (InvertedResidual, DepthwiseSeparableConv),
               'GlobalAveragePool': (nn.AdaptiveAvgPool2d,), 'Flatten': (nn.Flatten,),
               'Sub': (FeatureHead,), 'Div': (FeatureHead,), 'Gemm': (nn.Linear,),
               'Squeeze': (FeatureHead,)}
    records, keys = [], set()
    for item, node in zip(static['nodes'], source.graph.node):
        if item['category'] == 'constant_or_alias':
            continue
        scope, suffix = node.name.rsplit('/', 1)
        if suffix != node.op_type or scope not in owners:
            raise ValueError('unmapped native node scope/operator')
        name, module = owners[scope]
        if node.name in controls:
            if controls[node.name] != (name, module):
                raise ValueError('native control owner mismatch')
        elif type(module) not in classes[node.op_type]:
            raise ValueError('unsupported native remaining owner type')
        if ((node.op_type == 'Flatten' and (module.start_dim, module.end_dim) != (1, -1))
                or (node.op_type == 'GlobalAveragePool' and module.output_size not in (1, (1, 1)))
                or (node.op_type == 'Add' and not module.has_skip)):
            raise ValueError('native remaining owner geometry mismatch')
        key = (name, node.op_type)
        if key in keys:
            raise ValueError('ambiguous native owner/operator mapping')
        keys.add(key)
        records.append({**item, 'native_owner': name,
                        'native_type': type(module).__module__ + '.' + type(module).__qualname__})
    return {'notice': NOTICE, 'status': 'STATIC NATIVE MAPPING ONLY',
            'nodes': records, 'operator_counts': dict(Counter(r['operator'] for r in records)),
            'all_computational_nodes_mapped': True, 'baseline_inference': False,
            'serialized_graph_sha256': {name: hashlib.sha256(g.SerializeToString()).hexdigest()
                                         for name, g in (('preserved', source), ('rounded', rounded))}}


def array(value):
    if (not isinstance(value, torch.Tensor) or value.device.type != 'cpu'
            or value.dtype != torch.float32 or not torch.isfinite(value).all()):
        raise ValueError('native capture requires finite CPU float32 tensor')
    return value.detach().contiguous().numpy().copy()


def same_bits(before, after):
    return (before.dtype == after.dtype and before.shape == after.shape
            and before.tobytes() == after.tobytes())


def bind(args, kwargs, names, defaults):
    if len(args) > len(names) or kwargs.keys() - set(names):
        raise ValueError('unsupported native call arguments')
    result = dict(defaults)
    for name, value in zip(names, args):
        if name in kwargs:
            raise ValueError('duplicate native call argument')
        result[name] = value
    result.update(kwargs)
    if set(result) != set(names):
        raise ValueError('missing native call argument')
    return result


# Match function objects, never string names or a favourable event subset.
FUNCTIONS = {
    F.relu: ('Relu', ('input', 'inplace'), {'inplace': False}),
    F.hardswish: ('HardSwish', ('input', 'inplace'), {'inplace': False}),
    F.hardsigmoid: ('HardSigmoid', ('input', 'inplace'), {'inplace': False}),
    torch.Tensor.mean: ('ReduceMean', ('input', 'dim', 'keepdim', 'dtype'), {'keepdim': False, 'dtype': None}),
    F.adaptive_avg_pool2d: ('GlobalAveragePool', ('input', 'output_size'), {}),
    torch.Tensor.flatten: ('Flatten', ('input', 'start_dim', 'end_dim'), {'start_dim': 0, 'end_dim': -1}),
    torch.flatten: ('Flatten', ('input', 'start_dim', 'end_dim'), {'start_dim': 0, 'end_dim': -1}),
    torch.Tensor.__mul__: ('Mul', ('input', 'other'), {}),
    torch.Tensor.__add__: ('Add', ('input', 'other'), {}),
    torch.Tensor.__sub__: ('Sub', ('input', 'other'), {}),
    torch.Tensor.__truediv__: ('Div', ('input', 'other'), {}),
    # Python arithmetic dispatches these Tensor methods in the pinned PyTorch.
    torch.Tensor.mul: ('Mul', ('input', 'other'), {}),
    torch.Tensor.add: ('Add', ('input', 'other'), {}),
    torch.Tensor.sub: ('Sub', ('input', 'other'), {}),
    torch.Tensor.div: ('Div', ('input', 'other'), {}),
    F.linear: ('Gemm', ('input', 'weight', 'bias'), {'bias': None}),
    torch.Tensor.squeeze: ('Squeeze', ('input', 'dim'), {}),
    F.conv2d: ('Conv', ('input', 'weight', 'bias', 'stride', 'padding', 'dilation', 'groups'),
               {'bias': None, 'stride': 1, 'padding': 0, 'dilation': 1, 'groups': 1}),
    F.batch_norm: ('BatchNormalization', ('input', 'running_mean', 'running_var', 'weight', 'bias',
                                         'training', 'momentum', 'eps'),
                   {'weight': None, 'bias': None, 'training': False, 'momentum': 0.1, 'eps': 1e-5}),
}


def native_operands(op, call, module, node, source):
    """Copy every actual call operand; validate native settings before execution."""
    x = call['input']
    if op in ('Relu', 'HardSwish', 'HardSigmoid'):
        if type(call['inplace']) is not bool or call['inplace'] != module.inplace:
            raise ValueError('native activation setting mismatch')
    elif op == 'ReduceMean':
        if tuple(call['dim']) != (2, 3) or call['keepdim'] is not True or call['dtype'] is not None:
            raise ValueError('native reduction setting mismatch')
    elif op == 'GlobalAveragePool':
        if call['output_size'] not in (1, (1, 1)):
            raise ValueError('native pool setting mismatch')
    elif op == 'Flatten':
        if (call['start_dim'], call['end_dim']) != (1, -1):
            raise ValueError('native flatten setting mismatch')
    elif op == 'Conv':
        for name in ('stride', 'padding', 'dilation'):
            value = call[name]
            value = (value, value) if isinstance(value, int) else tuple(value)
            if value != getattr(module, name):
                raise ValueError('native Conv call geometry mismatch')
        if call['groups'] != module.groups:
            raise ValueError('native Conv call groups mismatch')
        values = [x, call['weight']] + ([] if module.bias is None else [call['bias']])
        if module.bias is None and call['bias'] is not None:
            raise ValueError('native Conv call bias mismatch')
        return [array(v) for v in values]
    elif op == 'BatchNormalization':
        if call['training'] is not False or call['eps'] != module.eps:
            raise ValueError('native BN call setting mismatch')
        return [array(call[key]) for key in ('input', 'weight', 'bias', 'running_mean', 'running_var')]
    elif op == 'Gemm':
        return [array(v) for v in (x, call['weight'], call['bias'])]
    elif op == 'Squeeze':
        axis = call['dim']
        axes = constant(source, node.input[1])
        if type(axis) is not int or not -x.ndim <= axis < x.ndim or axes.tolist() != [axis % x.ndim]:
            raise ValueError('native squeeze call axes mismatch')
        return [array(x), axes.copy()]
    elif op in ('Mul', 'Add', 'Sub', 'Div'):
        return [array(x), array(call['other'])]
    return [array(x)]


class NativeCapture(TorchFunctionMode):
    """Observe native operations under exact module owners; never re-evaluate them."""

    def __init__(self, model, source, plan, value):
        super().__init__()
        self.model, self.source, self.plan = model, source, plan
        self.modules = dict(model.named_modules())
        self.nodes = {n.name: n for n in source.graph.node}
        self.mapping = {(r['native_owner'], r['operator']): r for r in plan['nodes']}
        self.stack, self.events = [], []
        self.values = {source.graph.input[0].name: value.copy()}
        for node in source.graph.node:
            if node.op_type in ('Constant', 'Identity'):
                self.values[node.output[0]] = constant(source, node.output[0])
        for initializer in source.graph.initializer:
            self.values[initializer.name] = constant(source, initializer.name)
        self.specs = tensor_specs(source)

    def __torch_function__(self, func, types, args=(), kwargs=None):
        if func not in FUNCTIONS:
            return func(*args, **(kwargs or {}))
        op, names, defaults = FUNCTIONS[func]
        key = (self.stack[-1] if self.stack else None, op)
        record = self.mapping.get(key)
        if record is None or len(self.events) >= len(self.plan['nodes']) or record != self.plan['nodes'][len(self.events)]:
            raise ValueError('native capture extra, missing, reordered or unmapped operation')
        call = bind(args, kwargs or {}, names, defaults)
        node = self.nodes[record['name']]
        operands = native_operands(op, call, self.modules[key[0]], node, self.source)
        if len(operands) != len(node.input):
            raise ValueError('native capture operand count mismatch')
        for name, operand in zip(node.input, operands):
            if name not in self.values or not same_bits(operand, self.values[name]):
                raise ValueError('native capture graph operand bits/connectivity mismatch')
        # Copies above precede the native call, including all in-place activations.
        result = func(*args, **(kwargs or {}))
        output = array(result)
        if self.specs[node.output[0]] != {'dtype': 'float32', 'shape': list(output.shape)}:
            raise ValueError('native capture output specification mismatch')
        self.values[node.output[0]] = output.copy()
        self.events.append({'name': node.name, 'operator': op, 'native_owner': key[0],
                            'operands': operands, 'output': output,
                            'native_function': getattr(func, '__module__', 'torch.Tensor') + '.' + func.__qualname__})
        return result


def capture_native(model, source, rounded, value):
    """Copy complete graph boundaries on one supplied diagnostic tensor.

    Caller is responsible for the predeclared training-only baseline input scope.
    This primitive does not read datasets, select components or create sessions.
    """
    plan = native_plan(model, source, rounded)
    if (len(source.graph.input) != 1 or not isinstance(value, np.ndarray)
            or value.dtype != np.float32 or not np.isfinite(value).all()
            or tensor_specs(source)[source.graph.input[0].name] != {'dtype': 'float32', 'shape': list(value.shape)}):
        raise ValueError('native capture input specification mismatch')
    if any(m._forward_hooks or m._forward_pre_hooks for m in model.modules()):
        raise ValueError('native capture requires no pre-existing forward hooks')
    before, original = tensor_hash(model.state_dict()), value.copy()
    capture, handles = NativeCapture(model, source, plan, value), []

    def enter(name):
        def hook(module, args):
            capture.stack.append(name)
        return hook

    def leave(name):
        def hook(module, args, output):
            if not capture.stack or capture.stack.pop() != name:
                raise ValueError('native capture module stack mismatch')
        return hook

    try:
        for name, module in model.named_modules():
            handles.append(module.register_forward_pre_hook(enter(name)))
            handles.append(module.register_forward_hook(leave(name), always_call=True))
        with torch.inference_mode(), capture:
            logit = array(model(torch.from_numpy(value.copy())))
        if capture.stack or len(capture.events) != len(plan['nodes']):
            raise ValueError('native capture incomplete operation scope')
        if not same_bits(logit, capture.values[source.graph.output[0].name]):
            raise ValueError('native capture whole-model output mismatch')
        return {'notice': NOTICE, 'status': 'CAPTURE ONLY; NO EXPORT ACCEPTANCE',
                'plan': plan, 'logit': logit, 'events': capture.events}
    finally:
        for handle in handles:
            handle.remove()
        if tensor_hash(model.state_dict()) != before or not same_bits(original, value) or any(m.training for m in model.modules()):
            raise ValueError('native capture changed saved state, input or eval mode')


def native_fidelity(source, capture):
    """Report every independent eager recipe versus captured native output.

    Controls use existing saved-module recipes in the complete runner; this
    helper reports remaining operators only, without suppressing discrepancies.
    """
    nodes = {n.name: n for n in source.graph.node}
    ordered = [n for n in source.graph.node if n.op_type not in ('Constant', 'Identity')]
    if ([e['name'] for e in capture['events']] != [n.name for n in ordered]
            or [e['operator'] for e in capture['events']] != [n.op_type for n in ordered]):
        raise ValueError('native recipe fidelity incomplete operation scope')
    metrics = {}
    for event in capture['events']:
        if event['operator'] in ('Conv', 'BatchNormalization'):
            continue
        expected = recipe(nodes[event['name']], event['operands'])
        output = event['output']
        if (not isinstance(output, np.ndarray) or output.dtype != np.float32
                or not np.isfinite(output).all() or expected.shape != output.shape):
            raise ValueError('native recipe fidelity shape mismatch')
        delta = expected.astype(np.float64) - output.astype(np.float64)
        metrics[event['name']] = {'exact_bits': same_bits(expected, output),
            'signed_min': float(delta.min()), 'signed_max': float(delta.max()),
            'signed_mean': float(delta.mean()), 'max_absolute_error': float(np.abs(delta).max()),
            'mean_absolute_error': float(np.abs(delta).mean())}
    return {'notice': NOTICE, 'status': 'DIAGNOSTIC ONLY', 'remaining_operators': metrics}


def tap_complete_graph(source, plan):
    """Static multi-operand taps with byte-identical computation and constants."""
    graph = copy.deepcopy(source)
    records = plan['nodes']
    selected = {r['name']: r for r in records}
    if not records or len(selected) != len(records):
        raise ValueError('complete tap requires unique nonempty computational scope')
    if hashlib.sha256(source.SerializeToString()).hexdigest() not in plan['serialized_graph_sha256'].values():
        raise ValueError('complete tap original graph binding mismatch')
    # Every unchanged computational node must be present and byte-identical.
    # Replaced BN expressions are independently audited by the complete runner.
    from .export_promoted_bn import PREFIX
    original_outputs = [n.output[0] for n in source.graph.node
        if n.op_type not in ('Constant', 'Identity') and (not n.name.startswith(PREFIX)
            or (n.op_type == 'Cast' and {a.name: helper.get_attribute_value(a) for a in n.attribute}
                == {'to': onnx.TensorProto.FLOAT}))]
    if original_outputs != [r['outputs'][0] for r in records]:
        raise ValueError('complete tap original computational boundary scope mismatch')
    unchanged = [n for n in source.graph.node if n.op_type not in ('Constant', 'Identity')
                 and not n.name.startswith(PREFIX)]
    expected = [r for r in records if r['operator'] != 'BatchNormalization'
                or any(n.name == r['name'] for n in unchanged)]
    if ([n.name for n in unchanged] != [r['name'] for r in expected]
            or any(hashlib.sha256(n.SerializeToString()).hexdigest() != r['node_sha256']
                   for n, r in zip(unchanged, expected))):
        raise ValueError('complete tap computational scope/bits mismatch')
    names = list(dict.fromkeys(name for record in plan['nodes']
                              for name in (*record['inputs'], *record['outputs'])))
    # Rounded graphs contain internal double BN arithmetic. Only the declared
    # original boundaries may be tapped; every one retains its original dtype.
    specs = {}
    for record in plan['nodes']:
        for name, spec in record['boundaries'].items():
            if name in specs and specs[name] != spec:
                raise ValueError('inconsistent complete tap boundary declaration')
            specs[name] = spec
    inferred = onnx.shape_inference.infer_shapes(source, strict_mode=True, data_prop=True)
    actual = {}
    for item in (*inferred.graph.input, *inferred.graph.value_info, *inferred.graph.output):
        if item.name in names:
            t = item.type.tensor_type
            if (t.elem_type not in (onnx.TensorProto.FLOAT, onnx.TensorProto.INT64)
                    or any(not d.HasField('dim_value') or d.dim_value <= 0 for d in t.shape.dim)):
                raise ValueError('complete tap boundary specification mismatch')
            actual[item.name] = {'dtype': 'float32' if t.elem_type == onnx.TensorProto.FLOAT else 'int64',
                                 'shape': [d.dim_value for d in t.shape.dim]}
    for item in inferred.graph.initializer:
        if item.name in names:
            value = constant(inferred, item.name)
            actual[item.name] = {'dtype': str(value.dtype), 'shape': list(value.shape)}
    if actual != specs or set(names) != set(specs):
        raise ValueError('complete tap boundary scope/specification mismatch')
    existing = {o.name for o in graph.graph.output}
    for name in names:
        if name not in existing:
            spec = specs[name]
            dtype = onnx.TensorProto.FLOAT if spec['dtype'] == 'float32' else onnx.TensorProto.INT64
            graph.graph.output.append(helper.make_tensor_value_info(name, dtype, spec['shape']))
    mark_diagnostic(graph)
    onnx.checker.check_model(graph, full_check=True)
    return graph, names
