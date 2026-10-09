"""Generated-only PLACEHOLDER guarded runner and read-only full audit."""

from copy import deepcopy
import hashlib
import json
import subprocess

import numpy as np
import onnx
import onnxruntime as ort
import pytest
import torch

from numbra_ml import export_remaining_run as runner
from numbra_ml.export import export_environment
from numbra_ml.export_provenance import audit_environment
from numbra_ml.export_remaining_replay import CompleteReplay, audit_replay_setup
from numbra_ml.pretrained import sha256
from numbra_ml.train import json_text
from test_export_remaining_native import generated_pair
from test_export_runtime_profiles import profile_evidence
from test_export_replay import toy_backbone


@pytest.fixture(scope='module')
def complete_run(profile_evidence):
    repo, prepared, run, experiments, source, prior, profiles, _, index = profile_evidence
    output = profiles.parent / 'PLACEHOLDER-complete-training'
    retained = {p: sha256(p) for directory in (run, *experiments, source, prior, profiles)
                for p in directory.rglob('*') if p.is_file()}
    report = runner.training_run(repo, prepared, run, experiments, source, prior, profiles,
                                 output, backbone_factory=toy_backbone)
    assert retained == {p: sha256(p) for p in retained}
    return repo, prepared, run, experiments, source, prior, profiles, output, report, index


def audit(fixture, report=None):
    repo, prepared, run, experiments, source, prior, profiles, output, original, _ = fixture
    return runner.audit_training(repo, output, report or original, prepared, run, experiments,
                                  source, prior, profiles, backbone_factory=toy_backbone)


def test_full_generated_runner_has_complete_private_scope_and_fixed_protocol(complete_run):
    *_, output, report, index = complete_run
    ids = [c.id for c in index.components if c.split == 'train']
    assert report['status'] == 'DIAGNOSTIC ONLY'
    assert report['context']['protocol']['components'] == len(ids)
    assert report['model_state_after_sha256'] == report['context']['model_state_sha256']
    assert not any(report['context']['protocol'][key] for key in
                   ('frozen_evaluation_inputs_used', 'quantisation_fit', 'deployment_selection'))
    assert report['setup_audit']['status'] == 'PASS'
    assert report['observations']['prior_disabled_original_logits_exact_bits']
    assert json.loads((output / runner.REPORT).read_text()) == report
    text = json.dumps(report)
    for private in (*ids, 'python_logits"', 'original_onnx_logits"', 'failure_cases"', 'component_ids"'):
        assert private not in text
    for kind in ('preserved', 'rounded'):
        assert report['observations']['original_graph_training_parity'][kind]['n'] == len(ids)
        budget = report['observations']['original_graph_training_parity'][kind]['budget']
        assert budget['raw_absolute'] == 1e-4 and budget['probability_absolute'] == 1e-6


def test_complete_audit_needs_no_decode_forward_recipe_session_or_writes(complete_run, monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail('independent complete audit must not run inference or decode')
    repo, _, _, _, _, _, _, output, report, _ = complete_run
    files = {p: sha256(p) for p in output.rglob('*') if p.is_file()}
    monkeypatch.setattr(torch.nn.Module, '_call_impl', forbidden)
    monkeypatch.setattr(ort, 'InferenceSession', forbidden)
    monkeypatch.setattr('numbra_ml.dataset.load_rgb', forbidden)
    monkeypatch.setattr('numbra_ml.export_remaining_replay.recipe', forbidden)
    monkeypatch.setattr('numbra_ml.export_remaining_replay.python_operator', forbidden)
    result = audit(complete_run)
    assert result['status'] == 'PASS'
    assert result['baseline_inference'] is False
    assert result['historical_inference_authentication'] is False
    assert files == {p: sha256(p) for p in files}
    # Current HEAD and dirty context can advance, without relaxing live code.
    from numbra_ml import export_remaining
    original = export_remaining.export_environment
    def context_changed(root):
        env = original(root)
        env['git_commit'] = subprocess.check_output(['git', 'rev-parse', 'HEAD~1'], cwd=repo, text=True).strip()
        env['git_dirty'] = not report['context']['preflight']['environment']['git_dirty']
        return env
    monkeypatch.setattr(export_remaining, 'export_environment', context_changed)
    assert audit(complete_run)['status'] == 'PASS'


@pytest.mark.parametrize('bad', ['fit', 'component', 'source', 'saved', 'budget', 'aggregate', 'setup', 'state', 'timestamp'])
def test_full_report_corruption_fails_after_rehashing_saved_report(complete_run, bad):
    *_, output, report, _ = complete_run
    changed = deepcopy(report)
    if bad == 'fit':
        changed['context']['protocol']['threshold'] += 0.1
    elif bad == 'component':
        changed['context']['protocol']['components'] -= 1
    elif bad == 'source':
        changed['context']['preflight']['environment']['source_tree_sha256'] = 'bad'
    elif bad == 'saved':
        changed['context']['preflight']['saved_model_sha256'] = 'bad'
    elif bad == 'budget':
        changed['observations']['original_graph_training_parity']['rounded']['budget']['raw_absolute'] = 1.
    elif bad == 'aggregate':
        changed['observations']['complete_metric_aggregates']['native_instrumentation']['signed_mean']['mean'] = 1.
    elif bad == 'setup':
        changed['setup_audit']['operators'] -= 1
    elif bad == 'state':
        changed['model_state_after_sha256'] = 'bad'
    else:
        changed['created_utc'] = '2026-10-10T00:00:00'
    path = output / runner.REPORT
    original = path.read_bytes()
    try:
        path.write_text(json_text(changed))
        with pytest.raises(ValueError):
            audit(complete_run, changed)
    finally:
        path.write_bytes(original)


@pytest.mark.parametrize('bad', ['prior-profile', 'prior-details', 'prior-fit', 'empty-experiments', 'current-code'])
def test_guard_rejects_stale_evidence_before_creating_output_or_opening_image(profile_evidence, monkeypatch, bad):
    repo, prepared, run, experiments, source, prior, profiles, _, _ = profile_evidence
    output = profiles.parent / ('PLACEHOLDER-guard-' + bad)
    def forbidden(*args, **kwargs):
        pytest.fail('stale provenance must fail before any image or session')
    monkeypatch.setattr(runner, 'component_input', forbidden)
    monkeypatch.setattr(ort, 'InferenceSession', forbidden)
    path = profiles / runner.PROFILE_REPORT
    original = path.read_bytes()
    changed = json.loads(original)
    if bad == 'prior-profile':
        del changed['artifacts']['preserved_control']['profiles']['all']
    elif bad == 'prior-details':
        changed['diagnostic_details_sha256'] = 'bad'
    elif bad == 'prior-fit':
        changed['protocol']['temperature'] += 1.
    elif bad == 'empty-experiments':
        experiments = []
    else:
        changed['environment']['source_tree_sha256'] = 'bad'
    try:
        path.write_text(json_text(changed))
        with pytest.raises(ValueError):
            runner.training_run(repo, prepared, run, experiments, source, prior, profiles, output,
                                backbone_factory=toy_backbone)
        assert not output.exists()
    finally:
        path.write_bytes(original)


def test_every_setup_is_audited_before_first_training_decode(profile_evidence, monkeypatch):
    repo, prepared, run, experiments, source, prior, profiles, _, _ = profile_evidence
    output = profiles.parent / 'PLACEHOLDER-order-guard'
    audited = []
    original = runner.audit_replay_setup
    def setup(*args):
        result = original(*args)
        audited.append(result)
        return result
    def stopped(*args):
        assert len(audited) == 1 and audited[0]['status'] == 'PASS'
        raise RuntimeError('stop at first generated image')
    monkeypatch.setattr(runner, 'audit_replay_setup', setup)
    monkeypatch.setattr(runner, 'component_input', stopped)
    with pytest.raises(RuntimeError, match='first generated image'):
        runner.training_run(repo, prepared, run, experiments, source, prior, profiles, output,
                            backbone_factory=toy_backbone)
    assert not (output / runner.REPORT).exists()
    assert not (output / runner.OBSERVATIONS / 'PLACEHOLDER-evidence-index.json').exists()


@pytest.mark.parametrize('bad', ['constant', 'operand', 'runtime', 'records', 'extra-file', 'empty-directory', 'symlink'])
def test_all_expression_records_are_reconstructed_without_sessions(generated_pair, tmp_path, monkeypatch, bad):
    model, source, rounded, _ = generated_pair
    output = tmp_path / 'PLACEHOLDER-audit-kernels'
    output.mkdir()
    engine = CompleteReplay(model, source, rounded, output)
    records = deepcopy(engine.records)
    assert audit_replay_setup(model, source, rounded, output, records)['status'] == 'PASS'
    def forbidden(*args, **kwargs):
        pytest.fail('setup reconstruction cannot run inference')
    monkeypatch.setattr(torch.nn.Module, '_call_impl', forbidden)
    monkeypatch.setattr(ort, 'InferenceSession', forbidden)
    if bad == 'records':
        records['operators'].pop(next(iter(records['operators'])))
    elif bad == 'extra-file':
        (output / 'extra.json').write_text('{}')
    elif bad == 'empty-directory':
        (output / 'extra').mkdir()
    elif bad == 'symlink':
        (output / 'alias').symlink_to(output / 'PLACEHOLDER-preserved', target_is_directory=True)
    else:
        filename = 'PLACEHOLDER-tapped-runtime.onnx' if bad == 'runtime' else 'PLACEHOLDER-original.onnx'
        path = output / 'PLACEHOLDER-preserved' / filename
        graph = onnx.load(path)
        if bad == 'constant':
            value = graph.graph.initializer[0]
            array = onnx.numpy_helper.to_array(value).copy()
            array.flat[0] = np.nextafter(array.flat[0], np.float32(np.inf))
            value.CopyFrom(onnx.numpy_helper.from_array(array, value.name))
        else:
            node = next(n for n in graph.graph.node if n.op_type == 'Mul')
            node.input.reverse()
        onnx.save(graph, path)
    with pytest.raises(ValueError):
        audit_replay_setup(model, source, rounded, output, records)


@pytest.mark.parametrize('bad', [None, 'extra-source', 'changed-source', 'tree-hash', 'dependencies', 'unknown-commit', 'dirty-type'])
def test_explicit_historical_snapshot_keeps_complete_code_and_live_dependencies(profile_evidence, bad):
    repo = profile_evidence[0]
    current = export_environment(repo)
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=repo, text=True).strip()
    names = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', commit, '--', 'ml/src/numbra_ml'],
                                    cwd=repo, text=True).splitlines()
    code = {name: hashlib.sha256(subprocess.check_output(['git', 'show', commit + ':' + name], cwd=repo)).hexdigest()
            for name in names if name.endswith('.py')}
    recorded = deepcopy(current)
    recorded.update(source_files_sha256=code, source_tree_sha256=hashlib.sha256(json_text(code).encode()).hexdigest())
    if bad == 'extra-source':
        recorded['source_files_sha256']['ml/src/numbra_ml/extra.py'] = '0' * 64
    elif bad == 'changed-source':
        recorded['source_files_sha256'][next(iter(code))] = '0' * 64
    elif bad == 'tree-hash':
        recorded['source_tree_sha256'] = '0' * 64
    elif bad == 'dependencies':
        recorded['dependencies']['onnx'] = 'changed'
    elif bad == 'unknown-commit':
        commit = '0' * 40
    elif bad == 'dirty-type':
        recorded['git_dirty'] = 'yes'
    if bad is None:
        assert audit_environment(repo, recorded, current, source_commit=commit)['status'] == 'PASS'
        assert audit_environment(repo, recorded, current, source_commit=commit)['historical_inference_authentication'] is False
    else:
        with pytest.raises(ValueError, match='PLACEHOLDER'):
            audit_environment(repo, recorded, current, source_commit=commit)


def test_cli_refuses_existing_aggregate_before_any_work(profile_evidence, monkeypatch):
    repo = profile_evidence[0]
    def forbidden(*args, **kwargs):
        pytest.fail('existing target must fail before work')
    monkeypatch.setattr(runner, 'training_run', forbidden)
    assert runner.main(['--output', 'data/exports/PLACEHOLDER-m4-attempt1']) == 1
