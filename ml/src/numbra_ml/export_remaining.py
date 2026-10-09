"""ADR-023 PLACEHOLDER static preflight and isolated primitives, never bundle.

No baseline inference is exposed here. Native boundary capture and complete
training replay are deliberately separate, unfinished work.
"""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

import numpy as np
import onnx
from onnx import helper, numpy_helper
import onnxruntime as ort
import torch
from torch.nn import functional as F

from . import PLACEHOLDER_NOTICE
from .evaluation import read_component_index
from .export import export_environment, graph_report, session_options
from .export_batchnorm import mark_diagnostic
from .export_complete_replay import complete_operators
from .export_promoted_bn import PREFIX
from .export_runtime_profiles import verified_prior
from .prepare import repository_root
from .pretrained import ignored_path, sha256
from .train import json_text
from .training import tensor_hash
from .verify import backbone_architecture, load_reference

NOTICE = 'PLACEHOLDER diagnostic preflight only; never bundle'
REMAINING = ('Relu', 'HardSwish', 'HardSigmoid', 'ReduceMean',
             'GlobalAveragePool', 'Mul', 'Add', 'Flatten', 'Sub', 'Div', 'Gemm', 'Squeeze')
REPORT = 'PLACEHOLDER-remaining-preflight.json'


def attributes(node):
    values = {a.name: helper.get_attribute_value(a) for a in node.attribute}
    if len(values) != len(node.attribute):
        raise ValueError('duplicate remaining operator attributes')
    return values


def validate_node(node):
    """Restrict to the declared opset-17 native diagnostic expressions."""
    if (node.domain or node.op_type not in REMAINING or len(node.output) != 1
            or not all(node.input) or not node.output[0]):
        raise ValueError('unsupported remaining operator/interface')
    a, op = attributes(node), node.op_type
    unary = {'Relu', 'HardSwish', 'HardSigmoid', 'ReduceMean', 'GlobalAveragePool', 'Flatten'}
    arity = 1 if op in unary else 3 if op == 'Gemm' else 2
    if len(node.input) != arity:
        raise ValueError('remaining operator operand count mismatch')
    if op == 'HardSigmoid':
        valid = (not a.keys() - {'alpha', 'beta'}
                 and a.get('alpha', 0.2) == float(np.float32(1 / 6))
                 and a.get('beta', 0.5) == 0.5)
    elif op == 'ReduceMean':
        valid = (not a.keys() - {'axes', 'keepdims'}
                 and a.get('axes') == [2, 3] and a.get('keepdims', 1) == 1)
    elif op == 'Flatten':
        valid = not a.keys() - {'axis'} and a.get('axis', 1) == 1
    elif op == 'Gemm':
        valid = (not a.keys() - {'alpha', 'beta', 'transA', 'transB'}
                 and a.get('alpha', 1.) == a.get('beta', 1.) == 1.
                 and a.get('transA', 0) == 0 and a.get('transB', 0) == 1)
    else:
        valid = not a
    if not valid:
        raise ValueError('remaining operator attributes outside declared recipes')


def constant(graph, name, seen=None):
    """Resolve only finite tensor constants and exact Identity aliases."""
    seen = set() if seen is None else seen
    if name in seen:
        raise ValueError('remaining constant alias cycle')
    seen.add(name)
    items = [value for value in graph.graph.initializer if value.name == name]
    producers = [node for node in graph.graph.node if name in node.output]
    if len(items) == 1 and not producers:
        item = items[0]
    elif len(producers) == 1 and not items:
        node, = producers
        if node.domain or list(node.output) != [name]:
            raise ValueError('invalid remaining constant producer')
        if node.op_type == 'Identity' and len(node.input) == 1 and not node.attribute:
            return constant(graph, node.input[0], seen)
        a = attributes(node)
        if node.op_type != 'Constant' or node.input or set(a) != {'value'}:
            raise ValueError('remaining operand is not a tensor constant')
        item = a['value']
    else:
        raise ValueError('missing/ambiguous remaining constant')
    if item.data_location == onnx.TensorProto.EXTERNAL or item.external_data:
        raise ValueError('external remaining constant forbidden')
    array = numpy_helper.to_array(item).copy()
    if array.dtype not in (np.dtype('float32'), np.dtype('int64')) or not np.isfinite(array).all():
        raise ValueError('invalid remaining constant type/value')
    return array


def tensor_specs(graph):
    inferred = onnx.shape_inference.infer_shapes(graph, strict_mode=True, data_prop=True)
    specs = {}
    for item in (*inferred.graph.input, *inferred.graph.value_info, *inferred.graph.output):
        t = item.type.tensor_type
        if (t.elem_type not in (onnx.TensorProto.FLOAT, onnx.TensorProto.INT64)
                or not t.HasField('shape')
                or any(not d.HasField('dim_value') or d.dim_value <= 0 for d in t.shape.dim)):
            raise ValueError('remaining replay requires static float32/int64 boundaries')
        spec = {'dtype': 'float32' if t.elem_type == onnx.TensorProto.FLOAT else 'int64',
                'shape': [d.dim_value for d in t.shape.dim]}
        if item.name in specs and specs[item.name] != spec:
            raise ValueError('inconsistent remaining tensor specification')
        specs[item.name] = spec
    for item in inferred.graph.initializer:
        array = constant(inferred, item.name)
        spec = {'dtype': str(array.dtype), 'shape': list(array.shape)}
        if item.name in specs and specs[item.name] != spec:
            raise ValueError('inconsistent remaining constant specification')
        specs[item.name] = spec
    return specs


def saved_head(model, graph):
    nodes = list(graph.graph.node)
    wanted = {}
    for op in ('Sub', 'Div', 'Gemm', 'Squeeze'):
        matches = [n for n in nodes if n.op_type == op]
        if len(matches) != 1:
            raise ValueError('complete saved head scope mismatch')
        wanted[op], = matches
        validate_node(wanted[op])
    sub, div, gemm, squeeze = [wanted[op] for op in ('Sub', 'Div', 'Gemm', 'Squeeze')]
    if (div.input[0] != sub.output[0] or gemm.input[0] != div.output[0]
            or squeeze.input[0] != gemm.output[0]
            or [o.name for o in graph.graph.output] != list(squeeze.output)):
        raise ValueError('saved head connectivity mismatch')
    parameters = [(sub.input[1], model.head.mean), (div.input[1], model.head.scale),
                  (gemm.input[1], model.head.linear.weight), (gemm.input[2], model.head.linear.bias)]
    bits = {}
    for name, value in parameters:
        expected, actual = value.detach().numpy(), constant(graph, name)
        if (expected.dtype != np.float32 or actual.dtype != expected.dtype
                or actual.shape != expected.shape
                or actual.tobytes() != np.ascontiguousarray(expected).tobytes()):
            raise ValueError('saved head parameter bits mismatch')
        bits[name] = hashlib.sha256(actual.tobytes()).hexdigest()
    axes = constant(graph, squeeze.input[1])
    if axes.dtype != np.int64 or axes.shape != (1,) or axes.tolist() != [1]:
        raise ValueError('saved head squeeze axes mismatch')
    return {'parameter_bits_sha256': bits, 'squeeze_axes': [1], 'connectivity': True}


def remaining_plan(model, source, rounded):
    """Cover every node before inference; no optional layer/input selection."""
    for graph in (source, rounded):
        if ([(o.domain, o.version) for o in graph.opset_import] != [('', 17)]
                or graph.functions or graph.training_info):
            raise ValueError('remaining replay requires plain inference opset 17')
        onnx.checker.check_model(graph, full_check=True)
    controls = complete_operators(model, source)
    control_outputs = {node.output[0] for _, _, node in controls}
    specs = tensor_specs(source)
    known = {x.name for x in (*source.graph.input, *source.graph.initializer)}
    if len(known) != len(source.graph.input) + len(source.graph.initializer):
        raise ValueError('remaining graph input/constant collision')
    records, seen_names = [], set()
    for position, node in enumerate(source.graph.node):
        if (node.domain or not node.name or node.name in seen_names or len(node.output) != 1
                or not node.output[0] or node.output[0] in known
                or any(name not in known for name in node.input)):
            raise ValueError('remaining graph node order/name/connectivity mismatch')
        seen_names.add(node.name)
        if node.output[0] in control_outputs:
            category = 'saved_conv_bn_control'
        elif node.op_type in ('Constant', 'Identity'):
            constant(source, node.output[0])  # Identity must alias a constant.
            category = 'constant_or_alias'
        else:
            validate_node(node)
            category = 'remaining_replay'
        names = list(dict.fromkeys([*node.input, *node.output]))
        if any(name not in specs for name in names):
            raise ValueError('remaining boundary shape/type missing')
        if category == 'remaining_replay':
            for index, name in enumerate(node.input):
                expected = 'int64' if node.op_type == 'Squeeze' and index == 1 else 'float32'
                if specs[name]['dtype'] != expected:
                    raise ValueError('remaining boundary dtype mismatch')
        records.append({'position': position, 'name': node.name, 'operator': node.op_type,
                        'category': category, 'inputs': list(node.input), 'outputs': list(node.output),
                        'node_sha256': hashlib.sha256(node.SerializeToString()).hexdigest(),
                        'boundaries': {name: specs[name] for name in names}})
        known.add(node.output[0])
    producers = {node.output[0]: node for node in source.graph.node}
    live = {o.name for o in source.graph.output}
    for node in reversed(source.graph.node):
        if node.output[0] in live:
            live.update(node.input)
    if set(producers) - live:
        raise ValueError('disconnected remaining graph nodes forbidden')
    expected = [node.SerializeToString() for node in source.graph.node
                if node.op_type != 'BatchNormalization']
    actual = [node.SerializeToString() for node in rounded.graph.node if not node.name.startswith(PREFIX)]
    if expected != actual:
        raise ValueError('rounded graph changed remaining/control node scope or bits')
    # Check every original constant, including non-head controls and aliases.
    constants = []
    for item in source.graph.initializer:
        before, after = constant(source, item.name), constant(rounded, item.name)
        if before.dtype != after.dtype or before.shape != after.shape or before.tobytes() != after.tobytes():
            raise ValueError('rounded graph changed original constant bits')
        constants.append({'name': item.name, 'dtype': str(before.dtype), 'shape': list(before.shape),
                          'sha256': hashlib.sha256(before.tobytes()).hexdigest()})
    return {'notice': NOTICE, 'status': 'STATIC SCOPE ONLY', 'nodes': records,
            'node_counts': dict(Counter(r['category'] for r in records)),
            'remaining_operator_counts': dict(Counter(r['operator'] for r in records
                                                      if r['category'] == 'remaining_replay')),
            'initializers': constants, 'saved_head': saved_head(model, source),
            'remaining_native_mapping': 'UNIMPLEMENTED; recipes are not captured native outputs'}


def recipe(node, operands):
    """Independent eager expressions on copied actual operands, never a reference replacement."""
    validate_node(node)
    if len(operands) != len(node.input):
        raise ValueError('remaining recipe operand count mismatch')
    for index, value in enumerate(operands):
        dtype = np.int64 if node.op_type == 'Squeeze' and index == 1 else np.float32
        if not isinstance(value, np.ndarray) or value.dtype != dtype or not np.isfinite(value).all():
            raise ValueError('remaining recipe operand type/value mismatch')
    x, *rest = [torch.from_numpy(value.copy()) for value in operands]
    op = node.op_type
    with torch.inference_mode():
        if op == 'Relu':
            y = F.relu(x)
        elif op == 'HardSwish':
            y = F.hardswish(x)
        elif op == 'HardSigmoid':
            y = F.hardsigmoid(x)
        elif op in ('ReduceMean', 'GlobalAveragePool'):
            if x.ndim != 4:
                raise ValueError('remaining pooling requires NCHW input')
            y = x.mean((2, 3), keepdim=True) if op == 'ReduceMean' else F.adaptive_avg_pool2d(x, (1, 1))
        elif op == 'Flatten':
            if x.ndim < 1:
                raise ValueError('remaining flatten requires non-scalar input')
            y = x.reshape(x.shape[0], -1)
        elif op == 'Gemm':
            if x.ndim != 2 or rest[0].ndim != 2 or rest[1].shape != (rest[0].shape[0],):
                raise ValueError('remaining Gemm requires native linear geometry')
            y = F.linear(x, rest[0], rest[1])
        elif op == 'Squeeze':
            axes = rest[0].tolist()
            if rest[0].ndim != 1 or len(set(axes)) != len(axes):
                raise ValueError('remaining squeeze requires distinct axes')
            normalized = [axis % x.ndim for axis in axes] if x.ndim else []
            if (any(axis < -x.ndim or axis >= x.ndim for axis in axes)
                    or len(set(normalized)) != len(axes)
                    or any(x.shape[axis] != 1 for axis in normalized)):
                raise ValueError('remaining squeeze axes/shape mismatch')
            y = x
            for axis in sorted(normalized, reverse=True):
                y = y.squeeze(axis)
        else:
            y = {'Add': torch.add, 'Sub': torch.sub, 'Mul': torch.mul, 'Div': torch.div}[op](x, rest[0])
    result = y.numpy().copy()
    if result.dtype != np.float32 or not np.isfinite(result).all():
        raise ValueError('nonfinite remaining recipe result')
    return result


def isolated_graph(node, operands, source, path):
    """Each operand remains an explicit input: no favourable constant folding."""
    output = recipe(node, operands)
    distinct = {}
    for name, value in zip(node.input, operands):
        if name in distinct and (distinct[name].dtype != value.dtype or distinct[name].shape != value.shape
                                 or distinct[name].tobytes() != value.tobytes()):
            raise ValueError('inconsistent repeated remaining operand')
        distinct[name] = value
    def info(name, value):
        return helper.make_tensor_value_info(name, onnx.TensorProto.INT64 if value.dtype == np.int64
                                             else onnx.TensorProto.FLOAT, list(value.shape))
    graph = helper.make_graph([node], 'PLACEHOLDER-remaining-isolation',
                              [info(name, value) for name, value in distinct.items()],
                              [info(node.output[0], output)])
    model = helper.make_model(graph, opset_imports=list(source.opset_import), ir_version=source.ir_version)
    mark_diagnostic(model)
    onnx.checker.check_model(model, full_check=True)
    onnx.save(model, path)
    return output


def audit_isolated(node, operands, path, *, runtime=False):
    graph = onnx.load(path, load_external_data=False)
    output = recipe(node, operands)
    specs = tensor_specs(graph)
    wanted = {name: {'dtype': str(value.dtype), 'shape': list(value.shape)}
              for name, value in zip(node.input, operands)}
    wanted[node.output[0]] = {'dtype': 'float32', 'shape': list(output.shape)}
    exact = len(graph.graph.node) == 1 and graph.graph.node[0].SerializeToString() == node.SerializeToString()
    expanded = False
    if runtime and node.op_type == 'HardSwish' and len(graph.graph.node) == 2:
        gate, mul = graph.graph.node
        expanded = (not gate.domain and gate.op_type == 'HardSigmoid'
                    and list(gate.input) == list(node.input) and len(gate.output) == 1
                    and gate.output[0] not in (*node.input, *node.output)
                    and attributes(gate) == {'alpha': float(np.float32(1 / 6)), 'beta': 0.5}
                    and not mul.domain and mul.op_type == 'Mul' and not mul.attribute
                    and list(mul.input) == [node.input[0], gate.output[0]]
                    and list(mul.output) == list(node.output))
        if expanded:
            wanted[gate.output[0]] = wanted[node.input[0]]
    if (not (exact or expanded)
            or graph.graph.initializer or graph.functions or graph.training_info
            or [(o.domain, o.version) for o in graph.opset_import if not o.domain] != [('', 17)]
            or [v.name for v in graph.graph.input] != list(dict.fromkeys(node.input))
            or [v.name for v in graph.graph.output] != list(node.output)
            or specs != wanted):
        raise ValueError('isolated remaining arithmetic/interface mismatch')
    onnx.checker.check_model(graph, full_check=True)
    return {'notice': NOTICE, 'status': 'PASS', 'expression_and_boundaries': True,
            'expression': 'HardSigmoid/Mul function' if expanded else 'exact original node',
            # ORT adds unused custom-domain imports even with disabled optimisation.
            # The one audited node must still be byte-identical and default-domain.
            'unused_domain_imports': {o.domain: o.version for o in graph.opset_import if o.domain}}


def replay_isolated(node, operands, source, path, runtime_path):
    expected = isolated_graph(node, operands, source, path)
    serialized_audit = audit_isolated(node, operands, path)
    options = session_options('disabled')
    options.optimized_model_filepath = str(runtime_path)
    session = ort.InferenceSession(str(path), sess_options=options, providers=['CPUExecutionProvider'])
    runtime_audit = audit_isolated(node, operands, runtime_path, runtime=True)
    actual, = session.run(None, dict(zip(node.input, operands)))
    if actual.dtype != np.float32 or actual.shape != expected.shape or not np.isfinite(actual).all():
        raise ValueError('isolated remaining runtime result mismatch')
    delta = actual.astype(np.float64) - expected.astype(np.float64)
    return {'notice': NOTICE, 'status': 'DIAGNOSTIC ONLY',
            'serialized_audit': serialized_audit, 'runtime_audit': runtime_audit,
            'signed_min': float(delta.min()), 'signed_max': float(delta.max()),
            'signed_mean': float(delta.mean()), 'max_absolute_error': float(np.abs(delta).max()),
            'mean_absolute_error': float(np.abs(delta).mean())}, actual


def preflight_evidence(repo, prepared, run, experiments, source, prior, *, backbone_factory=backbone_architecture):
    prepared, run, source, prior = [ignored_path(repo, p) for p in (prepared, run, source, prior)]
    experiments = [ignored_path(repo, p) for p in experiments]
    if not experiments:
        raise ValueError('remaining preflight requires retained export experiments')
    model, saved = load_reference(run, backbone_factory=backbone_factory)
    before = tensor_hash(model.state_dict())
    index = read_component_index(prepared / 'manifest.jsonl', prepared / 'preparation-report.json')
    preserved, rounded, _, provenance = verified_prior(
        repo, prepared, run, experiments, source, prior, model, saved, index)
    ids = [c.id for c in index.components if c.split == 'train']
    if not ids:
        raise ValueError('remaining preflight requires nonempty training scope')
    plan = remaining_plan(model, onnx.load(preserved, load_external_data=False),
                          onnx.load(rounded, load_external_data=False))
    if tensor_hash(model.state_dict()) != before:
        raise ValueError('remaining preflight changed saved state')
    return {'notice': PLACEHOLDER_NOTICE, 'status': 'PREFLIGHT ONLY; NO INFERENCE',
            'protocol': {'decision': 'ADR-023', 'stage': 'static preflight', 'split': 'train',
                         'components': len(ids), 'component_ids_sha256': hashlib.sha256(json_text(ids).encode()).hexdigest(),
                         'baseline_inference': False, 'frozen_evaluation_inputs_used': False,
                         'quantisation_fit': False, 'deployment_selection': False},
            'model_state_sha256': before, 'saved_run_sha256': sha256(run / 'PLACEHOLDER-run.json'),
            'saved_model_sha256': saved['provenance']['model_sha256'],
            'manifest_sha256': index.manifest_sha256,
            'preparation_report_sha256': sha256(prepared / 'preparation-report.json'),
            'prior_provenance': provenance,
            'graphs': {'preserved': graph_report(preserved), 'rounded': graph_report(rounded)},
            'plan': plan, 'environment': export_environment(repo)}


def audit_preflight(repo, output, prepared, run, experiments, source, prior, *, backbone_factory=backbone_architecture):
    report = json.loads((output / REPORT).read_text())
    expected = preflight_evidence(repo, prepared, run, experiments, source, prior,
                                  backbone_factory=backbone_factory)
    # Historical checkout metadata must survive the required iteration commit.
    # All live code/dependency/artifact/scope fields remain reconstructed exactly.
    context = report.get('environment')
    if (not isinstance(context, dict) or not isinstance(context.get('git_commit'), str)
            or not re.fullmatch(r'[0-9a-f]{40}', context['git_commit'])
            or type(context.get('git_dirty')) is not bool
            or subprocess.run(['git', 'cat-file', '-e', context['git_commit'] + '^{commit}'],
                              cwd=repo, capture_output=True).returncode):
        raise ValueError('remaining preflight complete reconstruction/provenance mismatch')
    for key in ('git_commit', 'git_dirty'):
        expected['environment'][key] = context[key]
    if report != expected:
        raise ValueError('remaining preflight complete reconstruction/provenance mismatch')
    return {'notice': NOTICE, 'status': 'PASS', 'baseline_inference': False,
            'complete_scope_and_provenance_reconstruction': True,
            'historical_git_context_commit_exists': True}


def main(argv=None):
    parser = argparse.ArgumentParser(description=NOTICE + '; no baseline inference')
    parser.add_argument('--prepared', type=Path, default=Path('data/prepared/synthetic-v2-selection'))
    parser.add_argument('--run', type=Path, default=Path('data/models/PLACEHOLDER-m3-baseline'))
    parser.add_argument('--experiments', nargs='+', type=Path, default=[Path('data/exports/PLACEHOLDER-m4-attempt1'),
                                                                      Path('data/exports/PLACEHOLDER-m4-attempt2')])
    parser.add_argument('--source', type=Path, default=Path('data/exports/PLACEHOLDER-m4-batchnorm2'))
    parser.add_argument('--prior', type=Path, default=Path('data/exports/PLACEHOLDER-m4-rounded-bn2'))
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    repo = repository_root()
    try:
        prepared, run, source, prior, output = [ignored_path(repo, p) for p in
                                               (args.prepared, args.run, args.source, args.prior, args.output)]
        experiments = [ignored_path(repo, p) for p in args.experiments]
        target = repo / 'ml/reports' / f'{output.name}.json'
        if (output.exists() or target.exists() or target.is_symlink() or not output.name.startswith('PLACEHOLDER-')
                or target.parent.resolve() != target.parent):
            raise ValueError('remaining preflight requires new local PLACEHOLDER output/report')
        report = preflight_evidence(repo, prepared, run, experiments, source, prior)
        output.mkdir(parents=True)
        (output / REPORT).write_text(json_text(report))
        audit = audit_preflight(repo, output, prepared, run, experiments, source, prior)
        (output / 'PLACEHOLDER-independent-audit.json').write_text(json_text(audit))
        with target.open('x') as stream:
            stream.write(json_text(report))
    except (ValueError, OSError, RuntimeError, KeyError, TypeError, onnx.checker.ValidationError) as exc:
        print(f'PLACEHOLDER remaining preflight failed: {exc}', file=sys.stderr)
        return 1
    print(f'PLACEHOLDER PREFLIGHT ONLY, NO INFERENCE: {target.relative_to(repo)}; M4 incomplete')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
