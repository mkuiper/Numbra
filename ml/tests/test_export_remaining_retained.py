"""Generated-only PLACEHOLDER historical provenance and retained row guards."""

from copy import deepcopy
import hashlib
import subprocess

import onnxruntime as ort
import pytest
import torch

from numbra_ml import export_remaining_retained as retained
from numbra_ml import export_remaining_run as runner
from numbra_ml.export_remaining_evidence import INDEX, read_json
from numbra_ml.export_remaining_native import same_bits
from numbra_ml.pretrained import sha256
from numbra_ml.train import json_text
from test_export_remaining_run import complete_run, profile_evidence
from test_export_replay import toy_backbone


def rows(fixture, **kwargs):
    repo, prepared, run, experiments, source, prior, profiles, output, _, _ = fixture
    return retained.training_rows(repo, output, prepared, run, experiments, source,
                                  prior, profiles, backbone_factory=toy_backbone, **kwargs)


def audit(fixture, report, **kwargs):
    repo, prepared, run, experiments, source, prior, profiles, output, _, _ = fixture
    return runner.audit_training(repo, output, report, prepared, run, experiments,
        source, prior, profiles, backbone_factory=toy_backbone, **kwargs)


def snapshot(repo, environment):
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD~1'], cwd=repo, text=True).strip()
    names = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', commit,
        '--', 'ml/src/numbra_ml'], cwd=repo, text=True).splitlines()
    code = {name: hashlib.sha256(subprocess.check_output(['git', 'show', commit + ':' + name],
        cwd=repo)).hexdigest() for name in names if name.endswith('.py')}
    environment.update(source_files_sha256=code,
        source_tree_sha256=hashlib.sha256(json_text(code).encode()).hexdigest())
    return commit


@pytest.mark.parametrize('bad', [None, 'omitted-commit', 'unknown-commit', 'extra-source',
    'changed-source', 'tree-hash', 'live-dependencies', 'live-lock', 'live-hardware'])
def test_historical_complete_audit_binds_all_code_and_keeps_live_fields(complete_run, bad):
    report = deepcopy(complete_run[-2])
    environment = report['context']['preflight']['environment']
    commit = snapshot(complete_run[0], environment)
    if bad == 'omitted-commit':
        commit = None
    elif bad == 'unknown-commit':
        commit = '0' * 40
    elif bad == 'extra-source':
        environment['source_files_sha256']['ml/src/numbra_ml/extra.py'] = '0' * 64
    elif bad == 'changed-source':
        environment['source_files_sha256'][next(iter(environment['source_files_sha256']))] = '0' * 64
    elif bad == 'tree-hash':
        environment['source_tree_sha256'] = '0' * 64
    elif bad == 'live-dependencies':
        environment['dependencies']['onnx'] = 'changed'
    elif bad == 'live-lock':
        environment['dependency_lock_sha256'] = '0' * 64
    elif bad == 'live-hardware':
        # A non-source environment field cannot be silently replaced.
        environment['platform'] = 'changed'
    path = complete_run[-3] / runner.REPORT
    original = path.read_bytes()
    try:
        path.write_text(json_text(report))
        if bad is None:
            result = audit(complete_run, report, source_commit=commit)
            assert result['status'] == 'PASS'
            assert result['source_environment_audit']['source_commit'] == commit
            assert result['source_environment_audit']['live_dependencies_exact']
            assert not result['historical_inference_authentication']
        else:
            with pytest.raises(ValueError):
                audit(complete_run, report, source_commit=commit)
    finally:
        path.write_bytes(original)


def test_all_retained_rows_stream_without_decode_inference_or_writes(complete_run, monkeypatch):
    output, report, index = complete_run[-3:]
    files = {p: sha256(p) for p in output.rglob('*') if p.is_file()}
    def forbidden(*args, **kwargs):
        pytest.fail('retained reader must not decode, infer or persist evidence')
    monkeypatch.setattr(torch.nn.Module, '_call_impl', forbidden)
    monkeypatch.setattr(ort, 'InferenceSession', forbidden)
    monkeypatch.setattr('numbra_ml.dataset.load_rgb', forbidden)
    monkeypatch.setattr('numbra_ml.export_remaining_replay.recipe', forbidden)
    monkeypatch.setattr('numbra_ml.export_remaining_replay.python_operator', forbidden)
    monkeypatch.setattr('numbra_ml.export_remaining_evidence.ArrayStore.encode', forbidden)
    monkeypatch.setattr('numbra_ml.export_remaining_evidence.OrderedEvidence.append', forbidden)
    observed = []
    for identifier, evidence in rows(complete_run):
        observed.append(identifier)
        assert same_bits(evidence['native_original_logit'], evidence['native_captured_logit'])
        assert list(evidence['operators']) == [r['name'] for r in report['context']['native_plan']['nodes']]
        assert not evidence['input'].flags.writeable
        assert set(evidence['graphs']) == {'preserved', 'rounded'}
    assert observed == [c.id for c in index.components if c.split == 'train']
    assert files == {p: sha256(p) for p in files}


def test_corrupt_last_row_blocks_exposing_first_row(complete_run):
    root = complete_run[-3] / runner.OBSERVATIONS
    index = read_json(root / INDEX)
    path = root / index['rows'][-1]['path']
    original = path.read_bytes()
    try:
        path.write_text('{}')
        with pytest.raises(ValueError, match='checksum'):
            next(rows(complete_run))
    finally:
        path.write_bytes(original)


@pytest.mark.parametrize('bad', ['index', 'row', 'tensor'])
def test_reader_rechecks_accessed_bits_after_global_audit(complete_run, monkeypatch, bad):
    root = complete_run[-3] / runner.OBSERVATIONS
    index = read_json(root / INDEX)
    if bad == 'index':
        path = root / INDEX
    elif bad == 'row':
        path = root / index['rows'][0]['path']
    else:
        key = next(iter(index['arrays']))
        path = root / 'tensors' / f'PLACEHOLDER-{key}.npz'
    original = path.read_bytes()
    original_audit = retained.audit_training
    def changed_after_audit(*args, **kwargs):
        result = original_audit(*args, **kwargs)
        path.write_bytes(original + b'corrupt')
        return result
    monkeypatch.setattr(retained, 'audit_training', changed_after_audit)
    try:
        with pytest.raises(ValueError, match='changed|checksum'):
            list(rows(complete_run))
    finally:
        path.write_bytes(original)
