"""ADR-019 complete training-only PLACEHOLDER replay; never bundle graphs."""

from collections import Counter
import hashlib
import json

import numpy as np
import onnx
from onnx import helper
from torch import nn
from timm.layers import BatchNormAct2d

from . import PLACEHOLDER_NOTICE
from .export import export_environment, graph_report
from .export_batchnorm import DIAGNOSTIC_NOTICE, boundaries
from .export_promoted_bn import constant_array
from .export_replay import aggregate_values, bn_constants, validate_array
from .pretrained import sha256
from .train import json_text


def validate_native_node(module, graph, node):
    """Check every saved bit/geometry, including exporter Identity aliases."""
    if module.training or node.domain or len(node.output) != 1:
        raise ValueError('native replay requires eval/default-domain single output')
    attributes = {item.name: helper.get_attribute_value(item) for item in node.attribute}
    if isinstance(module, nn.Conv2d):
        if module.padding_mode != 'zeros' or isinstance(module.padding, str):
            raise ValueError('native replay requires numeric zero padding')
        expected = {'kernel_shape': list(module.kernel_size), 'strides': list(module.stride),
                    'dilations': list(module.dilation), 'pads': list(module.padding) * 2,
                    'group': module.groups}
        defaults = {'kernel_shape': list(module.kernel_size), 'strides': [1, 1],
                    'dilations': [1, 1], 'pads': [0, 0, 0, 0], 'group': 1}
        if (node.op_type != 'Conv' or attributes.pop('auto_pad', b'NOTSET') != b'NOTSET'
                or attributes.keys() - expected.keys()
                or any(attributes.get(key, defaults[key]) != value for key, value in expected.items())):
            raise ValueError('saved Conv geometry mismatch')
        parameters = [module.weight] + ([] if module.bias is None else [module.bias])
    elif type(module) in (nn.BatchNorm2d, BatchNormAct2d):
        if (node.op_type != 'BatchNormalization' or not module.affine or not module.track_running_stats
                or attributes.keys() - {'epsilon', 'momentum', 'training_mode'}
                or attributes.get('training_mode', 0) != 0
                or np.float32(attributes.get('epsilon', 1e-5)) != np.float32(module.eps)):
            raise ValueError('saved BatchNorm epsilon/mode/buffers mismatch')
        parameters = [module.weight, module.bias, module.running_mean, module.running_var]
    else:
        raise ValueError('unsupported saved replay module')
    if len(node.input) != len(parameters) + 1:
        raise ValueError('saved native parameter count mismatch')
    for key, parameter in zip(node.input[1:], parameters):
        actual, expected = constant_array(graph, key), parameter.detach().numpy()
        if (actual.dtype != np.float32 or expected.dtype != np.float32
                or actual.shape != expected.shape or not np.isfinite(actual).all()
                or actual.tobytes() != np.ascontiguousarray(expected).tobytes()):
            raise ValueError('saved native parameter bits mismatch')


def complete_operators(model, graph):
    """All saved Conv/BN modules in order; reject extra or ambiguous nodes."""
    try:
        matched = boundaries(model, graph)
    except ValueError as exc:
        raise ValueError(f'complete replay requires one-to-one saved nodes: {exc}') from exc
    nodes = [node for node in graph.graph.node if node.op_type in ('Conv', 'BatchNormalization')]
    result = []
    for name, module, output in matched:
        candidates = [node for node in nodes if output in node.output]
        if len(candidates) != 1:
            raise ValueError('complete replay requires one-to-one saved nodes')
        node, = candidates
        validate_native_node(module, graph, node)
        result.append((name, module, node))
    if (len(nodes) != len(result) or len({node.output[0] for _, _, node in result}) != len(nodes)):
        raise ValueError('complete replay requires one-to-one saved nodes')
    return result


def audit_native_graph(module, path):
    graph = onnx.load(path, load_external_data=False)
    native = [node for node in graph.graph.node if node.op_type != 'Identity']
    if (len(native) != 1 or len(graph.graph.input) != 1 or len(graph.graph.output) != 1
            or native[0].input[0] != graph.graph.input[0].name
            or native[0].output[0] != graph.graph.output[0].name):
        raise ValueError('isolated native graph scope/interface mismatch')
    validate_native_node(module, graph, native[0])
    for value in (*graph.graph.input, *graph.graph.output):
        if value.type.tensor_type.elem_type != onnx.TensorProto.FLOAT:
            raise ValueError('isolated native graph must retain float32 boundaries')
    return {'notice': DIAGNOSTIC_NOTICE, 'status': 'PASS',
            'saved_parameters_and_geometry': True, 'float32_boundaries': True}


def audit_affine_graph(module, formula, path):
    """Audit actual promoted runtime arithmetic, constants and both boundaries."""
    graph = onnx.load(path, load_external_data=False)
    nodes = list(graph.graph.node)
    steps = [('Cast', ['x'], ['double-x'], {'to': onnx.TensorProto.DOUBLE}),
             ('Cast', ['alpha'], ['double-alpha'], {'to': onnx.TensorProto.DOUBLE}),
             ('Cast', ['beta'], ['double-beta'], {'to': onnx.TensorProto.DOUBLE}),
             ('Mul', ['double-x', 'double-alpha'], ['product'], {}),
             ('Add', ['product', 'double-beta'], ['sum'], {}),
             ('Cast', ['sum'], ['y'], {'to': onnx.TensorProto.FLOAT})]
    if len(nodes) != len(steps):
        raise ValueError('promoted BN arithmetic/cast scope mismatch')
    for node, (op, inputs, outputs, attributes) in zip(nodes, steps):
        actual = {item.name: helper.get_attribute_value(item) for item in node.attribute}
        if (node.domain or node.op_type != op or list(node.input) != inputs
                or list(node.output) != outputs or actual != attributes):
            raise ValueError('promoted BN arithmetic/cast mismatch')
    constants = bn_constants(module, formula)
    if {item.name for item in graph.graph.initializer} != set(constants):
        raise ValueError('promoted BN constant scope mismatch')
    for key, expected in constants.items():
        actual = constant_array(graph, key)
        if (actual.dtype != np.float32 or actual.shape != expected.shape
                or not np.isfinite(actual).all() or actual.tobytes() != expected.tobytes()):
            raise ValueError('promoted BN coefficient bits mismatch')
    if ([value.name for value in graph.graph.input] != ['x']
            or [value.name for value in graph.graph.output] != ['y']
            or any(value.type.tensor_type.elem_type != onnx.TensorProto.FLOAT
                   for value in (*graph.graph.input, *graph.graph.output))):
        raise ValueError('promoted BN float32 interface mismatch')
    return {'notice': DIAGNOSTIC_NOTICE, 'status': 'PASS',
            'coefficient_bits_and_arithmetic': True, 'float32_boundaries': True}


def signed_accounting(py_output, py_on_py, py_on_ort, ort_on_ort, ort_output):
    arrays = [validate_array(value).astype(np.float64)
              for value in (py_output, py_on_py, py_on_ort, ort_on_ort, ort_output)]
    if any(value.shape != arrays[0].shape for value in arrays):
        raise ValueError('signed accounting shape mismatch')
    differences = {key: after - before for key, before, after in zip(
        ('python_replay', 'propagation', 'kernel', 'extraction'), arrays[:-1], arrays[1:])}
    total = arrays[-1] - arrays[0]
    residual = float(np.abs(total - sum(differences.values())).max())
    if residual != 0:
        raise ValueError('signed accounting telescoping identity failed')
    def stats(value):
        return {'signed_min': float(value.min()), 'signed_max': float(value.max()),
                'signed_mean': float(value.mean()), 'max_absolute': float(np.abs(value).max()),
                'mean_absolute': float(np.abs(value).mean())}
    return {'terms': {key: stats(value) for key, value in differences.items()},
            'total': stats(total), 'telescoping_max_residual': residual}


def operator_counts(selected):
    return dict(Counter(node.op_type for _, _, node in selected))


def audit_complete_report(repo, output, report):
    """No inference: reconstruct aggregates and check graph/detail/source hashes.

    Saved model/preparation/source provenance are independently rechecked by the
    caller; this audit concerns the new evidence and refuses partial row scope.
    """
    rounding = report['protocol']['decision'] == 'ADR-020'
    detail_path = output / ('PLACEHOLDER-bn-rounding-details.json' if rounding
                            else 'PLACEHOLDER-complete-replay-details.json')
    if sha256(detail_path) != report['diagnostic_details_sha256']:
        raise ValueError('complete replay detail checksum mismatch')
    details = json.loads(detail_path.read_text())
    protocol, summary = report['protocol'], report['diagnostics']
    if (report['notice'] != PLACEHOLDER_NOTICE or report['status'] != 'DIAGNOSTIC ONLY'
            or details['notice'] != PLACEHOLDER_NOTICE
            or protocol['decision'] != ('ADR-020' if rounding else 'ADR-019') or protocol['split'] != 'train'
            or any(protocol[key] for key in ('frozen_evaluation_inputs_used', 'quantisation_fit', 'deployment_selection'))
            or report['model_state_before_sha256'] != report['model_state_after_sha256']
            or protocol['optimisation'] != 'disabled' or protocol['execution'] != 'sequential'
            or protocol['intra_op_threads'] != 2 or protocol['inter_op_threads'] != 1):
        raise ValueError('complete replay protocol mismatch')
    rows, ids = details['rows'], details['component_ids']
    if (len(rows) != len(ids) or len(set(ids)) != len(ids) or not rows
            or len(rows) != protocol['components'] or len(rows) != summary['components']
            or hashlib.sha256(json_text(ids).encode()).hexdigest() != protocol['component_ids_sha256']):
        raise ValueError('complete replay ordered components mismatch')
    selection = summary['selection']
    if (len(set(selection)) != len(selection) or set(selection) != set(summary['operator_graphs'])
            or any(set(row['operators']) != set(selection) for row in rows)
            or operator_counts_from_report(summary) != summary['operator_counts']):
        raise ValueError('complete replay row/operator scope mismatch')
    if (aggregate_values([row['operators'] for row in rows], complete=True) != summary['operators']
            or aggregate_values([row['instrumentation_absolute_logit_change'] for row in rows], complete=True)
                != summary['instrumentation_absolute_logit_change']
            or any(row['instrumentation_absolute_logit_change'] != abs(
                row['instrumented_logit'] - row['original_logit']) for row in rows)):
        raise ValueError('complete replay aggregate reconstruction mismatch')
    for name, errors in summary['operators'].items():
        if (errors['signed_accounting']['telescoping_max_residual']['max'] != 0
                or errors['telescoping_max_residual']['max'] != 0):
            raise ValueError('complete replay accounting residual mismatch')
        graphs = summary['operator_graphs'][name]
        if graphs['original_operator'] == 'BatchNormalization':
            if (set(graphs['promoted_graphs']) != {'affine_rsqrt', 'affine_divide'}
                    or any(set(origin) != {'affine_rsqrt', 'affine_divide'}
                           for origin in errors['promoted'].values())):
                raise ValueError('complete replay BN recipe scope mismatch')
        elif 'promoted_graphs' in graphs or 'promoted' in errors:
            raise ValueError('complete replay must not promote Conv')
        if rounding:
            from .export_bn_rounding import validate_rounding_scope
            validate_rounding_scope(protocol, graphs, errors)
        elif 'rounding_coefficients' in graphs or 'rounding' in errors:
            raise ValueError('complete replay must not add undeclared rounding recipes')
    current = export_environment(repo)
    for key in ('source_files_sha256', 'source_tree_sha256', 'dependencies',
                'dependency_lock_sha256', 'export_dependency_lock_sha256'):
        if current[key] != report['environment'][key]:
            raise ValueError('complete replay source/dependency provenance mismatch')
    paths = {sha256(path): path for path in output.glob('*.onnx')}
    checked = []
    def walk(value):
        if not isinstance(value, dict):
            return
        if {'sha256', 'bytes', 'operators'} <= value.keys():
            path = paths.get(value['sha256'])
            if path is None or graph_report(path) != value:
                raise ValueError('complete replay graph checksum/report mismatch')
            checked.append(value['sha256'])
        else:
            for child in value.values():
                walk(child)
    walk(summary)
    return {'notice': DIAGNOSTIC_NOTICE, 'status': 'PASS', 'components': len(rows),
            'operators': len(selection), 'graph_records_checked': len(checked),
            'aggregate_reconstruction': True, 'ordered_component_hash': True,
            'source_and_dependency_hashes': True}


def operator_counts_from_report(summary):
    return dict(Counter(item['original_operator'] for item in summary['operator_graphs'].values()))


def main(argv=None):
    from .export_replay import main as replay_main
    return replay_main(argv, promoted=True, complete=True)


if __name__ == '__main__':
    raise SystemExit(main())
