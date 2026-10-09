"""Generated-only PLACEHOLDER integration; no selected saved M3 inference."""

import copy

import numpy as np
import onnx
import onnxruntime as ort
import pytest
import timm
import torch

from test_export_remaining_native import generated_pair, assert_clean
from numbra_ml.export_batchnorm import export_preserving_batchnorm
from numbra_ml.export_bn_rounding import RECIPES
from numbra_ml.export_promoted_bn import PREFIX, substitute_batchnorm
from numbra_ml.export_remaining_native import same_bits
from numbra_ml.export_remaining_replay import (CONTROL_KEYS, KINDS, ORIGINS,
    CompleteReplay, delta, ordered_feed, reconstruct_row)
from numbra_ml.export_rounded_bn import RECIPE
from numbra_ml.training import Baseline, FeatureHead, tensor_hash


@pytest.fixture
def engine(generated_pair, tmp_path):
    model, source, rounded, value = generated_pair
    output = tmp_path / 'PLACEHOLDER-replay'
    output.mkdir()
    return CompleteReplay(model, source, rounded, output), value


def test_setup_audits_all_expressions_before_forward_or_decode(generated_pair, tmp_path, monkeypatch):
    model, source, rounded, _ = generated_pair
    output = tmp_path / 'PLACEHOLDER-static'
    output.mkdir()
    def forbidden(*a, **kw):
        pytest.fail('setup cannot run model/operator inference or decode')
    monkeypatch.setattr(torch.nn.Module, '_call_impl', forbidden)
    monkeypatch.setattr(ort.InferenceSession, 'run', forbidden)
    monkeypatch.setattr('numbra_ml.dataset.load_rgb', forbidden)
    result = CompleteReplay(model, source, rounded, output)
    assert list(result.records['operators']) == [r['name'] for r in result.plan['nodes']]
    assert result.records['rounded_saved_binding']['all_saved_rounded_expressions_and_bits']
    assert set(result.records['whole_graphs']) == set(KINDS)
    for kind in KINDS:
        assert all(a['status'] == 'PASS' for a in result.records['whole_graphs'][kind].values())
    for r in result.plan['nodes']:
        graphs = result.records['operators'][r['name']]
        assert all(graphs[k]['audit']['status'] == 'PASS' for k in KINDS)
        if r['operator'] == 'BatchNormalization':
            assert len(graphs['controls']) == 5
            assert set(graphs['rounding_coefficients']['recipes']) == set(RECIPES)
            assert graphs['rounded']['serialized'] != graphs['preserved']['serialized']
    assert_clean(model)


def assert_complete(result, engine):
    assert list(result['operators']) == [r['name'] for r in engine.plan['nodes']]
    assert result['native_instrumentation']['exact_bits']
    for graph in result['graphs'].values():
        assert graph['instrumentation']['exact_bits']
    for r in engine.plan['nodes']:
        for kind, values in result['operators'][r['name']].items():
            assert kind in KINDS
            assert values['native_replay_fidelity']['exact_bits']
            assert values['signed_accounting']['telescoping_max_residual'] == 0
            assert set(values['signed_accounting']['terms']) == {'python_replay', 'propagation', 'kernel', 'extraction'}
            assert list(values['operand_drift']) == [str(i) for i in range(len(r['inputs']))]
            if r['operator'] in ('Conv', 'BatchNormalization'):
                assert set(values['controls']) == set(ORIGINS)
                expected = set(CONTROL_KEYS) if r['operator'] == 'BatchNormalization' else {'native_onnx'}
                assert all(set(v['vs_native']) == expected for v in values['controls'].values())
                if r['operator'] == 'BatchNormalization':
                    assert all(len(v['paired']) == 37 for v in values['controls'].values())
            else:
                assert values['controls'] == {}


def test_both_graphs_origins_complete_controls_and_head_accounting(engine, monkeypatch):
    replay, value = engine
    before, original = tensor_hash(replay.model.state_dict()), value.copy()
    monkeypatch.setattr('numbra_ml.dataset.load_rgb', lambda *a: pytest.fail('supplied tensors only'))
    result, evidence = replay.run(value)
    assert_complete(result, replay)
    assert same_bits(original, value)
    assert tensor_hash(replay.model.state_dict()) == before
    assert_clean(replay.model)
    # Every residual/SE operand participates; outputs of in-place operators are
    # retained separately from the actual pre-mutation inputs.
    assert any(r['operator'] == 'Add' for r in replay.plan['nodes'])
    for r in replay.plan['nodes']:
        if r['operator'] in ('Add', 'Mul'):
            assert len(evidence['operators'][r['name']]['native_operands']) == 2
        if r['operator'] == 'HardSwish':
            row = evidence['operators'][r['name']]
            assert not np.shares_memory(row['native_output'], row['native_operands'][0])
    # This fixed generated fixture retains the actual nonzero native/ORT
    # HardSwish kernel discrepancy; there is no tolerance-based suppression.
    assert any(v['local_kernel_native_input']['max_absolute'] > 0
        for r in replay.plan['nodes'] if r['operator'] == 'HardSwish'
        for v in result['operators'][r['name']].values())


def test_independent_reconstruction_needs_no_inference_decode_or_session(engine, monkeypatch):
    replay, value = engine
    result, evidence = replay.run(value)
    def forbidden(*a, **kw):
        pytest.fail('independent metric reconstruction cannot execute inference')
    monkeypatch.setattr(torch.nn.Module, '_call_impl', forbidden)
    monkeypatch.setattr(ort, 'InferenceSession', forbidden)
    monkeypatch.setattr('numbra_ml.dataset.load_rgb', forbidden)
    monkeypatch.setattr('numbra_ml.export_remaining_replay.recipe', forbidden)
    monkeypatch.setattr('numbra_ml.export_remaining_replay.python_operator', forbidden)
    assert reconstruct_row(replay.source, replay.plan, evidence) == result


@pytest.mark.parametrize('change', ['operator', 'order', 'graph', 'origin', 'control', 'rounding',
    'operand', 'shape', 'dtype', 'nonfinite', 'constant', 'axes', 'captured_logit', 'tapped_logit', 'extra_metric'])
def test_corrupted_partial_tensor_evidence_fails_closed(engine, change):
    replay, value = engine
    _, evidence = replay.run(value)
    operators = evidence['operators']
    name = next(r['name'] for r in replay.plan['nodes'] if r['operator'] == 'BatchNormalization')
    row = operators[name]
    data = row['graphs']['rounded']
    if change == 'operator':
        operators.pop(name)
    elif change == 'order':
        evidence['operators'] = dict(reversed(list(operators.items())))
    elif change == 'graph':
        row['graphs'].pop('rounded')
    elif change == 'origin':
        data['controls'].pop('runtime_input')
    elif change in ('control', 'rounding'):
        key = 'native_onnx' if change == 'control' else 'rounding_' + RECIPES[-1] + '_torch'
        data['controls']['runtime_input'].pop(key)
    elif change == 'operand':
        data['runtime_operands'][0] = data['runtime_operands'][0] + np.float32(1.)
    elif change == 'shape':
        data['eager_runtime'] = data['eager_runtime'].reshape(-1)
    elif change == 'dtype':
        data['isolated_native'] = data['isolated_native'].astype(np.float64)
    elif change == 'nonfinite':
        data['isolated_runtime'].flat[0] = np.nan
    elif change in ('constant', 'axes'):
        operator = 'Gemm' if change == 'constant' else 'Squeeze'
        r = next(r for r in replay.plan['nodes'] if r['operator'] == operator)
        operators[r['name']]['native_operands'][1] = operators[r['name']]['native_operands'][1].copy()
        operators[r['name']]['native_operands'][1].flat[0] += 1
    elif change == 'captured_logit':
        evidence['native_captured_logit'] = evidence['native_captured_logit'] + np.float32(1.)
    elif change == 'tapped_logit':
        evidence['graphs']['rounded']['tapped_logit'] = evidence['graphs']['rounded']['tapped_logit'] + np.float32(1.)
    else:
        data['unreported_metric'] = np.float32(0)
    with pytest.raises(ValueError, match='complete replay'):
        reconstruct_row(replay.source, replay.plan, evidence)


@pytest.mark.parametrize('change', ['input_dtype', 'input_shape', 'input_nan', 'state', 'mode', 'geometry', 'hook'])
def test_invalid_input_or_changed_model_fails_before_any_inference(engine, monkeypatch, change):
    replay, value = engine
    handle = None
    if change == 'input_dtype':
        value = value.astype(np.float64)
    elif change == 'input_shape':
        value = value[:, :, :2, :2]
    elif change == 'input_nan':
        value.flat[0] = np.nan
    elif change == 'state':
        replay.model.head.linear.bias.add_(1)
    elif change == 'mode':
        replay.model.train()
    elif change == 'geometry':
        replay.model.backbone[0].stride = (1, 1)
    else:
        handle = replay.model.register_forward_hook(lambda *a: None)
    def forbidden(*a, **kw):
        pytest.fail('invalid input/stale model must fail before inference')
    monkeypatch.setattr(torch.nn.Module, '_call_impl', forbidden)
    monkeypatch.setattr(ort.InferenceSession, 'run', forbidden)
    try:
        with pytest.raises(ValueError):
            replay.run(value)
    finally:
        if handle is not None:
            handle.remove()


def test_native_and_runtime_instrumentation_drift_is_unsuppressed(engine):
    replay, value = engine
    _, evidence = replay.run(value)
    evidence['native_original_logit'] += np.float32(0.25)
    evidence['graphs']['rounded']['original_logit'] += np.float32(0.5)
    report = reconstruct_row(replay.source, replay.plan, evidence)
    assert report['native_instrumentation']['signed_mean'] == -0.25
    assert report['graphs']['rounded']['instrumentation']['signed_mean'] == -0.5


def test_reconstruction_retains_nonzero_native_replay_term(engine):
    replay, value = engine
    _, evidence = replay.run(value)
    name = next(r['name'] for r in replay.plan['nodes'] if r['operator'] == 'Flatten')
    evidence['operators'][name]['eager_native'] += np.float32(0.125)
    report = reconstruct_row(replay.source, replay.plan, evidence)
    for values in report['operators'][name].values():
        assert values['signed_accounting']['terms']['python_replay']['signed_mean'] == 0.125
        assert values['signed_accounting']['telescoping_max_residual'] == 0


def test_full_random_mobile_replay_generated_only(tmp_path, monkeypatch):
    torch.manual_seed(234)
    torch.set_num_threads(2)
    backbone = timm.create_model('mobilenetv3_small_100.lamb_in1k', pretrained=False)
    backbone.reset_classifier(0)
    model = Baseline(backbone, FeatureHead(torch.zeros(1024), torch.ones(1024))).requires_grad_(False).eval()
    paths = [tmp_path / 'PLACEHOLDER-full.onnx', tmp_path / 'PLACEHOLDER-full-rounded.onnx']
    export_preserving_batchnorm(model, paths[0])
    substitute_batchnorm(model, paths[0], paths[1], rounding_recipe=RECIPE)
    source, rounded = [onnx.load(p) for p in paths]
    directory = tmp_path / 'PLACEHOLDER-full-replay'
    directory.mkdir()
    before = tensor_hash(model.state_dict())
    replay = CompleteReplay(model, source, rounded, directory)
    assert len(replay.plan['nodes']) == 159
    monkeypatch.setattr('numbra_ml.dataset.load_rgb', lambda *a: pytest.fail('generated-only fixture'))
    value = np.random.default_rng(234).normal(size=(1, 3, 224, 224)).astype(np.float32)
    result, evidence = replay.run(value)
    assert_complete(result, replay)
    assert sum(r['operator'] == 'BatchNormalization' for r in replay.plan['nodes']) == 34
    assert sum(r['operator'] == 'Conv' for r in replay.plan['nodes']) == 53
    monkeypatch.setattr(ort, 'InferenceSession', lambda *a, **kw: pytest.fail('audit cannot create sessions'))
    assert reconstruct_row(source, replay.plan, evidence) == result
    assert tensor_hash(model.state_dict()) == before
    assert_clean(model)


def test_ordered_feed_checks_repeated_operand_bits():
    node = onnx.helper.make_node('Mul', ['x', 'x'], ['y'])
    value = np.array([1], np.float32)
    assert len(ordered_feed(node, [value, value.copy()])) == 1
    with pytest.raises(ValueError, match='repeated operand bits'):
        ordered_feed(node, [value, -value])
    with pytest.raises(ValueError, match='operand count'):
        ordered_feed(node, [value])


@pytest.mark.parametrize('change', ['missing', 'occupied', 'unlabelled'])
def test_output_refused_before_sessions_or_model(generated_pair, tmp_path, monkeypatch, change):
    model, source, rounded, _ = generated_pair
    directory = tmp_path / ('unlabelled' if change == 'unlabelled' else 'PLACEHOLDER-refused')
    if change != 'missing':
        directory.mkdir()
    if change == 'occupied':
        (directory / 'retain.txt').write_text('retained')
    monkeypatch.setattr(ort, 'InferenceSession', lambda *a, **kw: pytest.fail('refuse before sessions'))
    with pytest.raises(ValueError, match='fresh empty PLACEHOLDER'):
        CompleteReplay(model, source, rounded, directory)


def test_signed_zero_drift_retains_bit_disagreement():
    result = delta(np.array([0.], np.float32), np.array([-0.], np.float32))
    assert result['max_absolute'] == 0
    assert result['exact_bits'] is False


def test_graph_or_plan_tampering_is_refused_without_inference(engine):
    replay, value = engine
    _, evidence = replay.run(value)
    plan = copy.deepcopy(replay.plan)
    plan['nodes'][0]['node_sha256'] = '0' * 64
    with pytest.raises(ValueError, match='graph/plan binding'):
        reconstruct_row(replay.source, plan, evidence)
    source = copy.deepcopy(replay.source)
    source.graph.node[0].name += '-changed'
    with pytest.raises(ValueError, match='graph/plan binding'):
        reconstruct_row(source, replay.plan, evidence)


@pytest.mark.parametrize('change', ['coefficient', 'signed_zero', 'expression', 'extra_constant'])
def test_corrupted_serialized_rounded_graph_refused_before_sessions(generated_pair, tmp_path, monkeypatch, change):
    model, source, rounded, _ = generated_pair
    if change in ('coefficient', 'signed_zero'):
        suffix = '-alpha' if change == 'coefficient' else '-beta'
        item = next(i for i in rounded.graph.initializer if i.name.endswith(suffix))
        value = onnx.numpy_helper.to_array(item).copy()
        if change == 'coefficient':
            value.flat[0] += np.float32(0.125)
        else:
            assert value.flat[0] == 0
            value.flat[0] = np.float32(-0.)
        item.CopyFrom(onnx.numpy_helper.from_array(value, item.name))
    elif change == 'expression':
        next(n for n in rounded.graph.node if n.name.startswith(PREFIX) and n.op_type == 'Mul').input.reverse()
    else:
        rounded.graph.initializer.append(onnx.numpy_helper.from_array(np.zeros(1, np.float32), 'unexpected'))
    directory = tmp_path / 'PLACEHOLDER-corrupt-rounded'
    directory.mkdir()
    monkeypatch.setattr(ort, 'InferenceSession', lambda *a, **kw: pytest.fail('must reject before sessions'))
    with pytest.raises(ValueError, match='complete replay rounded saved'):
        CompleteReplay(model, source, rounded, directory)
    assert not list(directory.iterdir())


@pytest.mark.parametrize('change', ['count', 'shape', 'dtype', 'nonfinite'])
def test_isolated_inputs_fail_before_kernel_inference(engine, monkeypatch, change):
    replay, _ = engine
    node = replay.nodes[replay.plan['nodes'][0]['name']]
    kernel = replay.kernels[node.name, 'preserved']
    operands = [np.zeros(kernel.specs[name]['shape'], dtype=kernel.specs[name]['dtype']) for name in kernel.inputs]
    if change == 'count':
        operands.pop()
    elif change == 'shape':
        operands[0] = operands[0].reshape(-1)
    elif change == 'dtype':
        operands[0] = operands[0].astype(np.float64)
    else:
        operands[0].flat[0] = np.inf
    monkeypatch.setattr(ort.InferenceSession, 'run', lambda *a: pytest.fail('must refuse invalid operand first'))
    with pytest.raises(ValueError):
        kernel.run(operands)


def test_failure_cleans_native_capture_hooks(engine, monkeypatch):
    replay, value = engine
    before = tensor_hash(replay.model.state_dict())
    monkeypatch.setattr(replay.runtimes['rounded'], 'run', lambda *a: (_ for _ in ()).throw(RuntimeError('injected failure')))
    with pytest.raises(RuntimeError, match='injected failure'):
        replay.run(value)
    assert_clean(replay.model)
    assert tensor_hash(replay.model.state_dict()) == before


def test_returned_evidence_survives_later_runs_and_input_changes(engine):
    replay, value = engine
    result, evidence = replay.run(value)
    snapshot = copy.deepcopy(evidence)
    replay.run(-value)
    value *= np.float32(-1)
    assert same_bits(evidence['input'], snapshot['input'])
    for name, row in evidence['operators'].items():
        assert same_bits(row['native_output'], snapshot['operators'][name]['native_output'])
        for kind in KINDS:
            assert same_bits(row['graphs'][kind]['runtime_output'], snapshot['operators'][name]['graphs'][kind]['runtime_output'])
    assert reconstruct_row(replay.source, replay.plan, evidence) == result
