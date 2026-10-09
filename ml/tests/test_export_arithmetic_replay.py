"""Generated-only PLACEHOLDER retained arithmetic integration regressions."""

import copy
from pathlib import Path
import tempfile

import numpy as np
import onnx
import onnxruntime as ort
import pytest
import timm
import torch

from numbra_ml import export_arithmetic_replay as arithmetic
from numbra_ml.export_batchnorm import export_preserving_batchnorm
from numbra_ml.export_promoted_bn import substitute_batchnorm
from numbra_ml.export_remaining_arithmetic import RECIPES
from numbra_ml.export_remaining_evidence import array_id
from numbra_ml.export_remaining_replay import CompleteReplay, KINDS, ORIGINS
from numbra_ml.export_remaining_retained import training_rows
from numbra_ml.export_remaining_run import training_context
from numbra_ml.export_rounded_bn import RECIPE
from numbra_ml.prepare import repository_root
from numbra_ml.pretrained import sha256
from numbra_ml.training import Baseline, FeatureHead, tensor_hash
from test_export_remaining_native import generated_pair
from test_export_remaining_run import complete_run, profile_evidence
from test_export_replay import toy_backbone


def fingerprint(tree):
    if isinstance(tree, np.ndarray):
        return array_id(tree)
    if isinstance(tree, dict):
        return [(key, fingerprint(value)) for key, value in tree.items()]
    if isinstance(tree, list):
        return [fingerprint(value) for value in tree]
    return tree


def readonly(tree):
    if isinstance(tree, np.ndarray):
        tree.flags.writeable = False
    elif isinstance(tree, dict):
        for value in tree.values():
            readonly(value)
    elif isinstance(tree, list):
        for value in tree:
            readonly(value)


@pytest.fixture(scope='module')
def replayed():
    parent = repository_root() / 'data/test-runs'
    parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=parent) as temporary:
        root = Path(temporary)
        model, source, rounded, value = generated_pair.__wrapped__(root)
        original = root / 'PLACEHOLDER-original'
        original.mkdir()
        retained = CompleteReplay(model, source, rounded, original).run(value)[1]
        readonly(retained)
        output = root / 'PLACEHOLDER-arithmetic'
        output.mkdir()
        engine = arithmetic.ArithmeticReplay(model, source, rounded, output)
        result, evidence = engine.run(retained)
        yield engine, output, retained, result, evidence


def forbidden(*args, **kwargs):
    pytest.fail('this operation must not decode, infer the native model, or replay original controls')


def test_complete_setup_precedes_any_recipe_or_model_execution(generated_pair, tmp_path, monkeypatch):
    model, source, rounded, _ = generated_pair
    output = tmp_path / 'PLACEHOLDER-static-arithmetic'
    output.mkdir()
    before = tensor_hash(model.state_dict())
    monkeypatch.setattr(torch.nn.Module, '_call_impl', forbidden)
    monkeypatch.setattr(ort.InferenceSession, 'run', forbidden)
    monkeypatch.setattr('numbra_ml.dataset.load_rgb', forbidden)
    monkeypatch.setattr(arithmetic, 'eager_expression', forbidden)
    engine = arithmetic.ArithmeticReplay(model, source, rounded, output)
    assert engine.setup_audit['status'] == 'PASS'
    assert engine.setup_audit['serialized_and_runtime_graphs'] == 4 * engine.records['scope']['graph_count']
    assert engine.setup_audit['complete_expressions_constants_and_boundaries']
    assert tensor_hash(model.state_dict()) == before


def test_both_graphs_origins_every_recipe_and_original_control_are_retained(replayed, monkeypatch):
    engine, _, retained, expected, _ = replayed
    before = fingerprint(retained)
    monkeypatch.setattr(torch.nn.Module, '_call_impl', forbidden)
    monkeypatch.setattr('numbra_ml.dataset.load_rgb', forbidden)
    monkeypatch.setattr('numbra_ml.export_remaining_replay.recipe', forbidden)
    monkeypatch.setattr('numbra_ml.export_remaining_replay.python_operator', forbidden)
    monkeypatch.setattr(CompleteReplay, 'run', forbidden)
    result, evidence = engine.run(retained)
    assert result == expected
    assert evidence['retained'] is retained
    assert fingerprint(retained) == before
    assert result['whole_model_parity'] == 'UNVERIFIED'
    assert result['deployment_selection'] is False
    assert set(result['original_controls']['operators']) == set(retained['operators'])
    for kind in KINDS:
        assert list(evidence['recipes'][kind]) == [r['name'] for r in arithmetic.targets(engine.plan)]
        for record in arithmetic.targets(engine.plan):
            row = evidence['recipes'][kind][record['name']]
            metrics = result['recipes'][kind][record['name']]
            assert list(row) == list(ORIGINS)
            for origin in ORIGINS:
                assert list(row[origin]) == list(RECIPES[record['operator']])
                for variant, outputs in row[origin].items():
                    delta = outputs['runtime'].astype(np.float64) - outputs['eager'].astype(np.float64)
                    comparison = metrics['origins'][origin][variant]['runtime_vs_eager_recipe']
                    assert comparison['signed_mean'] == float(delta.mean())
                    assert comparison['max_absolute'] == float(np.abs(delta).max())
            assert all(chain['telescoping_max_residual'] == 0 for chain in metrics['signed_accounting'].values())
    # Head comparisons use retained all-input isolation as a separate control.
    head = next(r for r in arithmetic.targets(engine.plan) if r['operator'] == 'Gemm')
    for kind in KINDS:
        metric = result['recipes'][kind][head['name']]['origins']['runtime_input']['constant_parameters']
        assert metric['runtime_recipe_vs_tapped_boundary']['exact_bits']


def test_reconstruction_needs_no_sessions_eager_recipes_native_calls_or_writes(replayed, monkeypatch):
    engine, output, _, expected, evidence = replayed
    files = {path: sha256(path) for path in output.rglob('*') if path.is_file()}
    monkeypatch.setattr(torch.nn.Module, '_call_impl', forbidden)
    monkeypatch.setattr(ort, 'InferenceSession', forbidden)
    monkeypatch.setattr(arithmetic, 'eager_expression', forbidden)
    monkeypatch.setattr('numbra_ml.dataset.load_rgb', forbidden)
    monkeypatch.setattr('numbra_ml.export_remaining_evidence.ArrayStore.encode', forbidden)
    assert arithmetic.reconstruct_arithmetic(engine.source, engine.plan, evidence) == expected
    assert arithmetic.audit_arithmetic_setup(engine.model, engine.source, engine.rounded,
        output, engine.records) == engine.setup_audit
    assert files == {path: sha256(path) for path in files}


@pytest.mark.parametrize('bad', ['target', 'target_order', 'origin', 'origin_order', 'recipe',
    'recipe_order', 'engine', 'shape', 'dtype', 'nonfinite', 'control', 'lineage', 'constant', 'plan'])
def test_partial_or_corrupt_evidence_fails_without_inference(replayed, monkeypatch, bad):
    engine, _, _, _, original = replayed
    evidence = copy.deepcopy(original)
    selected = arithmetic.targets(engine.plan)
    name = next(r['name'] for r in selected if r['operator'] == 'HardSwish')
    recipes = evidence['recipes']['rounded']
    row = recipes[name]
    outputs = row['runtime_input']['divide']
    plan = engine.plan
    if bad == 'target':
        recipes.pop(name)
    elif bad == 'target_order':
        evidence['recipes']['rounded'] = dict(reversed(list(recipes.items())))
    elif bad == 'origin':
        row.pop('native_input')
    elif bad == 'origin_order':
        recipes[name] = dict(reversed(list(row.items())))
    elif bad == 'recipe':
        row['runtime_input'].pop('reciprocal')
    elif bad == 'recipe_order':
        row['runtime_input'] = dict(reversed(list(row['runtime_input'].items())))
    elif bad == 'engine':
        outputs.pop('eager')
    elif bad == 'shape':
        outputs['runtime'] = outputs['runtime'].reshape(-1)
    elif bad == 'dtype':
        outputs['runtime'] = outputs['runtime'].astype(np.float64)
    elif bad == 'nonfinite':
        outputs['runtime'].flat[0] = np.nan
    elif bad == 'control':
        control = next(r for r in engine.plan['nodes'] if r['operator'] == 'BatchNormalization')
        evidence['retained']['operators'][control['name']]['graphs']['rounded']['controls'].pop('native_input')
    elif bad == 'lineage':
        evidence['retained']['operators'][name]['native_operands'][0] += np.float32(1.)
    elif bad == 'constant':
        head = next(r for r in selected if r['operator'] == 'Gemm')
        evidence['retained']['operators'][head['name']]['native_operands'][1].flat[0] += np.float32(1.)
    else:
        plan = copy.deepcopy(plan)
        plan['nodes'][0]['node_sha256'] = '0' * 64
    monkeypatch.setattr(arithmetic, 'eager_expression', forbidden)
    monkeypatch.setattr(ort, 'InferenceSession', forbidden)
    with pytest.raises(ValueError):
        arithmetic.reconstruct_arithmetic(engine.source, plan, evidence)


@pytest.mark.parametrize('bad', ['records', 'missing', 'extra', 'serialized', 'runtime', 'symlink'])
def test_setup_reconstructs_all_files_records_and_runtime_bits(replayed, tmp_path, monkeypatch, bad):
    import shutil
    engine, original, _, _, _ = replayed
    output = tmp_path / 'PLACEHOLDER-copy'
    shutil.copytree(original, output)
    records = copy.deepcopy(engine.records)
    expression = next(output.rglob('PLACEHOLDER-expression.onnx'))
    runtime = expression.parent / 'PLACEHOLDER-runtime.onnx'
    if bad == 'records':
        records['graphs']['rounded'].pop(next(iter(records['graphs']['rounded'])))
    elif bad == 'missing':
        runtime.unlink()
    elif bad == 'extra':
        (output / 'PLACEHOLDER-unexpected-empty-directory').mkdir()
    elif bad in ('serialized', 'runtime'):
        path = expression if bad == 'serialized' else runtime
        graph = onnx.load(path)
        graph.graph.node[0].name += '-changed'
        onnx.save(graph, path)
    else:
        runtime.unlink()
        runtime.symlink_to(next(original.rglob('PLACEHOLDER-runtime.onnx')))
    monkeypatch.setattr(ort, 'InferenceSession', forbidden)
    with pytest.raises(ValueError):
        arithmetic.audit_arithmetic_setup(engine.model, engine.source, engine.rounded, output, records)


def test_invalid_retained_controls_refused_before_first_recipe(replayed, monkeypatch):
    engine, _, original, _, _ = replayed
    retained = copy.deepcopy(original)
    retained['operators'].pop(next(reversed(retained['operators'])))
    monkeypatch.setattr(arithmetic, 'eager_expression', forbidden)
    monkeypatch.setattr(ort.InferenceSession, 'run', forbidden)
    with pytest.raises(ValueError):
        engine.run(retained)


@pytest.mark.parametrize('bad', ['model_state', 'mode', 'graph', 'session_graph', 'hook'])
def test_changed_state_mapping_or_expression_refused_before_recipe(replayed, monkeypatch, bad):
    engine, _, retained, _, _ = replayed
    hook = None
    state = copy.deepcopy(engine.model.state_dict())
    source = copy.deepcopy(engine.source)
    session = next(iter(engine.sessions.values()))
    session_graph = copy.deepcopy(session.graph)
    try:
        if bad == 'model_state':
            engine.model.head.linear.bias.add_(1.)
        elif bad == 'mode':
            engine.model.train()
        elif bad == 'graph':
            engine.source.graph.node[0].name += '-changed'
        elif bad == 'session_graph':
            session.graph.graph.node[0].name += '-changed'
        else:
            hook = engine.model.register_forward_hook(lambda *a: None)
        monkeypatch.setattr(arithmetic, 'eager_expression', forbidden)
        monkeypatch.setattr(ort.InferenceSession, 'run', forbidden)
        with pytest.raises(ValueError):
            engine.run(retained)
    finally:
        engine.model.load_state_dict(state)
        engine.model.eval()
        engine.source.CopyFrom(source)
        session.graph.CopyFrom(session_graph)
        if hook is not None:
            hook.remove()


def test_signed_nonzero_and_zero_bit_disagreement_are_unsuppressed(replayed):
    engine, _, _, _, original = replayed
    evidence = copy.deepcopy(original)
    row = next(iter(evidence['recipes']['preserved'].values()))
    variant = next(iter(row['runtime_input']))
    row['runtime_input'][variant]['runtime'] += np.float32(0.125)
    metrics = arithmetic.reconstruct_arithmetic(engine.source, engine.plan, evidence)
    name = next(iter(evidence['recipes']['preserved']))
    metric = metrics['recipes']['preserved'][name]['origins']['runtime_input'][variant]
    assert metric['runtime_vs_eager_recipe']['max_absolute'] > 0
    chain = metrics['recipes']['preserved'][name]['signed_accounting'][variant]
    assert chain['telescoping_max_residual'] == 0
    row['runtime_input'][variant]['runtime'].fill(-0.)
    row['runtime_input'][variant]['eager'].fill(0.)
    comparison = arithmetic.reconstruct_arithmetic(engine.source, engine.plan, evidence)[
        'recipes']['preserved'][name]['origins']['runtime_input'][variant]['runtime_vs_eager_recipe']
    assert comparison['max_absolute'] == 0 and not comparison['exact_bits']


def test_generated_guarded_reader_exhausts_all_rows_without_new_model_calls(complete_run, tmp_path, monkeypatch):
    repo, prepared, run, experiments, source, prior, profiles, retained, _, index = complete_run
    context, model, graphs, components, _ = training_context(repo, prepared, run, experiments,
        source, prior, profiles, backbone_factory=toy_backbone)
    output = tmp_path / 'PLACEHOLDER-reader-arithmetic'
    output.mkdir()
    engine = arithmetic.ArithmeticReplay(model, *graphs, output)
    assert engine.plan == context['native_plan']
    monkeypatch.setattr(torch.nn.Module, '_call_impl', forbidden)
    monkeypatch.setattr('numbra_ml.dataset.load_rgb', forbidden)
    monkeypatch.setattr('numbra_ml.export_remaining_replay.recipe', forbidden)
    monkeypatch.setattr('numbra_ml.export_remaining_replay.python_operator', forbidden)
    observed = []
    for identifier, evidence in training_rows(repo, retained, prepared, run, experiments,
            source, prior, profiles, backbone_factory=toy_backbone):
        observed.append(identifier)
        before = fingerprint(evidence)
        result, row = engine.run(evidence)
        assert result['original_controls']['native_instrumentation']['exact_bits']
        assert arithmetic.reconstruct_arithmetic(graphs[0], engine.plan, row) == result
        assert fingerprint(evidence) == before
    assert observed == [c.id for c in components] == [c.id for c in index.components if c.split == 'train']


def test_full_generated_mobile_has_all_39_targets_77_recipes_both_contexts(tmp_path, monkeypatch):
    torch.manual_seed(235)
    torch.set_num_threads(2)
    backbone = timm.create_model('mobilenetv3_small_100.lamb_in1k', pretrained=False)
    backbone.reset_classifier(0)
    model = Baseline(backbone, FeatureHead(torch.zeros(1024), torch.ones(1024))).requires_grad_(False).eval()
    paths = [tmp_path / 'PLACEHOLDER-full.onnx', tmp_path / 'PLACEHOLDER-full-rounded.onnx']
    export_preserving_batchnorm(model, paths[0])
    substitute_batchnorm(model, paths[0], paths[1], rounding_recipe=RECIPE)
    source, rounded = [onnx.load(path) for path in paths]
    output = tmp_path / 'PLACEHOLDER-full-original'
    output.mkdir()
    value = np.random.default_rng(235).normal(size=(1, 3, 224, 224)).astype(np.float32)
    retained = CompleteReplay(model, source, rounded, output).run(value)[1]
    output = tmp_path / 'PLACEHOLDER-full-arithmetic'
    output.mkdir()
    monkeypatch.setattr(torch.nn.Module, '_call_impl', forbidden)
    monkeypatch.setattr('numbra_ml.dataset.load_rgb', forbidden)
    engine = arithmetic.ArithmeticReplay(model, source, rounded, output)
    assert engine.records['scope']['operator_counts'] == {'HardSwish': 19, 'HardSigmoid': 9,
        'ReduceMean': 9, 'GlobalAveragePool': 1, 'Gemm': 1}
    assert len(engine.sessions) == 154
    assert engine.setup_audit['serialized_and_runtime_graphs'] == 308
    result, evidence = engine.run(retained)
    assert len(result['original_controls']['operators']) == 159
    assert all(len(evidence['recipes'][kind]) == 39 for kind in KINDS)
    monkeypatch.setattr(ort, 'InferenceSession', forbidden)
    monkeypatch.setattr(arithmetic, 'eager_expression', forbidden)
    assert arithmetic.reconstruct_arithmetic(source, engine.plan, evidence) == result


@pytest.mark.parametrize('bad', ['missing', 'occupied', 'unlabelled', 'symlink'])
def test_output_refused_before_any_sessions_or_writes(replayed, tmp_path, monkeypatch, bad):
    engine, original, _, _, _ = replayed
    output = tmp_path / ('unlabelled' if bad == 'unlabelled' else 'PLACEHOLDER-refused')
    if bad == 'symlink':
        output.symlink_to(original, target_is_directory=True)
    elif bad != 'missing':
        output.mkdir()
    if bad == 'occupied':
        (output / 'retained.txt').write_text('retain')
    monkeypatch.setattr(ort, 'InferenceSession', forbidden)
    with pytest.raises(ValueError, match='fresh empty PLACEHOLDER'):
        arithmetic.ArithmeticReplay(engine.model, engine.source, engine.rounded, output)
    if bad == 'occupied':
        assert (output / 'retained.txt').read_text() == 'retain'
