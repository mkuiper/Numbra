"""ADR-015 same-input PLACEHOLDER operator diagnostics; never bundle graphs."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
import onnx
from onnx import helper, numpy_helper
import onnxruntime as ort
import torch
from torch import nn
from torch.nn import functional as F
from timm.layers import BatchNormAct2d

from . import PLACEHOLDER_NOTICE
from .evaluation import read_component_index
from .export import (INPUT_NAME, INPUT_SHAPE, OUTPUT_NAME, component_input,
                     export_environment, graph_report, runtime, runtime_logit,
                     session_options)
from .export_batchnorm import (DIAGNOSTIC_NOTICE, assert_batchnorm, boundaries,
                              mark_diagnostic)
from .export_diagnostics import verified_artifacts
from .prepare import repository_root
from .pretrained import ignored_path, sha256
from .train import json_text
from .training import tensor_hash
from .verify import backbone_architecture, load_reference

FORMULAS = ('subtract_divide', 'affine_rsqrt', 'affine_divide')


def selected_operators(model, graph):
    """First stem/depthwise pairs by saved order/connectivity, independent of drift."""
    matched = boundaries(model, graph)
    convs = [item for item in matched if isinstance(item[1], nn.Conv2d)]
    depthwise = [item for item in convs if item[1].groups > 1
                 and item[1].groups == item[1].in_channels == item[1].out_channels]
    if not convs or not depthwise or convs[0] == depthwise[0]:
        raise ValueError('replay requires distinct first stem and depthwise convolutions')
    result = []
    for conv in (convs[0], depthwise[0]):
        conv_node = next(node for node in graph.graph.node if node.output[0] == conv[2])
        norms = [(name, module, node) for name, module, tensor in matched
                 if isinstance(module, nn.BatchNorm2d)
                 for node in graph.graph.node if node.output[0] == tensor and node.input[0] == conv[2]]
        if len(norms) != 1:
            raise ValueError('expected one immediately following saved BatchNorm')
        result.append((conv[0], conv[1], conv_node))
        result.append(norms[0])
    return result


def validate_array(value):
    if (not isinstance(value, np.ndarray) or value.dtype != np.float32
            or value.ndim != 4 or not np.isfinite(value).all()):
        raise ValueError('replay requires finite float32 NCHW tensors')
    return value


def difference(before, after):
    validate_array(before)
    validate_array(after)
    if before.shape != after.shape:
        raise ValueError('replay output shape mismatch')
    delta = after.astype(np.float64) - before.astype(np.float64)
    return {'max_absolute_error': float(np.abs(delta).max()),
            'mean_absolute_error': float(np.abs(delta).mean())}


def python_operator(module, value):
    tensor = torch.from_numpy(validate_array(value).copy())
    with torch.inference_mode():
        if isinstance(module, nn.Conv2d):
            if module.padding_mode != 'zeros':
                raise ValueError('unsupported Conv padding mode')
            output = F.conv2d(tensor, module.weight, module.bias, module.stride,
                              module.padding, module.dilation, module.groups)
        elif isinstance(module, nn.BatchNorm2d):
            # Bypass timm's activation to match inference-only ONNX BN.
            output = F.batch_norm(tensor, module.running_mean, module.running_var,
                                  module.weight, module.bias, training=False, eps=module.eps)
        else:
            raise ValueError('unsupported replay module')
    return output.numpy().copy()


def bn_constants(module, formula):
    if not isinstance(module, nn.BatchNorm2d) or not module.affine or not module.track_running_stats:
        raise ValueError('BN formula requires saved affine eval buffers')
    with torch.inference_mode():
        weight, bias, mean, variance = [value.detach().clone() for value in
            (module.weight, module.bias, module.running_mean, module.running_var)]
        denominator = variance + module.eps
        if formula == 'subtract_divide':
            constants = {'mean': mean, 'denominator': torch.sqrt(denominator),
                         'weight': weight, 'bias': bias}
        elif formula in ('affine_rsqrt', 'affine_divide'):
            alpha = weight * torch.rsqrt(denominator) if formula == 'affine_rsqrt' else weight / torch.sqrt(denominator)
            constants = {'alpha': alpha, 'beta': bias - mean * alpha}
        else:
            raise ValueError('unknown declared BN formula')
    return {name: value.numpy().reshape(1, -1, 1, 1).copy() for name, value in constants.items()}


def python_formula(module, value, formula):
    constants = {name: torch.from_numpy(array) for name, array in bn_constants(module, formula).items()}
    with torch.inference_mode():
        tensor = torch.from_numpy(validate_array(value).copy())
        if formula == 'subtract_divide':
            output = ((tensor - constants['mean']) / constants['denominator']) * constants['weight'] + constants['bias']
        else:
            output = tensor * constants['alpha'] + constants['beta']
    return output.numpy().copy()


def double_formula(module, value):
    # Diagnostic mathematical formula, not the saved native float32 reference.
    weight, bias, mean, variance = [value.detach().numpy().astype(np.float64).reshape(1, -1, 1, 1)
        for value in (module.weight, module.bias, module.running_mean, module.running_var)]
    return (((validate_array(value).astype(np.float64) - mean) / np.sqrt(variance + module.eps))
            * weight + bias).astype(np.float32)


def formula_graph(module, shape, formula, source, path):
    constants = bn_constants(module, formula)
    if formula == 'subtract_divide':
        steps = [('Sub', ['x', 'mean'], 'centred'), ('Div', ['centred', 'denominator'], 'normal'),
                 ('Mul', ['normal', 'weight'], 'scaled'), ('Add', ['scaled', 'bias'], 'y')]
    else:
        steps = [('Mul', ['x', 'alpha'], 'scaled'), ('Add', ['scaled', 'beta'], 'y')]
    graph = helper.make_graph([helper.make_node(op, inputs, [output]) for op, inputs, output in steps],
        f'PLACEHOLDER-{formula}', [helper.make_tensor_value_info('x', onnx.TensorProto.FLOAT, shape)],
        [helper.make_tensor_value_info('y', onnx.TensorProto.FLOAT, shape)],
        [numpy_helper.from_array(value, name) for name, value in constants.items()])
    model = helper.make_model(graph, opset_imports=list(source.opset_import), ir_version=source.ir_version)
    mark_diagnostic(model)
    onnx.checker.check_model(model, full_check=True)
    onnx.save(model, path)


def operator_session(path, optimized):
    options = session_options('disabled')
    options.optimized_model_filepath = str(optimized)
    session = ort.InferenceSession(str(path), sess_options=options, providers=['CPUExecutionProvider'])
    if len(session.get_inputs()) != 1 or len(session.get_outputs()) != 1:
        raise ValueError('isolated operator requires one input and output')
    return session


def run_operator(session, value):
    output, = session.run(None, {session.get_inputs()[0].name: validate_array(value)})
    return validate_array(output)


def verified_preserved(source, model, saved, index, prepared, run):
    report_path = source / 'PLACEHOLDER-batchnorm-report.json'
    report = json.loads(report_path.read_text())
    path = source / 'PLACEHOLDER-preserved.onnx'
    ids = [item.id for item in index.components if item.split == 'train']
    if (report.get('notice') != PLACEHOLDER_NOTICE or report.get('status') != 'DIAGNOSTIC ONLY'
            or report['saved_model_sha256'] != saved['provenance']['model_sha256']
            or report['saved_run_sha256'] != sha256(run / 'PLACEHOLDER-run.json')):
        raise ValueError('preserved graph provenance mismatch')
    if (report['manifest_sha256'] != index.manifest_sha256
            or report['preparation_report_sha256'] != sha256(prepared / 'preparation-report.json')
            or report['model_state_before_sha256'] != tensor_hash(model.state_dict())
            or report['model_state_after_sha256'] != report['model_state_before_sha256']
            or report['protocol']['decision'] != 'ADR-014'
            or report['protocol']['split'] != 'train'
            or report['protocol']['components'] != len(ids)
            or report['protocol']['component_ids_sha256'] != hashlib.sha256(json_text(ids).encode()).hexdigest()
            or report['protocol']['frozen_evaluation_inputs_used']
            or report['protocol']['quantisation_fit']
            or report['protocol']['temperature'] != saved['calibration']['temperature']
            or report['protocol']['threshold'] != saved['primary_operating_point']['threshold']):
        raise ValueError('preserved graph provenance mismatch')
    profiles = report['artifacts']['batchnorm_preserved']['profiles']
    if (('boundary_diagnostics' in report
            and report['boundary_diagnostics']['status'] != 'VALID DIAGNOSTIC ONLY')
            or ('boundary_diagnostics' not in report
                and any(profile['original_graph_training_parity']['status'] != 'PASS' for profile in profiles.values()))):
        raise ValueError('preserved graph lacks valid boundary evidence')
    if (graph_report(path) != report['artifacts']['batchnorm_preserved']['graph']
            or sha256(source / 'PLACEHOLDER-batchnorm-details.json') != report['diagnostic_details_sha256']):
        raise ValueError('preserved graph checksum/report mismatch')
    graph = onnx.load(path, load_external_data=False)
    assert_batchnorm(graph, sum(isinstance(module, nn.BatchNorm2d) for module in model.modules()))
    return path, report_path, report


def replay_diagnostics(model, source, output, inputs, *, promoted=False):
    if promoted:
        from .export_precision import (AFFINE_FORMULAS, promoted_affine_graph,
            promoted_conv_graph, python_promoted_affine, python_promoted_conv)
    graph = onnx.shape_inference.infer_shapes(onnx.load(source, load_external_data=False), strict_mode=True)
    selected = selected_operators(model, graph)
    observed, handles = {}, []
    def input_hook(name):
        def capture(module, args):
            observed.setdefault(name, {})['input'] = args[0].detach().numpy().copy()
        return capture
    def output_hook(name):
        def capture(module, args, value):
            observed.setdefault(name, {})['output'] = value.detach().numpy().copy()
        return capture
    def norm_hook(name):
        def capture(module, args):
            observed.setdefault(name, {})['output'] = args[0].detach().numpy().copy()
        return capture
    try:
        for name, module, _ in selected:
            handles.append(module.register_forward_pre_hook(input_hook(name)))
            if isinstance(module, BatchNormAct2d):
                handles.append(module.drop.register_forward_pre_hook(norm_hook(name)))
            elif isinstance(module, nn.BatchNorm2d) and type(module) is not nn.BatchNorm2d:
                raise ValueError('unsupported BatchNorm subclass replay semantics')
            else:
                handles.append(module.register_forward_hook(output_hook(name)))
        with torch.inference_mode():
            model(torch.zeros(INPUT_SHAPE))
        tensor_names = list(dict.fromkeys(tensor for _, _, node in selected for tensor in (node.input[0], node.output[0])))
        shapes = {tensor: list(observed[name][key].shape) for name, _, node in selected
                  for tensor, key in ((node.input[0], 'input'), (node.output[0], 'output'))}
        original_output_names = {value.name for value in graph.graph.output}
        for tensor in tensor_names:
            if tensor not in original_output_names:
                graph.graph.output.append(helper.make_tensor_value_info(tensor, onnx.TensorProto.FLOAT, shapes[tensor]))
        mark_diagnostic(graph)
        onnx.checker.check_model(graph, full_check=True)
        tapped_path = output / 'PLACEHOLDER-replay-taps.onnx'
        onnx.save(graph, tapped_path)
        options = session_options('disabled')
        tapped_audit = output / 'PLACEHOLDER-replay-taps-optimized.onnx'
        options.optimized_model_filepath = str(tapped_audit)
        tapped = ort.InferenceSession(str(tapped_path), sess_options=options, providers=['CPUExecutionProvider'])
        original_audit = output / 'PLACEHOLDER-original-optimized.onnx'
        original = runtime(source, optimisation='disabled', optimized_path=original_audit)
        sessions, graphs, formula_sessions, promoted_sessions = {}, {}, {}, {}
        for position, (name, module, node) in enumerate(selected):
            path = output / f'PLACEHOLDER-operator-{position}.onnx'
            extracted = onnx.utils.Extractor(graph).extract_model([node.input[0]], [node.output[0]])
            extracted.ir_version = graph.ir_version
            mark_diagnostic(extracted)
            onnx.checker.check_model(extracted, full_check=True)
            onnx.save(extracted, path)
            optimized = output / f'PLACEHOLDER-operator-{position}-optimized.onnx'
            sessions[name] = operator_session(path, optimized)
            graphs[name] = {'original_operator': node.op_type, 'input_shape': shapes[node.input[0]],
                'output_shape': shapes[node.output[0]], 'graph': graph_report(path), 'runtime_graph': graph_report(optimized)}
            if isinstance(module, nn.BatchNorm2d):
                graphs[name]['formula_graphs'] = {}
                for formula in FORMULAS:
                    path = output / f'PLACEHOLDER-operator-{position}-{formula}.onnx'
                    optimized = output / f'PLACEHOLDER-operator-{position}-{formula}-optimized.onnx'
                    formula_graph(module, shapes[node.input[0]], formula, graph, path)
                    formula_sessions[name, formula] = operator_session(path, optimized)
                    graphs[name]['formula_graphs'][formula] = {'graph': graph_report(path), 'runtime_graph': graph_report(optimized)}
            if promoted and (position == 0 or isinstance(module, nn.BatchNorm2d)):
                strategies = AFFINE_FORMULAS if isinstance(module, nn.BatchNorm2d) else ('stem_matmul',)
                graphs[name]['promoted_graphs'] = {}
                for strategy in strategies:
                    path = output / f'PLACEHOLDER-operator-{position}-promoted-{strategy}.onnx'
                    optimized = output / f'PLACEHOLDER-operator-{position}-promoted-{strategy}-optimized.onnx'
                    if strategy == 'stem_matmul':
                        promoted_conv_graph(module, shapes[node.input[0]], graph, path)
                    else:
                        promoted_affine_graph(module, shapes[node.input[0]], strategy, graph, path)
                    promoted_sessions[name, strategy] = operator_session(path, optimized)
                    graphs[name]['promoted_graphs'][strategy] = {'graph': graph_report(path),
                        'runtime_graph': graph_report(optimized)}
        rows, ids = [], []
        with torch.inference_mode():
            for identifier, value in inputs:
                observed.clear()
                python_logit = float(model(torch.from_numpy(value))[0])
                original_logit = runtime_logit(original, value)
                results = tapped.run([OUTPUT_NAME] + tensor_names, {INPUT_NAME: value})
                tensors = dict(zip(tensor_names, results[1:]))
                local = {}
                for name, module, node in selected:
                    py_input, py_output = observed[name]['input'], observed[name]['output']
                    ort_input, ort_output = tensors[node.input[0]], tensors[node.output[0]]
                    py_on_py, py_on_ort = [python_operator(module, x) for x in (py_input, ort_input)]
                    ort_on_py, ort_on_ort = [run_operator(sessions[name], x) for x in (py_input, ort_input)]
                    propagation = py_on_ort.astype(np.float64) - py_output.astype(np.float64)
                    kernel = ort_on_ort.astype(np.float64) - py_on_ort.astype(np.float64)
                    extraction = ort_output.astype(np.float64) - ort_on_ort.astype(np.float64)
                    total = ort_output.astype(np.float64) - py_output.astype(np.float64)
                    stats = {'input_drift': difference(py_input, ort_input),
                        'whole_graph_output_drift': difference(py_output, ort_output),
                        'python_replay_fidelity': difference(py_output, py_on_py),
                        'local_kernel_on_python_input': difference(py_on_py, ort_on_py),
                        'local_kernel_on_onnx_input': difference(py_on_ort, ort_on_ort),
                        'propagated_input_effect': difference(py_output, py_on_ort),
                        'onnx_replay_fidelity': difference(ort_output, ort_on_ort),
                        'telescoping_max_residual': float(np.abs(total - (propagation + kernel + extraction)).max())}
                    if isinstance(module, nn.BatchNorm2d):
                        stats['formulas'] = {}
                        for origin, x, native in (('python_input', py_input, py_on_py), ('onnx_input', ort_input, py_on_ort)):
                            stats['formulas'][origin] = {'float64_rounded_vs_native': difference(native, double_formula(module, x))}
                            for formula in FORMULAS:
                                py_formula = python_formula(module, x, formula)
                                ort_formula = run_operator(formula_sessions[name, formula], x)
                                stats['formulas'][origin][formula] = {
                                    'python_vs_native': difference(native, py_formula),
                                    'onnx_vs_native': difference(native, ort_formula),
                                    'onnx_vs_python_formula': difference(py_formula, ort_formula)}
                    if 'promoted_graphs' in graphs[name]:
                        stats['promoted'] = {}
                        for origin, x, native in (('python_input', py_input, py_on_py), ('onnx_input', ort_input, py_on_ort)):
                            stats['promoted'][origin] = {}
                            for strategy in graphs[name]['promoted_graphs']:
                                py_promoted = (python_promoted_conv(module, x) if strategy == 'stem_matmul'
                                    else python_promoted_affine(module, x, strategy))
                                ort_promoted = run_operator(promoted_sessions[name, strategy], x)
                                stats['promoted'][origin][strategy] = {
                                    'python_vs_native': difference(native, py_promoted),
                                    'onnx_vs_native': difference(native, ort_promoted),
                                    'onnx_vs_python_promoted': difference(py_promoted, ort_promoted)}
                    local[name] = stats
                ids.append(identifier)
                rows.append({'operators': local, 'python_logit': python_logit, 'original_logit': original_logit,
                    'instrumented_logit': float(results[0][0]),
                    'instrumentation_absolute_logit_change': abs(float(results[0][0]) - original_logit)})
    finally:
        for handle in handles:
            handle.remove()
    if not rows:
        raise ValueError('replay diagnostics require training inputs')
    def aggregate(values):
        first = values[0]
        if isinstance(first, dict):
            return {key: aggregate([value[key] for value in values]) for key in first}
        return {'max': max(values), 'mean': float(np.mean(values))}
    summary = {'notice': DIAGNOSTIC_NOTICE, 'components': len(rows), 'selection': [name for name, _, _ in selected],
        'original_runtime_graph': graph_report(original_audit), 'instrumented_graph': graph_report(tapped_path),
        'instrumented_runtime_graph': graph_report(tapped_audit), 'operator_graphs': graphs,
        'operators': aggregate([row['operators'] for row in rows]),
        'instrumentation_absolute_logit_change': aggregate([row['instrumentation_absolute_logit_change'] for row in rows]),
        'status': 'VALID DIAGNOSTIC ONLY',
        'warning': 'signed elementwise telescoping; separate maxima cannot be added; extraction/taps may change execution'}
    return summary, {'notice': PLACEHOLDER_NOTICE, 'component_ids': ids, 'rows': rows}


def replay_run(repo, prepared, run, experiments, source, output, *, backbone_factory=backbone_architecture,
               promoted=False):
    prepared, run, source, output = [ignored_path(repo, path) for path in (prepared, run, source, output)]
    experiments = tuple(ignored_path(repo, path) for path in experiments)
    if not experiments:
        raise ValueError('replay requires retained export experiments')
    if output.exists() or not output.name.startswith('PLACEHOLDER-'):
        raise ValueError('replay output must be new and named PLACEHOLDER-*')
    environment = export_environment(repo)
    model, saved = load_reference(run, backbone_factory=backbone_factory)
    before = tensor_hash(model.state_dict())
    index = read_component_index(prepared / 'manifest.jsonl', prepared / 'preparation-report.json')
    artifacts = verified_artifacts(prepared, run, experiments, saved, index)
    path, report_path, _ = verified_preserved(source, model, saved, index, prepared, run)
    training = tuple(item for item in index.components if item.split == 'train')
    if not training:
        raise ValueError('replay requires training components')
    selected_operators(model, onnx.load(path, load_external_data=False))
    output.mkdir(parents=True, exist_ok=False)
    summary, details = replay_diagnostics(model, path, output,
        ((item.id, component_input(prepared, item)) for item in training), promoted=promoted)
    after = tensor_hash(model.state_dict())
    if after != before or any(module.training for module in model.modules()):
        raise ValueError('replay changed saved model state or eval mode')
    kind = 'precision' if promoted else 'replay'
    details_path = output / f'PLACEHOLDER-{kind}-details.json'
    details_path.write_text(json_text(details))
    report = {'notice': PLACEHOLDER_NOTICE, 'status': 'DIAGNOSTIC ONLY', 'version': '1.0.0',
        'created_utc': datetime.now(timezone.utc).isoformat(), 'environment': environment,
        'saved_model_sha256': saved['provenance']['model_sha256'], 'saved_run_sha256': sha256(run / 'PLACEHOLDER-run.json'),
        'manifest_sha256': index.manifest_sha256, 'preparation_report_sha256': sha256(prepared / 'preparation-report.json'),
        'model_state_before_sha256': before, 'model_state_after_sha256': after,
        'source_graph': graph_report(path), 'source_report_sha256': sha256(report_path),
        'retained_artifacts': {digest: {'kind': artifact['kind'], 'graph': artifact['graph'],
            'source_experiments': artifact['sources']} for digest, artifact in artifacts.items()},
        'protocol': {'decision': 'ADR-016' if promoted else 'ADR-015', 'split': 'train', 'components': len(training),
            'component_ids_sha256': hashlib.sha256(json_text([item.id for item in training]).encode()).hexdigest(),
            'frozen_evaluation_inputs_used': False, 'quantisation_fit': False, 'optimisation': 'disabled',
            'intra_op_threads': 2, 'inter_op_threads': 1, 'execution': 'sequential', 'formulas': list(FORMULAS),
            'deployment_selection': False},
        'diagnostics': summary, 'diagnostic_details_sha256': sha256(details_path),
        'scope': 'PLACEHOLDER training-only operator replay; never bundle; no deployment/mobile/clinical evidence'}
    if promoted:
        from .export_precision import AFFINE_FORMULAS
        report['protocol']['promoted_strategies'] = {'stem': 'float64 patch MatMul, bias, float32 boundary',
            'batchnorm': ['float32 coefficients, float64 multiply/add, float32 boundary: ' + formula
                          for formula in AFFINE_FORMULAS]}
    (output / f'PLACEHOLDER-{kind}-report.json').write_text(json_text(report))
    return report


def main(argv=None, *, promoted=False):
    parser = argparse.ArgumentParser(description=f'{PLACEHOLDER_NOTICE}; training-only operator replay')
    parser.add_argument('--prepared', type=Path, default=Path('data/prepared/synthetic-v2-selection'))
    parser.add_argument('--run', type=Path, default=Path('data/models/PLACEHOLDER-m3-baseline'))
    parser.add_argument('--experiments', nargs='+', type=Path, default=[
        Path('data/exports/PLACEHOLDER-m4-attempt1'), Path('data/exports/PLACEHOLDER-m4-attempt2')])
    parser.add_argument('--source', type=Path, default=Path('data/exports/PLACEHOLDER-m4-batchnorm2'))
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    repo = repository_root()
    try:
        output = ignored_path(repo, args.output)
        reports = repo / 'ml/reports'
        target = reports / f'{output.name}.json'
        if (target.exists() or target.is_symlink() or reports.resolve() != reports
                or not output.name.startswith('PLACEHOLDER-')):
            raise ValueError('aggregate target must be new, local and PLACEHOLDER-*')
        report = replay_run(repo, args.prepared, args.run, args.experiments, args.source, output, promoted=promoted)
        with target.open('x') as stream:
            stream.write(json_text(report))
    except (ValueError, OSError, RuntimeError, KeyError, TypeError) as exc:
        print(f'PLACEHOLDER operator replay failed: {exc}', file=sys.stderr)
        return 1
    print(f'PLACEHOLDER DIAGNOSTIC ONLY: {target.relative_to(repo)}; M4 remains incomplete')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
