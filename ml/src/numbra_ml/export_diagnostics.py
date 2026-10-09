"""Training-only PLACEHOLDER drift attribution; never deployment acceptance."""

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

from . import PLACEHOLDER_NOTICE
from .evaluation import read_component_index
from .export import (INPUT_NAME, INPUT_SHAPE, OUTPUT_NAME, OPTIMISATION_LEVELS,
                     aggregate_parity, component_input, export_environment,
                     graph_report, runtime, runtime_logit, session_options)
from .parity import FLOAT_BUDGET, QUANTISED_BUDGET, parity_report
from .prepare import repository_root
from .pretrained import ignored_path, sha256
from .train import json_text
from .verify import backbone_architecture, load_reference


def tap_features(source, target, dimensions):
    """Expose the unscaled features; outputs can affect ORT optimisation.

    The original graph is always run separately. Instrumented output differences
    are evidence rather than an assumed identity with deployment execution.
    """
    graph = onnx.load(source, load_external_data=False)
    candidates = [node for node in graph.graph.node if node.op_type == 'Sub'
                  and len(node.input) == 2 and node.input[1] == 'head.mean']
    if len(candidates) != 1 or dimensions < 1:
        raise ValueError('expected one saved-head feature boundary')
    name = candidates[0].input[0]
    graph.graph.output.append(onnx.helper.make_tensor_value_info(
        name, onnx.TensorProto.FLOAT, [1, dimensions]))
    onnx.helper.set_model_props(graph, {
        **{item.key: item.value for item in graph.metadata_props},
        'diagnostic_notice': 'PLACEHOLDER instrumented graph; never bundle',
    })
    onnx.checker.check_model(graph, full_check=True)
    onnx.save(graph, target)
    return name


def feature_drift(head, python_features, onnx_features, python_raw, tapped_raw):
    """Affine sensitivity in float64; observed head execution remains float32."""
    before, after = [np.asarray(value) for value in (python_features, onnx_features)]
    if (before.shape != (1, head.mean.numel()) or after.shape != before.shape
            or before.dtype != np.float32 or after.dtype != np.float32
            or not np.isfinite(before).all() or not np.isfinite(after).all()
            or not np.isfinite([python_raw, tapped_raw]).all()):
        raise ValueError('invalid diagnostic feature/logit output')
    with torch.inference_mode():
        head_raw = float(head(torch.from_numpy(after.copy()))[0])
    delta = after.astype(np.float64) - before.astype(np.float64)
    coefficients = (head.linear.weight.detach().numpy().astype(np.float64)
                    / head.scale.numpy().astype(np.float64))
    return {
        'max_feature_absolute_error': float(np.abs(delta).max()),
        'mean_feature_absolute_error': float(np.abs(delta).mean()),
        'induced_python_head_absolute_error': abs(head_raw - python_raw),
        'tapped_runtime_vs_python_head_absolute_error': abs(tapped_raw - head_raw),
        'affine_feature_error_bound': float((np.abs(delta) * np.abs(coefficients)).sum()),
        'affine_signed_feature_effect': float((delta * coefficients).sum()),
        'python_head_on_onnx_features': head_raw,
    }


def head_sensitivity(head):
    scale = head.scale.numpy().astype(np.float64)
    coefficients = head.linear.weight.detach().numpy().astype(np.float64) / scale
    return {'features': int(scale.size), 'minimum_scale': float(scale.min()),
            'maximum_scale': float(scale.max()),
            'maximum_absolute_effective_coefficient': float(np.abs(coefficients).max()),
            'effective_coefficient_l1': float(np.abs(coefficients).sum()),
            'warning': 'real-arithmetic affine sensitivity; does not bound float rounding'}


def diagnose_profile(model, original_path, tapped_path, feature_name, inputs,
                     *, optimisation, temperature, threshold, budget, audit_directory=None):
    original_audit = None if audit_directory is None else audit_directory / 'PLACEHOLDER-original-optimized.onnx'
    tapped_audit = None if audit_directory is None else audit_directory / 'PLACEHOLDER-features-optimized.onnx'
    if audit_directory is not None:
        audit_directory.mkdir(parents=True, exist_ok=False)
    original = runtime(original_path, optimisation=optimisation, optimized_path=original_audit)
    options = session_options(optimisation)
    if tapped_audit is not None:
        options.optimized_model_filepath = str(tapped_audit)
    tapped = ort.InferenceSession(str(tapped_path), sess_options=options,
                                 providers=['CPUExecutionProvider'])
    ids, reference, candidate, instrumented, rows = [], [], [], [], []
    with torch.inference_mode():
        for identifier, value in inputs:
            features = model.backbone(torch.from_numpy(value))
            before = float(model.head(features)[0])
            after = runtime_logit(original, value)
            raw, observed = tapped.run([OUTPUT_NAME, feature_name], {INPUT_NAME: value})
            if raw.shape != (1,) or raw.dtype != np.float32 or not np.isfinite(raw).all():
                raise ValueError('invalid instrumented raw-logit output')
            drift = feature_drift(model.head, features.numpy(), observed, before, float(raw[0]))
            drift['instrumentation_absolute_logit_change'] = abs(float(raw[0]) - after)
            ids.append(identifier)
            reference.append(before)
            candidate.append(after)
            instrumented.append(float(raw[0]))
            rows.append(drift)
    parity = parity_report(reference, candidate, identifiers=ids, temperature=temperature,
                           threshold=threshold, budget=budget)
    aggregate_keys = ('max_feature_absolute_error', 'mean_feature_absolute_error',
                      'induced_python_head_absolute_error',
                      'tapped_runtime_vs_python_head_absolute_error',
                      'affine_feature_error_bound', 'instrumentation_absolute_logit_change')
    summary = {'original_graph_training_parity': aggregate_parity(parity),
               'instrumented_attribution': {key: {'max': max(row[key] for row in rows),
                        'mean': float(np.mean([row[key] for row in rows]))} for key in aggregate_keys},
               'warning': 'attribution uses an extra graph output; original parity is measured separately'}
    if audit_directory is not None:
        summary['runtime_graphs'] = {'original': graph_report(original_audit),
                                    'instrumented': graph_report(tapped_audit)}
    details = {'component_ids': ids, 'python_logits': reference, 'original_onnx_logits': candidate,
               'instrumented_onnx_logits': instrumented, 'feature_attribution': rows, 'parity': parity}
    return summary, details


def verified_artifacts(prepared, run, experiments, model_report, index):
    """Reject stale/swapped graphs before any new input inference."""
    artifacts = {}
    provenance = model_report['provenance']
    if (index.manifest_sha256 != provenance['manifest_sha256']
            or sha256(prepared / 'preparation-report.json') != provenance['preparation_report_sha256']):
        raise ValueError('diagnostic preparation checksum mismatch')
    for experiment in experiments:
        report_path = experiment / 'PLACEHOLDER-export-report.json'
        report = json.loads(report_path.read_text())
        if (report.get('notice') != PLACEHOLDER_NOTICE
                or report['saved_model_sha256'] != provenance['model_sha256']
                or report['saved_run_sha256'] != sha256(run / 'PLACEHOLDER-run.json')
                or report['python_saved_verification']['manifest_sha256'] != index.manifest_sha256
                or report['interface']['temperature'] != model_report['calibration']['temperature']
                or report['interface']['threshold'] != model_report['primary_operating_point']['threshold']):
            raise ValueError('diagnostic experiment provenance mismatch')
        for name in ('float', 'int8'):
            path = experiment / f'PLACEHOLDER-{name}.onnx'
            actual = graph_report(path)
            if actual != report['artifacts'][name]['graph']:
                raise ValueError('diagnostic graph checksum/report mismatch')
            # Deduplicate identical float graphs, retaining both source reports.
            digest = actual['sha256']
            if digest not in artifacts:
                artifacts[digest] = {'path': path, 'kind': name, 'graph': actual, 'sources': []}
            artifacts[digest]['sources'].append({'attempt': report['attempt'],
                                                'report_sha256': sha256(report_path)})
    return artifacts


def diagnose_run(repo, prepared, run, experiments, output, *, backbone_factory=backbone_architecture):
    prepared, run, output = [ignored_path(repo, path) for path in (prepared, run, output)]
    experiments = tuple(ignored_path(repo, path) for path in experiments)
    if not experiments:
        raise ValueError('diagnostics require retained export experiments')
    if output.exists() or not output.name.startswith('PLACEHOLDER-'):
        raise ValueError('diagnostic output must be new and named PLACEHOLDER-*')
    environment = export_environment(repo)
    model, saved = load_reference(run, backbone_factory=backbone_factory)
    index = read_component_index(prepared / 'manifest.jsonl', prepared / 'preparation-report.json')
    artifacts = verified_artifacts(prepared, run, experiments, saved, index)
    training = tuple(item for item in index.components if item.split == 'train')
    if not training:
        raise ValueError('diagnostics require training components')
    temperature, threshold = saved['calibration']['temperature'], saved['primary_operating_point']['threshold']
    output.mkdir(parents=True, exist_ok=False)
    report = {'notice': PLACEHOLDER_NOTICE, 'version': '1.0.0',
              'created_utc': datetime.now(timezone.utc).isoformat(), 'environment': environment,
              'saved_model_sha256': saved['provenance']['model_sha256'],
              'saved_run_sha256': sha256(run / 'PLACEHOLDER-run.json'),
              'manifest_sha256': index.manifest_sha256,
              'preparation_report_sha256': sha256(prepared / 'preparation-report.json'),
              'protocol': {'decision': 'ADR-013', 'split': 'train', 'components': len(training),
                 'component_ids_sha256': hashlib.sha256(json_text([c.id for c in training]).encode()).hexdigest(),
                 'optimisation_levels': list(OPTIMISATION_LEVELS), 'intra_op_threads': 2,
                 'inter_op_threads': 1, 'execution': 'sequential', 'shape': list(INPUT_SHAPE),
                 'frozen_evaluation_inputs_used': False, 'temperature': temperature, 'threshold': threshold},
              'head_sensitivity': head_sensitivity(model.head), 'artifacts': {},
              'status': 'DIAGNOSTIC ONLY',
              'scope': 'PLACEHOLDER training-only attribution; no deployment acceptance or clinical/mobile evidence'}
    details = {'notice': PLACEHOLDER_NOTICE, 'artifacts': {}}
    for digest, artifact in artifacts.items():
        tapped = output / f'PLACEHOLDER-features-{digest}.onnx'
        feature_name = tap_features(artifact['path'], tapped, model.head.mean.numel())
        summary = {'kind': artifact['kind'], 'original_graph': artifact['graph'],
                   'source_experiments': artifact['sources'], 'instrumented_graph_sha256': sha256(tapped),
                   'profiles': {}}
        details['artifacts'][digest] = {}
        for profile in OPTIMISATION_LEVELS:
            aggregate, full = diagnose_profile(model, artifact['path'], tapped, feature_name,
                ((item.id, component_input(prepared, item)) for item in training),
                optimisation=profile, temperature=temperature, threshold=threshold,
                budget=FLOAT_BUDGET if artifact['kind'] == 'float' else QUANTISED_BUDGET)
            summary['profiles'][profile] = aggregate
            details['artifacts'][digest][profile] = full
        report['artifacts'][digest] = summary
    detail_path = output / 'PLACEHOLDER-diagnostic-details.json'
    detail_path.write_text(json_text(details))
    report['diagnostic_details_sha256'] = sha256(detail_path)
    (output / 'PLACEHOLDER-diagnostic-report.json').write_text(json_text(report))
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=f'{PLACEHOLDER_NOTICE}; training-only export diagnostics')
    parser.add_argument('--prepared', type=Path, default=Path('data/prepared/synthetic-v2-selection'))
    parser.add_argument('--run', type=Path, default=Path('data/models/PLACEHOLDER-m3-baseline'))
    parser.add_argument('--experiments', nargs='+', type=Path, default=[
        Path('data/exports/PLACEHOLDER-m4-attempt1'), Path('data/exports/PLACEHOLDER-m4-attempt2')])
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    repo = repository_root()
    try:
        # Like training reports, write only aggregate evidence to a new tracked target.
        output = ignored_path(repo, args.output)
        target = repo / 'ml/reports' / f'{output.name}.json'
        if target.exists() or not output.name.startswith('PLACEHOLDER-'):
            raise ValueError('diagnostic aggregate target must be new and PLACEHOLDER-*')
        report = diagnose_run(repo, args.prepared, args.run, args.experiments, output)
        with target.open('x') as stream:
            stream.write(json_text(report))
    except (ValueError, OSError, RuntimeError, KeyError, TypeError) as exc:
        print(f'PLACEHOLDER diagnostics failed: {exc}', file=sys.stderr)
        return 1
    print(f'PLACEHOLDER DIAGNOSTIC ONLY: evidence written to {target.relative_to(repo)}; M4 remains incomplete')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
