"""Generated RGB/toy weights only; actual ONNX export/quantisation/CPU runtime."""

from dataclasses import replace
import json
from pathlib import Path
import tempfile

import numpy as np
import onnx
import pytest
import torch
from torch import nn

from numbra_ml.evaluation import read_component_index
from numbra_ml.export import (INPUT_SHAPE, TrainingCalibration, aggregate_parity, compare,
                             export_environment, export_float, export_run, frozen_evaluation,
                             graph_report, local_temporaries, runtime, stress_inputs, summarise_run, tensor_input)
from numbra_ml.parity import FLOAT_BUDGET
from numbra_ml.prepare import prepare_run, repository_root
from numbra_ml.train import train_run
from numbra_ml.training import Baseline, FeatureHead, TrainingConfig


def toy_backbone():
    return nn.Sequential(nn.Conv2d(3, 4, 1), nn.BatchNorm2d(4),
                         nn.AdaptiveAvgPool2d(1), nn.Flatten()).requires_grad_(False)


@pytest.fixture
def prepared(tmp_path):
    root = tmp_path / 'prepared'
    prepare_run(root, groups_per_source=16)
    return root, read_component_index(root / 'manifest.jsonl', root / 'preparation-report.json')


def test_export_environment_has_hash_pinned_additions():
    result = export_environment(repository_root())
    assert result['dependencies']['onnx'] == '1.19.1'
    assert result['dependencies']['onnxruntime'] == '1.23.2'
    assert len(result['dependencies']) == 42
    assert len(result['export_dependency_lock_sha256']) == 64
    for line in (repository_root() / 'ml/requirements-export.lock').read_text().splitlines():
        if '==' in line:
            assert len(line.split('--hash=sha256:')[1]) == 64


@pytest.mark.parametrize('bad', [np.zeros(INPUT_SHAPE, np.float64),
    np.zeros((2, 3, 224, 224), np.float32), np.zeros((1, 224, 224, 3), np.float32),
    np.full(INPUT_SHAPE, np.nan, np.float32), np.full(INPUT_SHAPE, np.inf, np.float32),
    np.zeros(INPUT_SHAPE, np.float32)[:, :, :, ::-1]])
def test_runtime_input_rejects_invalid_tensors(bad):
    with pytest.raises(ValueError, match='finite contiguous'):
        tensor_input(bad)


def test_calibration_reader_uses_all_and_only_train_rewinds(prepared):
    root, index = prepared
    reader = TrainingCalibration(index, root)
    assert {c.id for c in reader.components} == {c.id for c in index.components if c.split == 'train'}
    assert all(c.split != 'held_out' for c in reader.components)
    first = reader.get_next()['rgb']
    n = 1
    while reader.get_next() is not None:
        n += 1
    assert n == len(reader.components)
    reader.rewind()
    assert np.array_equal(first, reader.get_next()['rgb'])
    empty = replace(index, components=tuple(c for c in index.components if c.split != 'train'))
    with pytest.raises(ValueError, match='training components'):
        TrainingCalibration(empty, root)
    # Altered held-out bytes cannot affect the calibration reader.
    held = next(c for c in index.components if c.split == 'held_out')
    (root / held.row.image_path).write_bytes(b'bad held-out bytes')
    reader.rewind()
    assert np.array_equal(first, reader.get_next()['rgb'])


def test_stress_suite_is_fixed_bounded_independent_and_varied():
    before, after = stress_inputs(), stress_inputs()
    assert len(before) == 14 and len({name for name, _ in before}) == 14
    for (name, tensor), (repeat_name, repeat_tensor) in zip(before, after):
        assert name == repeat_name and np.array_equal(tensor, repeat_tensor)
        assert tensor_input(tensor) is tensor
    assert not np.array_equal(before[0][1], before[2][1])
    assert any('4096x1' in name for name, _ in before)


def test_actual_float_export_runtime_and_interface_validation(tmp_path):
    torch.manual_seed(42)
    # An exactly small spatial reduction provides a known passing interface
    # fixture. The separate full training path keeps the average-pooling toy.
    backbone = nn.Sequential(nn.Conv2d(3, 4, 1, stride=224), nn.Flatten()).requires_grad_(False)
    model = Baseline(backbone, FeatureHead(torch.zeros(4), torch.ones(4))).eval()
    path = tmp_path / 'PLACEHOLDER-float.onnx'
    export_float(model, path)
    graph = graph_report(path)
    assert graph['size_pass'] and graph['operators']['Conv'] == 1
    assert graph['remaining_float_weight_operators'] == {'Conv': 1, 'Gemm': 1}
    assert not graph['int8_weight_qdq_operators']
    session = runtime(path)
    report, _, _ = compare(model, session, stress_inputs(), temperature=1., threshold=0., budget=FLOAT_BUDGET)
    assert report['status'] == 'PASS'
    assert 'failure_cases' not in aggregate_parity(report)
    modified = onnx.load(path)
    modified.graph.input[0].type.tensor_type.shape.dim[0].dim_value = 2
    onnx.save(modified, path)
    with pytest.raises(ValueError, match='interface mismatch'):
        runtime(path)


def test_real_runtime_rounding_drift_is_not_accepted(tmp_path):
    # A 224x224 reduction demonstrates why a successfully exported graph must
    # not be assumed to meet the strict numeric budgets. Retain this failing
    # fixture as a regression case, rather than increasing a tolerance.
    torch.manual_seed(42)
    model = Baseline(toy_backbone(), FeatureHead(torch.zeros(4), torch.ones(4))).eval()
    path = tmp_path / 'PLACEHOLDER-rounding.onnx'
    export_float(model, path)
    report, _, _ = compare(model, runtime(path), stress_inputs(), temperature=1., threshold=0., budget=FLOAT_BUDGET)
    assert report['status'] == 'FAIL'
    assert report['probability_budget_exceeded_count'] > 0
    assert report['failure_cases']
    assert report['frozen_threshold_flip_count'] == 0


def test_temporary_files_restore_even_on_error(tmp_path):
    previous = tempfile.tempdir
    with pytest.raises(RuntimeError):
        with local_temporaries(tmp_path):
            assert tempfile.gettempdir() == str(tmp_path.resolve())
            raise RuntimeError('test')
    assert tempfile.tempdir == previous


def test_frozen_export_evaluation_does_not_fit_and_suppresses_small_cells(prepared):
    _, index = prepared
    # deliberately large scores; frozen temperature/threshold remain supplied.
    logits = {c.id: 20 * (2*c.target - 1) for c in index.components}
    result = frozen_evaluation(index, logits, 19.15, 0.40079881738785716)
    assert result['temperature'] == 19.15
    assert result['threshold'] == 0.40079881738785716
    assert result['splits']['held_out']['primary']['sensitivity'] == 1
    assert result['splits']['held_out']['primary']['specificity'] == 1
    source = result['splits']['held_out']['by_source']['synthetic-source-c']
    assert source['below_minimum_cell'] and source['auc'] is None
    assert source['reliability_bins'] == []
    assert result['splits']['held_out']['by_synthetic_colour']


def test_complete_toy_training_export_int8_and_failed_parity_preserved():
    repo = repository_root()
    parent = repo / 'data/test-runs'
    parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=parent) as temporary:
        root = Path(temporary)
        prepared = root / 'prepared'
        prepare_run(prepared, groups_per_source=16)
        name = f'PLACEHOLDER-export-test-{root.name}'
        paths = [repo / 'ml/reports' / f'{name}{suffix}' for suffix in ('.json', '-MODEL-CARD.md')]
        try:
            train_run(repo, prepared, root / 'checkpoint', root / 'model', name=name,
                      config=TrainingConfig(epochs=3), bootstrap_replicates=100,
                      backbone_loader=lambda _: (toy_backbone().eval(), {'notice': 'PLACEHOLDER toy; no pretraining'}))
            output = root / 'PLACEHOLDER-export'
            report = export_run(repo, prepared, root / 'model', output, backbone_factory=toy_backbone)
            assert report['python_saved_verification']['status'] == 'PASS'
            assert report['artifacts']['int8']['graph']['int8_weight_qdq_operators'] == {'Conv': 1, 'Gemm': 1}
            assert report['artifacts']['float']['all_components_parity']['status'] == 'PASS'
            assert report['calibration']['split'] == 'train'
            assert report['artifacts']['int8']['frozen_evaluation']['fits'] == 'frozen M3 values; no refitting'
            assert json.loads((output / 'PLACEHOLDER-export-report.json').read_text()) == report
            detail = json.loads((output / 'PLACEHOLDER-parity-details.json').read_text())
            # Tracked-safe aggregates contain no per-component IDs/predictions/failures.
            assert 'failure_cases' not in json.dumps(report)
            assert 'failure_cases' in json.dumps(detail)
            statuses = [a[k]['status'] for a in report['artifacts'].values() for k in
                        ('all_components_parity', 'test_held_out_parity', 'stress_parity')]
            assert report['status'] == ('PASS' if all(s == 'PASS' for s in statuses) else 'FAIL')
            # Give this temporary run a unique report basename.
            renamed = root / f'PLACEHOLDER-export-{root.name}'
            output.rename(renamed)
            output = renamed
            summary_path = repo / 'ml/reports' / f'{output.name}.json'
            paths.append(summary_path)
            summary = summarise_run(repo, prepared, output, run=root / 'model')
            assert summary['reporting_revision']['version'] == '1.0.1'
            assert summary['status'] == report['status']
            assert summary['artifacts']['int8']['frozen_evaluation'] == report['artifacts']['int8']['frozen_evaluation']
            assert json.loads(summary_path.read_text()) == summary
            with pytest.raises(ValueError, match='summary target'):
                summarise_run(repo, prepared, output, run=root / 'model')
            detail_path = output / 'PLACEHOLDER-parity-details.json'
            tampered = json.loads(detail_path.read_text())
            tampered['artifacts']['int8']['onnx_logits'][0] += 1000
            detail_path.write_text(json.dumps(tampered))
            with pytest.raises(ValueError, match='parity summary mismatch'):
                summarise_run(repo, prepared, output, run=root / 'model')
            with pytest.raises(ValueError, match='new and named'):
                export_run(repo, prepared, root / 'model', output, backbone_factory=toy_backbone)
            with pytest.raises(ValueError, match='unknown'):
                export_run(repo, prepared, root / 'model', root / 'PLACEHOLDER-other', attempt='tuned')
            with pytest.raises(ValueError, match='ignored data'):
                export_run(repo, prepared, root / 'model', repo / 'ml/reports/PLACEHOLDER-unsafe')
        finally:
            for path in paths:
                path.unlink(missing_ok=True)
