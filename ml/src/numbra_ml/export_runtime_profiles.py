"""ADR-022 fixed training-only PLACEHOLDER runtime profiles; never bundle."""

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

from . import PLACEHOLDER_NOTICE
from .evaluation import read_component_index
from .export import INPUT_SHAPE, OPTIMISATION_LEVELS, aggregate_parity, component_input, export_environment, graph_report
from .export_diagnostics import diagnose_profile, tap_features, verified_artifacts
from .export_promoted_bn import PREFIX, constant_array
from .export_replay import verified_preserved
from .export_rounded_bn import RECIPE, audit_rounded_report, audit_saved_coefficients
from .parity import FLOAT_BUDGET, parity_report
from .prepare import repository_root
from .pretrained import ignored_path, sha256
from .train import json_text
from .training import tensor_hash
from .verify import backbone_architecture, load_reference

PROFILES = ('disabled', 'basic', 'extended', 'all')
ARTIFACTS = ('preserved_control', 'complete_promoted_bn')
REPORT = 'PLACEHOLDER-runtime-profiles-report.json'
DETAILS = 'PLACEHOLDER-runtime-profiles-details.json'
NOTICE = 'PLACEHOLDER diagnostic only; never bundle'


def audit_runtime_expression(path, original, records):
    """Permit exact constant-Cast folding, never a different BN expression."""
    graph = onnx.load(path, load_external_data=False)
    source = onnx.load(original, load_external_data=False)
    initializers = {item.name: item for item in graph.graph.initializer}
    producers = {output: node for node in graph.graph.node for output in node.output}
    if len(producers) != sum(len(node.output) for node in graph.graph.node):
        raise ValueError('runtime expression has duplicate tensor producers')
    if not records or any(node.op_type == 'BatchNormalization' for node in graph.graph.node):
        raise ValueError('runtime expression must replace every BN')
    checked, constant_casts, folded = set(), 0, 0

    def constant(name, seen=None):
        seen = set() if seen is None else seen
        if name in seen:
            raise ValueError('runtime expression constant alias cycle')
        seen.add(name)
        if name in initializers:
            return numpy_helper.to_array(initializers[name])
        node = producers.get(name)
        if (node is None or node.domain or len(node.input) != 1 or len(node.output) != 1
                or node.op_type not in ('Identity', 'Cast')):
            raise ValueError('runtime expression coefficient is not a constant')
        checked.add(node.name)
        value = constant(node.input[0], seen)
        if node.op_type == 'Identity':
            if node.attribute:
                raise ValueError('runtime expression Identity attributes')
            return value
        attributes = {a.name: helper.get_attribute_value(a) for a in node.attribute}
        if attributes != {'to': onnx.TensorProto.DOUBLE} or value.dtype != np.float32:
            raise ValueError('runtime expression constant Cast type mismatch')
        return value.astype(np.float64)

    for record in records:
        prefix = f"{PREFIX}{record['position']}-"
        # Follow actual output connectivity rather than trusting node names.
        stages = [('Cast', [record['input']], prefix + 'double-input', {'to': onnx.TensorProto.DOUBLE}),
                  ('Mul', None, prefix + 'product', {}),
                  ('Add', None, prefix + 'sum', {}),
                  ('Cast', [prefix + 'sum'], record['output'], {'to': onnx.TensorProto.FLOAT})]
        nodes = []
        for op, inputs, output, attributes in stages:
            node = producers.get(output)
            if (node is None or node.domain or node.op_type != op or list(node.output) != [output]
                    or (inputs is not None and list(node.input) != inputs)
                    or {a.name: helper.get_attribute_value(a) for a in node.attribute} != attributes):
                raise ValueError('runtime expression arithmetic/output Cast mismatch')
            checked.add(node.name)
            nodes.append(node)
        for node, upstream, key in ((nodes[1], prefix + 'double-input', 'alpha'),
                                     (nodes[2], prefix + 'product', 'beta')):
            if len(node.input) != 2 or node.input[0] != upstream:
                raise ValueError('runtime expression Mul/Add ordering mismatch')
            expected = constant_array(source, prefix + key).astype(np.float64)
            actual = constant(node.input[1])
            if (actual.dtype != np.float64 or actual.shape != expected.shape
                    or actual.tobytes() != expected.tobytes()):
                raise ValueError('runtime expression folded coefficient bits mismatch')
            producer = producers.get(node.input[1])
            if producer is not None and producer.op_type == 'Cast':
                constant_casts += 1
            else:
                folded += 1
    promoted = [node for node in graph.graph.node if node.name.startswith(PREFIX)]
    if any(node.name not in checked for node in promoted):
        raise ValueError('runtime expression has unexpected promoted nodes')
    return {'notice': NOTICE, 'status': 'PASS', 'layers': len(records),
            'runtime_promoted_nodes': len(promoted), 'constant_casts': constant_casts,
            'folded_double_coefficients': folded, 'exact_promoted_coefficient_bits': True,
            'double_Mul_Add_and_float32_boundaries': True,
            'outside_BN_arithmetic_equivalence': 'UNVERIFIED; operator inventories retained'}


def runtime_audit(path, rounded, records, candidate):
    if candidate:
        try:
            return audit_runtime_expression(path, rounded, records)
        except ValueError as exc:
            return {'notice': NOTICE, 'status': 'FAIL', 'reason': str(exc)}
    counts = Counter(node.op_type for node in onnx.load(path).graph.node)
    return {'notice': NOTICE, 'status': 'INVENTORY ONLY', 'batchnorm_nodes': counts['BatchNormalization'],
            'arithmetic_equivalence': 'UNVERIFIED; original runtime parity measured separately'}


def verified_prior(repo, prepared, run, experiments, source, prior, model, saved, index):
    retained = verified_artifacts(prepared, run, experiments, saved, index)
    preserved, source_report, _ = verified_preserved(source, model, saved, index, prepared, run)
    old_path = prior / 'PLACEHOLDER-promoted-bn-report.json'
    old = json.loads(old_path.read_text())
    retained_summary = {digest: {'kind': a['kind'], 'graph': a['graph'], 'source_experiments': a['sources']}
                        for digest, a in retained.items()}
    if (old['saved_run_sha256'] != sha256(run / 'PLACEHOLDER-run.json')
            or old['preparation_report_sha256'] != sha256(prepared / 'preparation-report.json')
            or old['source_report_sha256'] != sha256(source_report)
            or old['retained_artifacts'] != retained_summary):
        raise ValueError('runtime profiles prior provenance mismatch')
    audit_rounded_report(prior, old, model, preserved, index, saved)
    rounded = prior / 'PLACEHOLDER-complete-promoted-bn.onnx'
    return preserved, rounded, old, {'prior_report_sha256': sha256(old_path),
        'prior_details_sha256': old['diagnostic_details_sha256'],
        'source_report_sha256': sha256(source_report), 'retained_artifacts': retained_summary}


def audit_profile_report(repo, output, report, prepared, run, experiments, source, prior,
                         *, backbone_factory=backbone_architecture):
    """Independent no-inference reconstruction of scope, provenance and evidence."""
    model, saved = load_reference(run, backbone_factory=backbone_factory)
    index = read_component_index(prepared / 'manifest.jsonl', prepared / 'preparation-report.json')
    preserved, rounded, old, provenance = verified_prior(
        repo, prepared, run, experiments, source, prior, model, saved, index)
    ids = [item.id for item in index.components if item.split == 'train']
    protocol = {'decision': 'ADR-022', 'split': 'train', 'components': len(ids),
        'component_ids_sha256': hashlib.sha256(json_text(ids).encode()).hexdigest(),
        'profiles': list(PROFILES), 'execution': 'sequential', 'intra_op_threads': 2,
        'inter_op_threads': 1, 'shape': list(INPUT_SHAPE), 'rounding_recipe': RECIPE,
        'temperature': saved['calibration']['temperature'],
        'threshold': saved['primary_operating_point']['threshold'],
        'frozen_evaluation_inputs_used': False, 'quantisation_fit': False, 'deployment_selection': False}
    environment = export_environment(repo)
    if (not ids or report['notice'] != PLACEHOLDER_NOTICE or report['status'] != 'DIAGNOSTIC ONLY'
            or report['protocol'] != protocol or report['prior_provenance'] != provenance
            or report['saved_run_sha256'] != sha256(run / 'PLACEHOLDER-run.json')
            or report['saved_model_sha256'] != saved['provenance']['model_sha256']
            or report['manifest_sha256'] != index.manifest_sha256
            or report['preparation_report_sha256'] != sha256(prepared / 'preparation-report.json')
            or report['model_state_before_sha256'] != tensor_hash(model.state_dict())
            or report['model_state_after_sha256'] != report['model_state_before_sha256']
            or report['substitutions'] != old['substitutions']
            or set(report['artifacts']) != set(ARTIFACTS)):
        raise ValueError('runtime profiles protocol/model/provenance mismatch')
    for key in ('source_files_sha256', 'source_tree_sha256', 'dependencies',
                'dependency_lock_sha256', 'export_dependency_lock_sha256'):
        if environment[key] != report['environment'][key]:
            raise ValueError('runtime profiles source/dependency provenance mismatch')
    audit_saved_coefficients(model, preserved, report['substitutions'])
    detail_path = output / DETAILS
    if sha256(detail_path) != report['diagnostic_details_sha256']:
        raise ValueError('runtime profiles detail checksum mismatch')
    details = json.loads(detail_path.read_text())
    previous = json.loads((prior / 'PLACEHOLDER-promoted-bn-details.json').read_text())
    if details['notice'] != PLACEHOLDER_NOTICE or set(details['artifacts']) != set(ARTIFACTS):
        raise ValueError('runtime profiles artifact scope mismatch')
    reference = previous['artifacts']['preserved_control']['python_logits']
    for name, path in zip(ARTIFACTS, (preserved, rounded)):
        aggregate, full = report['artifacts'][name], details['artifacts'][name]
        tapped = output / f'PLACEHOLDER-{name}-features.onnx'
        if (aggregate['graph'] != graph_report(path) or aggregate['instrumented_graph'] != graph_report(tapped)
                or set(aggregate['profiles']) != set(PROFILES) or set(full) != set(PROFILES)):
            raise ValueError('runtime profiles graph/profile scope mismatch')
        for profile in PROFILES:
            values, rows = aggregate['profiles'][profile], full[profile]
            if rows['component_ids'] != ids or rows['python_logits'] != reference:
                raise ValueError('runtime profiles ordered inputs/reference mismatch')
            if profile == 'disabled' and rows != previous['artifacts'][name]:
                raise ValueError('runtime profiles prior disabled evidence mismatch')
            parity = parity_report(reference, rows['original_onnx_logits'], identifiers=ids,
                temperature=protocol['temperature'], threshold=protocol['threshold'], budget=FLOAT_BUDGET)
            if rows['parity'] != parity or values['diagnostics']['original_graph_training_parity'] != aggregate_parity(parity):
                raise ValueError('runtime profiles fixed-budget parity mismatch')
            features, tapped_logits = rows['feature_attribution'], rows['instrumented_onnx_logits']
            if len(features) != len(ids) or len(tapped_logits) != len(ids):
                raise ValueError('runtime profiles feature scope mismatch')
            for key, summary in values['diagnostics']['instrumented_attribution'].items():
                if summary != {'max': max(row[key] for row in features), 'mean': float(np.mean([row[key] for row in features]))}:
                    raise ValueError('runtime profiles feature aggregate mismatch')
            if any(row['instrumentation_absolute_logit_change'] != abs(tap - raw)
                   for row, tap, raw in zip(features, tapped_logits, rows['original_onnx_logits'])):
                raise ValueError('runtime profiles tap accounting mismatch')
            for tag, runtime_tag in (('original', 'original'), ('features', 'instrumented')):
                graph_path = output / f'PLACEHOLDER-{name}-{profile}-audit' / f'PLACEHOLDER-{tag}-optimized.onnx'
                if (graph_report(graph_path) != values['diagnostics']['runtime_graphs'][runtime_tag]
                        or values['runtime_audits'][tag] != runtime_audit(graph_path, rounded,
                            report['substitutions'], name == 'complete_promoted_bn')):
                    raise ValueError('runtime profiles runtime graph/semantics mismatch')
    return {'notice': NOTICE, 'status': 'PASS', 'components': len(ids), 'artifacts': 2,
            'profiles_per_artifact': 4, 'graph_records_checked': 20,
            'ordered_scope_fixed_budget_parity_features_and_taps': True,
            'prior_disabled_details_exact': True, 'runtime_semantic_outcomes_reconstructed': True,
            'saved_model_preparation_retained_source_and_dependency_provenance': True}


def profiles_run(repo, prepared, run, experiments, source, prior, output,
                 *, backbone_factory=backbone_architecture):
    prepared, run, source, prior, output = [ignored_path(repo, path) for path in (prepared, run, source, prior, output)]
    experiments = tuple(ignored_path(repo, path) for path in experiments)
    if not experiments:
        raise ValueError('runtime profiles require retained export experiments')
    if output.exists() or not output.name.startswith('PLACEHOLDER-'):
        raise ValueError('runtime profiles output must be new and named PLACEHOLDER-*')
    if tuple(OPTIMISATION_LEVELS) != PROFILES:
        raise ValueError('runtime profiles declared settings changed')
    model, saved = load_reference(run, backbone_factory=backbone_factory)
    before = tensor_hash(model.state_dict())
    index = read_component_index(prepared / 'manifest.jsonl', prepared / 'preparation-report.json')
    preserved, rounded, old, provenance = verified_prior(
        repo, prepared, run, experiments, source, prior, model, saved, index)
    training = tuple(item for item in index.components if item.split == 'train')
    if not training:
        raise ValueError('runtime profiles require training components')
    protocol = dict(old['protocol'])
    for key in ('optimisation', 'formula', 'expected_batchnorm_substitutions'):
        del protocol[key]
    protocol.update(decision='ADR-022', profiles=list(PROFILES))
    report = {'notice': PLACEHOLDER_NOTICE, 'status': 'DIAGNOSTIC ONLY', 'version': '1.0.0',
        'created_utc': datetime.now(timezone.utc).isoformat(), 'protocol': protocol,
        'environment': export_environment(repo), 'prior_provenance': provenance,
        'saved_model_sha256': saved['provenance']['model_sha256'], 'saved_run_sha256': sha256(run / 'PLACEHOLDER-run.json'),
        'manifest_sha256': index.manifest_sha256, 'preparation_report_sha256': sha256(prepared / 'preparation-report.json'),
        'model_state_before_sha256': before, 'substitutions': old['substitutions'], 'artifacts': {},
        'scope': NOTICE + '; all profiles retained; no mobile/clinical/deployment evidence'}
    details = {'notice': PLACEHOLDER_NOTICE, 'artifacts': {}}
    output.mkdir(parents=True, exist_ok=False)
    for name, path in zip(ARTIFACTS, (preserved, rounded)):
        tapped = output / f'PLACEHOLDER-{name}-features.onnx'
        feature_name = tap_features(path, tapped, model.head.mean.numel())
        artifact = {'graph': graph_report(path), 'instrumented_graph': graph_report(tapped), 'profiles': {}}
        details['artifacts'][name] = {}
        for profile in PROFILES:
            audit_dir = output / f'PLACEHOLDER-{name}-{profile}-audit'
            aggregate, full = diagnose_profile(model, path, tapped, feature_name,
                ((item.id, component_input(prepared, item)) for item in training),
                optimisation=profile, temperature=protocol['temperature'], threshold=protocol['threshold'],
                budget=FLOAT_BUDGET, audit_directory=audit_dir)
            audits = {tag: runtime_audit(audit_dir / f'PLACEHOLDER-{tag}-optimized.onnx', rounded,
                old['substitutions'], name == 'complete_promoted_bn') for tag in ('original', 'features')}
            artifact['profiles'][profile] = {'diagnostics': aggregate, 'runtime_audits': audits}
            details['artifacts'][name][profile] = full
        report['artifacts'][name] = artifact
    report['model_state_after_sha256'] = tensor_hash(model.state_dict())
    if report['model_state_after_sha256'] != before or any(module.training for module in model.modules()):
        raise ValueError('runtime profiles changed saved model state or mode')
    detail_path = output / DETAILS
    detail_path.write_text(json_text(details))
    report['diagnostic_details_sha256'] = sha256(detail_path)
    report['evidence_audit'] = audit_profile_report(repo, output, report, prepared, run, experiments,
        source, prior, backbone_factory=backbone_factory)
    (output / REPORT).write_text(json_text(report))
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=NOTICE + '; fixed training-only runtime profiles')
    parser.add_argument('--prepared', type=Path, default=Path('data/prepared/synthetic-v2-selection'))
    parser.add_argument('--run', type=Path, default=Path('data/models/PLACEHOLDER-m3-baseline'))
    parser.add_argument('--experiments', nargs='+', type=Path, default=[
        Path('data/exports/PLACEHOLDER-m4-attempt1'), Path('data/exports/PLACEHOLDER-m4-attempt2')])
    parser.add_argument('--source', type=Path, default=Path('data/exports/PLACEHOLDER-m4-batchnorm2'))
    parser.add_argument('--prior', type=Path, default=Path('data/exports/PLACEHOLDER-m4-rounded-bn2'))
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    repo = repository_root()
    try:
        output = ignored_path(repo, args.output)
        reports = repo / 'ml/reports'
        target = reports / f'{output.name}.json'
        if target.exists() or target.is_symlink() or reports.resolve() != reports or not output.name.startswith('PLACEHOLDER-'):
            raise ValueError('aggregate target must be new, local and PLACEHOLDER-*')
        report = profiles_run(repo, args.prepared, args.run, args.experiments, args.source, args.prior, output)
        with target.open('x') as stream:
            stream.write(json_text(report))
    except (ValueError, OSError, RuntimeError, KeyError, TypeError) as exc:
        print(f'PLACEHOLDER runtime profiles failed: {exc}', file=sys.stderr)
        return 1
    print(f'PLACEHOLDER DIAGNOSTIC ONLY: {target.relative_to(repo)}; M4 remains incomplete')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
