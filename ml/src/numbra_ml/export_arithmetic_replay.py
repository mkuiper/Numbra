"""ADR-024 supplied retained-tensor PLACEHOLDER replay; diagnostic only.

No dataset or saved-baseline entry point. A training caller must use the guarded
reader's complete pre-access audit, exhaust it, and persist/audit all rows. This
primitive alone cannot create a completed training experiment or accept M4.
"""

import copy
from pathlib import Path

import onnx

from .export import graph_report
from .export_complete_replay import signed_accounting
from .export_provenance import checked_file
from .export_remaining_arithmetic import (RECIPES, arithmetic_graph,
    audit_arithmetic_graph, complete_arithmetic_scope, eager_expression)
from .export_remaining_native import native_plan
from .export_remaining_replay import (KINDS, ORIGINS, NOTICE as SESSION_NOTICE,
    IsolatedSession, audit_rounded_binding, delta, reconstruct_row, validate)
from .export_remaining_runtime import audit_complete_runtime
from .training import tensor_hash

NOTICE = 'PLACEHOLDER retained arithmetic replay diagnostic only; never bundle'


def targets(plan):
    """Every declared target in original order, with every fixed recipe."""
    return [record for record in plan['nodes'] if record['operator'] in RECIPES]


def recipe_directory(kind, position, variant):
    return f'PLACEHOLDER-{kind}-{position}-{variant}'


def audit_arithmetic_setup(model, source, rounded, output, records):
    """Rebuild complete serialized/runtime recipe scope without any inference."""
    plan = native_plan(model, source, rounded)
    expected = {'notice': NOTICE, 'scope': complete_arithmetic_scope(model, source, rounded),
        'rounded_saved_binding': audit_rounded_binding(model, source, rounded), 'graphs': {}}
    files, directories = set(), set()
    for kind, graph in zip(KINDS, (source, rounded)):
        nodes = {node.name: node for node in graph.graph.node}
        expected['graphs'][kind] = {}
        for record in targets(plan):
            node = nodes[record['name']]
            expressions = {}
            for variant in RECIPES[node.op_type]:
                relative = recipe_directory(kind, record['position'], variant)
                directories.add(relative)
                paths = [relative + '/PLACEHOLDER-' + tag + '.onnx'
                         for tag in ('expression', 'runtime')]
                files.update(paths)
                serialized, runtime = [checked_file(output, name) for name in paths]
                expected_graph = arithmetic_graph(graph, node, variant)
                audit_arithmetic_graph(graph, node, variant,
                    onnx.load(serialized, load_external_data=False))
                # The session record uses the unchanged complete runtime auditor.
                expressions[variant] = {'notice': SESSION_NOTICE,
                    'serialized': graph_report(serialized), 'runtime': graph_report(runtime),
                    'audit': audit_complete_runtime(expected_graph,
                        onnx.load(runtime, load_external_data=False))}
            expected['graphs'][kind][node.name] = expressions
    seen_files, seen_directories = set(), set()
    if output.is_symlink() or not output.is_dir():
        raise ValueError('arithmetic setup unsafe/missing directory')
    for path in output.rglob('*'):
        if path.is_symlink():
            raise ValueError('arithmetic setup unsafe evidence path')
        relative = str(path.relative_to(output))
        (seen_directories if path.is_dir() else seen_files).add(relative)
    if (files != seen_files or directories != seen_directories or records != expected):
        raise ValueError('arithmetic setup complete scope/record reconstruction mismatch')
    return {'notice': NOTICE, 'status': 'PASS', 'graph_contexts': list(KINDS),
        'target_nodes': len(targets(plan)), 'recipe_graphs': expected['scope']['graph_count'] * len(KINDS),
        'serialized_and_runtime_graphs': len(files),
        'complete_expressions_constants_and_boundaries': True, 'baseline_inference': False}


def reconstruct_arithmetic(source, plan, evidence):
    """Reconstruct all signed comparisons from arrays, never execute a recipe.

    The complete ADR-023 controls and native/runtime lineage are reconstructed
    first. New outputs are recorded observations; this does not independently
    authenticate their arithmetic truth against rerun inference.
    """
    if (set(evidence) != {'notice', 'retained', 'recipes'} or evidence['notice'] != NOTICE
            or list(evidence['recipes']) != list(KINDS)):
        raise ValueError('arithmetic replay evidence scope mismatch')
    retained = evidence['retained']
    controls = reconstruct_row(source, plan, retained)
    selected = targets(plan)
    names = [r['name'] for r in selected]
    result = {}
    for kind in KINDS:
        recipes = evidence['recipes'][kind]
        if list(recipes) != names:
            raise ValueError('arithmetic replay complete ordered target scope mismatch')
        result[kind] = {}
        for record in selected:
            name, operator = record['name'], record['operator']
            row, original = recipes[name], retained['operators'][name]
            data = original['graphs'][kind]
            if list(row) != list(ORIGINS):
                raise ValueError('arithmetic replay input origin scope mismatch')
            metrics = {}
            for origin in ORIGINS:
                if list(row[origin]) != list(RECIPES[operator]):
                    raise ValueError('arithmetic replay complete fixed recipe scope mismatch')
                metrics[origin] = {}
                native_reference = original['eager_native'] if origin == 'native_input' else data['eager_runtime']
                isolated_reference = data['isolated_native'] if origin == 'native_input' else data['isolated_runtime']
                for variant, outputs in row[origin].items():
                    if list(outputs) != ['eager', 'runtime']:
                        raise ValueError('arithmetic replay engine output scope mismatch')
                    for value in outputs.values():
                        validate(value, record['boundaries'][record['outputs'][0]])
                    eager, runtime = outputs['eager'], outputs['runtime']
                    comparisons = {
                        'runtime_vs_eager_recipe': delta(eager, runtime),
                        'eager_recipe_vs_native_operator': delta(native_reference, eager),
                        'runtime_recipe_vs_native_operator': delta(native_reference, runtime),
                        'runtime_recipe_vs_original_isolated': delta(isolated_reference, runtime)}
                    if origin == 'native_input':
                        comparisons['runtime_recipe_vs_captured_native'] = delta(original['native_output'], runtime)
                    else:
                        comparisons['runtime_recipe_vs_tapped_boundary'] = delta(data['runtime_output'], runtime)
                    metrics[origin][variant] = comparisons
            accounting = {}
            for variant in RECIPES[operator]:
                chain = signed_accounting(original['native_output'], row['native_input'][variant]['eager'],
                    row['runtime_input'][variant]['eager'], row['runtime_input'][variant]['runtime'],
                    data['runtime_output'])
                # Replacement arithmetic is not an extraction-equivalence test.
                chain['terms'] = dict(zip(('eager_recipe_vs_captured_native', 'recipe_input_propagation',
                    'runtime_vs_eager_recipe', 'tapped_boundary_vs_runtime_recipe'), chain['terms'].values()))
                accounting[variant] = chain
            result[kind][name] = {'origins': metrics, 'signed_accounting': accounting}
    return {'notice': NOTICE, 'status': 'DIAGNOSTIC ONLY', 'original_controls': controls,
        'recipes': result, 'whole_model_parity': 'UNVERIFIED', 'deployment_selection': False}


class ArithmeticReplay:
    """Audit every fixed recipe first, then run only supplied retained operands.

    No native model call, whole-model session, image decode or native control
    replay. Original control arrays remain shared and unmodified in the result.
    """

    def __init__(self, model, source, rounded, output):
        output = Path(output)
        if (output.is_symlink() or not output.is_dir() or any(output.iterdir())
                or not output.name.startswith('PLACEHOLDER-')):
            raise ValueError('arithmetic replay requires a fresh empty PLACEHOLDER directory')
        self.model, self.source, self.rounded = model, copy.deepcopy(source), copy.deepcopy(rounded)
        source, rounded = self.source, self.rounded
        self.plan = native_plan(model, source, rounded)
        self.state = tensor_hash(model.state_dict())
        self.records = {'notice': NOTICE, 'scope': complete_arithmetic_scope(model, source, rounded),
            'rounded_saved_binding': audit_rounded_binding(model, source, rounded), 'graphs': {}}
        self.graph_bits = [graph.SerializeToString() for graph in (source, rounded)]
        self.sessions, self.nodes = {}, {}
        for kind, graph in zip(KINDS, (source, rounded)):
            self.nodes[kind] = {node.name: node for node in graph.graph.node}
            self.records['graphs'][kind] = {}
            for record in targets(self.plan):
                node = self.nodes[kind][record['name']]
                expressions = {}
                for variant in RECIPES[node.op_type]:
                    session = IsolatedSession(arithmetic_graph(graph, node, variant),
                        output / recipe_directory(kind, record['position'], variant))
                    self.sessions[kind, node.name, variant] = session
                    expressions[variant] = session.record
                self.records['graphs'][kind][node.name] = expressions
        # Complete independent disk reconstruction precedes any supplied inputs.
        self.setup_audit = audit_arithmetic_setup(model, source, rounded, output, self.records)
        if tensor_hash(model.state_dict()) != self.state:
            raise ValueError('arithmetic replay setup changed saved model state')

    def run(self, retained):
        # Entire retained lineage/control scope is validated before any kernel.
        reconstruct_row(self.source, self.plan, retained)
        if (tensor_hash(self.model.state_dict()) != self.state
                or any(m.training or m._forward_hooks or m._forward_pre_hooks for m in self.model.modules())
                or [g.SerializeToString() for g in (self.source, self.rounded)] != self.graph_bits
                or native_plan(self.model, self.source, self.rounded) != self.plan):
            raise ValueError('arithmetic replay model/graph/mapping changed before inference')
        for key, session in self.sessions.items():
            kind, name, variant = key
            graph = self.source if kind == 'preserved' else self.rounded
            audit_arithmetic_graph(graph, self.nodes[kind][name], variant, session.graph)
        evidence = {'notice': NOTICE, 'retained': retained, 'recipes': {}}
        for kind, graph in zip(KINDS, (self.source, self.rounded)):
            evidence['recipes'][kind] = {}
            for record in targets(self.plan):
                name, node = record['name'], self.nodes[kind][record['name']]
                original = retained['operators'][name]
                origins = (original['native_operands'], original['graphs'][kind]['runtime_operands'])
                row = {}
                for origin, operands in zip(ORIGINS, origins):
                    row[origin] = {}
                    for variant in RECIPES[node.op_type]:
                        eager = eager_expression(graph, node, variant, operands)
                        runtime = self.sessions[kind, name, variant].run([operands[0]])
                        row[origin][variant] = {'eager': eager, 'runtime': runtime}
                evidence['recipes'][kind][name] = row
        return reconstruct_arithmetic(self.source, self.plan, evidence), evidence
