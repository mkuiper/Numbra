"""ADR-023 complete supplied-tensor PLACEHOLDER replay; never bundle.

This is an integration primitive, not a saved-baseline CLI. The caller must
establish the complete training scope and provenance before supplying inputs.
The independent evidence reconstruction performs no model/operator inference.
"""

import copy
from collections import Counter
import hashlib
from pathlib import Path

import numpy as np
import onnx
from onnx import helper, numpy_helper
import onnxruntime as ort
import torch
from torch import nn

from .export import graph_report, session_options
from .export_batchnorm import mark_diagnostic
from .export_bn_rounding import (RECIPES, apply_recipe, coefficient_cache,
                                 coefficient_records)
from .export_complete_replay import complete_operators, signed_accounting
from .export_precision import (AFFINE_FORMULAS, promoted_affine_graph,
                               python_promoted_affine)
from .export_promoted_bn import PREFIX, expression_nodes
from .export_remaining import constant, recipe, tensor_specs
from .export_remaining_native import capture_native, native_plan, same_bits, tap_complete_graph
from .export_provenance import checked_file
from .export_remaining_runtime import CompleteRuntime, audit_complete_runtime, specs
from .export_replay import (FORMULAS, double_formula, formula_graph,
                            python_formula, python_operator)
from .export_rounded_bn import rounded_coefficients
from .training import tensor_hash

NOTICE = 'PLACEHOLDER complete supplied-tensor replay diagnostic only; never bundle'
KINDS = ('preserved', 'rounded')
ORIGINS = ('native_input', 'runtime_input')
CONTROL_KEYS = ('native_onnx', 'float64_formula',
                *('formula_' + f + '_' + e for f in FORMULAS for e in ('python', 'onnx')),
                *('promoted_' + f + '_' + e for f in AFFINE_FORMULAS for e in ('python', 'onnx')),
                *('rounding_' + r + '_' + e for r in RECIPES for e in ('numpy', 'torch')))


def audit_replay_setup(model, source, rounded, output, records):
    """Rebuild every saved expression and runtime record without any sessions.

    The graph factories construct constants/expressions only. No forward call,
    operator recipe on observations, image decoding, or evidence writes occur.
    Exact serialized binding precedes bounded runtime expression auditing.
    """
    plan = native_plan(model, source, rounded)
    expected = {'notice': NOTICE, 'rounded_saved_binding': audit_rounded_binding(model, source, rounded),
                'whole_graphs': {}, 'operators': {},
                'operator_counts': dict(Counter(r['operator'] for r in plan['nodes']))}
    files = set()

    def graph_file(relative, graph):
        files.add(relative)
        path = checked_file(output, relative)
        actual = onnx.load(path, load_external_data=False)
        if actual.SerializeToString() != graph.SerializeToString():
            raise ValueError('complete setup serialized saved expression mismatch')
        return path

    def isolated(graph, relative):
        graph = copy.deepcopy(graph)
        mark_diagnostic(graph)
        path = graph_file(relative + '/PLACEHOLDER-expression.onnx', graph)
        runtime_relative = relative + '/PLACEHOLDER-runtime.onnx'
        files.add(runtime_relative)
        runtime_path = checked_file(output, runtime_relative)
        return {'notice': NOTICE, 'serialized': graph_report(path), 'runtime': graph_report(runtime_path),
                'audit': audit_complete_runtime(graph, onnx.load(runtime_path, load_external_data=False))}

    for kind, graph in zip(KINDS, (source, rounded)):
        tapped, _ = tap_complete_graph(graph, plan)
        expected['whole_graphs'][kind] = {}
        for tag, original in (('original', graph), ('tapped', tapped)):
            graph_file(f'PLACEHOLDER-{kind}/PLACEHOLDER-{tag}.onnx', original)
            relative = f'PLACEHOLDER-{kind}/PLACEHOLDER-{tag}-runtime.onnx'
            files.add(relative)
            expected['whole_graphs'][kind][tag] = audit_complete_runtime(original,
                onnx.load(checked_file(output, relative), load_external_data=False))
    nodes = {node.name: node for node in source.graph.node}
    modules = {node.name: module for _, module, node in complete_operators(model, source)}
    for position, record in enumerate(plan['nodes']):
        node = nodes[record['name']]
        kernel = isolated(explicit_graph(source, node, record), f'PLACEHOLDER-operator-{position}')
        graphs = {'preserved': kernel, 'rounded': kernel}
        if node.op_type == 'BatchNormalization':
            inferred = onnx.shape_inference.infer_shapes(rounded, strict_mode=True, data_prop=True)
            extracted = onnx.utils.Extractor(inferred).extract_model([node.input[0]], [node.output[0]])
            extracted.ir_version = source.ir_version
            graphs['rounded'] = isolated(extracted, f'PLACEHOLDER-rounded-bn-{position}')
            module, shape = modules[node.name], record['boundaries'][node.input[0]]['shape']
            controls = {}
            for label, formulas, factory in (('formula', FORMULAS, formula_graph),
                                            ('promoted', AFFINE_FORMULAS, promoted_affine_graph)):
                for formula in formulas:
                    graph = factory(module, shape, formula, source)
                    graph_file(f'PLACEHOLDER-{position}-{label}-{formula}.onnx', graph)
                    controls[label + '_' + formula] = isolated(graph, f'PLACEHOLDER-{position}-{label}-{formula}')
            graphs['controls'] = controls
            graphs['rounding_coefficients'] = coefficient_records(module, coefficient_cache(module))
        expected['operators'][node.name] = graphs
    # Recursively check exact directory/file scope and reject symlinks, including
    # empty unexpected directories. All output paths come from fixed templates.
    directories = {str(Path(name).parent) for name in files if str(Path(name).parent) != '.'}
    observed_files, observed_directories = set(), set()
    for path in output.rglob('*'):
        if path.is_symlink():
            raise ValueError('complete setup unsafe evidence path')
        relative = str(path.relative_to(output))
        (observed_directories if path.is_dir() else observed_files).add(relative)
    if (observed_files != files or observed_directories != directories or records != expected):
        raise ValueError('complete setup scope/record reconstruction mismatch')
    return {'notice': NOTICE, 'status': 'PASS', 'serialized_and_runtime_graphs': len(files),
            'operators': len(plan['nodes']), 'complete_saved_expressions_constants_and_records': True,
            'baseline_inference': False, 'historical_inference_authentication': False}


def validate(value, spec):
    if (not isinstance(value, np.ndarray) or not value.size or not np.isfinite(value).all()
            or {'dtype': str(value.dtype), 'shape': list(value.shape)} != spec):
        raise ValueError('complete replay tensor specification mismatch')


def delta(before, after):
    """Unsuppressed signed statistics, including exact bits at zero drift."""
    if (not isinstance(before, np.ndarray) or before.dtype != np.float32
            or not before.size or not np.isfinite(before).all()
            or not isinstance(after, np.ndarray) or after.dtype != np.float32
            or after.shape != before.shape or not np.isfinite(after).all()):
        raise ValueError('complete replay difference requires matching finite float32 arrays')
    value = after.astype(np.float64) - before.astype(np.float64)
    return {'exact_bits': same_bits(before, after), 'signed_min': float(value.min()),
            'signed_max': float(value.max()), 'signed_mean': float(value.mean()),
            'max_absolute': float(np.abs(value).max()), 'mean_absolute': float(np.abs(value).mean())}


class IsolatedSession:
    """Build and audit a fixed expression before any supplied input is opened."""

    def __init__(self, graph, directory):
        directory.mkdir()
        self.graph = copy.deepcopy(graph)
        mark_diagnostic(self.graph)
        onnx.checker.check_model(self.graph, full_check=True)
        self.specs = specs(self.graph)
        self.inputs = [v.name for v in self.graph.graph.input]
        if len(self.inputs) != len(set(self.inputs)) or len(self.graph.graph.output) != 1:
            raise ValueError('isolated complete replay interface mismatch')
        self.output = self.graph.graph.output[0].name
        path, runtime_path = directory / 'PLACEHOLDER-expression.onnx', directory / 'PLACEHOLDER-runtime.onnx'
        onnx.save(self.graph, path)
        options = session_options('disabled')
        options.optimized_model_filepath = str(runtime_path)
        self.session = ort.InferenceSession(str(path), sess_options=options, providers=['CPUExecutionProvider'])
        self.audit = audit_complete_runtime(self.graph, onnx.load(runtime_path, load_external_data=False))
        self.record = {'notice': NOTICE, 'serialized': graph_report(path),
                       'runtime': graph_report(runtime_path), 'audit': self.audit}

    def run(self, operands):
        if len(operands) != len(self.inputs):
            raise ValueError('isolated complete replay operand count mismatch')
        for name, value in zip(self.inputs, operands):
            validate(value, self.specs[name])
        feed = {name: value.copy() for name, value in zip(self.inputs, operands)}
        result, = self.session.run(None, feed)
        validate(result, self.specs[self.output])
        return result.copy()


def explicit_graph(source, node, record):
    """All ordered operands, including saved parameters/axes, remain inputs."""
    def info(name):
        spec = record['boundaries'][name]
        dtype = onnx.TensorProto.INT64 if spec['dtype'] == 'int64' else onnx.TensorProto.FLOAT
        return helper.make_tensor_value_info(name, dtype, spec['shape'])
    graph = helper.make_graph([copy.deepcopy(node)], 'PLACEHOLDER-complete-isolation',
        [info(name) for name in dict.fromkeys(node.input)], [info(node.output[0])])
    result = helper.make_model(graph, opset_imports=list(source.opset_import), ir_version=source.ir_version)
    mark_diagnostic(result)
    onnx.checker.check_model(result, full_check=True)
    return result


def ordered_feed(node, operands):
    if len(operands) != len(node.input):
        raise ValueError('complete replay ordered operand count mismatch')
    result = {}
    for name, value in zip(node.input, operands):
        if name in result and not same_bits(result[name], value):
            raise ValueError('complete replay repeated operand bits mismatch')
        result[name] = value
    return list(result.values())


def audit_rounded_binding(model, source, rounded):
    """Independently rebuild the fixed saved-coefficient graph without inference.

    Auditing a runtime against its own serialized graph cannot detect altered
    serialized coefficients. Bind every rounded expression to the selected
    saved recipe first, including exact original constants and graph metadata.
    """
    expected, replacements, extra = copy.deepcopy(source), {}, []
    selected = [(name, module, node) for name, module, node in complete_operators(model, source)
                if node.op_type == 'BatchNormalization']
    for position, (_, module, node) in enumerate(selected):
        constants, _ = rounded_coefficients(module)
        replacements[node.output[0]] = expression_nodes(position, node.input[0], node.output[0])
        extra.extend(numpy_helper.from_array(array, f'{PREFIX}{position}-{key}')
                     for key, array in constants.items())
    nodes = [n for node in source.graph.node for n in replacements.get(node.output[0], [node])]
    del expected.graph.node[:]
    expected.graph.node.extend(nodes)
    expected.graph.initializer.extend(extra)
    mark_diagnostic(expected)
    if not selected or expected.SerializeToString() != rounded.SerializeToString():
        raise ValueError('complete replay rounded saved expression/coefficient binding mismatch')
    return {'notice': NOTICE, 'status': 'PASS', 'all_saved_rounded_expressions_and_bits': True,
            'batchnorm_layers': len(selected)}


def reconstruct_row(source, plan, evidence):
    """Reconstruct every metric from retained arrays, without executing kernels.

    Exact boundary lineage and complete graph/operator/origin/control scope are
    checked separately from arithmetic: recorded outputs are observations, not
    independently recomputed model predictions. A future runner must bind these
    arrays to prior ordered component logits and saved/source provenance.
    """
    nodes = [n for n in source.graph.node if n.op_type not in ('Constant', 'Identity')]
    boundaries = tensor_specs(source)
    if (hashlib.sha256(source.SerializeToString()).hexdigest() != plan['serialized_graph_sha256']['preserved']
            or [n.name for n in nodes] != [r['name'] for r in plan['nodes']]
            or any(hashlib.sha256(n.SerializeToString()).hexdigest() != r['node_sha256']
                   or n.op_type != r['operator'] or list(n.input) != r['inputs']
                   or list(n.output) != r['outputs']
                   or r['boundaries'] != {name: boundaries[name] for name in (*n.input, *n.output)}
                   for n, r in zip(nodes, plan['nodes']))
            or plan['operator_counts'] != dict(Counter(n.op_type for n in nodes))):
        raise ValueError('complete replay evidence graph/plan binding mismatch')
    if (set(evidence) != {'notice', 'input', 'native_original_logit', 'native_captured_logit',
                         'graphs', 'operators'} or evidence['notice'] != NOTICE
            or set(evidence['graphs']) != set(KINDS)
            or list(evidence['operators']) != [r['name'] for r in plan['nodes']]):
        raise ValueError('complete replay evidence scope mismatch')
    input_name = plan['nodes'][0]['inputs'][0]
    final_name = plan['nodes'][-1]['outputs'][0]
    boundaries = {name: spec for r in plan['nodes'] for name, spec in r['boundaries'].items()}
    validate(evidence['input'], boundaries[input_name])
    for key in ('native_original_logit', 'native_captured_logit'):
        validate(evidence[key], boundaries[final_name])
    native_values = {input_name: evidence['input']}
    runtime_values = {kind: {input_name: evidence['input']} for kind in KINDS}
    computed = {n.output[0] for n in nodes}
    metrics = {}
    for record in plan['nodes']:
        name, output = record['name'], record['outputs'][0]
        row = evidence['operators'][name]
        if (set(row) != {'native_operands', 'native_output', 'eager_native', 'graphs'}
                or set(row['graphs']) != set(KINDS)
                or len(row['native_operands']) != len(record['inputs'])):
            raise ValueError('complete replay operator evidence scope mismatch')
        def check_operands(values, operands):
            if len(operands) != len(record['inputs']):
                raise ValueError('complete replay operand evidence scope mismatch')
            for key, operand in zip(record['inputs'], operands):
                validate(operand, record['boundaries'][key])
                if key != input_name and key not in computed and not same_bits(constant(source, key), operand):
                    raise ValueError('complete replay saved constant bits mismatch')
                if key in computed and key not in values:
                    raise ValueError('complete replay missing producer boundary')
                if key in values and not same_bits(values[key], operand):
                    raise ValueError('complete replay boundary lineage mismatch')
                values[key] = operand
        check_operands(native_values, row['native_operands'])
        for key in ('native_output', 'eager_native'):
            validate(row[key], record['boundaries'][output])
        native_values[output] = row['native_output']
        per_graph = {}
        for kind in KINDS:
            data = row['graphs'][kind]
            if set(data) != {'runtime_operands', 'runtime_output', 'eager_runtime',
                             'isolated_native', 'isolated_runtime', 'controls'}:
                raise ValueError('complete replay graph evidence scope mismatch')
            check_operands(runtime_values[kind], data['runtime_operands'])
            for key in ('runtime_output', 'eager_runtime', 'isolated_native', 'isolated_runtime'):
                validate(data[key], record['boundaries'][output])
            runtime_values[kind][output] = data['runtime_output']
            input_drift = {}
            for position, (key, before, after) in enumerate(zip(record['inputs'], row['native_operands'], data['runtime_operands'])):
                if record['boundaries'][key]['dtype'] == 'int64':
                    if not same_bits(before, after):
                        raise ValueError('complete replay axes bits mismatch')
                    input_drift[str(position)] = {'exact_bits': True}
                else:
                    input_drift[str(position)] = delta(before, after)
            controls = data['controls']
            expected_controls = set(CONTROL_KEYS) if record['operator'] == 'BatchNormalization' else (
                {'native_onnx'} if record['operator'] == 'Conv' else set())
            if (set(controls) != (set(ORIGINS) if expected_controls else set())
                    or any(set(outputs) != expected_controls for outputs in controls.values())):
                raise ValueError('complete replay control/origin scope mismatch')
            control_metrics = {}
            for origin, outputs in controls.items():
                reference = row['eager_native'] if origin == 'native_input' else data['eager_runtime']
                for value in outputs.values():
                    validate(value, record['boundaries'][output])
                comparisons = {}
                if record['operator'] == 'BatchNormalization':
                    for label, formulas in (('formula', FORMULAS), ('promoted', AFFINE_FORMULAS)):
                        for formula in formulas:
                            prefix = label + '_' + formula
                            comparisons[prefix + '_onnx_vs_python'] = delta(outputs[prefix + '_python'], outputs[prefix + '_onnx'])
                    for rounding in RECIPES:
                        prefix = 'rounding_' + rounding
                        comparisons[prefix + '_numpy_vs_torch'] = delta(outputs[prefix + '_torch'], outputs[prefix + '_numpy'])
                control_metrics[origin] = {'vs_native': {key: delta(reference, value) for key, value in outputs.items()},
                                           'paired': comparisons}
            per_graph[kind] = {
                'operand_drift': input_drift,
                'native_replay_fidelity': delta(row['native_output'], row['eager_native']),
                'local_kernel_native_input': delta(row['eager_native'], data['isolated_native']),
                'local_kernel_runtime_input': delta(data['eager_runtime'], data['isolated_runtime']),
                'isolated_extraction': delta(data['isolated_runtime'], data['runtime_output']),
                'whole_boundary_drift': delta(row['native_output'], data['runtime_output']),
                'signed_accounting': signed_accounting(row['native_output'], row['eager_native'],
                    data['eager_runtime'], data['isolated_runtime'], data['runtime_output']),
                'controls': control_metrics}
        metrics[name] = per_graph
    if not same_bits(native_values[final_name], evidence['native_captured_logit']):
        raise ValueError('complete replay captured logit lineage mismatch')
    graph_metrics = {}
    for kind in KINDS:
        row = evidence['graphs'][kind]
        if set(row) != {'original_logit', 'tapped_logit'}:
            raise ValueError('complete replay whole logit scope mismatch')
        for value in row.values():
            validate(value, boundaries[final_name])
        if not same_bits(runtime_values[kind][final_name], row['tapped_logit']):
            raise ValueError('complete replay tapped logit lineage mismatch')
        graph_metrics[kind] = {
            'instrumentation': delta(row['original_logit'], row['tapped_logit']),
            'whole_model_drift': delta(evidence['native_original_logit'], row['original_logit'])}
    return {'notice': NOTICE, 'status': 'DIAGNOSTIC ONLY', 'operators': metrics,
            'graphs': graph_metrics, 'native_instrumentation': delta(
                evidence['native_original_logit'], evidence['native_captured_logit'])}


class CompleteReplay:
    """Both graphs, both exact input origins and every saved Conv/BN control."""

    def __init__(self, model, source, rounded, output):
        if not output.is_dir() or any(output.iterdir()) or not output.name.startswith('PLACEHOLDER-'):
            raise ValueError('complete replay requires a fresh empty PLACEHOLDER directory')
        self.model, self.source, self.rounded = model, copy.deepcopy(source), copy.deepcopy(rounded)
        source, rounded = self.source, self.rounded
        self.plan = native_plan(model, source, rounded)
        binding = audit_rounded_binding(model, source, rounded)
        self.state = tensor_hash(model.state_dict())
        self.nodes = {n.name: n for n in source.graph.node}
        self.modules = {node.name: module for _, module, node in complete_operators(model, source)}
        self.runtimes, self.kernels, self.controls, self.rounding = {}, {}, {}, {}
        self.records = {'notice': NOTICE, 'rounded_saved_binding': binding, 'whole_graphs': {}, 'operators': {}}
        # Complete graph and isolated runtime expressions are audited before run.
        for kind, graph in zip(KINDS, (source, rounded)):
            directory = output / f'PLACEHOLDER-{kind}'
            directory.mkdir()
            self.runtimes[kind] = CompleteRuntime(graph, self.plan, directory)
            self.records['whole_graphs'][kind] = self.runtimes[kind].audit
        for position, record in enumerate(self.plan['nodes']):
            name, node = record['name'], self.nodes[record['name']]
            kernel = IsolatedSession(explicit_graph(source, node, record),
                output / f'PLACEHOLDER-operator-{position}')
            self.kernels[name, 'preserved'] = kernel
            self.kernels[name, 'rounded'] = kernel
            graphs = {'preserved': kernel.record, 'rounded': kernel.record}
            if node.op_type == 'BatchNormalization':
                graph = onnx.shape_inference.infer_shapes(rounded, strict_mode=True, data_prop=True)
                extracted = onnx.utils.Extractor(graph).extract_model([node.input[0]], [node.output[0]])
                extracted.ir_version = source.ir_version
                candidate = IsolatedSession(extracted, output / f'PLACEHOLDER-rounded-bn-{position}')
                self.kernels[name, 'rounded'] = candidate
                graphs['rounded'] = candidate.record
                module, shape = self.modules[name], record['boundaries'][node.input[0]]['shape']
                controls = {}
                for label, formulas, factory in (('formula', FORMULAS, formula_graph),
                                                ('promoted', AFFINE_FORMULAS, promoted_affine_graph)):
                    for formula in formulas:
                        path = output / f'PLACEHOLDER-{position}-{label}-{formula}.onnx'
                        factory(module, shape, formula, source, path)
                        control = IsolatedSession(onnx.load(path, load_external_data=False),
                            output / f'PLACEHOLDER-{position}-{label}-{formula}')
                        self.controls[name, label, formula] = control
                        controls[label + '_' + formula] = control.record
                self.rounding[name] = coefficient_cache(module)
                graphs['controls'] = controls
                graphs['rounding_coefficients'] = coefficient_records(module, self.rounding[name])
            self.records['operators'][name] = graphs
        if tensor_hash(model.state_dict()) != self.state:
            raise ValueError('complete replay setup changed saved state')
        self.records['operator_counts'] = dict(Counter(r['operator'] for r in self.plan['nodes']))

    def eager(self, node, operands):
        return python_operator(self.modules[node.name], operands[0]) if node.name in self.modules else recipe(node, operands)

    def control_outputs(self, node, operands):
        if node.name not in self.modules:
            return {}
        outputs = {'native_onnx': self.kernels[node.name, 'preserved'].run(ordered_feed(node, operands))}
        if node.op_type == 'Conv':
            return outputs
        module, value = self.modules[node.name], operands[0]
        outputs['float64_formula'] = double_formula(module, value)
        for formula in FORMULAS:
            outputs['formula_' + formula + '_python'] = python_formula(module, value, formula)
            outputs['formula_' + formula + '_onnx'] = self.controls[node.name, 'formula', formula].run([value])
        for formula in AFFINE_FORMULAS:
            outputs['promoted_' + formula + '_python'] = python_promoted_affine(module, value, formula)
            outputs['promoted_' + formula + '_onnx'] = self.controls[node.name, 'promoted', formula].run([value])
        for rounding in RECIPES:
            for engine in ('numpy', 'torch'):
                outputs['rounding_' + rounding + '_' + engine] = apply_recipe(
                    value, rounding, self.rounding[node.name][rounding][engine], engine)
        return outputs

    def run(self, value):
        # Validation and stale-state rejection precede any model/session call.
        validate(value, self.plan['nodes'][0]['boundaries'][self.source.graph.input[0].name])
        if tensor_hash(self.model.state_dict()) != self.state or any(m.training for m in self.model.modules()):
            raise ValueError('complete replay model state/mode changed before inference')
        if (any(m._forward_hooks or m._forward_pre_hooks for m in self.model.modules())
                or native_plan(self.model, self.source, self.rounded) != self.plan):
            raise ValueError('complete replay mapping/hooks changed before inference')
        original = value.copy()
        try:
            with torch.inference_mode():
                native_original = self.model(torch.from_numpy(value.copy())).numpy().copy()
            capture = capture_native(self.model, self.source, self.rounded, value)
            if capture['plan'] != self.plan:
                raise ValueError('complete replay native mapping changed')
            runtime = {kind: self.runtimes[kind].run(value) for kind in KINDS}
            evidence = {'notice': NOTICE, 'input': value.copy(), 'native_original_logit': native_original,
                'native_captured_logit': capture['logit'], 'graphs': {kind: {
                    key: result[key] for key in ('original_logit', 'tapped_logit')}
                    for kind, result in runtime.items()}, 'operators': {}}
            for event in capture['events']:
                node, operands = self.nodes[event['name']], event['operands']
                row = {'native_operands': operands, 'native_output': event['output'],
                       'eager_native': self.eager(node, operands), 'graphs': {}}
                for kind in KINDS:
                    tensors = runtime[kind]['values']
                    actual_operands = [tensors[name] for name in node.input]
                    kernel = self.kernels[node.name, kind]
                    native_feed = [operands[0]] if node.op_type == 'BatchNormalization' and kind == 'rounded' else ordered_feed(node, operands)
                    runtime_feed = [actual_operands[0]] if node.op_type == 'BatchNormalization' and kind == 'rounded' else ordered_feed(node, actual_operands)
                    row['graphs'][kind] = {
                        'runtime_operands': actual_operands, 'runtime_output': tensors[node.output[0]],
                        'eager_runtime': self.eager(node, actual_operands),
                        'isolated_native': kernel.run(native_feed), 'isolated_runtime': kernel.run(runtime_feed),
                        'controls': {origin: self.control_outputs(node, inputs) for origin, inputs in
                            zip(ORIGINS, (operands, actual_operands))} if node.name in self.modules else {}}
                evidence['operators'][node.name] = row
            return reconstruct_row(self.source, self.plan, evidence), evidence
        finally:
            if (tensor_hash(self.model.state_dict()) != self.state or not same_bits(original, value)
                    or any(m.training for m in self.model.modules())):
                raise ValueError('complete replay changed saved state/input/eval mode')
