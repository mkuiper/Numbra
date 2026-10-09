"""ADR-017 complete training-only PLACEHOLDER BN arithmetic; never bundle."""

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
import onnx
from onnx import helper, numpy_helper
import torch
from torch import nn
from timm.layers import BatchNormAct2d

from . import PLACEHOLDER_NOTICE
from .evaluation import read_component_index
from .export import INPUT_SHAPE, component_input, export_environment, graph_report
from .export_batchnorm import assert_batchnorm, mark_diagnostic
from .export_diagnostics import diagnose_profile, head_sensitivity, tap_features, verified_artifacts
from .export_replay import bn_constants, verified_preserved
from .parity import FLOAT_BUDGET
from .prepare import repository_root
from .pretrained import ignored_path, sha256
from .train import json_text
from .training import tensor_hash
from .verify import backbone_architecture, load_reference

PREFIX = 'PLACEHOLDER-promoted-bn-'


def constant_array(graph, name):
    """Resolve exporter Identity aliases without treating arbitrary ops as constants."""
    initializers = {item.name: item for item in graph.graph.initializer}
    producers = {output: node for node in graph.graph.node for output in node.output}
    seen = set()
    while name not in initializers:
        if name in seen:
            raise ValueError('cyclic saved parameter alias')
        seen.add(name)
        node = producers.get(name)
        if node is None or node.op_type != 'Identity' or len(node.input) != 1:
            raise ValueError('expected constant saved parameter or Identity alias')
        name = node.input[0]
    return numpy_helper.to_array(initializers[name])


def expression_nodes(position, input_name, output_name):
    prefix = f'{PREFIX}{position}-'
    steps = [('Cast', [input_name], 'double-input', {'to': onnx.TensorProto.DOUBLE}),
             ('Cast', [prefix + 'alpha'], 'double-alpha', {'to': onnx.TensorProto.DOUBLE}),
             ('Cast', [prefix + 'beta'], 'double-beta', {'to': onnx.TensorProto.DOUBLE}),
             ('Mul', [prefix + 'double-input', prefix + 'double-alpha'], 'product', {}),
             ('Add', [prefix + 'product', prefix + 'double-beta'], 'sum', {}),
             ('Cast', [prefix + 'sum'], None, {'to': onnx.TensorProto.FLOAT})]
    return [helper.make_node(op, inputs, [output_name if output is None else prefix + output],
                             name=prefix + str(index), **attributes)
            for index, (op, inputs, output, attributes) in enumerate(steps)]


def coefficient_hash(array):
    return hashlib.sha256(np.ascontiguousarray(array).tobytes()).hexdigest()


def substitute_batchnorm(model, source, target, *, rounding_recipe=None):
    """Replace all saved BN nodes while preserving every other serialized node."""
    if rounding_recipe is not None:
        from .export_rounded_bn import RECIPE
        if rounding_recipe != RECIPE:
            raise ValueError('only the predeclared complete rounded BN recipe is allowed')
    if any(module.training for module in model.modules()):
        raise ValueError('complete substitution requires every module in eval mode')
    graph = onnx.load(source, load_external_data=False)
    assert_batchnorm(graph, sum(isinstance(module, nn.BatchNorm2d) for module in model.modules()))
    matched = []
    for name, module in model.named_modules():
        if not isinstance(module, nn.BatchNorm2d):
            continue
        nodes = [node for node in graph.graph.node if node.op_type == 'BatchNormalization'
                 and len(node.input) > 1 and node.input[1] == f'{name}.weight']
        if len(nodes) != 1:
            raise ValueError(f'expected one saved BatchNorm boundary node: {name}')
        matched.append((name, module, nodes[0].output[0]))
    names = [item.name for item in graph.graph.initializer]
    names += [value.name for value in (*graph.graph.input, *graph.graph.output, *graph.graph.value_info)]
    names += [name for node in graph.graph.node for name in (*node.input, *node.output, node.name)]
    if any(name.startswith(PREFIX) for name in names):
        raise ValueError('promoted BatchNorm namespace collision')
    before = tensor_hash(model.state_dict())
    replacement, records, extra = {}, [], []
    for position, (name, module, tensor) in enumerate(matched):
        if type(module) not in (nn.BatchNorm2d, BatchNormAct2d):
            raise ValueError('unsupported saved BatchNorm subclass')
        if not module.affine or not module.track_running_stats:
            raise ValueError('substitution requires saved affine eval buffers')
        node = next(node for node in graph.graph.node if node.output[0] == tensor)
        attributes = {attr.name: helper.get_attribute_value(attr) for attr in node.attribute}
        if (len(node.input) != 5
                or np.float32(attributes.get('epsilon', 1e-5)) != np.float32(module.eps)):
            raise ValueError('saved BatchNorm epsilon or parameter count mismatch')
        for input_name, value in zip(node.input[1:],
                (module.weight, module.bias, module.running_mean, module.running_var)):
            array = constant_array(graph, input_name)
            expected = value.detach().numpy()
            if (array.dtype != np.float32 or expected.dtype != np.float32
                    or array.shape != expected.shape or not np.array_equal(array, expected)):
                raise ValueError('saved BatchNorm parameter mismatch')
        rounding = None
        if rounding_recipe is None:
            constants = bn_constants(module, 'affine_rsqrt')
        else:
            from .export_rounded_bn import rounded_coefficients
            constants, rounding = rounded_coefficients(module)
        if any(not np.isfinite(array).all() for array in constants.values()):
            raise ValueError('non-finite promoted BatchNorm coefficients')
        prefix = f'{PREFIX}{position}-'
        extra.extend(numpy_helper.from_array(array, prefix + key) for key, array in constants.items())
        replacement[tensor] = expression_nodes(position, node.input[0], tensor)
        records.append({'module': name, 'position': position, 'input': node.input[0], 'output': tensor,
                        'coefficient_shape': list(constants['alpha'].shape),
                        'coefficients_sha256': {key: coefficient_hash(array) for key, array in constants.items()}})
        if rounding is not None:
            records[-1]['rounding'] = rounding
    nodes = [replacement[node.output[0]] if node.op_type == 'BatchNormalization' else [node]
             for node in graph.graph.node]
    del graph.graph.node[:]
    graph.graph.node.extend(node for group in nodes for node in group)
    graph.graph.initializer.extend(extra)
    mark_diagnostic(graph)
    onnx.checker.check_model(graph, full_check=True)
    if tensor_hash(model.state_dict()) != before:
        raise ValueError('substitution changed saved model state')
    onnx.save(graph, target)
    audit_promoted_graph(target, source, records, serialized=True)
    return records


def audit_promoted_graph(path, source, records, *, serialized=False):
    """Inspect the actual ORT graph, including coefficient bits and stage casts."""
    graph, original = [onnx.load(item, load_external_data=False) for item in (path, source)]
    if not records or any(node.op_type == 'BatchNormalization' for node in graph.graph.node):
        raise ValueError('promoted graph must replace every BatchNorm')
    promoted = [node for node in graph.graph.node if node.name.startswith(PREFIX)]
    expected = [node for record in records for node in expression_nodes(
        record['position'], record['input'], record['output'])]
    actual_by_name = {node.name: node for node in promoted}
    if (len(promoted) != len(expected) or len(actual_by_name) != len(expected)
            or any(node.name not in actual_by_name
                or actual_by_name[node.name].SerializeToString() != node.SerializeToString() for node in expected)):
        raise ValueError('promoted arithmetic/cast audit mismatch')
    for record in records:
        for key in ('alpha', 'beta'):
            array = constant_array(graph, f"{PREFIX}{record['position']}-{key}")
            if (array.dtype != np.float32 or list(array.shape) != record['coefficient_shape']
                    or coefficient_hash(array) != record['coefficients_sha256'][key]):
                raise ValueError('promoted coefficient audit mismatch')
    original_ops = Counter(node.op_type for node in original.graph.node)
    actual_ops = Counter(node.op_type for node in graph.graph.node)
    for op in ('Conv', 'Gemm', 'MatMul'):
        if actual_ops[op] != original_ops[op]:
            raise ValueError('promoted graph changed Conv/head operator count')
    if serialized:
        retained = [node.SerializeToString() for node in graph.graph.node if not node.name.startswith(PREFIX)]
        original_retained = [node.SerializeToString() for node in original.graph.node if node.op_type != 'BatchNormalization']
        original_constants = [item.SerializeToString() for item in original.graph.initializer]
        if (retained != original_retained
                or [item.SerializeToString() for item in graph.graph.initializer[:len(original_constants)]] != original_constants
                or graph.graph.input != original.graph.input or graph.graph.output != original.graph.output):
            raise ValueError('substitution changed retained nodes/constants/interface')
    return {'notice': 'PLACEHOLDER diagnostic graph; never bundle', 'status': 'PASS',
            'replaced_batchnorm_nodes': len(records), 'promoted_expression_nodes': len(expected),
            'float32_coefficients_and_output_boundaries': True,
            'original_conv_head_counts_retained': True,
            'original_other_nodes_and_initializers_retained': serialized}


def promoted_bn_run(repo, prepared, run, experiments, source, output,
                    *, backbone_factory=backbone_architecture, joint_stem=False, rounding_recipe=None):
    if joint_stem and rounding_recipe is not None:
        raise ValueError('rounded BN protocol forbids joint stem substitution')
    prepared, run, source, output = [ignored_path(repo, path) for path in (prepared, run, source, output)]
    experiments = tuple(ignored_path(repo, path) for path in experiments)
    if not experiments:
        raise ValueError('complete BN diagnostics require retained export experiments')
    if output.exists() or not output.name.startswith('PLACEHOLDER-'):
        raise ValueError('complete BN output must be new and named PLACEHOLDER-*')
    environment = export_environment(repo)
    model, saved = load_reference(run, backbone_factory=backbone_factory)
    before = tensor_hash(model.state_dict())
    index = read_component_index(prepared / 'manifest.jsonl', prepared / 'preparation-report.json')
    retained = verified_artifacts(prepared, run, experiments, saved, index)
    preserved, source_report, _ = verified_preserved(source, model, saved, index, prepared, run)
    training = tuple(item for item in index.components if item.split == 'train')
    if not training:
        raise ValueError('complete BN diagnostics require training components')
    temperature = saved['calibration']['temperature']
    threshold = saved['primary_operating_point']['threshold']
    output.mkdir(parents=True, exist_ok=False)
    promoted = output / 'PLACEHOLDER-complete-promoted-bn.onnx'
    records = substitute_batchnorm(model, preserved, promoted, rounding_recipe=rounding_recipe)
    artifacts = [('preserved_control', preserved), ('complete_promoted_bn', promoted)]
    stem_record = None
    if joint_stem:
        from .export_joint import substitute_stem, audit_stem_graph
        stem_only = output / 'PLACEHOLDER-promoted-stem-preserved-bn.onnx'
        stem_record = substitute_stem(model, preserved, stem_only)
        joint = output / 'PLACEHOLDER-joint-promoted-stem-bn.onnx'
        joint_records = substitute_batchnorm(model, stem_only, joint)
        if joint_records != records:
            raise ValueError('joint substitution changed BatchNorm coefficients or boundaries')
        audit_stem_graph(joint, promoted, stem_record, serialized=True)
        artifacts.append(('joint_promoted_stem_bn', joint))
    report = {'notice': PLACEHOLDER_NOTICE, 'status': 'DIAGNOSTIC ONLY', 'version': '1.0.0',
        'created_utc': datetime.now(timezone.utc).isoformat(), 'environment': environment,
        'saved_model_sha256': saved['provenance']['model_sha256'], 'saved_run_sha256': sha256(run / 'PLACEHOLDER-run.json'),
        'manifest_sha256': index.manifest_sha256, 'preparation_report_sha256': sha256(prepared / 'preparation-report.json'),
        'model_state_before_sha256': before, 'source_graph': graph_report(preserved),
        'source_report_sha256': sha256(source_report), 'head_sensitivity': head_sensitivity(model.head),
        'retained_artifacts': {digest: {'kind': artifact['kind'], 'graph': artifact['graph'],
            'source_experiments': artifact['sources']} for digest, artifact in retained.items()},
        'protocol': {'decision': 'ADR-017', 'split': 'train', 'components': len(training),
            'component_ids_sha256': hashlib.sha256(json_text([item.id for item in training]).encode()).hexdigest(),
            'frozen_evaluation_inputs_used': False, 'quantisation_fit': False, 'deployment_selection': False,
            'optimisation': 'disabled', 'intra_op_threads': 2, 'inter_op_threads': 1, 'execution': 'sequential',
            'shape': list(INPUT_SHAPE), 'temperature': temperature, 'threshold': threshold,
            'formula': 'saved float32 affine_rsqrt coefficients; double Mul/Add; float32 boundary',
            'expected_batchnorm_substitutions': len(records)},
        'substitutions': records, 'artifacts': {},
        'scope': 'PLACEHOLDER complete training-only BN graph experiment; never bundle; no mobile/clinical/deployment evidence'}
    if rounding_recipe is not None:
        from .export_rounded_bn import audit_saved_coefficients
        report['protocol'].update(decision='ADR-021', rounding_recipe=rounding_recipe,
            formula='e32-r32-a32-b64 coefficients rounded to float32; double Mul/Add; float32 boundary')
        report['coefficient_audit'] = audit_saved_coefficients(model, preserved, records)
        report['scope'] = 'PLACEHOLDER training-only complete rounded BN graph; never bundle; no mobile/clinical/deployment evidence'
    if joint_stem:
        report['protocol'].update(decision='ADR-018', promoted_stem_convolutions=1,
            stem_formula='saved float32 weights; fixed patches; double MatMul; float32 boundary')
        report['stem_substitution'] = stem_record
        report['stem_only_graph'] = graph_report(stem_only)
        report['isolated_stem_graph'] = graph_report(stem_only.with_name(stem_only.stem + '-isolated.onnx'))
        report['scope'] = 'PLACEHOLDER training-only joint stem/BN experiment; never bundle; no mobile/clinical/deployment evidence'
    details = {'notice': PLACEHOLDER_NOTICE, 'artifacts': {}}
    for name, path in artifacts:
        tapped = output / f'PLACEHOLDER-{name}-features.onnx'
        feature_name = tap_features(path, tapped, model.head.mean.numel())
        audit_directory = output / f'PLACEHOLDER-{name}-audit'
        aggregate, full = diagnose_profile(model, path, tapped, feature_name,
            ((item.id, component_input(prepared, item)) for item in training),
            optimisation='disabled', temperature=temperature, threshold=threshold,
            budget=FLOAT_BUDGET, audit_directory=audit_directory)
        audits = {}
        for tag in ('original', 'features'):
            audit_path = audit_directory / f'PLACEHOLDER-{tag}-optimized.onnx'
            if name == 'complete_promoted_bn':
                audits[tag] = audit_promoted_graph(audit_path, preserved, records)
            elif name == 'joint_promoted_stem_bn':
                audits[tag] = {'status': 'PASS',
                    'batchnorm': audit_promoted_graph(audit_path, stem_only, records),
                    'stem': audit_stem_graph(audit_path, preserved, stem_record)}
            else:
                assert_batchnorm(onnx.load(audit_path), len(records))
                audits[tag] = {'status': 'PASS', 'batchnorm_nodes': len(records)}
        report['artifacts'][name] = {'graph': graph_report(path), 'instrumented_graph': graph_report(tapped),
                                    'diagnostics': aggregate, 'runtime_audits': audits}
        details['artifacts'][name] = full
    after = tensor_hash(model.state_dict())
    if after != before or any(module.training for module in model.modules()):
        raise ValueError('complete BN diagnostics changed model state or eval mode')
    report['model_state_after_sha256'] = after
    detail_path = output / 'PLACEHOLDER-promoted-bn-details.json'
    detail_path.write_text(json_text(details))
    report['diagnostic_details_sha256'] = sha256(detail_path)
    if rounding_recipe is not None:
        from .export_rounded_bn import audit_rounded_report
        report['evidence_audit'] = audit_rounded_report(output, report, model, preserved, index, saved)
    (output / 'PLACEHOLDER-promoted-bn-report.json').write_text(json_text(report))
    return report


def main(argv=None, *, joint_stem=False, rounding_recipe=None):
    parser = argparse.ArgumentParser(description=f'{PLACEHOLDER_NOTICE}; complete training-only BN experiment')
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
        report = promoted_bn_run(repo, args.prepared, args.run, args.experiments, args.source, output,
                                 joint_stem=joint_stem, rounding_recipe=rounding_recipe)
        with target.open('x') as stream:
            stream.write(json_text(report))
    except (ValueError, OSError, RuntimeError, KeyError, TypeError) as exc:
        print(f'PLACEHOLDER complete BN diagnostics failed: {exc}', file=sys.stderr)
        return 1
    print(f'PLACEHOLDER DIAGNOSTIC ONLY: {target.relative_to(repo)}; M4 remains incomplete')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
