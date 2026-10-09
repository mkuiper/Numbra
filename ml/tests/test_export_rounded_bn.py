"""PLACEHOLDER generated cancellation, runtime and saved-scope regressions."""

from copy import deepcopy
import json

import numpy as np
import onnx
import onnxruntime as ort
import pytest
import torch
from torch import nn

from numbra_ml.export import INPUT_NAME, session_options
from numbra_ml.export_batchnorm import export_preserving_batchnorm
from numbra_ml.export_bn_rounding import apply_recipe
from numbra_ml.export_promoted_bn import audit_promoted_graph, substitute_batchnorm
from numbra_ml.export_rounded_bn import RECIPE, audit_prior_control, audit_saved_coefficients, rounded_coefficients
from numbra_ml.pretrained import sha256
from numbra_ml.training import tensor_hash
from test_export_replay import toy_model


def test_declared_coefficients_keep_cancellation_rounding_and_state():
    bn = nn.BatchNorm2d(1, eps=1.).eval()
    with torch.no_grad():
        bn.weight.fill_(1 + 2**-23)
        bn.bias.fill_(1.)
        bn.running_mean.fill_(1 - 2**-23)
        bn.running_var.zero_()
    before = tensor_hash(bn.state_dict())
    constants, record = rounded_coefficients(bn)
    assert constants['alpha'].item() == 1 + 2**-23
    assert constants['beta'].item() == 2**-46
    assert record['engines']['numpy'] == record['engines']['torch']
    assert tensor_hash(bn.state_dict()) == before


def test_actual_runtime_bn_boundary_matches_independent_recipe(tmp_path):
    model = toy_model()
    with torch.no_grad():
        for module in model.modules():
            if isinstance(module, nn.Conv2d):
                module.weight.fill_(1.)
                module.bias.zero_()
    source, target, optimized = [tmp_path / f'PLACEHOLDER-{name}.onnx' for name in ('source', 'rounded', 'runtime')]
    before = tensor_hash(model.state_dict())
    export_preserving_batchnorm(model, source)
    records = substitute_batchnorm(model, source, target, rounding_recipe=RECIPE)
    assert audit_saved_coefficients(model, source, records)['layers'] == 2
    # Expose each replaced BN output directly on a copy; actual ORT coefficients
    # and double operations are checked, not just their metadata hashes.
    graph = onnx.load(target)
    for record in records:
        graph.graph.output.append(onnx.helper.make_tensor_value_info(record['output'], onnx.TensorProto.FLOAT, None))
    tapped = tmp_path / 'PLACEHOLDER-tapped.onnx'
    onnx.save(graph, tapped)
    options = session_options('disabled')
    options.optimized_model_filepath = str(optimized)
    session = ort.InferenceSession(str(tapped), sess_options=options, providers=['CPUExecutionProvider'])
    audit_promoted_graph(optimized, source, records)
    for value in (-7., -0., 1., 9.):
        x = np.full((1, 3, 224, 224), value, np.float32)
        outputs = session.run(None, {INPUT_NAME: x})
        graph_inputs = []
        hooks = [module.register_forward_pre_hook(lambda _, args: graph_inputs.append(args[0].detach().numpy().copy()))
                 for module in model.modules() if isinstance(module, nn.BatchNorm2d)]
        try:
            with torch.inference_mode():
                model(torch.from_numpy(x))
        finally:
            for hook in hooks:
                hook.remove()
        # Conv kernels here are centre pixels (no summation discrepancy).
        for record, bn_input, observed in zip(records, graph_inputs, outputs[1:]):
            module = dict(model.named_modules())[record['module']]
            constants, _ = rounded_coefficients(module)
            expected = apply_recipe(bn_input, RECIPE, constants, 'numpy')
            np.testing.assert_array_equal(observed, expected)
    assert tensor_hash(model.state_dict()) == before


@pytest.mark.parametrize('bad', ['order', 'missing', 'recipe', 'saved-bits', 'coefficient-bits'])
def test_saved_audit_rejects_scope_and_bit_corruption(tmp_path, bad):
    model = toy_model()
    source, target = [tmp_path / f'PLACEHOLDER-{name}.onnx' for name in ('source', 'rounded')]
    export_preserving_batchnorm(model, source)
    records = deepcopy(substitute_batchnorm(model, source, target, rounding_recipe=RECIPE))
    if bad == 'order':
        records.reverse()
    elif bad == 'missing':
        records.pop()
    elif bad == 'recipe':
        records[0]['rounding']['recipe'] = 'adaptive'
    elif bad == 'saved-bits':
        records[0]['rounding']['saved_parameters']['mean']['bits_sha256'] = 'bad'
    else:
        records[0]['coefficients_sha256']['beta'] = 'bad'
    with pytest.raises(ValueError, match='rounded BN'):
        audit_saved_coefficients(model, source, records)


def test_refuses_undeclared_recipe_before_writing_graph(tmp_path):
    with pytest.raises(ValueError, match='predeclared'):
        substitute_batchnorm(toy_model(), tmp_path / 'missing', tmp_path / 'target', rounding_recipe='adaptive')
    assert not (tmp_path / 'target').exists()


def test_independent_coefficient_bit_disagreement_is_rejected(monkeypatch):
    from numbra_ml import export_rounded_bn
    original = export_rounded_bn.coefficients
    def disagree(module, recipe, engine):
        values = original(module, recipe, engine)
        if engine == 'torch':
            values['beta'].flat[0] = np.nextafter(values['beta'].flat[0], np.float32(np.inf))
        return values
    monkeypatch.setattr(export_rounded_bn, 'coefficients', disagree)
    with pytest.raises(ValueError, match='independent coefficient bits disagree'):
        rounded_coefficients(nn.BatchNorm2d(1).eval())


@pytest.mark.parametrize('bad', [None, 'logit', 'order', 'provenance', 'detail-checksum'])
def test_prior_control_checks_exact_logits_order_provenance_and_detail_hash(tmp_path, bad):
    output, prior = tmp_path / 'PLACEHOLDER-output', tmp_path / 'PLACEHOLDER-prior'
    output.mkdir()
    prior.mkdir()
    current = {'component_ids': ['first', 'second'], 'python_logits': [1., 2.], 'original_onnx_logits': [1.01, 2.01]}
    previous = {'component_ids': current['component_ids'], 'rows': [
        {'python_logit': a, 'original_logit': b} for a, b in zip(current['python_logits'], current['original_onnx_logits'])]}
    (output / 'PLACEHOLDER-promoted-bn-details.json').write_text(json.dumps({'artifacts': {'preserved_control': current}}))
    previous_details = prior / 'PLACEHOLDER-bn-rounding-details.json'
    previous_details.write_text(json.dumps(previous))
    report = {key: 'identical' for key in ('saved_model_sha256', 'saved_run_sha256', 'manifest_sha256',
        'preparation_report_sha256', 'source_graph', 'source_report_sha256')}
    report['protocol'] = {'components': 2, 'component_ids_sha256': 'identical', 'temperature': 1., 'threshold': 0.5, 'split': 'train'}
    old = deepcopy(report)
    old['protocol']['decision'] = 'ADR-020'
    old['diagnostic_details_sha256'] = sha256(previous_details)
    if bad == 'provenance':
        old['saved_model_sha256'] = 'different'
    elif bad is not None:
        if bad == 'logit':
            previous['rows'][0]['original_logit'] += 1e-8
        else:
            previous['component_ids'].reverse()
        previous_details.write_text(json.dumps(previous))
        if bad != 'detail-checksum':
            old['diagnostic_details_sha256'] = sha256(previous_details)
    (prior / 'PLACEHOLDER-bn-rounding-report.json').write_text(json.dumps(old))
    if bad is None:
        assert audit_prior_control(output, report, prior)['status'] == 'PASS'
    else:
        with pytest.raises(ValueError, match='prior complete control'):
            audit_prior_control(output, report, prior)
