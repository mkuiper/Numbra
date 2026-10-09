"""Generated-only PLACEHOLDER complete retained arithmetic runner contracts."""

from copy import deepcopy
import hashlib
import json
import subprocess

import onnxruntime as ort
import pytest
import torch

from numbra_ml import export_arithmetic_run as runner
from numbra_ml.export_arithmetic_evidence import OrderedArithmeticEvidence
from numbra_ml.export_arithmetic_replay import ArithmeticReplay
from numbra_ml.export_remaining_evidence import ArrayStore, INDEX
from numbra_ml.export_remaining_run import REPORT as RETAINED_REPORT
from numbra_ml.pretrained import sha256
from numbra_ml.train import json_text
from test_export_remaining_run import complete_run, profile_evidence
from test_export_replay import toy_backbone


def forbidden(*args, **kwargs):
    pytest.fail('retained arithmetic must not decode, call native model or replay original controls')


def execute(fixture, output, **kwargs):
    repo, prepared, run, experiments, source, prior, profiles, retained, _, _ = fixture
    return runner.arithmetic_run(repo, retained, prepared, run, experiments, source, prior,
        profiles, output, backbone_factory=toy_backbone, **kwargs)


@pytest.fixture(scope='module')
def arithmetic_run(complete_run):
    output = complete_run[7].parent / 'PLACEHOLDER-generated-arithmetic-training'
    retained = complete_run[7]
    before = {p: sha256(p) for p in retained.rglob('*') if p.is_file()}
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(torch.nn.Module, '_call_impl', forbidden)
        patch.setattr('numbra_ml.dataset.load_rgb', forbidden)
        patch.setattr('numbra_ml.export_remaining_replay.recipe', forbidden)
        patch.setattr('numbra_ml.export_remaining_replay.python_operator', forbidden)
        report = execute(complete_run, output)
    assert before == {p: sha256(p) for p in before}
    return complete_run, output, report


def audit(fixture, report=None, **kwargs):
    original, output, saved = fixture
    repo, prepared, run, experiments, source, prior, profiles, retained, _, _ = original
    return runner.audit_arithmetic_training(repo, output, report or saved, retained, prepared,
        run, experiments, source, prior, profiles, backbone_factory=toy_backbone, **kwargs)


def test_complete_runner_keeps_scope_fits_budgets_controls_and_private_rows(arithmetic_run):
    original, output, report = arithmetic_run
    ids = [c.id for c in original[-1].components if c.split == 'train']
    context = report['context']
    assert report['status'] == 'DIAGNOSTIC ONLY'
    assert context['protocol']['decision'] == 'ADR-024'
    assert context['protocol']['components'] == len(ids)
    for key in ('temperature', 'threshold', 'preprocessing', 'component_ids_sha256'):
        assert context['protocol'][key] == original[-2]['context']['protocol'][key]
    for key in ('new_native_model_inference', 'image_decoding', 'original_control_replay',
                'frozen_evaluation_inputs_used', 'quantisation_fit', 'deployment_selection'):
        assert context['protocol'][key] is False
    assert context['retained_report_sha256'] == sha256(original[7] / RETAINED_REPORT)
    assert report['model_state_after_sha256'] == context['model_state_sha256']
    assert report['setup_audit']['status'] == 'PASS'
    assert report['observations']['prior_disabled_original_logits_exact_bits']
    assert report['observations']['whole_model_parity'] == 'UNVERIFIED'
    assert report['observations']['deployment_selection'] is False
    assert json.loads((output / runner.REPORT).read_text()) == report
    for kind in ('preserved', 'rounded'):
        assert report['observations']['original_graph_training_parity'][kind] == original[-2][
            'observations']['original_graph_training_parity'][kind]
    text = json.dumps(report)
    for private in (*ids, 'python_logits"', 'original_onnx_logits"', 'component_ids"', 'failure_cases"'):
        assert private not in text


def test_independent_audit_has_no_inference_or_writes(arithmetic_run, monkeypatch):
    original, output, _ = arithmetic_run
    files = {p: sha256(p) for root in (original[7], output) for p in root.rglob('*') if p.is_file()}
    monkeypatch.setattr(torch.nn.Module, '_call_impl', forbidden)
    monkeypatch.setattr('numbra_ml.dataset.load_rgb', forbidden)
    monkeypatch.setattr(ort, 'InferenceSession', forbidden)
    monkeypatch.setattr('numbra_ml.export_arithmetic_replay.eager_expression', forbidden)
    monkeypatch.setattr('numbra_ml.export_remaining_replay.recipe', forbidden)
    monkeypatch.setattr(ArrayStore, 'encode', forbidden)
    result = audit(arithmetic_run)
    assert result['status'] == 'PASS'
    assert result['complete_original_and_arithmetic_evidence']
    assert result['baseline_inference'] is False
    assert result['historical_inference_authentication'] is False
    assert result['whole_model_recipe_parity'] == 'UNVERIFIED'
    assert result['deployment_selection'] is False
    assert files == {p: sha256(p) for p in files}


@pytest.mark.parametrize('bad', ['fit', 'component', 'source', 'dependency', 'hardware',
    'saved', 'retained_hash', 'retained_audit', 'budget', 'aggregate', 'setup', 'state',
    'timestamp', 'notice', 'acceptance', 'native_inference'])
def test_rehashed_report_corruption_rejected(arithmetic_run, bad):
    _, output, original = arithmetic_run
    report = deepcopy(original)
    if bad == 'fit':
        report['context']['protocol']['threshold'] += 0.1
    elif bad == 'component':
        report['context']['protocol']['components'] -= 1
    elif bad == 'source':
        report['context']['preflight']['environment']['source_tree_sha256'] = 'bad'
    elif bad == 'dependency':
        report['context']['preflight']['environment']['dependencies']['onnx'] = 'bad'
    elif bad == 'hardware':
        report['context']['preflight']['environment']['machine'] = 'bad'
    elif bad == 'saved':
        report['context']['preflight']['saved_model_sha256'] = 'bad'
    elif bad == 'retained_hash':
        report['context']['retained_report_sha256'] = 'bad'
    elif bad == 'retained_audit':
        report['context']['retained_report_audit']['components'] -= 1
    elif bad == 'budget':
        report['observations']['original_graph_training_parity']['rounded']['budget']['raw_absolute'] = 1.
    elif bad == 'aggregate':
        report['observations']['complete_metric_aggregates']['original_controls'][
            'native_instrumentation']['signed_mean']['mean'] = 1.
    elif bad == 'setup':
        report['setup_audit']['recipe_graphs'] -= 1
    elif bad == 'state':
        report['model_state_after_sha256'] = 'bad'
    elif bad == 'timestamp':
        report['created_utc'] = '2026-10-10T00:00:00'
    elif bad == 'notice':
        report['notice'] = 'accepted model'
    elif bad == 'acceptance':
        report['observations']['whole_model_parity'] = 'PASS'
    else:
        report['context']['protocol']['new_native_model_inference'] = True
    path = output / runner.REPORT
    saved = path.read_bytes()
    try:
        path.write_text(json_text(report))
        with pytest.raises(ValueError):
            audit(arithmetic_run, report)
    finally:
        path.write_bytes(saved)


def test_corrupt_last_original_row_blocks_sessions_and_output(complete_run, monkeypatch):
    retained = complete_run[7]
    path = sorted((retained / 'PLACEHOLDER-observations/rows').glob('*.json'))[-1]
    saved = path.read_bytes()
    output = retained.parent / 'PLACEHOLDER-corrupt-original-arithmetic'
    monkeypatch.setattr(ort, 'InferenceSession', forbidden)
    try:
        path.write_text('{}')
        with pytest.raises(ValueError):
            execute(complete_run, output)
        assert not output.exists()
    finally:
        path.write_bytes(saved)


def test_complete_context_and_setup_precede_first_retained_access(complete_run, monkeypatch):
    output = complete_run[7].parent / 'PLACEHOLDER-arithmetic-order-guard'
    observed = []
    context, setup = runner.arithmetic_context, runner.audit_arithmetic_setup
    def checked_context(*args, **kwargs):
        value = context(*args, **kwargs)
        observed.append('context')
        return value
    def checked_setup(*args, **kwargs):
        value = setup(*args, **kwargs)
        observed.append('setup')
        return value
    def stopped(*args, **kwargs):
        assert observed == ['context', 'setup']
        raise RuntimeError('stop before first retained access')
    monkeypatch.setattr(runner, 'arithmetic_context', checked_context)
    monkeypatch.setattr(runner, 'audit_arithmetic_setup', checked_setup)
    monkeypatch.setattr(runner, 'training_rows', stopped)
    with pytest.raises(RuntimeError, match='first retained access'):
        execute(complete_run, output)
    assert not (output / runner.REPORT).exists()
    assert not (output / runner.OBSERVATIONS / INDEX).exists()


@pytest.mark.parametrize('stage', ['partial', 'reader_final', 'persist', 'final_audit'])
def test_interrupted_or_unaudited_execution_publishes_no_report(complete_run, monkeypatch, stage):
    output = complete_run[7].parent / ('PLACEHOLDER-arithmetic-interrupted-' + stage)
    monkeypatch.setattr(torch.nn.Module, '_call_impl', forbidden)
    monkeypatch.setattr('numbra_ml.dataset.load_rgb', forbidden)
    if stage in ('partial', 'reader_final'):
        reader = runner.training_rows
        def incomplete(*args, **kwargs):
            for position, row in enumerate(reader(*args, **kwargs)):
                yield row
                if stage == 'partial' and position == 0:
                    return
            raise ValueError('reader final scope rejected')
        monkeypatch.setattr(runner, 'training_rows', incomplete)
    else:
        def stopped(*args, **kwargs):
            raise ValueError('deliberate failure before publication')
        monkeypatch.setattr(OrderedArithmeticEvidence if stage == 'persist' else runner,
            'append' if stage == 'persist' else 'audit_arithmetic_training', stopped)
    with pytest.raises(ValueError):
        execute(complete_run, output)
    assert not (output / runner.REPORT).exists()
    if stage != 'final_audit':
        assert not (output / runner.OBSERVATIONS / INDEX).exists()


def test_setup_mutation_during_run_is_rejected_at_final_audit(complete_run, monkeypatch):
    output = complete_run[7].parent / 'PLACEHOLDER-arithmetic-setup-mutation'
    original = ArithmeticReplay.run
    def corrupt_after_recipe(self, row):
        value = original(self, row)
        path = next((output / runner.KERNELS).rglob('PLACEHOLDER-runtime.onnx'))
        path.write_bytes(b'corrupt runtime')
        return value
    monkeypatch.setattr(ArithmeticReplay, 'run', corrupt_after_recipe)
    # ONNX DecodeError is intentionally allowed to propagate: no report is published.
    from google.protobuf.message import DecodeError
    with pytest.raises((ValueError, DecodeError)):
        execute(complete_run, output)
    assert not (output / runner.REPORT).exists()


@pytest.mark.parametrize('bad', ['existing', 'tracked', 'unlabelled', 'symlink'])
def test_invalid_output_is_rejected_before_context(complete_run, monkeypatch, bad):
    repo, *_, retained, _, _ = complete_run
    output = retained.parent / ('PLACEHOLDER-refused-arithmetic-' + bad)
    if bad == 'existing':
        output = retained
    elif bad == 'tracked':
        output = repo / 'ml/reports/PLACEHOLDER-refused'
    elif bad == 'unlabelled':
        output = retained.parent / 'unlabelled-arithmetic'
    else:
        output.symlink_to(retained, target_is_directory=True)
    monkeypatch.setattr(runner, 'arithmetic_context', forbidden)
    with pytest.raises(ValueError):
        execute(complete_run, output)


def test_separate_explicit_historical_source_bindings(complete_run, monkeypatch):
    repo = complete_run[0]
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=repo, text=True).strip()
    names = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', commit, '--',
        'ml/src/numbra_ml'], cwd=repo, text=True).splitlines()
    code = {name: hashlib.sha256(subprocess.check_output(['git', 'show', commit + ':' + name],
        cwd=repo)).hexdigest() for name in names if name.endswith('.py')}
    def historical_environment(report):
        report['context']['preflight']['environment'].update(source_files_sha256=code,
            source_tree_sha256=hashlib.sha256(json_text(code).encode()).hexdigest())
    path = complete_run[7] / RETAINED_REPORT
    saved = path.read_bytes()
    retained = json.loads(saved)
    historical_environment(retained)
    output = path.parent.parent / 'PLACEHOLDER-arithmetic-historical'
    monkeypatch.setattr(torch.nn.Module, '_call_impl', forbidden)
    monkeypatch.setattr('numbra_ml.dataset.load_rgb', forbidden)
    try:
        path.write_text(json_text(retained))
        with pytest.raises(ValueError, match='source/dependency'):
            execute(complete_run, output)
        assert not output.exists()
        report = execute(complete_run, output, retained_source_commit=commit)
        historical_environment(report)
        (output / runner.REPORT).write_text(json_text(report))
        fixture = complete_run, output, report
        monkeypatch.setattr(ort, 'InferenceSession', forbidden)
        with pytest.raises(ValueError, match='source/dependency'):
            audit(fixture, retained_source_commit=commit)
        result = audit(fixture, retained_source_commit=commit, source_commit=commit)
        assert result['source_environment_audit']['source_commit'] == commit
        assert result['retained']['source_environment_audit']['source_commit'] == commit
    finally:
        path.write_bytes(saved)


def test_cli_existing_aggregate_is_rejected_before_work(complete_run, monkeypatch):
    monkeypatch.setattr(runner, 'arithmetic_run', forbidden)
    assert runner.main(['--output', 'data/exports/PLACEHOLDER-m4-attempt1']) == 1
