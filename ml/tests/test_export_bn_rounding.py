"""Generated-only PLACEHOLDER rounding boundaries, scope and pipeline tests."""

from copy import deepcopy
import json
from pathlib import Path
import tempfile

import numpy as np
import pytest
import torch
from torch import nn

from numbra_ml.evaluation import read_component_index
from numbra_ml.export import export_run, stress_inputs
from numbra_ml.export_batchnorm import batchnorm_run, export_preserving_batchnorm
from numbra_ml.export_bn_rounding import (RECIPES, apply_recipe, audit_rounding_coefficients,
    coefficient_cache, coefficients, rounding_differences)
from numbra_ml.export_complete_replay import audit_complete_report
from numbra_ml.export_replay import replay_diagnostics, replay_run
from numbra_ml.prepare import prepare_run, repository_root
from numbra_ml.pretrained import sha256
from numbra_ml.train import train_run
from numbra_ml.training import TrainingConfig, tensor_hash
from test_export_complete_replay import complete_backbone, complete_model


def test_rounding_preserves_declared_cartesian_scope_and_explicit_boundaries():
    assert len(RECIPES) == len(set(RECIPES)) == 32
    bn = nn.BatchNorm2d(1, eps=1e-5).eval()
    before = tensor_hash(bn.state_dict())
    e32 = coefficients(bn, 'e32-r64-a64-b64-o64', 'numpy')
    e64 = coefficients(bn, 'e64-r64-a64-b64-o64', 'numpy')
    assert e32['denominator'].dtype == np.float32
    assert e64['denominator'].dtype == np.float64
    assert float(e32['denominator'].item()) != float(e64['denominator'].item())
    # Cancellation distinguishes an intermediate float32 product from the
    # declared rounded-double affine diagnostic, without a tolerance assertion.
    x = np.full((1, 1, 1, 1), 1 - 2**-23, np.float32)
    constants = {'alpha': np.full_like(x, 1 + 2**-23), 'beta': np.full_like(x, -1)}
    for engine in ('numpy', 'torch'):
        sequential = apply_recipe(x, 'e32-r32-a32-b32-o32', constants, engine)
        promoted = apply_recipe(x, 'e32-r32-a32-b32-o64', constants, engine)
        assert sequential.item() == 0
        assert promoted.item() == -2**-46
    with torch.no_grad():
        bn.weight.fill_(1 + 2**-23)
        bn.running_mean.fill_(1 - 2**-23)
        bn.bias.fill_(1)
        bn.running_var.fill_(0)
    bn.eps = 1.
    for engine in ('numpy', 'torch'):
        assert coefficients(bn, 'e32-r32-a32-b32-o32', engine)['beta'].item() == 0
        assert coefficients(bn, 'e32-r32-a32-b64-o32', engine)['beta'].item() == 2**-46
    assert before != tensor_hash(bn.state_dict())  # only explicit fixture edits


@pytest.mark.parametrize('recipe', RECIPES)
def test_independent_engines_and_finite_signed_parameter_fixture(recipe):
    bn = nn.BatchNorm2d(4, eps=0.03125).eval()
    with torch.no_grad():
        bn.weight.copy_(torch.tensor([-2., -0., 1.25, 4.]))
        bn.bias.copy_(torch.tensor([-0., 0.5, -1., 2.]))
        bn.running_mean.copy_(torch.tensor([0., -0., 0.75, -2.]))
        # After epsilon, exact square denominators avoid an unjustified
        # cross-library equality assumption for irrational square roots.
        bn.running_var.copy_(torch.tensor([0.21875, 0.96875, 3.96875, 15.96875]))
    before = tensor_hash(bn.state_dict())
    a, b = [coefficients(bn, recipe, engine) for engine in ('numpy', 'torch')]
    assert a['alpha'].dtype == a['beta'].dtype == np.float32
    # Independent scalar engines agree on this explicit fixture. Deployment
    # diagnostics still record disagreements on all inputs rather than assuming it.
    for key in a:
        np.testing.assert_array_equal(a[key], b[key])
    x = np.linspace(-4, 4, 48, dtype=np.float32).reshape(1, 4, 3, 4)
    np.testing.assert_array_equal(apply_recipe(x, recipe, a, 'numpy'), apply_recipe(x, recipe, b, 'torch'))
    assert tensor_hash(bn.state_dict()) == before


def test_irrational_reciprocal_engine_difference_is_retained_in_bit_records():
    from numbra_ml.export_bn_rounding import coefficient_records
    bn = nn.BatchNorm2d(4, eps=0.03125).eval()
    with torch.no_grad():
        bn.running_var.copy_(torch.tensor([0., 1., 4., 16.]))
    recipe = 'e32-r64-a32-b32-o32'
    cache = coefficient_cache(bn)
    first, second = [cache[recipe][engine]['reciprocal'] for engine in ('numpy', 'torch')]
    assert np.abs(first - second).max() == 2**-54
    records = coefficient_records(bn, cache)['recipes'][recipe]
    assert records['numpy']['reciprocal']['bits_sha256'] != records['torch']['reciprocal']['bits_sha256']


@pytest.mark.parametrize('bad', ['training', 'nonfinite', 'dtype', 'negative_var', 'epsilon'])
def test_rounding_refuses_invalid_reference(bad):
    bn = nn.BatchNorm2d(2).eval()
    if bad == 'training':
        bn.train()
    elif bad == 'dtype':
        bn.double()
    elif bad == 'epsilon':
        bn.eps = float('nan')
    else:
        with torch.no_grad():
            bn.running_var[0] = -1 if bad == 'negative_var' else float('inf')
    with pytest.raises(ValueError, match='rounding requires'):
        coefficient_cache(bn)


def test_rounding_refuses_unknown_recipe_and_invalid_input():
    bn = nn.BatchNorm2d(2).eval()
    with pytest.raises(ValueError, match='unknown declared'):
        coefficients(bn, 'selected-after-errors', 'torch')
    with pytest.raises(ValueError, match='unknown declared'):
        coefficients(bn, RECIPES[0], 'other')
    constants = coefficients(bn, RECIPES[0], 'numpy')
    with pytest.raises(ValueError, match='channel mismatch'):
        apply_recipe(np.ones((1, 3, 2, 2), np.float32), RECIPES[0], constants, 'numpy')
    with pytest.raises(ValueError, match='finite float32'):
        apply_recipe(np.ones((1, 2, 2, 2), np.float64), RECIPES[0], constants, 'numpy')


def test_rounding_all_origins_no_activation_aliasing_or_state_change(tmp_path):
    model = complete_model()
    before = tensor_hash(model.state_dict())
    source = tmp_path / 'PLACEHOLDER-source.onnx'
    export_preserving_batchnorm(model, source)
    summary, details = replay_diagnostics(model, source, tmp_path, stress_inputs()[:2],
                                          complete=True, promoted=True, rounding=True)
    assert summary['instrumentation_absolute_logit_change']['max'] == 0
    for name, graph in summary['operator_graphs'].items():
        errors = summary['operators'][name]
        assert errors['python_replay_fidelity']['max_absolute_error']['max'] == 0
        if graph['original_operator'] == 'BatchNormalization':
            assert set(errors['rounding']) == {'python_input', 'onnx_input'}
            assert len(graph['rounding_coefficients']['recipes']) == 32
            for origin in errors['rounding'].values():
                assert set(origin) == set(RECIPES)
                for result in origin.values():
                    assert set(result) == {'numpy_vs_native', 'torch_vs_native', 'numpy_vs_torch'}
        else:
            assert 'rounding' not in errors and 'rounding_coefficients' not in graph
    assert len(details['rows']) == 2
    assert tensor_hash(model.state_dict()) == before
    assert not any(module._forward_hooks or module._forward_pre_hooks for module in model.modules())
    def broken():
        raise RuntimeError('rounding failure')
        yield
    with pytest.raises(RuntimeError, match='rounding failure'):
        replay_diagnostics(model, source, tmp_path, broken(), complete=True, promoted=True, rounding=True)
    assert not any(module._forward_hooks or module._forward_pre_hooks for module in model.modules())
    with pytest.raises(ValueError, match='complete promoted control'):
        replay_diagnostics(model, source, tmp_path, [], rounding=True)


def test_rounding_pipeline_training_isolation_provenance_and_audit_refusals():
    repo = repository_root()
    parent = repo / 'data/test-runs'
    parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=parent) as temporary:
        root = Path(temporary)
        prepared, run = root / 'prepared', root / 'model'
        prepare_run(prepared, groups_per_source=16)
        name = f'PLACEHOLDER-rounding-test-{root.name}'
        reports = [repo / 'ml/reports' / f'{name}{suffix}' for suffix in ('.json', '-MODEL-CARD.md')]
        try:
            train_run(repo, prepared, root / 'checkpoint', run, name=name,
                      config=TrainingConfig(epochs=3), bootstrap_replicates=100,
                      backbone_loader=lambda _: (complete_backbone(), {'notice': 'PLACEHOLDER toy; no pretraining'}))
            experiment, source = root / 'PLACEHOLDER-export', root / 'PLACEHOLDER-source'
            export_run(repo, prepared, run, experiment, backbone_factory=complete_backbone)
            batchnorm_run(repo, prepared, run, [experiment], source, backbone_factory=complete_backbone)
            retained = {path: sha256(path) for folder in (run, experiment, source)
                        for path in folder.rglob('*') if path.is_file()}
            index = read_component_index(prepared / 'manifest.jsonl', prepared / 'preparation-report.json')
            for component in index.components:
                if component.split != 'train':
                    (prepared / component.row.image_path).write_bytes(b'frozen images must not be opened')
            output = root / 'PLACEHOLDER-rounding'
            result = replay_run(repo, prepared, run, [experiment], source, output,
                                backbone_factory=complete_backbone, complete=True, promoted=True, rounding=True)
            assert result['protocol']['decision'] == 'ADR-020'
            assert result['coefficient_audit']['layers'] == 3
            assert result['coefficient_audit']['recipes_per_layer'] == 32
            assert result['evidence_audit']['graph_records_checked'] == 47
            assert result['model_state_before_sha256'] == result['model_state_after_sha256']
            assert not any(result['protocol'][key] for key in
                           ('frozen_evaluation_inputs_used', 'quantisation_fit', 'deployment_selection'))
            details_path = output / 'PLACEHOLDER-bn-rounding-details.json'
            details = json.loads(details_path.read_text())
            assert details['component_ids'] == [item.id for item in index.components if item.split == 'train']
            assert {path: sha256(path) for path in retained} == retained
            assert json.loads((output / 'PLACEHOLDER-bn-rounding-report.json').read_text()) == result
            from numbra_ml.verify import load_reference
            model, _ = load_reference(run, backbone_factory=complete_backbone)
            assert audit_rounding_coefficients(model, result)['status'] == 'PASS'
            serialized = json.loads(json.dumps(result, sort_keys=True))
            # Dictionary insertion order is not saved module order. Only the
            # explicit selection sequence carries that contract.
            serialized['diagnostics']['operator_graphs'] = dict(reversed(
                list(serialized['diagnostics']['operator_graphs'].items())))
            assert audit_rounding_coefficients(model, serialized)['status'] == 'PASS'
            serialized['diagnostics']['selection'].reverse()
            with pytest.raises(ValueError, match='complete saved BN scope'):
                audit_rounding_coefficients(model, serialized)
            assert audit_complete_report(repo, output, result)['status'] == 'PASS'
            changed = deepcopy(result)
            changed['protocol']['rounding_recipes'].pop()
            with pytest.raises(ValueError, match='recipe/engine scope'):
                audit_complete_report(repo, output, changed)
            changed = deepcopy(result)
            changed['diagnostics']['operator_graphs']['backbone.1']['rounding_coefficients']['recipes'][RECIPES[0]]['numpy']['alpha']['bits_sha256'] = '0' * 64
            with pytest.raises(ValueError, match='coefficient bits'):
                audit_rounding_coefficients(model, changed)
            changed = deepcopy(result)
            changed['diagnostics']['operator_graphs']['backbone.3']['rounding_coefficients']['epsilon_bits']['float64'] = '0' * 16
            with pytest.raises(ValueError, match='coefficient bits'):
                audit_rounding_coefficients(model, changed)
            changed = deepcopy(result)
            del changed['diagnostics']['operator_graphs']['backbone.5']
            with pytest.raises(ValueError, match='complete saved BN scope'):
                audit_rounding_coefficients(model, changed)
            changed = deepcopy(result)
            changed['diagnostics']['operators']['backbone.1']['rounding']['python_input'][RECIPES[0]]['torch_vs_native']['max_absolute_error']['max'] += 1
            with pytest.raises(ValueError, match='aggregate reconstruction'):
                audit_complete_report(repo, output, changed)
            # Self-consistent omission must fail the recipe scope check too.
            for row in details['rows']:
                del row['operators']['backbone.1']['rounding']['onnx_input'][RECIPES[0]]
            details_path.write_text(json.dumps(details))
            from numbra_ml.export_replay import aggregate_values
            changed = deepcopy(result)
            changed['diagnostic_details_sha256'] = sha256(details_path)
            changed['diagnostics']['operators'] = aggregate_values([row['operators'] for row in details['rows']], complete=True)
            with pytest.raises(ValueError, match='origin/recipe/metric scope'):
                audit_complete_report(repo, output, changed)
            with pytest.raises(ValueError, match='new and named'):
                replay_run(repo, prepared, run, [experiment], source, output,
                           backbone_factory=complete_backbone, complete=True, promoted=True, rounding=True)
        finally:
            for path in reports:
                path.unlink(missing_ok=True)
