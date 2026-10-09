"""Generated-only PLACEHOLDER runtime scope; never saved baseline inference."""

import numpy as np
import onnx
from onnx import helper, numpy_helper
import onnxruntime as ort
import pytest
import timm
import torch

from test_export_remaining_native import generated_pair
from numbra_ml.export_batchnorm import export_preserving_batchnorm
from numbra_ml.export_complete_replay import signed_accounting
from numbra_ml.export_promoted_bn import PREFIX, substitute_batchnorm
from numbra_ml.export_remaining_native import native_plan, same_bits
from numbra_ml.export_remaining_runtime import CompleteRuntime, audit_complete_runtime
from numbra_ml.export_rounded_bn import RECIPE
from numbra_ml.training import Baseline, FeatureHead, tensor_hash


@pytest.fixture
def runtime_pair(generated_pair, tmp_path):
    model, source, rounded, value = generated_pair
    plan = native_plan(model, source, rounded)
    result = {}
    for kind, graph in (('preserved', source), ('rounded', rounded)):
        output = tmp_path / f'PLACEHOLDER-{kind}-sessions'
        output.mkdir()
        result[kind] = CompleteRuntime(graph, plan, output)
    return result, value


def test_both_complete_runtime_graphs_audited_before_inputs_open(runtime_pair, monkeypatch):
    runtimes, value = runtime_pair
    # The static audit must reconstruct independently without sessions/decoding.
    def forbidden(*a, **kw):
        pytest.fail('runtime audit cannot perform inference or decode')
    monkeypatch.setattr(ort, 'InferenceSession', forbidden)
    monkeypatch.setattr('numbra_ml.dataset.load_rgb', forbidden)
    for runtime in runtimes.values():
        for kind, graph in (('original', runtime.source), ('tapped', runtime.tapped)):
            path = runtime.sessions[kind].get_session_options().optimized_model_filepath
            audit = audit_complete_runtime(graph, onnx.load(path))
            assert audit == runtime.audit[kind]
            assert audit['status'] == 'PASS'
            assert len(audit['expanded_hardswish_nodes']) == 3
            assert audit['lowered_constant_outputs'] == ['/head/Constant_output_0']
        result = runtime.run(value)
        assert result['instrumentation']['exact_bits']
        assert result['instrumentation']['max_absolute'] == 0
        assert same_bits(result['original_logit'], result['tapped_logit'])
        for r in runtime.plan['nodes']:
            assert all(n in result['values'] for n in (*r['inputs'], *r['outputs']))
        assert all(r['all_expressions_constants_boundaries'] for r in runtime.audit.values())


@pytest.mark.parametrize('kind', ['preserved', 'rounded'])
@pytest.mark.parametrize('change', ['weight', 'extra_constant', 'omit_constant', 'dtype_constant',
    'hardswish_alpha', 'hardswish_order', 'hardswish_gate', 'hardswish_extra_attribute',
    'reorder', 'omit', 'extra', 'conv_padding', 'custom_domain', 'head_transpose',
    'input_type', 'output_shape', 'opset', 'training_info'])
def test_whole_runtime_corruption_fails_closed(runtime_pair, kind, change):
    runtimes, _ = runtime_pair
    original = runtimes[kind].source
    path = runtimes[kind].sessions['original'].get_session_options().optimized_model_filepath
    actual = onnx.load(path)
    if change in ('weight', 'dtype_constant'):
        item = next(i for i in actual.graph.initializer if i.name == 'head.linear.weight')
        value = numpy_helper.to_array(item).copy()
        if change == 'weight':
            value.flat[0] += np.float32(0.125)
        else:
            value = value.astype(np.float64)
        item.CopyFrom(numpy_helper.from_array(value, item.name))
    elif change == 'extra_constant':
        actual.graph.initializer.append(numpy_helper.from_array(np.ones(1, np.float32), 'unexpected'))
    elif change == 'omit_constant':
        actual.graph.initializer.remove(actual.graph.initializer[0])
    elif change.startswith('hardswish_'):
        gate = next(n for n in actual.graph.node if n.op_type == 'HardSigmoid' and not n.name)
        mul = next(n for n in actual.graph.node if n.op_type == 'Mul' and gate.output[0] in n.input)
        if change == 'hardswish_alpha':
            next(a for a in gate.attribute if a.name == 'alpha').f = 0.2
        elif change == 'hardswish_order':
            mul.input.reverse()
        elif change == 'hardswish_gate':
            mul.input[1] = mul.input[0]
        else:
            gate.attribute.append(helper.make_attribute('unexpected', 1))
    elif change == 'reorder':
        actual.graph.node.reverse()
    elif change == 'omit':
        actual.graph.node.remove(next(n for n in actual.graph.node if n.op_type == 'Add'))
    elif change == 'extra':
        actual.graph.node.append(helper.make_node('Identity', ['rgb'], ['extra-output'], name='extra'))
    elif change == 'conv_padding':
        conv = next(n for n in actual.graph.node if n.op_type == 'Conv')
        next(a for a in conv.attribute if a.name == 'auto_pad').s = b'SAME_UPPER'
    elif change == 'custom_domain':
        actual.opset_import.append(helper.make_opsetid('custom', 1))
        next(n for n in actual.graph.node if n.op_type == 'Relu').domain = 'custom'
    elif change == 'head_transpose':
        node = next(n for n in actual.graph.node if n.op_type == 'Gemm')
        next(a for a in node.attribute if a.name == 'transA').i = 1
    elif change == 'input_type':
        actual.graph.input[0].type.tensor_type.elem_type = onnx.TensorProto.DOUBLE
    elif change == 'output_shape':
        actual.graph.output[0].type.tensor_type.shape.dim[0].dim_value = 2
    elif change == 'opset':
        next(o for o in actual.opset_import if not o.domain).version = 18
    else:
        actual.training_info.add()
    with pytest.raises((ValueError, onnx.checker.ValidationError, onnx.shape_inference.InferenceError)):
        audit_complete_runtime(original, actual)


@pytest.mark.parametrize('change', ['cast', 'coefficient', 'mul_order', 'output_cast'])
def test_rounded_runtime_audit_checks_every_internal_expression(runtime_pair, change):
    runtimes, _ = runtime_pair
    runtime = runtimes['rounded']
    path = runtime.sessions['original'].get_session_options().optimized_model_filepath
    actual = onnx.load(path)
    if change == 'coefficient':
        item = next(i for i in actual.graph.initializer if i.name.endswith('-alpha'))
        value = numpy_helper.to_array(item).copy()
        value.flat[0] += np.float32(0.125)
        item.CopyFrom(numpy_helper.from_array(value, item.name))
    elif change == 'mul_order':
        next(n for n in actual.graph.node if n.name.startswith(PREFIX) and n.op_type == 'Mul').input.reverse()
    else:
        dtype = onnx.TensorProto.DOUBLE if change == 'output_cast' else onnx.TensorProto.FLOAT
        cast = next(n for n in actual.graph.node if n.op_type == 'Cast'
                    and next(a for a in n.attribute if a.name == 'to').i != dtype)
        next(a for a in cast.attribute if a.name == 'to').i = dtype
    with pytest.raises((ValueError, onnx.checker.ValidationError, onnx.shape_inference.InferenceError)):
        audit_complete_runtime(runtime.source, actual)


def test_instrumentation_drift_is_retained(runtime_pair):
    runtimes, value = runtime_pair
    runtime = runtimes['preserved']
    original = runtime.sessions['original']
    class Drift:
        def run(self, *args):
            output, = original.run(*args)
            return [output + np.float32(0.25)]
    runtime.sessions['original'] = Drift()
    result = runtime.run(value)
    assert not result['instrumentation']['exact_bits']
    assert result['instrumentation']['signed_min'] == -0.25
    assert result['instrumentation']['max_absolute'] == 0.25


@pytest.mark.parametrize('change', ['dtype', 'shape', 'nonfinite'])
def test_invalid_inputs_fail_before_any_session_run(runtime_pair, change):
    runtimes, value = runtime_pair
    if change == 'dtype':
        value = value.astype(np.float64)
    elif change == 'shape':
        value = value[:, :, :1, :1]
    else:
        value.flat[0] = np.nan
    class Forbidden:
        def run(self, *a):
            pytest.fail('invalid input must fail before runtime inference')
    for runtime in runtimes.values():
        runtime.sessions = {k: Forbidden() for k in runtime.sessions}
        with pytest.raises(ValueError, match='input specification'):
            runtime.run(value)


@pytest.mark.parametrize('change', ['constant', 'axes', 'input', 'missing', 'nonfinite', 'dtype', 'shape'])
def test_invalid_taps_fail_closed(runtime_pair, change):
    runtimes, value = runtime_pair
    runtime = runtimes['preserved']
    session = runtime.sessions['tapped']
    class Corrupt:
        def run(self, *a):
            outputs = session.run(*a)
            names = [o.name for o in runtime.tapped.graph.output]
            if change == 'missing':
                return outputs[:-1]
            key = ('head.linear.weight' if change == 'constant' else '/head/Constant_output_0'
                   if change == 'axes' else 'rgb' if change == 'input' else 'raw_logit')
            index = names.index(key)
            if change in ('constant', 'axes', 'input'):
                outputs[index] = outputs[index].copy()
                outputs[index].flat[0] += 1
            elif change == 'nonfinite':
                outputs[index] = np.full_like(outputs[index], np.nan)
            elif change == 'dtype':
                outputs[index] = outputs[index].astype(np.float64)
            else:
                outputs[index] = outputs[index].reshape(1, 1)
            return outputs
    runtime.sessions['tapped'] = Corrupt()
    with pytest.raises(ValueError, match='complete runtime'):
        runtime.run(value)


def test_changed_static_plan_refused_before_session_creation(generated_pair, tmp_path, monkeypatch):
    model, source, rounded, _ = generated_pair
    plan = native_plan(model, source, rounded)
    plan['nodes'].pop()
    output = tmp_path / 'PLACEHOLDER-invalid'
    output.mkdir()
    monkeypatch.setattr(ort, 'InferenceSession', lambda *a, **kw: pytest.fail('partial plan must fail statically'))
    with pytest.raises(ValueError, match='complete tap'):
        CompleteRuntime(source, plan, output)
    assert not list(output.iterdir())


def test_complete_runtime_full_random_mobile_architecture_generated_only(tmp_path, monkeypatch):
    torch.manual_seed(233)
    torch.set_num_threads(2)
    backbone = timm.create_model('mobilenetv3_small_100.lamb_in1k', pretrained=False)
    backbone.reset_classifier(0)
    model = Baseline(backbone, FeatureHead(torch.zeros(1024), torch.ones(1024))).requires_grad_(False).eval()
    before = tensor_hash(model.state_dict())
    source_path, rounded_path = tmp_path / 'PLACEHOLDER-full.onnx', tmp_path / 'PLACEHOLDER-full-rounded.onnx'
    export_preserving_batchnorm(model, source_path)
    substitute_batchnorm(model, source_path, rounded_path, rounding_recipe=RECIPE)
    source, rounded = onnx.load(source_path), onnx.load(rounded_path)
    plan = native_plan(model, source, rounded)
    assert len(plan['nodes']) == 159
    monkeypatch.setattr('numbra_ml.dataset.load_rgb', lambda *a: pytest.fail('generated-only fixture cannot decode a dataset'))
    value = np.random.default_rng(233).normal(size=(1, 3, 224, 224)).astype(np.float32)
    for kind, graph in (('preserved', source), ('rounded', rounded)):
        output = tmp_path / f'PLACEHOLDER-full-{kind}-sessions'
        output.mkdir()
        runtime = CompleteRuntime(graph, plan, output)
        result = runtime.run(value)
        assert result['instrumentation']['exact_bits']
        assert len(result['values']) == 373
        for audit in runtime.audit.values():
            assert audit['status'] == 'PASS'
            assert len(audit['expanded_hardswish_nodes']) == plan['operator_counts']['HardSwish']
        for item in plan['nodes']:
            assert all(name in result['values'] for name in (*item['inputs'], *item['outputs']))
    assert tensor_hash(model.state_dict()) == before


def test_runtime_buffer_lifetime_and_returned_copies_are_stable(runtime_pair):
    runtimes, value = runtime_pair
    runtime = runtimes['preserved']
    first = runtime.run(value)
    snapshot = {k: v.copy() for k, v in first['values'].items()}
    runtime.run(-value)
    assert all(same_bits(first['values'][k], v) for k, v in snapshot.items())
    assert same_bits(value, first['values']['rgb'])
    assert not any(np.shares_memory(value, v) for v in first['values'].values())
    first['original_logit'][0] += 1
    assert same_bits(first['values']['raw_logit'], first['tapped_logit'])


@pytest.mark.parametrize('change', ['alias_operand', 'coefficient_signed_zero', 'extra_boundary', 'duplicate_attribute'])
def test_additional_exact_scope_corruptions_are_refused(runtime_pair, change):
    runtimes, _ = runtime_pair
    runtime = runtimes['preserved']
    actual = onnx.load(runtime.sessions['original'].get_session_options().optimized_model_filepath)
    if change == 'alias_operand':
        node = next(n for n in actual.graph.node if n.op_type == 'Identity')
        node.input[0] = 'backbone.0.bias'
    elif change == 'coefficient_signed_zero':
        item = next(i for i in actual.graph.initializer if i.name == 'backbone.1.bias')
        value = numpy_helper.to_array(item).copy()
        assert value.flat[0] == 0
        value.flat[0] = np.float32(-0.)
        item.CopyFrom(numpy_helper.from_array(value, item.name))
    elif change == 'extra_boundary':
        actual.graph.value_info.append(helper.make_tensor_value_info('unused_boundary', onnx.TensorProto.FLOAT, [1]))
    else:
        node = next(n for n in actual.graph.node if n.op_type == 'Gemm')
        node.attribute.append(helper.make_attribute('alpha', 1.))
    with pytest.raises((ValueError, onnx.checker.ValidationError, onnx.shape_inference.InferenceError)):
        audit_complete_runtime(runtime.source, actual)


def test_runtime_audit_preserves_identity_bits_when_independent_schedule_changes(runtime_pair):
    runtimes, _ = runtime_pair
    runtime = runtimes['preserved']
    actual = onnx.load(runtime.sessions['original'].get_session_options().optimized_model_filepath)
    # Every Identity in this fixture aliases an initializer; moving these to
    # the front changes scheduling only, while arithmetic and edges stay exact.
    nodes = list(actual.graph.node)
    reordered = [n for n in nodes if n.op_type == 'Identity'] + [n for n in nodes if n.op_type != 'Identity']
    assert [n.name for n in nodes] != [n.name for n in reordered]
    del actual.graph.node[:]
    actual.graph.node.extend(reordered)
    audit = audit_complete_runtime(runtime.source, actual)
    assert audit['status'] == 'PASS'
    assert audit['runtime_node_order'] != runtime.audit['original']['runtime_node_order']
    assert audit['runtime_sha256'] != runtime.audit['original']['runtime_sha256']


def test_generated_nondefault_bn_constants_are_pruned_only_without_consumers(generated_pair, tmp_path, monkeypatch):
    model, _, _, value = generated_pair
    # Distinct invented BN values expose the cleanup path hidden by default
    # random-model parameters, which export as equal-valued Identity aliases.
    with torch.no_grad():
        for index, module in enumerate(model.modules()):
            if isinstance(module, torch.nn.BatchNorm2d):
                offsets = torch.arange(module.num_features, dtype=torch.float32) / 100
                module.weight.copy_(1 + offsets + index / 100)
                module.bias.copy_(offsets + index / 100)
                module.running_mean.copy_(offsets - index / 100)
                module.running_var.copy_(2 + offsets + index / 100)
    source_path, rounded_path = tmp_path / 'PLACEHOLDER-distinct.onnx', tmp_path / 'PLACEHOLDER-distinct-rounded.onnx'
    export_preserving_batchnorm(model, source_path)
    substitute_batchnorm(model, source_path, rounded_path, rounding_recipe=RECIPE)
    source, rounded = onnx.load(source_path), onnx.load(rounded_path)
    plan = native_plan(model, source, rounded)
    output = tmp_path / 'PLACEHOLDER-distinct-runtime'
    output.mkdir()
    runtime = CompleteRuntime(rounded, plan, output)
    missing = set(runtime.audit['original']['removed_unused_initializers'])
    assert missing
    assert not runtime.audit['tapped']['removed_unused_initializers']
    assert missing <= {i.name for i in rounded.graph.initializer}
    assert not missing & {name for node in rounded.graph.node for name in node.input}
    assert not missing & {v.name for v in (*rounded.graph.input, *rounded.graph.output)}
    result = runtime.run(value)
    assert missing <= result['values'].keys()
    assert all(same_bits(result['values'][key], runtime.constants[key]) for key in missing)
    monkeypatch.setattr(ort, 'InferenceSession', lambda *a, **kw: pytest.fail('audit cannot create sessions'))
    monkeypatch.setattr(torch.nn.Module, '_call_impl', lambda *a, **kw: pytest.fail('audit cannot run native inference'))
    for kind, graph in (('original', runtime.source), ('tapped', runtime.tapped)):
        actual = onnx.load(output / f'PLACEHOLDER-{kind}-runtime.onnx')
        assert audit_complete_runtime(graph, actual) == runtime.audit[kind]


@pytest.mark.parametrize('change', ['retained_bits', 'retained_type', 'extra', 'live', 'alias', 'input', 'output', 'constant'])
def test_unused_initializer_rule_preserves_all_other_constant_checks(runtime_pair, change):
    runtimes, _ = runtime_pair
    runtime = runtimes['preserved']
    original = onnx.ModelProto()
    original.CopyFrom(runtime.source)
    actual = onnx.load(runtime.sessions['original'].get_session_options().optimized_model_filepath)
    orphan = numpy_helper.from_array(np.array([-0., 1.], np.float32), 'PLACEHOLDER-unused')
    original.graph.initializer.append(orphan)
    audit = audit_complete_runtime(original, actual)
    assert audit['removed_unused_initializers'] == ['PLACEHOLDER-unused']
    if change in ('retained_bits', 'retained_type'):
        array = np.array([0., 1.], np.float32) if change == 'retained_bits' else np.array([-0., 1.], np.float64)
        actual.graph.initializer.append(numpy_helper.from_array(array, orphan.name))
    elif change == 'extra':
        actual.graph.initializer.append(numpy_helper.from_array(np.array([1.], np.float32), 'PLACEHOLDER-extra'))
    elif change == 'live':
        actual.graph.initializer.remove(next(i for i in actual.graph.initializer if i.name == 'head.linear.weight'))
    elif change == 'alias':
        original.graph.node.insert(0, helper.make_node('Identity', [orphan.name], ['PLACEHOLDER-alias'], name='PLACEHOLDER-alias'))
        actual.graph.node.insert(0, original.graph.node[0])
    elif change == 'input':
        boundary = helper.make_tensor_value_info(orphan.name, onnx.TensorProto.FLOAT, [2])
        original.graph.input.append(boundary)
        actual.graph.input.append(boundary)
    elif change == 'output':
        boundary = helper.make_tensor_value_info(orphan.name, onnx.TensorProto.FLOAT, [2])
        original.graph.output.append(boundary)
        actual.graph.output.append(boundary)
    else:
        original.graph.node.append(helper.make_node('Constant', [], ['PLACEHOLDER-lowered'],
            name='PLACEHOLDER-constant', value=numpy_helper.from_array(np.array([1.], np.float32))))
    with pytest.raises((ValueError, onnx.checker.ValidationError, onnx.shape_inference.InferenceError)):
        audit_complete_runtime(original, actual)


@pytest.mark.parametrize('kind', ['missing_directory', 'occupied_directory'])
def test_runtime_refuses_overwrite_before_sessions(generated_pair, tmp_path, monkeypatch, kind):
    model, source, rounded, _ = generated_pair
    output = tmp_path / 'PLACEHOLDER-refuse-output'
    if kind == 'occupied_directory':
        output.mkdir()
        (output / 'retained.txt').write_text('retained')
    monkeypatch.setattr(ort, 'InferenceSession', lambda *a, **kw: pytest.fail('must not start a session'))
    with pytest.raises(ValueError, match='fresh empty directory'):
        CompleteRuntime(source, native_plan(model, source, rounded), output)
    if kind == 'occupied_directory':
        assert (output / 'retained.txt').read_text() == 'retained'


@pytest.mark.parametrize('shape', [(), (1,), (1, 2), (1, 2, 3, 4)])
def test_signed_accounting_retains_all_terms_at_head_and_feature_ranks(shape):
    values = [np.full(shape, x, np.float32) for x in (0., 1., 3., -1., 4.)]
    report = signed_accounting(*values)
    assert [v['signed_mean'] for v in report['terms'].values()] == [1., 2., -4., 5.]
    assert report['total']['signed_mean'] == 4.
    assert report['telescoping_max_residual'] == 0


@pytest.mark.parametrize('change', ['dtype', 'empty', 'nonfinite', 'shape', 'not_array'])
def test_signed_accounting_rejects_invalid_head_arrays(change):
    values = [np.ones((1,), np.float32) for _ in range(5)]
    if change == 'dtype':
        values[2] = values[2].astype(np.float64)
    elif change == 'empty':
        values[2] = np.empty((0,), np.float32)
    elif change == 'nonfinite':
        values[2][0] = np.inf
    elif change == 'shape':
        values[2] = values[2].reshape(1, 1)
    else:
        values[2] = [1.]
    with pytest.raises(ValueError, match='signed accounting'):
        signed_accounting(*values)
