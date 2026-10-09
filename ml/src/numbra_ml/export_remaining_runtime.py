"""ADR-023 complete PLACEHOLDER runtime audits and taps; never bundle.

These primitives receive graphs/tensors from a caller. They do not load a saved
model, read datasets, choose an input scope or establish baseline parity. The
guarded training runner and independent ordered-detail audit remain separate.
"""

from collections import Counter
import hashlib

import numpy as np
import onnx
from onnx import helper, numpy_helper
import onnxruntime as ort

from .export import session_options
from .export_remaining import attributes
from .export_remaining_native import same_bits, tap_complete_graph

NOTICE = 'PLACEHOLDER complete runtime diagnostic only; never bundle'

# Only explicit defaults observed in the pinned disabled runtime on generated
# fixtures. This is expression normalisation, never a numerical equality claim.
DEFAULTS = {'Conv': {'auto_pad': b'NOTSET'},
            'HardSigmoid': {'alpha': float(np.float32(0.2)), 'beta': 0.5},
            'Gemm': {'alpha': 1., 'beta': 1., 'transA': 0, 'transB': 0}}


def specs(graph):
    """Static original/runtime boundaries, including internal double BN values."""
    inferred = onnx.shape_inference.infer_shapes(graph, strict_mode=True, data_prop=True)
    result = {}
    types = {onnx.TensorProto.FLOAT: 'float32', onnx.TensorProto.DOUBLE: 'float64',
             onnx.TensorProto.INT64: 'int64'}
    for item in (*inferred.graph.input, *inferred.graph.value_info, *inferred.graph.output):
        t = item.type.tensor_type
        if (t.elem_type not in types or not t.HasField('shape')
                or any(not d.HasField('dim_value') or d.dim_value <= 0 for d in t.shape.dim)):
            raise ValueError('complete runtime requires static supported boundaries')
        value = {'dtype': types[t.elem_type], 'shape': [d.dim_value for d in t.shape.dim]}
        if item.name in result and result[item.name] != value:
            raise ValueError('complete runtime inconsistent boundary specification')
        result[item.name] = value
    for item in inferred.graph.initializer:
        value = tensor(item)
        spec = {'dtype': str(value.dtype), 'shape': list(value.shape)}
        if item.name in result and result[item.name] != spec:
            raise ValueError('complete runtime inconsistent constant specification')
        result[item.name] = spec
    return result


def tensor(item):
    if item.data_location == onnx.TensorProto.EXTERNAL or item.external_data:
        raise ValueError('complete runtime external constants forbidden')
    value = numpy_helper.to_array(item).copy()
    if value.dtype not in (np.dtype('float32'), np.dtype('float64'), np.dtype('int64')) or not np.isfinite(value).all():
        raise ValueError('complete runtime unsupported constant type/value')
    return value


def audit_complete_runtime(original, runtime):
    """Audit *every* expression/constant/boundary of a disabled runtime graph.

    Allow removal of directly unused initializers, exact tensor Constant lowering,
    attribute order/default materialisation and the fixed HardSwish function
    expansion. Everything else, including every
    rounded-BN Cast/Mul/Add and coefficient bit, must remain unchanged. Runtime
    topological scheduling may reorder independent nodes; operand order and
    connectivity must stay exact. Generated HardSwish names carry no authority.
    """
    for graph in (original, runtime):
        onnx.checker.check_model(graph, full_check=True)
        if (graph.functions or graph.training_info or graph.graph.sparse_initializer
                or [(o.domain, o.version) for o in graph.opset_import if not o.domain] != [('', 17)]):
            raise ValueError('complete runtime graph protocol mismatch')
    if ([v.SerializeToString() for v in runtime.graph.input]
            != [v.SerializeToString() for v in original.graph.input]
            or [v.SerializeToString() for v in runtime.graph.output]
            != [v.SerializeToString() for v in original.graph.output]):
        raise ValueError('complete runtime input/output interface mismatch')
    expected = {item.name: tensor(item) for item in original.graph.initializer}
    if len(expected) != len(original.graph.initializer):
        raise ValueError('complete runtime duplicate original constants')
    source_nodes, lowered = [], []
    for node in original.graph.node:
        if node.op_type != 'Constant':
            source_nodes.append(node)
            continue
        a = attributes(node)
        if (node.domain or node.input or len(node.output) != 1 or set(a) != {'value'}
                or node.output[0] in expected):
            raise ValueError('complete runtime unsupported Constant lowering')
        expected[node.output[0]] = tensor(a['value'])
        lowered.append(node.output[0])
    actual = {item.name: tensor(item) for item in runtime.graph.initializer}
    # Disabled ORT still removes unused initializers. Only an original initializer
    # with no node consumer and no input/output role may disappear. Constant
    # lowering, Identity aliases and every tapped parameter remain mandatory.
    used = {name for node in original.graph.node for name in node.input}
    used.update(value.name for value in (*original.graph.input, *original.graph.output))
    removable = {item.name for item in original.graph.initializer if item.name not in used}
    removed = expected.keys() - actual.keys()
    if (len(actual) != len(runtime.graph.initializer) or actual.keys() - expected.keys()
            or removed - removable
            or any(not same_bits(expected[key], value) for key, value in actual.items())):
        raise ValueError('complete runtime constant scope/bits mismatch')

    nodes, checked, expanded, gates = list(runtime.graph.node), set(), [], {}
    producers = {name: (index, node) for index, node in enumerate(nodes) for name in node.output}
    if len(producers) != sum(len(n.output) for n in nodes):
        raise ValueError('complete runtime duplicate producers')
    original_specs = specs(original)
    for node in source_nodes:
        if len(node.output) != 1 or node.output[0] not in producers:
            raise ValueError('complete runtime missing expression')
        index, actual_node = producers[node.output[0]]
        if index in checked:
            raise ValueError('complete runtime reused expression')
        if node.op_type == 'HardSwish':
            if (node.domain or node.attribute or len(node.input) != 1 or len(node.output) != 1
                    or len(actual_node.input) != 2 or actual_node.input[1] not in producers):
                raise ValueError('complete runtime invalid HardSwish scope')
            gate_index, gate = producers[actual_node.input[1]]
            mul = actual_node
            if (gate.domain or gate.op_type != 'HardSigmoid' or list(gate.input) != list(node.input)
                    or len(gate.output) != 1 or gate.output[0] in original_specs or gate.output[0] in gates
                    or attributes(gate) != {'alpha': float(np.float32(1 / 6)), 'beta': 0.5}
                    or mul.domain or mul.op_type != 'Mul' or mul.attribute
                    or list(mul.input) != [node.input[0], gate.output[0]]
                    or list(mul.output) != list(node.output) or gate_index in checked or gate_index == index):
                raise ValueError('complete runtime HardSwish expression mismatch')
            gates[gate.output[0]] = original_specs[node.input[0]]
            expanded.append(node.name)
            checked.update((gate_index, index))
            continue
        defaults = DEFAULTS.get(node.op_type, {})
        if (actual_node.name != node.name or actual_node.domain != node.domain
                or node.domain or actual_node.op_type != node.op_type
                or list(actual_node.input) != list(node.input) or list(actual_node.output) != list(node.output)
                or {**defaults, **attributes(actual_node)} != {**defaults, **attributes(node)}):
            raise ValueError('complete runtime ordered arithmetic/connectivity mismatch')
        checked.add(index)
    if len(checked) != len(nodes):
        raise ValueError('complete runtime extra expression')
    expected_specs = {key: value for key, value in original_specs.items() if key not in removed}
    if specs(runtime) != {**expected_specs, **gates}:
        raise ValueError('complete runtime boundary scope/type/shape mismatch')
    return {'notice': NOTICE, 'status': 'PASS', 'all_expressions_constants_boundaries': True,
            'original_nodes': len(original.graph.node), 'runtime_nodes': len(nodes),
            'operator_counts': dict(Counter(n.op_type for n in nodes)),
            'runtime_node_order': [n.name for n in nodes],
            'lowered_constant_outputs': lowered, 'expanded_hardswish_nodes': expanded,
            'removed_unused_initializers': sorted(removed),
            'unused_domain_imports': {o.domain: o.version for o in runtime.opset_import if o.domain},
            'serialized_sha256': hashlib.sha256(original.SerializeToString()).hexdigest(),
            'runtime_sha256': hashlib.sha256(runtime.SerializeToString()).hexdigest(),
            'numerical_equivalence': 'UNVERIFIED; must measure original and tapped outputs separately'}


class CompleteRuntime:
    """Audited original/tapped sessions; no dataset or baseline entry point."""

    def __init__(self, source, plan, output):
        if not output.is_dir() or any(output.iterdir()):
            raise ValueError('complete runtime output must be a fresh empty directory')
        tapped, names = tap_complete_graph(source, plan)
        self.sessions, self.audit = {}, {}
        self.source, self.tapped, self.names, self.plan = source, tapped, names, plan
        self.boundaries = {name: spec for r in plan['nodes'] for name, spec in r['boundaries'].items()}
        self.constants = {i.name: tensor(i) for i in source.graph.initializer}
        # Include original Constant/Identity aliases and unchanged original
        # parameters retained in the rounded graph, using the static tap values.
        from .export_remaining import constant
        producers = {v: n for n in source.graph.node for v in n.output}
        for name in names:
            if name in producers and producers[name].op_type in ('Constant', 'Identity'):
                self.constants[name] = constant(source, name)
        for kind, graph in (('original', source), ('tapped', tapped)):
            path = output / f'PLACEHOLDER-{kind}.onnx'
            runtime_path = output / f'PLACEHOLDER-{kind}-runtime.onnx'
            onnx.save(graph, path)
            options = session_options('disabled')
            options.optimized_model_filepath = str(runtime_path)
            session = ort.InferenceSession(str(path), sess_options=options, providers=['CPUExecutionProvider'])
            self.audit[kind] = audit_complete_runtime(graph, onnx.load(runtime_path, load_external_data=False))
            self.sessions[kind] = session

    def run(self, value):
        """Return separately measured logits and all validated original operands."""
        name = self.source.graph.input[0].name
        if (not isinstance(value, np.ndarray) or value.dtype != np.float32
                or not np.isfinite(value).all()
                or self.boundaries[name] != {'dtype': 'float32', 'shape': list(value.shape)}):
            raise ValueError('complete runtime input specification mismatch')
        # ORT can expose an output which aliases a fed input. Retain both feeds
        # until all outputs have been validated/copied; a temporary dict would
        # free the input backing a pass-through tap after session.run returns.
        original_feed, tapped_feed = {name: value.copy()}, {name: value.copy()}
        original, = self.sessions['original'].run(None, original_feed)
        outputs = self.sessions['tapped'].run(None, tapped_feed)
        if len(outputs) != len(self.tapped.graph.output):
            raise ValueError('complete runtime output count mismatch')
        values = dict(zip([o.name for o in self.tapped.graph.output], outputs))
        if set(values) != set(self.names):
            raise ValueError('complete runtime output scope mismatch')
        for key, actual in values.items():
            if (not isinstance(actual, np.ndarray) or not np.isfinite(actual).all()
                    or self.boundaries[key] != {'dtype': str(actual.dtype), 'shape': list(actual.shape)}):
                raise ValueError('complete runtime output specification mismatch')
            if key in self.constants and not same_bits(actual, self.constants[key]):
                raise ValueError('complete runtime tapped constant bits mismatch')
        if not same_bits(value, values[name]):
            raise ValueError('complete runtime tapped input bits mismatch')
        tapped = values[self.source.graph.output[0].name]
        if (not isinstance(original, np.ndarray) or original.dtype != np.float32
                or not np.isfinite(original).all() or original.shape != tapped.shape):
            raise ValueError('complete runtime original logit specification mismatch')
        delta = tapped.astype(np.float64) - original.astype(np.float64)
        return {'notice': NOTICE, 'status': 'DIAGNOSTIC ONLY',
                'original_logit': original.copy(), 'tapped_logit': tapped.copy(),
                'values': {key: v.copy() for key, v in values.items()},
                'instrumentation': {'exact_bits': same_bits(original, tapped),
                    'signed_min': float(delta.min()), 'signed_max': float(delta.max()),
                    'signed_mean': float(delta.mean()), 'max_absolute': float(np.abs(delta).max()),
                    'mean_absolute': float(np.abs(delta).mean())}}
