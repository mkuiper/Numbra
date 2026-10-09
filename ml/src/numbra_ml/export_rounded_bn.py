"""ADR-021 complete training-only PLACEHOLDER rounded-affine BN; never bundle."""

import hashlib
import json

import numpy as np
import onnx
from torch import nn

from . import PLACEHOLDER_NOTICE
from .export import INPUT_SHAPE, aggregate_parity, graph_report
from .export_bn_rounding import array_record, coefficients, saved_arrays
from .export_promoted_bn import (audit_promoted_graph,
                                 coefficient_hash, main as promoted_main)
from .parity import FLOAT_BUDGET, parity_report
from .pretrained import sha256
from .train import json_text
from .training import tensor_hash

RECIPE = 'e32-r32-a32-b64-o64'


def rounded_coefficients(module):
    """Reject coefficient bit disagreement rather than choosing an engine."""
    engines = {engine: coefficients(module, RECIPE, engine) for engine in ('numpy', 'torch')}
    records = {engine: {key: array_record(value) for key, value in constants.items()}
               for engine, constants in engines.items()}
    if records['numpy'] != records['torch']:
        raise ValueError('rounded BN independent coefficient bits disagree')
    evidence = {'recipe': RECIPE, 'engines': records,
        'saved_parameters': {key: array_record(value) for key, value in zip(
            ('weight', 'bias', 'mean', 'variance'), saved_arrays(module))},
        'epsilon_bits': {key: np.asarray(module.eps, dtype=dtype).tobytes().hex()
                         for key, dtype in (('float32', np.float32), ('float64', np.float64))}}
    return {key: engines['numpy'][key] for key in ('alpha', 'beta')}, evidence


def audit_saved_coefficients(model, source, records):
    """Independent reconstruction of every saved BN and original parameter bit."""
    from .export_complete_replay import complete_operators
    graph = onnx.load(source, load_external_data=False)
    matched = [(name, module, node) for name, module, node in complete_operators(model, graph)
               if isinstance(module, nn.BatchNorm2d)]
    if not records or len(records) != len(matched):
        raise ValueError('rounded BN complete saved module scope mismatch')
    for position, ((name, module, node), record) in enumerate(zip(matched, records)):
        constants, evidence = rounded_coefficients(module)
        expected = {'module': name, 'position': position, 'input': node.input[0], 'output': node.output[0],
            'coefficient_shape': list(constants['alpha'].shape),
            'coefficients_sha256': {key: coefficient_hash(value) for key, value in constants.items()},
            'rounding': evidence}
        if record != expected:
            raise ValueError('rounded BN saved recipe/coefficient bits or order mismatch')
    return {'notice': 'PLACEHOLDER diagnostic only; never bundle', 'status': 'PASS',
            'layers': len(matched), 'recipe': RECIPE, 'independent_engines': ['numpy', 'torch'],
            'all_saved_parameter_epsilon_and_coefficient_bits': True, 'module_order': True}


def audit_rounded_report(output, report, model, source, index, saved):
    """No input inference: reconstruct scope, coefficients, graphs and parity."""
    details_path = output / 'PLACEHOLDER-promoted-bn-details.json'
    if sha256(details_path) != report['diagnostic_details_sha256']:
        raise ValueError('rounded BN detail checksum mismatch')
    details = json.loads(details_path.read_text())
    protocol = report['protocol']
    ids = [item.id for item in index.components if item.split == 'train']
    if (report['notice'] != PLACEHOLDER_NOTICE or report['status'] != 'DIAGNOSTIC ONLY'
            or details['notice'] != PLACEHOLDER_NOTICE or protocol['decision'] != 'ADR-021'
            or protocol['rounding_recipe'] != RECIPE or protocol['split'] != 'train'
            or protocol['shape'] != list(INPUT_SHAPE) or protocol['components'] != len(ids)
            or protocol['component_ids_sha256'] != hashlib.sha256(json_text(ids).encode()).hexdigest()
            or protocol['optimisation'] != 'disabled' or protocol['execution'] != 'sequential'
            or protocol['intra_op_threads'] != 2 or protocol['inter_op_threads'] != 1
            or any(protocol[key] for key in ('frozen_evaluation_inputs_used', 'quantisation_fit', 'deployment_selection'))
            or protocol['temperature'] != saved['calibration']['temperature']
            or protocol['threshold'] != saved['primary_operating_point']['threshold']
            or report['model_state_before_sha256'] != tensor_hash(model.state_dict())
            or report['model_state_after_sha256'] != report['model_state_before_sha256']
            or report['source_graph'] != graph_report(source)
            or report['manifest_sha256'] != index.manifest_sha256
            or report['saved_model_sha256'] != saved['provenance']['model_sha256']):
        raise ValueError('rounded BN protocol/model/scope mismatch')
    coefficient_audit = audit_saved_coefficients(model, source, report['substitutions'])
    if (report['coefficient_audit'] != coefficient_audit
            or protocol['expected_batchnorm_substitutions'] != coefficient_audit['layers']):
        raise ValueError('rounded BN coefficient audit mismatch')
    names = {'preserved_control', 'complete_promoted_bn'}
    if set(details['artifacts']) != names or set(report['artifacts']) != names:
        raise ValueError('rounded BN complete artifact scope mismatch')
    for name in names:
        full, aggregate = details['artifacts'][name], report['artifacts'][name]
        if full['component_ids'] != ids:
            raise ValueError('rounded BN ordered training inputs mismatch')
        parity = parity_report(full['python_logits'], full['original_onnx_logits'],
            identifiers=ids, temperature=protocol['temperature'], threshold=protocol['threshold'], budget=FLOAT_BUDGET)
        if (full['parity'] != parity
                or aggregate['diagnostics']['original_graph_training_parity'] != aggregate_parity(parity)):
            raise ValueError('rounded BN fixed-budget parity reconstruction mismatch')
        rows = full['feature_attribution']
        if len(rows) != len(ids) or len(full['instrumented_onnx_logits']) != len(ids):
            raise ValueError('rounded BN feature row scope mismatch')
        for key, summary in aggregate['diagnostics']['instrumented_attribution'].items():
            if summary != {'max': max(row[key] for row in rows), 'mean': float(np.mean([row[key] for row in rows]))}:
                raise ValueError('rounded BN attribution reconstruction mismatch')
        if any(row['instrumentation_absolute_logit_change'] != abs(tapped - original)
               for row, tapped, original in zip(rows, full['instrumented_onnx_logits'], full['original_onnx_logits'])):
            raise ValueError('rounded BN tap accounting mismatch')
        graph_path = source if name == 'preserved_control' else output / 'PLACEHOLDER-complete-promoted-bn.onnx'
        tapped_path = output / f'PLACEHOLDER-{name}-features.onnx'
        graphs = [(graph_path, aggregate['graph']), (tapped_path, aggregate['instrumented_graph'])]
        for tag, runtime_tag in (('original', 'original'), ('features', 'instrumented')):
            path = output / f'PLACEHOLDER-{name}-audit' / f'PLACEHOLDER-{tag}-optimized.onnx'
            graphs.append((path, aggregate['diagnostics']['runtime_graphs'][runtime_tag]))
        for path, evidence in graphs:
            if graph_report(path) != evidence:
                raise ValueError('rounded BN graph checksum/report mismatch')
            if name == 'complete_promoted_bn':
                audit_promoted_graph(path, source, report['substitutions'], serialized=path == graph_path)
    if details['artifacts']['preserved_control']['python_logits'] != details['artifacts']['complete_promoted_bn']['python_logits']:
        raise ValueError('rounded BN reference changed between artifacts')
    return {'notice': 'PLACEHOLDER diagnostic only; never bundle', 'status': 'PASS',
            'ordered_training_components': len(ids), 'artifacts': len(names), 'graphs_checked': 8,
            'coefficient_bits_and_runtime_expressions': True, 'fixed_budget_parity_reconstructed': True,
            'feature_aggregates_and_tap_accounting': True}


def audit_prior_control(output, report, prior):
    """No inference: compare complete ordered logits to committed ADR-020 evidence."""
    prior_report_path = prior / 'PLACEHOLDER-bn-rounding-report.json'
    prior_details_path = prior / 'PLACEHOLDER-bn-rounding-details.json'
    old = json.loads(prior_report_path.read_text())
    previous = json.loads(prior_details_path.read_text())
    current = json.loads((output / 'PLACEHOLDER-promoted-bn-details.json').read_text())['artifacts']['preserved_control']
    if (sha256(prior_details_path) != old['diagnostic_details_sha256']
            or old['protocol']['decision'] != 'ADR-020'
            or any(old[key] != report[key] for key in ('saved_model_sha256', 'saved_run_sha256',
                'manifest_sha256', 'preparation_report_sha256', 'source_graph', 'source_report_sha256'))
            or any(old['protocol'][key] != report['protocol'][key] for key in (
                'components', 'component_ids_sha256', 'temperature', 'threshold', 'split'))
            or current['component_ids'] != previous['component_ids']
            or current['python_logits'] != [row['python_logit'] for row in previous['rows']]
            or current['original_onnx_logits'] != [row['original_logit'] for row in previous['rows']]):
        raise ValueError('rounded BN prior complete control mismatch')
    return {'notice': 'PLACEHOLDER diagnostic only; never bundle', 'status': 'PASS',
            'prior_report_sha256': sha256(prior_report_path), 'prior_details_sha256': sha256(prior_details_path),
            'ordered_python_and_control_logits_exact': True}


def main(argv=None):
    return promoted_main(argv, rounding_recipe=RECIPE)


if __name__ == '__main__':
    raise SystemExit(main())
