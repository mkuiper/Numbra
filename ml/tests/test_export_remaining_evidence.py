"""Generated-only PLACEHOLDER persistence and no-inference ordered audit."""

import copy
import json
from pathlib import Path
import shutil
import tempfile

import numpy as np
import onnxruntime as ort
import pytest
import torch

from numbra_ml.export_remaining_evidence import (ARTIFACTS, INDEX, ArrayStore, Metrics,
    OrderedEvidence, array_id, audit_ordered, decode, prior_logits, read_json)
from numbra_ml.export_remaining_replay import CompleteReplay, KINDS
from numbra_ml.prepare import repository_root
from numbra_ml.pretrained import sha256
from numbra_ml.train import json_text
from test_export_remaining_native import generated_pair


@pytest.fixture(scope='module')
def persisted():
    repo = repository_root()
    parent = repo / 'data/test-runs'
    parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=parent) as temporary:
        root = Path(temporary)
        model, source, rounded, value = generated_pair.__wrapped__(root)
        kernels = root / 'PLACEHOLDER-kernels'
        kernels.mkdir()
        engine = CompleteReplay(model, source, rounded, kernels)
        observations = [engine.run(value + np.float32(offset))[1] for offset in (0., 0.125)]
        ids = ['generated-component-0', 'generated-component-1']
        prior = {'artifacts': {artifact: {'disabled': {'component_ids': ids,
            'python_logits': [float(row['native_original_logit'][0]) for row in observations],
            'original_onnx_logits': [float(row['graphs'][kind]['original_logit'][0]) for row in observations]}}
            for kind, artifact in ARTIFACTS.items()}}
        output = root / 'PLACEHOLDER-evidence'
        writer = OrderedEvidence(repo, output, source, engine.plan, ids, prior, temperature=2., threshold=0.5)
        for identifier, evidence in zip(ids, observations):
            writer.append(identifier, evidence)
        report = writer.finish()
        yield repo, root, output, source, engine.plan, ids, prior, report, observations


def audit(fixture, output=None, report=None, prior=None, ids=None):
    repo, _, original, source, plan, scope, previous, aggregate, _ = fixture
    return audit_ordered(repo, output or original, source, plan, ids or scope,
        prior or previous, report or aggregate, temperature=2., threshold=0.5)


def test_lossless_ordered_reconstruction_no_inference_and_private_details(persisted, monkeypatch):
    def forbidden(*a, **kw):
        pytest.fail('persisted reconstruction cannot decode images or run inference')
    monkeypatch.setattr(torch.nn.Module, '_call_impl', forbidden)
    monkeypatch.setattr(ort, 'InferenceSession', forbidden)
    monkeypatch.setattr('numbra_ml.dataset.load_rgb', forbidden)
    monkeypatch.setattr('numbra_ml.export_remaining_replay.recipe', forbidden)
    monkeypatch.setattr('numbra_ml.export_remaining_replay.python_operator', forbidden)
    result = audit(persisted)
    assert result['status'] == 'PASS' and result['components'] == 2
    assert result['baseline_inference'] is False
    assert result['historical_inference_authentication'] is False
    report = persisted[7]
    text = json.dumps(report)
    for private in ('generated-component-0', 'generated-component-1', 'python_logits', 'component_id"', 'failure_cases'):
        assert private not in text
    assert set(report['original_graph_training_parity']) == set(KINDS)
    assert report['protocol']['budget']['raw_absolute'] == 1e-4
    assert report['protocol']['budget']['probability_absolute'] == 1e-6
    for metric in report['complete_metric_aggregates']['operators'].values():
        for values in metric.values():
            assert values['native_replay_fidelity']['exact_bits'] == {'all': True, 'true_count': 2}
            assert values['signed_accounting']['telescoping_max_residual']['max'] == 0


def test_ordered_tree_roundtrip_keeps_order_signed_zero_int64_and_all_bits(persisted):
    _, root, _, *_ = persisted
    output = root / 'PLACEHOLDER-simple-arrays'
    output.mkdir()
    (output / 'tensors').mkdir()
    store = ArrayStore(output)
    first = np.array([0., -0., np.nextafter(np.float32(1.), np.float32(2.))], np.float32)
    value = {'z': first, 'a': [first.copy(), np.array([-1, 0, 2], np.int64)], 'scalar': np.array(-0., np.float32)}
    tree = store.encode(value)
    assert len(store.records) == 3
    used = set()
    restored = decode(output, tree, store.records, used, {})
    assert list(restored) == ['z', 'a', 'scalar']
    assert restored['z'].tobytes() == first.tobytes()
    assert restored['scalar'].shape == () and np.signbit(restored['scalar'])
    assert restored['a'][1].dtype == np.int64
    assert restored['z'] is restored['a'][0]
    assert not restored['z'].flags.writeable
    assert used == set(store.records)


@pytest.mark.parametrize('bad', ['object', 'float64', 'empty', 'nan', 'inf'])
def test_invalid_arrays_never_serialize(bad):
    values = {'object': np.array([object()], object), 'float64': np.ones(1, np.float64),
              'empty': np.zeros(0, np.float32), 'nan': np.array([np.nan], np.float32),
              'inf': np.array([np.inf], np.float32)}
    with pytest.raises(ValueError, match='persisted replay'):
        array_id(values[bad])


def test_aggregates_retain_signed_values_and_one_nonexact_row():
    metrics = Metrics()
    metrics.add({'notice': 'PLACEHOLDER', 'terms': {'signed': -2., 'exact_bits': True}})
    metrics.add({'notice': 'PLACEHOLDER', 'terms': {'signed': 1., 'exact_bits': False}})
    assert metrics.summary() == {'terms': {'signed': {'min': -2., 'max': 1., 'mean': -0.5},
                                          'exact_bits': {'all': False, 'true_count': 1}}}
    with pytest.raises(ValueError, match='metric scope'):
        metrics.add({'different': 0.})


@pytest.mark.parametrize('bad', ['duplicate', 'empty', 'order', 'python', 'onnx', 'not-float32', 'nan', 'reference'])
def test_invalid_scope_or_prior_fails_before_writing(persisted, bad):
    repo, root, _, source, plan, ids, prior, *_ = persisted
    ids, prior = copy.deepcopy(ids), copy.deepcopy(prior)
    row = prior['artifacts']['preserved_control']['disabled']
    if bad == 'duplicate':
        ids[1] = ids[0]
    elif bad == 'empty':
        ids = []
    elif bad == 'order':
        row['component_ids'].reverse()
    elif bad == 'python':
        row['python_logits'].pop()
    elif bad == 'onnx':
        row['original_onnx_logits'].pop()
    elif bad == 'not-float32':
        row['python_logits'][0] = 0.1
    elif bad == 'nan':
        row['original_onnx_logits'][0] = float('nan')
    else:
        row['python_logits'][0] = float(np.float32(row['python_logits'][0]) + np.float32(1.))
    output = root / ('PLACEHOLDER-refused-' + bad)
    with pytest.raises(ValueError, match='persisted replay'):
        OrderedEvidence(repo, output, source, plan, ids, prior, temperature=2., threshold=0.5)
    assert not output.exists()


def test_partial_out_of_order_and_repeated_runs_cannot_complete(persisted):
    repo, root, _, source, plan, ids, prior, _, rows = persisted
    output = root / 'PLACEHOLDER-partial'
    writer = OrderedEvidence(repo, output, source, plan, ids, prior, temperature=2., threshold=0.5)
    with pytest.raises(ValueError, match='ordered component'):
        writer.append(ids[1], rows[1])
    writer.append(ids[0], rows[0])
    with pytest.raises(ValueError, match='partial'):
        writer.finish()
    assert not (output / INDEX).exists()
    with pytest.raises(ValueError, match='fresh'):
        OrderedEvidence(repo, output, source, plan, ids, prior, temperature=2., threshold=0.5)
    writer.append(ids[1], rows[1])
    writer.finish()
    with pytest.raises(ValueError, match='repeated'):
        writer.finish()
    with pytest.raises(ValueError, match='ordered component'):
        writer.append(ids[0], rows[0])


def test_changed_original_logit_rejected_before_row_write(persisted):
    repo, root, _, source, plan, ids, prior, _, rows = persisted
    output = root / 'PLACEHOLDER-logit-refused'
    writer = OrderedEvidence(repo, output, source, plan, ids, prior, temperature=2., threshold=0.5)
    changed = copy.deepcopy(rows[0])
    changed['native_original_logit'] += np.float32(0.125)
    with pytest.raises(ValueError, match='prior disabled logit bits'):
        writer.append(ids[0], changed)
    assert not list((output / 'rows').iterdir())
    assert not list((output / 'tensors').iterdir())


@pytest.mark.parametrize('bad', ['row-order', 'row-id', 'row-checksum', 'metrics', 'array-checksum',
    'array-bits', 'array-spec', 'extra-array', 'extra-file', 'missing-row', 'duplicate-json',
    'scope', 'fit', 'aggregate', 'budget', 'prior', 'symlink'])
def test_corruption_rejected_even_with_rehashed_containers(persisted, bad):
    repo, root, original, source, plan, ids, prior, report, _ = persisted
    output = root / ('PLACEHOLDER-corruption-' + bad)
    shutil.copytree(original, output)
    changed, previous = copy.deepcopy(report), copy.deepcopy(prior)
    path = output / INDEX
    index = read_json(path)
    row_record = index['rows'][0]
    row_path = output / row_record['path']
    row = read_json(row_path)
    key = next(iter(index['arrays']))
    tensor_path = output / 'tensors' / f'PLACEHOLDER-{key}.npz'
    if bad == 'row-order':
        index['rows'].reverse()
    elif bad == 'row-id':
        row['component_id'] = ids[1]
    elif bad == 'row-checksum':
        row_record['sha256'] = '0' * 64
    elif bad == 'metrics':
        row['metrics']['native_instrumentation']['signed_mean'] = 7.
    elif bad == 'array-checksum':
        index['arrays'][key]['file_sha256'] = '0' * 64
    elif bad == 'array-bits':
        with np.load(tensor_path, allow_pickle=False) as archive:
            value = archive['value'].copy()
        value.flat[0] += 1
        np.savez_compressed(tensor_path, value=value)
        index['arrays'][key]['file_sha256'] = sha256(tensor_path)
        index['arrays'][key]['file_bytes'] = tensor_path.stat().st_size
    elif bad == 'array-spec':
        index['arrays'][key]['shape'] = [1]
    elif bad == 'extra-array':
        other = 'f' * 64
        index['arrays'][other] = dict(index['arrays'][key], array_sha256=other)
        shutil.copyfile(tensor_path, output / 'tensors' / f'PLACEHOLDER-{other}.npz')
    elif bad == 'extra-file':
        (output / 'rows' / 'extra.json').write_text('{}')
    elif bad == 'missing-row':
        row_path.unlink()
    elif bad == 'duplicate-json':
        row_path.write_text('{"notice": "PLACEHOLDER", "notice": "duplicate"}')
        row_record['sha256'] = sha256(row_path)
    elif bad == 'scope':
        index['protocol']['components'] = 1
    elif bad == 'fit':
        index['protocol']['temperature'] = 3.
    elif bad == 'aggregate':
        changed['complete_metric_aggregates']['native_instrumentation']['signed_mean']['mean'] = 1.
    elif bad == 'budget':
        changed['original_graph_training_parity']['rounded']['budget']['raw_absolute'] = 1.
    elif bad == 'prior':
        previous['artifacts']['complete_promoted_bn']['disabled']['original_onnx_logits'][0] += 1.
    else:
        tensor_path.unlink()
        tensor_path.symlink_to(original / 'tensors' / tensor_path.name)
    if bad in ('row-id', 'metrics'):
        row_path.write_text(json_text(row))
        row_record['sha256'] = sha256(row_path)
    path.write_text(json_text(index))
    changed['evidence_index_sha256'] = sha256(path)
    with pytest.raises(ValueError, match='persisted replay'):
        audit_ordered(repo, output, source, plan, ids, previous, changed, temperature=2., threshold=0.5)


def test_writes_are_confined_to_ignored_data(persisted):
    repo, _, _, source, plan, ids, prior, *_ = persisted
    with pytest.raises(ValueError, match='ignored data'):
        OrderedEvidence(repo, repo / 'ml/reports/PLACEHOLDER-unsafe', source, plan, ids, prior,
                        temperature=2., threshold=0.5)


def test_exact_prior_check_retains_signed_zero():
    prior = {'artifacts': {artifact: {'disabled': {'component_ids': ['generated-zero'],
             'python_logits': [-0.0], 'original_onnx_logits': [-0.0]}} for artifact in ARTIFACTS.values()}}
    assert np.signbit(prior_logits(prior, ['generated-zero'])['rounded']['python_logits'][0][0])
    prior['artifacts']['complete_promoted_bn']['disabled']['python_logits'][0] = 0.0
    with pytest.raises(ValueError, match='inconsistent prior Python'):
        prior_logits(prior, ['generated-zero'])
