"""Generated-only ordered arithmetic persistence and independent audit."""

import copy
import json
import shutil
import weakref

import numpy as np
import onnxruntime as ort
import pytest
import torch

from numbra_ml import export_arithmetic_evidence as persistence
from numbra_ml import export_remaining_evidence as storage
from numbra_ml.export_arithmetic_replay import reconstruct_arithmetic, targets
from numbra_ml.export_remaining_arithmetic import RECIPES
from numbra_ml.export_remaining_replay import CompleteReplay, KINDS
from numbra_ml.prepare import repository_root
from numbra_ml.pretrained import sha256
from numbra_ml.train import json_text
from test_export_arithmetic_replay import replayed, fingerprint, forbidden


@pytest.fixture(scope='module')
def arithmetic_persisted(replayed):
    engine, setup, retained, _, first = replayed
    root = setup.parent
    original_output = root / 'PLACEHOLDER-second-original'
    original_output.mkdir()
    value = retained['operators'][engine.plan['nodes'][0]['name']]['native_operands'][0]
    second_retained = CompleteReplay(engine.model, engine.source, engine.rounded,
        original_output).run(value + np.float32(0.125))[1]
    second = engine.run(second_retained)[1]
    rows = [first, second]
    ids = ['generated-arithmetic-0', 'generated-arithmetic-1']
    prior = {'artifacts': {artifact: {'disabled': {'component_ids': ids,
        'python_logits': [float(row['retained']['native_original_logit'][0]) for row in rows],
        'original_onnx_logits': [float(row['retained']['graphs'][kind]['original_logit'][0]) for row in rows]}}
        for kind, artifact in storage.ARTIFACTS.items()}}
    repo = repository_root()
    output = root / 'PLACEHOLDER-arithmetic-observations'
    writer = persistence.OrderedArithmeticEvidence(repo, output, engine.source, engine.plan,
        ids, prior, temperature=2., threshold=0.5)
    before = fingerprint(rows)
    for identifier, row in zip(ids, rows):
        writer.append(identifier, row)
    report = writer.finish()
    assert fingerprint(rows) == before
    return repo, root, output, engine, ids, prior, report, rows


def audit(fixture, *, output=None, report=None, prior=None, ids=None):
    repo, _, original, engine, scope, previous, aggregate, _ = fixture
    return persistence.audit_arithmetic_ordered(repo, output or original, engine.source,
        engine.plan, ids if ids is not None else scope, prior or previous, report or aggregate,
        temperature=2., threshold=0.5)


def test_complete_audit_has_no_decode_inference_recipes_or_writes(arithmetic_persisted, monkeypatch):
    monkeypatch.setattr(torch.nn.Module, '_call_impl', forbidden)
    monkeypatch.setattr(ort, 'InferenceSession', forbidden)
    monkeypatch.setattr('numbra_ml.dataset.load_rgb', forbidden)
    monkeypatch.setattr('numbra_ml.export_arithmetic_replay.eager_expression', forbidden)
    monkeypatch.setattr('numbra_ml.export_remaining_replay.recipe', forbidden)
    monkeypatch.setattr('numbra_ml.export_remaining_replay.python_operator', forbidden)
    monkeypatch.setattr(storage.ArrayStore, 'encode', forbidden)
    result = audit(arithmetic_persisted)
    assert result['status'] == 'PASS' and result['components'] == 2
    assert result['baseline_inference'] is False
    assert result['historical_inference_authentication'] is False
    report = arithmetic_persisted[6]
    assert report['whole_model_parity'] == 'UNVERIFIED'
    assert report['deployment_selection'] is False
    assert report['protocol']['decision'] == 'ADR-024'
    assert report['protocol']['fixed_recipes'] == [[op, list(v)] for op, v in RECIPES.items()]
    assert set(report['original_graph_training_parity']) == set(KINDS)
    for private in ('generated-arithmetic-0', 'generated-arithmetic-1', 'python_logits', 'failure_cases'):
        assert private not in json.dumps(report)


def test_every_ordered_array_and_metric_roundtrips_exactly(arithmetic_persisted):
    _, _, output, engine, _, _, report, rows = arithmetic_persisted
    index = storage.read_json(output / storage.INDEX)
    used, metrics = set(), storage.Metrics()
    for record, original in zip(index['rows'], rows):
        row = storage.read_json(output / record['path'])
        evidence = storage.decode(output, row['evidence'], index['arrays'], used, {})
        assert fingerprint(evidence) == fingerprint(original)
        reconstructed = reconstruct_arithmetic(engine.source, engine.plan, evidence)
        assert reconstructed == row['metrics']
        metrics.add(reconstructed)
    assert used == set(index['arrays'])
    assert metrics.summary() == report['complete_metric_aggregates']
    assert list(report['complete_metric_aggregates']['recipes']) == list(KINDS)
    # All original observations participate; no replacement graph parity claim.
    assert len(report['complete_metric_aggregates']['original_controls']['operators']) == len(engine.plan['nodes'])


def test_streaming_audit_releases_previous_component_arrays(arithmetic_persisted, monkeypatch):
    original_decode = storage.decode
    previous, depth, calls = [], 0, 0

    def tracked(*args):
        nonlocal depth, calls
        if depth == 0:
            assert all(ref() is None for ref in previous)
            previous.clear()
        depth += 1
        result = original_decode(*args)
        depth -= 1
        if depth == 0:
            previous.extend(weakref.ref(array) for array in args[-1].values())
            calls += 1
        return result

    monkeypatch.setattr(storage, 'decode', tracked)
    assert audit(arithmetic_persisted)['status'] == 'PASS'
    assert calls == 2 and all(ref() is None for ref in previous)


def test_partial_ordered_append_and_bad_prior_never_complete(arithmetic_persisted):
    repo, root, _, engine, ids, prior, _, rows = arithmetic_persisted
    output = root / 'PLACEHOLDER-arithmetic-partial'
    writer = persistence.OrderedArithmeticEvidence(repo, output, engine.source, engine.plan,
        ids, prior, temperature=2., threshold=0.5)
    with pytest.raises(ValueError, match='ordered component'):
        writer.append(ids[1], rows[1])
    with pytest.raises(ValueError, match='partial'):
        writer.finish()
    changed = copy.deepcopy(rows[0])
    changed['retained']['native_original_logit'] += np.float32(1.)
    with pytest.raises(ValueError, match='prior disabled logit bits'):
        writer.append(ids[0], changed)
    assert not list((output / 'rows').iterdir()) and not list((output / 'tensors').iterdir())
    writer.append(ids[0], rows[0])
    with pytest.raises(ValueError, match='partial'):
        writer.finish()
    assert not (output / storage.INDEX).exists()
    writer.append(ids[1], rows[1])
    writer.finish()
    with pytest.raises(ValueError, match='repeated'):
        writer.finish()
    with pytest.raises(ValueError, match='ordered component'):
        writer.append(ids[0], rows[0])


@pytest.mark.parametrize('bad', ['graph-order', 'target-order', 'origin', 'recipe', 'engine',
    'engine-order', 'control', 'lineage', 'nonfinite'])
def test_invalid_arithmetic_row_is_refused_before_any_write(arithmetic_persisted, bad):
    repo, root, _, engine, ids, prior, _, rows = arithmetic_persisted
    output = root / ('PLACEHOLDER-arithmetic-refused-' + bad)
    writer = persistence.OrderedArithmeticEvidence(repo, output, engine.source, engine.plan,
        ids, prior, temperature=2., threshold=0.5)
    changed = copy.deepcopy(rows[0])
    recipes = changed['recipes']['rounded']
    name = next(iter(recipes))
    row = recipes[name]
    origin = row['runtime_input']
    variant = next(iter(origin))
    if bad == 'graph-order':
        changed['recipes'] = dict(reversed(list(changed['recipes'].items())))
    elif bad == 'target-order':
        changed['recipes']['rounded'] = dict(reversed(list(recipes.items())))
    elif bad == 'origin':
        row.pop('native_input')
    elif bad == 'recipe':
        origin.pop(variant)
    elif bad == 'engine':
        origin[variant].pop('runtime')
    elif bad == 'engine-order':
        origin[variant] = dict(reversed(list(origin[variant].items())))
    elif bad == 'control':
        changed['retained']['operators'].pop(engine.plan['nodes'][0]['name'])
    elif bad == 'lineage':
        changed['retained']['operators'][name]['native_operands'][0] += np.float32(1.)
    else:
        origin[variant]['runtime'].flat[0] = np.nan
    with pytest.raises(ValueError):
        writer.append(ids[0], changed)
    assert not list((output / 'rows').iterdir()) and not list((output / 'tensors').iterdir())


@pytest.mark.parametrize('bad', ['row-order', 'row-id', 'row-checksum', 'recipe-metric',
    'control-metric', 'array-checksum', 'array-bits', 'extra-array', 'extra-file', 'missing-row',
    'duplicate-json', 'fit', 'recipes', 'target-scope', 'aggregate', 'budget', 'prior', 'symlink'])
def test_independent_audit_rejects_corruption_even_after_rehash(arithmetic_persisted, bad, monkeypatch):
    repo, root, original, engine, ids, prior, report, _ = arithmetic_persisted
    output = root / ('PLACEHOLDER-arithmetic-corruption-' + bad)
    shutil.copytree(original, output)
    changed, previous = copy.deepcopy(report), copy.deepcopy(prior)
    path = output / storage.INDEX
    index = storage.read_json(path)
    record = index['rows'][0]
    row_path = output / record['path']
    row = storage.read_json(row_path)
    key = next(iter(index['arrays']))
    tensor_path = output / 'tensors' / f'PLACEHOLDER-{key}.npz'
    name = targets(engine.plan)[0]['name']
    variant = next(iter(RECIPES[targets(engine.plan)[0]['operator']]))
    if bad == 'row-order':
        index['rows'].reverse()
    elif bad == 'row-id':
        row['component_id'] = ids[1]
    elif bad == 'row-checksum':
        record['sha256'] = '0' * 64
    elif bad == 'recipe-metric':
        row['metrics']['recipes']['rounded'][name]['origins']['runtime_input'][variant][
            'runtime_vs_eager_recipe']['signed_mean'] = 7.
    elif bad == 'control-metric':
        row['metrics']['original_controls']['native_instrumentation']['signed_mean'] = 7.
    elif bad == 'array-checksum':
        index['arrays'][key]['file_sha256'] = '0' * 64
    elif bad == 'array-bits':
        with np.load(tensor_path, allow_pickle=False) as archive:
            value = archive['value'].copy()
        value.flat[0] += 1
        np.savez(tensor_path, value=value)
        index['arrays'][key]['file_sha256'] = sha256(tensor_path)
        index['arrays'][key]['file_bytes'] = tensor_path.stat().st_size
    elif bad == 'extra-array':
        other = 'f' * 64
        index['arrays'][other] = dict(index['arrays'][key], array_sha256=other)
        shutil.copyfile(tensor_path, output / 'tensors' / f'PLACEHOLDER-{other}.npz')
    elif bad == 'extra-file':
        (output / 'unexpected').mkdir()
    elif bad == 'missing-row':
        row_path.unlink()
    elif bad == 'duplicate-json':
        row_path.write_text('{"notice":"PLACEHOLDER","notice":"duplicate"}')
        record['sha256'] = sha256(row_path)
    elif bad == 'fit':
        index['protocol']['temperature'] = 3.
    elif bad == 'recipes':
        index['protocol']['fixed_recipes'][0][1].pop()
    elif bad == 'target-scope':
        index['protocol']['ordered_targets_sha256'] = '0' * 64
    elif bad == 'aggregate':
        changed['complete_metric_aggregates']['recipes']['rounded'][name]['origins'][
            'runtime_input'][variant]['runtime_vs_eager_recipe']['signed_mean']['mean'] = 1.
    elif bad == 'budget':
        changed['original_graph_training_parity']['rounded']['budget']['raw_absolute'] = 1.
    elif bad == 'prior':
        previous['artifacts']['complete_promoted_bn']['disabled']['original_onnx_logits'][0] += 1.
    else:
        tensor_path.unlink()
        tensor_path.symlink_to(original / 'tensors' / tensor_path.name)
    if bad in ('row-id', 'recipe-metric', 'control-metric'):
        row_path.write_text(json_text(row))
        record['sha256'] = sha256(row_path)
    path.write_text(json_text(index))
    changed['evidence_index_sha256'] = sha256(path)
    monkeypatch.setattr(ort, 'InferenceSession', forbidden)
    with pytest.raises(ValueError):
        audit(arithmetic_persisted, output=output, report=changed, prior=previous)


def test_signed_zero_and_nonzero_recipe_errors_survive_persistence(arithmetic_persisted):
    repo, root, _, engine, ids, prior, _, rows = arithmetic_persisted
    changed = copy.deepcopy(rows)
    name = targets(engine.plan)[0]['name']
    variant = next(iter(RECIPES[targets(engine.plan)[0]['operator']]))
    for position, row in enumerate(changed):
        outputs = row['recipes']['rounded'][name]['runtime_input'][variant]
        outputs['eager'].fill(0.)
        outputs['runtime'].fill(-0. if position == 0 else 0.125)
    output = root / 'PLACEHOLDER-arithmetic-signed-errors'
    writer = persistence.OrderedArithmeticEvidence(repo, output, engine.source, engine.plan,
        ids, prior, temperature=2., threshold=0.5)
    for identifier, row in zip(ids, changed):
        writer.append(identifier, row)
    report = writer.finish()
    assert audit(arithmetic_persisted, output=output, report=report)['status'] == 'PASS'
    metric = report['complete_metric_aggregates']['recipes']['rounded'][name]['origins'][
        'runtime_input'][variant]['runtime_vs_eager_recipe']
    assert metric['max_absolute'] == {'min': 0., 'max': 0.125, 'mean': 0.0625}
    assert metric['exact_bits'] == {'all': False, 'true_count': 0}
    assert metric['signed_mean']['mean'] == 0.0625


def test_arithmetic_output_is_ignored_fresh_and_labelled(arithmetic_persisted):
    repo, _, output, engine, ids, prior, _, _ = arithmetic_persisted
    for invalid in (repo / 'ml/reports/PLACEHOLDER-unsafe', output, output.parent / 'unlabelled'):
        with pytest.raises(ValueError):
            persistence.OrderedArithmeticEvidence(repo, invalid, engine.source, engine.plan,
                ids, prior, temperature=2., threshold=0.5)


def test_arithmetic_evidence_cannot_be_audited_as_original_only(arithmetic_persisted):
    repo, _, output, engine, ids, prior, report, _ = arithmetic_persisted
    with pytest.raises(ValueError, match='index scope/protocol'):
        storage.audit_ordered(repo, output, engine.source, engine.plan, ids, prior,
            report, temperature=2., threshold=0.5)


@pytest.mark.parametrize('field,value', [('whole_model_parity', 'PASS'),
    ('deployment_selection', True), ('notice', storage.NOTICE)])
def test_aggregate_cannot_claim_acceptance_or_another_protocol(arithmetic_persisted, field, value):
    report = copy.deepcopy(arithmetic_persisted[6])
    report[field] = value
    with pytest.raises(ValueError, match='aggregate reconstruction'):
        audit(arithmetic_persisted, report=report)
