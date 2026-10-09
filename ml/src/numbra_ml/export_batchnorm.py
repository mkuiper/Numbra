"""ADR-014 training-only PLACEHOLDER graph experiments; never bundle copies."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
import onnx
import onnxruntime as ort
import torch
from torch import nn
from timm.layers import BatchNormAct2d

from . import PLACEHOLDER_NOTICE
from .evaluation import read_component_index
from .export import (INPUT_NAME, INPUT_SHAPE, OUTPUT_NAME, component_input,
                     export_environment, export_float, graph_report,
                     local_temporaries, runtime, runtime_logit, session_options)
from .export_diagnostics import (diagnose_profile, head_sensitivity, tap_features,
                                 verified_artifacts)
from .parity import FLOAT_BUDGET
from .prepare import repository_root
from .preprocessing import SPEC
from .pretrained import ignored_path, sha256
from .train import json_text
from .training import tensor_hash
from .verify import backbone_architecture, load_reference

PROFILES = ('disabled', 'all')
DIAGNOSTIC_NOTICE = 'PLACEHOLDER diagnostic graph; never bundle'


def mark_diagnostic(graph):
    onnx.helper.set_model_props(graph, {
        **{item.key: item.value for item in graph.metadata_props},
        'notice': PLACEHOLDER_NOTICE, 'preprocessing_version': SPEC['version'],
        'diagnostic_notice': DIAGNOSTIC_NOTICE,
    })


def assert_batchnorm(graph, expected):
    nodes = [node for node in graph.graph.node if node.op_type == 'BatchNormalization']
    if len(nodes) != expected or expected < 1:
        raise ValueError('BatchNorm-preserving graph node count mismatch')
    for node in nodes:
        attributes = {item.name: onnx.helper.get_attribute_value(item) for item in node.attribute}
        if attributes.get('training_mode', 0) != 0 or len(node.output) != 1:
            raise ValueError('BatchNorm graph must use inference mode')


def export_preserving_batchnorm(model, path):
    """Keep original eval buffers and export separate, inference-only BN nodes."""
    if any(module.training for module in model.modules()):
        raise ValueError('BatchNorm export requires every module in eval mode')
    count = sum(isinstance(module, nn.BatchNorm2d) for module in model.modules())
    if not count:
        raise ValueError('BatchNorm experiment requires saved BatchNorm2d modules')
    before = tensor_hash(model.state_dict())
    with local_temporaries(path.parent), torch.inference_mode():
        torch.onnx.export(model, torch.zeros(INPUT_SHAPE), str(path),
            input_names=[INPUT_NAME], output_names=[OUTPUT_NAME], opset_version=17,
            dynamo=False, external_data=False, do_constant_folding=False,
            training=torch.onnx.TrainingMode.PRESERVE)
    if tensor_hash(model.state_dict()) != before or any(m.training for m in model.modules()):
        raise ValueError('export changed saved model state or eval mode')
    graph = onnx.load(path, load_external_data=False)
    assert_batchnorm(graph, count)
    mark_diagnostic(graph)
    onnx.checker.check_model(graph, full_check=True)
    onnx.save(graph, path)
    return count


def boundaries(model, graph):
    """Match every Conv/BN module to one ONNX node using saved parameter names."""
    result = []
    for name, module in model.named_modules():
        if not isinstance(module, (nn.Conv2d, nn.BatchNorm2d)):
            continue
        operator = 'Conv' if isinstance(module, nn.Conv2d) else 'BatchNormalization'
        nodes = [node for node in graph.graph.node if node.op_type == operator
                 and len(node.input) > 1 and node.input[1] == f'{name}.weight']
        if len(nodes) != 1:
            raise ValueError(f'expected one saved boundary node: {name}')
        result.append((name, module, nodes[0].output[0]))
    if not result:
        raise ValueError('no saved Conv/BatchNorm boundaries')
    return result


def boundary_diagnostics(model, source, output, inputs):
    """All module boundaries, disabled optimisation; original parity is separate."""
    graph = onnx.load(source, load_external_data=False)
    matched = boundaries(model, graph)
    observed, handles = {}, []
    def capture(name):
        def hook(module, args, value):
            observed[name] = value.detach().numpy().copy()
        return hook
    def capture_before_activation(name):
        def hook(module, args):
            observed[name] = args[0].detach().numpy().copy()
        return hook
    try:
        for name, module, _ in matched:
            if isinstance(module, BatchNormAct2d):
                # timm performs BN -> drop -> act inside one BatchNorm subclass.
                # Its module output is already activated (often in place). Tap
                # the drop INPUT to match ONNX's pre-activation BN output.
                handles.append(module.drop.register_forward_pre_hook(capture_before_activation(name)))
            elif isinstance(module, nn.BatchNorm2d) and type(module) is not nn.BatchNorm2d:
                raise ValueError('unsupported BatchNorm subclass boundary semantics')
            else:
                handles.append(module.register_forward_hook(capture(name)))
        with torch.inference_mode():
            model(torch.zeros(INPUT_SHAPE))
        for name, _, tensor in matched:
            graph.graph.output.append(onnx.helper.make_tensor_value_info(
                tensor, onnx.TensorProto.FLOAT, list(observed[name].shape)))
        mark_diagnostic(graph)
        onnx.checker.check_model(graph, full_check=True)
        path = output / 'PLACEHOLDER-boundaries.onnx'
        onnx.save(graph, path)
        original = runtime(source, optimisation='disabled')
        options = session_options('disabled')
        optimized_path = output / 'PLACEHOLDER-boundaries-optimized.onnx'
        options.optimized_model_filepath = str(optimized_path)
        tapped = ort.InferenceSession(str(path), sess_options=options, providers=['CPUExecutionProvider'])
        count = sum(isinstance(module, nn.BatchNorm2d) for module in model.modules())
        assert_batchnorm(onnx.load(optimized_path), count)
        rows, ids = [], []
        with torch.inference_mode():
            for identifier, value in inputs:
                observed.clear()
                before = float(model(torch.from_numpy(value))[0])
                original_raw = runtime_logit(original, value)
                outputs = tapped.run([OUTPUT_NAME] + [tensor for _, _, tensor in matched], {INPUT_NAME: value})
                raw = outputs[0]
                if raw.shape != (1,) or raw.dtype != np.float32 or not np.isfinite(raw).all():
                    raise ValueError('invalid boundary raw-logit output')
                local = {}
                for (name, _, _), candidate in zip(matched, outputs[1:]):
                    reference = observed[name]
                    if (candidate.shape != reference.shape or candidate.dtype != np.float32
                            or not np.isfinite(candidate).all() or not np.isfinite(reference).all()):
                        raise ValueError('invalid boundary output')
                    error = np.abs(candidate.astype(np.float64) - reference.astype(np.float64))
                    local[name] = {'max_absolute_error': float(error.max()),
                                   'mean_absolute_error': float(error.mean())}
                ids.append(identifier)
                rows.append({'boundaries': local, 'python_logit': before,
                             'original_logit': original_raw, 'instrumented_logit': float(raw[0]),
                             'instrumentation_absolute_logit_change': abs(float(raw[0]) - original_raw)})
    finally:
        for handle in handles:
            handle.remove()
    if not rows:
        raise ValueError('boundary diagnostics require training inputs')
    summary = {'notice': DIAGNOSTIC_NOTICE, 'components': len(rows), 'optimisation': 'disabled',
        'instrumented_graph': graph_report(path), 'runtime_graph': graph_report(optimized_path),
        'boundaries': {name: {'operator': 'Conv' if isinstance(module, nn.Conv2d) else 'BatchNormalization',
            'python_capture': 'BatchNormAct2d.drop input before activation' if isinstance(module, BatchNormAct2d) else 'module output',
            'shape': list(observed[name].shape),
            'max_absolute_error': max(row['boundaries'][name]['max_absolute_error'] for row in rows),
            'mean_absolute_error': float(np.mean([row['boundaries'][name]['mean_absolute_error'] for row in rows]))}
            for name, module, _ in matched},
        'instrumentation_absolute_logit_change': {'max': max(row['instrumentation_absolute_logit_change'] for row in rows),
            'mean': float(np.mean([row['instrumentation_absolute_logit_change'] for row in rows]))},
        'status': 'VALID DIAGNOSTIC ONLY',
        'warning': 'local accumulated boundary drift; taps can affect execution; not causal attribution'}
    return summary, {'notice': PLACEHOLDER_NOTICE, 'component_ids': ids, 'rows': rows}


def batchnorm_run(repo, prepared, run, experiments, output, *, backbone_factory=backbone_architecture):
    prepared, run, output = [ignored_path(repo, path) for path in (prepared, run, output)]
    experiments = tuple(ignored_path(repo, path) for path in experiments)
    if not experiments:
        raise ValueError('BatchNorm diagnostics require retained export experiments')
    if output.exists() or not output.name.startswith('PLACEHOLDER-'):
        raise ValueError('diagnostic output must be new and named PLACEHOLDER-*')
    environment = export_environment(repo)
    model, saved = load_reference(run, backbone_factory=backbone_factory)
    index = read_component_index(prepared / 'manifest.jsonl', prepared / 'preparation-report.json')
    retained = verified_artifacts(prepared, run, experiments, saved, index)
    training = tuple(item for item in index.components if item.split == 'train')
    if not training:
        raise ValueError('BatchNorm diagnostics require training components')
    before = tensor_hash(model.state_dict())
    temperature, threshold = saved['calibration']['temperature'], saved['primary_operating_point']['threshold']
    output.mkdir(parents=True, exist_ok=False)
    preserved = output / 'PLACEHOLDER-preserved.onnx'
    count = export_preserving_batchnorm(model, preserved)
    folded = output / 'PLACEHOLDER-folded-control.onnx'
    export_float(model, folded)
    # Compare unmarked bytes to the original export, then label this diagnostic copy.
    folded_hash = sha256(folded)
    matches = [digest for digest, artifact in retained.items() if artifact['kind'] == 'float' and digest == folded_hash]
    graph = onnx.load(folded)
    mark_diagnostic(graph)
    onnx.save(graph, folded)
    report = {'notice': PLACEHOLDER_NOTICE, 'version': '1.0.0',
        'created_utc': datetime.now(timezone.utc).isoformat(), 'environment': environment,
        'saved_model_sha256': saved['provenance']['model_sha256'],
        'saved_run_sha256': sha256(run / 'PLACEHOLDER-run.json'),
        'manifest_sha256': index.manifest_sha256,
        'preparation_report_sha256': sha256(prepared / 'preparation-report.json'),
        'model_state_before_sha256': before, 'head_sensitivity': head_sensitivity(model.head),
        'protocol': {'decision': 'ADR-014', 'split': 'train', 'components': len(training),
            'component_ids_sha256': hashlib.sha256(json_text([item.id for item in training]).encode()).hexdigest(),
            'frozen_evaluation_inputs_used': False, 'quantisation_fit': False,
            'optimisation_levels': list(PROFILES), 'expected_batchnorm_nodes': count,
            'do_constant_folding': False, 'training': 'PRESERVE; every module eval',
            'shape': list(INPUT_SHAPE), 'intra_op_threads': 2, 'inter_op_threads': 1,
            'execution': 'sequential', 'temperature': temperature, 'threshold': threshold,
            'exporter_utils_sha256': sha256(Path(torch.onnx.utils.__file__))},
        'folded_control_before_diagnostic_marking_sha256': folded_hash,
        'folded_control_matches_retained_float': bool(matches),
        'retained_artifacts': {digest: {'kind': artifact['kind'], 'graph': artifact['graph'],
            'source_experiments': artifact['sources']} for digest, artifact in retained.items()},
        'artifacts': {}, 'status': 'DIAGNOSTIC ONLY',
        'scope': 'PLACEHOLDER training-only graph experiment; never bundle; no clinical/mobile/deployment evidence'}
    details = {'notice': PLACEHOLDER_NOTICE, 'artifacts': {}}
    for name, path in (('folded_control', folded), ('batchnorm_preserved', preserved)):
        tapped = output / f'PLACEHOLDER-{name}-features.onnx'
        feature_name = tap_features(path, tapped, model.head.mean.numel())
        summary = {'graph': graph_report(path), 'instrumented_graph': graph_report(tapped), 'profiles': {}}
        details['artifacts'][name] = {}
        for profile in PROFILES:
            aggregate, full = diagnose_profile(model, path, tapped, feature_name,
                ((item.id, component_input(prepared, item)) for item in training),
                optimisation=profile, temperature=temperature, threshold=threshold, budget=FLOAT_BUDGET,
                audit_directory=output / f'PLACEHOLDER-{name}-{profile}-audit')
            if name == 'batchnorm_preserved' and profile == 'disabled':
                for audit in ('original', 'features'):
                    audit_path = output / f'PLACEHOLDER-{name}-{profile}-audit' / f'PLACEHOLDER-{audit}-optimized.onnx'
                    assert_batchnorm(onnx.load(audit_path), count)
            summary['profiles'][profile] = aggregate
            details['artifacts'][name][profile] = full
        report['artifacts'][name] = summary
    if any(profile['original_graph_training_parity']['status'] != 'PASS'
           for profile in report['artifacts']['batchnorm_preserved']['profiles'].values()):
        report['boundary_diagnostics'], details['boundary_diagnostics'] = boundary_diagnostics(
            model, preserved, output, ((item.id, component_input(prepared, item)) for item in training))
    after = tensor_hash(model.state_dict())
    if after != before or any(module.training for module in model.modules()):
        raise ValueError('diagnostics changed saved model state or eval mode')
    report['model_state_after_sha256'] = after
    detail_path = output / 'PLACEHOLDER-batchnorm-details.json'
    detail_path.write_text(json_text(details))
    report['diagnostic_details_sha256'] = sha256(detail_path)
    (output / 'PLACEHOLDER-batchnorm-report.json').write_text(json_text(report))
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=f'{PLACEHOLDER_NOTICE}; training-only BatchNorm experiment')
    parser.add_argument('--prepared', type=Path, default=Path('data/prepared/synthetic-v2-selection'))
    parser.add_argument('--run', type=Path, default=Path('data/models/PLACEHOLDER-m3-baseline'))
    parser.add_argument('--experiments', nargs='+', type=Path, default=[
        Path('data/exports/PLACEHOLDER-m4-attempt1'), Path('data/exports/PLACEHOLDER-m4-attempt2')])
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
        report = batchnorm_run(repo, args.prepared, args.run, args.experiments, output)
        with target.open('x') as stream:
            stream.write(json_text(report))
    except (ValueError, OSError, RuntimeError, KeyError, TypeError) as exc:
        print(f'PLACEHOLDER BatchNorm diagnostics failed: {exc}', file=sys.stderr)
        return 1
    print(f'PLACEHOLDER DIAGNOSTIC ONLY: {target.relative_to(repo)}; M4 remains incomplete')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
