"""Generated PLACEHOLDER profile, constant folding and evidence regressions."""

from copy import deepcopy
import json
from pathlib import Path
import tempfile

import numpy as np
import onnx
import onnxruntime as ort
import pytest
import torch
from torch import nn

from numbra_ml.evaluation import read_component_index
from numbra_ml.export import INPUT_NAME, export_run, runtime, session_options
from numbra_ml.export_bn_rounding import apply_recipe
from numbra_ml.export_batchnorm import batchnorm_run, export_preserving_batchnorm
from numbra_ml.export_promoted_bn import PREFIX, promoted_bn_run, substitute_batchnorm
from numbra_ml.export_rounded_bn import RECIPE, rounded_coefficients
from numbra_ml.export_runtime_profiles import (ARTIFACTS, DETAILS, PROFILES, REPORT,
    audit_profile_report, audit_runtime_expression, profiles_run, runtime_audit)
from numbra_ml.prepare import prepare_run, repository_root
from numbra_ml.pretrained import sha256
from numbra_ml.train import train_run
from numbra_ml.training import TrainingConfig
from test_export_replay import toy_backbone, toy_model


@pytest.mark.parametrize('profile', PROFILES)
def test_actual_profile_coefficients_fold_without_changing_arithmetic(tmp_path, profile):
    model = toy_model()
    # Cancellation distinguishes exact float32->double promotion from recomputing
    # the beta subtraction at float32 or removing the output rounding boundary.
    with torch.no_grad():
        for module in model.modules():
            if isinstance(module, nn.Conv2d):
                module.weight.fill_(1.)
                module.bias.zero_()
        bn = model.backbone[1]
        bn.eps = 1.
        bn.weight.fill_(1 + 2**-23)
        bn.bias.fill_(1.)
        bn.running_mean.fill_(1 - 2**-23)
        bn.running_var.zero_()
    source, rounded, optimized = [tmp_path / f'PLACEHOLDER-{tag}.onnx' for tag in ('source', 'rounded', 'runtime')]
    export_preserving_batchnorm(model, source)
    records = substitute_batchnorm(model, source, rounded, rounding_recipe=RECIPE)
    runtime(rounded, optimisation=profile, optimized_path=optimized)
    audit = audit_runtime_expression(optimized, rounded, records)
    assert audit['status'] == 'PASS' and audit['layers'] == 2
    assert audit['constant_casts'] + audit['folded_double_coefficients'] == 4
    assert audit['constant_casts'] == (4 if profile == 'disabled' else 0)
    assert audit['folded_double_coefficients'] == (0 if profile == 'disabled' else 4)
    graph = onnx.load(rounded)
    for record in records:
        for boundary in ('input', 'output'):
            graph.graph.output.append(onnx.helper.make_tensor_value_info(record[boundary], onnx.TensorProto.FLOAT, None))
    tapped = tmp_path / 'PLACEHOLDER-boundaries.onnx'
    onnx.save(graph, tapped)
    options = session_options(profile)
    options.optimized_model_filepath = str(optimized)
    session = ort.InferenceSession(str(tapped), sess_options=options, providers=['CPUExecutionProvider'])
    audit_runtime_expression(optimized, rounded, records)
    for value in (-7., -0., 1., 9.):
        image = np.full((1, 3, 224, 224), value, np.float32)
        observed_boundaries = session.run(None, {INPUT_NAME: image})[1:]
        # Compare the independent recipe on each actual ORT input. Upstream
        # native hard-swish vs HardSigmoid/Mul rounding need not be identical.
        for record, inputs, observed in zip(records, observed_boundaries[::2], observed_boundaries[1::2]):
            constants, _ = rounded_coefficients(dict(model.named_modules())[record['module']])
            np.testing.assert_array_equal(observed, apply_recipe(inputs, RECIPE, constants, 'numpy'))


@pytest.mark.parametrize('bad', ['bits', 'dtype', 'cast', 'order', 'extra', 'missing', 'cycle'])
def test_semantic_corruption_is_rejected_and_failure_retained(tmp_path, bad):
    model = toy_model()
    source, rounded, optimized = [tmp_path / f'PLACEHOLDER-{tag}.onnx' for tag in ('source', 'rounded', 'runtime')]
    export_preserving_batchnorm(model, source)
    records = substitute_batchnorm(model, source, rounded, rounding_recipe=RECIPE)
    runtime(rounded, optimisation='basic', optimized_path=optimized)
    graph = onnx.load(optimized)
    if bad in ('bits', 'dtype'):
        mul = next(node for node in graph.graph.node if node.name == PREFIX + '0-3')
        value = next(item for item in graph.graph.initializer if item.name == mul.input[1])
        array = onnx.numpy_helper.to_array(value).copy()
        if bad == 'bits':
            array.flat[0] = np.nextafter(array.flat[0], np.inf)
        else:
            array = array.astype(np.float32)
        value.CopyFrom(onnx.numpy_helper.from_array(array, value.name))
    elif bad == 'cast':
        cast = next(node for node in graph.graph.node if node.name == PREFIX + '0-5')
        cast.attribute[0].i = onnx.TensorProto.DOUBLE
    elif bad == 'order':
        mul = next(node for node in graph.graph.node if node.name == PREFIX + '0-3')
        mul.input.reverse()
    elif bad == 'extra':
        graph.graph.node.append(onnx.helper.make_node('Identity', ['rgb'], ['unused'], name=PREFIX + 'extra'))
    elif bad == 'missing':
        records.pop()
    else:
        mul = next(node for node in graph.graph.node if node.name == PREFIX + '0-3')
        mul.input[1] = 'cycle-a'
        graph.graph.node.extend([
            onnx.helper.make_node('Identity', ['cycle-b'], ['cycle-a']),
            onnx.helper.make_node('Identity', ['cycle-a'], ['cycle-b'])])
    onnx.save(graph, optimized)
    with pytest.raises(ValueError, match='runtime expression'):
        audit_runtime_expression(optimized, rounded, records)
    failed = runtime_audit(optimized, rounded, records, True)
    assert failed['status'] == 'FAIL' and failed['notice'].startswith('PLACEHOLDER')


@pytest.fixture(scope='module')
def profile_evidence():
    repo = repository_root()
    parent = repo / 'data/test-runs'
    parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=parent) as temporary:
        root = Path(temporary)
        prepared, run = root / 'prepared', root / 'model'
        prepare_run(prepared, groups_per_source=16)
        name = f'PLACEHOLDER-profiles-test-{root.name}'
        reports = [repo / 'ml/reports' / f'{name}{suffix}' for suffix in ('.json', '-MODEL-CARD.md')]
        try:
            train_run(repo, prepared, root / 'checkpoint', run, name=name,
                config=TrainingConfig(epochs=3), bootstrap_replicates=100,
                backbone_loader=lambda _: (toy_backbone(), {'notice': 'PLACEHOLDER toy; no pretraining'}))
            experiment, source, prior = [root / f'PLACEHOLDER-{tag}' for tag in ('export', 'preserved', 'rounded')]
            export_run(repo, prepared, run, experiment, backbone_factory=toy_backbone)
            batchnorm_run(repo, prepared, run, [experiment], source, backbone_factory=toy_backbone)
            promoted_bn_run(repo, prepared, run, [experiment], source, prior,
                            backbone_factory=toy_backbone, rounding_recipe=RECIPE)
            index = read_component_index(prepared / 'manifest.jsonl', prepared / 'preparation-report.json')
            for item in index.components:
                if item.split != 'train':
                    (prepared / item.row.image_path).write_bytes(b'invalid frozen image')
            paths = [path for directory in (run, experiment, source, prior) for path in directory.rglob('*') if path.is_file()]
            hashes = {path: sha256(path) for path in paths}
            output = root / 'PLACEHOLDER-profiles'
            result = profiles_run(repo, prepared, run, [experiment], source, prior, output, backbone_factory=toy_backbone)
            assert {path: sha256(path) for path in paths} == hashes
            yield repo, prepared, run, [experiment], source, prior, output, result, index
        finally:
            for path in reports:
                path.unlink(missing_ok=True)


def test_complete_pipeline_is_training_only_and_retains_every_profile(profile_evidence):
    repo, prepared, run, experiments, source, prior, output, result, index = profile_evidence
    assert result['status'] == 'DIAGNOSTIC ONLY'
    assert result['evidence_audit']['status'] == 'PASS'
    assert result['model_state_before_sha256'] == result['model_state_after_sha256']
    assert result['protocol']['profiles'] == list(PROFILES)
    assert not any(result['protocol'][key] for key in ('frozen_evaluation_inputs_used', 'quantisation_fit', 'deployment_selection'))
    details = json.loads((output / DETAILS).read_text())
    ids = [item.id for item in index.components if item.split == 'train']
    for name in ARTIFACTS:
        assert set(result['artifacts'][name]['profiles']) == set(PROFILES)
        for profile in PROFILES:
            assert details['artifacts'][name][profile]['component_ids'] == ids
            assert result['artifacts'][name]['profiles'][profile]['diagnostics']['original_graph_training_parity']['n'] == len(ids)
    for private in ('component_ids"', 'python_logits"', 'rows"', 'failure_cases"'):
        assert private not in json.dumps(result)
    assert json.loads((output / REPORT).read_text()) == result
    assert audit_profile_report(repo, output, result, prepared, run, experiments, source, prior,
        backbone_factory=toy_backbone) == result['evidence_audit']
    with pytest.raises(ValueError, match='new and named'):
        profiles_run(repo, prepared, run, experiments, source, prior, output, backbone_factory=toy_backbone)
    with pytest.raises(ValueError, match='ignored data'):
        profiles_run(repo, prepared, run, experiments, source, prior, repo / 'docs/unsafe', backbone_factory=toy_backbone)


@pytest.mark.parametrize('bad', ['profile', 'fit', 'budget', 'semantics', 'runtime-graph', 'provenance', 'code'])
def test_report_audit_rejects_scope_fit_and_aggregate_corruption(profile_evidence, bad):
    repo, prepared, run, experiments, source, prior, output, result, _ = profile_evidence
    changed = deepcopy(result)
    values = changed['artifacts']['complete_promoted_bn']['profiles']['basic']
    if bad == 'profile':
        del changed['artifacts']['preserved_control']['profiles']['all']
    elif bad == 'fit':
        changed['protocol']['threshold'] += 0.1
    elif bad == 'budget':
        values['diagnostics']['original_graph_training_parity']['budget']['raw_absolute'] = 1.
    elif bad == 'semantics':
        values['runtime_audits']['original']['status'] = 'invented'
    elif bad == 'runtime-graph':
        values['diagnostics']['runtime_graphs']['original']['sha256'] = 'bad'
    elif bad == 'provenance':
        changed['prior_provenance']['prior_details_sha256'] = 'bad'
    else:
        changed['environment']['source_tree_sha256'] = 'bad'
    with pytest.raises(ValueError, match='runtime profiles'):
        audit_profile_report(repo, output, changed, prepared, run, experiments, source, prior, backbone_factory=toy_backbone)


@pytest.mark.parametrize('bad', ['order', 'python', 'onnx', 'feature', 'tap', 'detail-checksum'])
def test_rehashed_detail_corruption_cannot_hide_failure(profile_evidence, bad):
    repo, prepared, run, experiments, source, prior, output, result, _ = profile_evidence
    path = output / DETAILS
    original = path.read_text()
    details, changed = json.loads(original), deepcopy(result)
    row = details['artifacts']['complete_promoted_bn']['basic']
    if bad == 'order':
        row['component_ids'].reverse()
    elif bad == 'python':
        row['python_logits'][0] += 1e-5
    elif bad == 'onnx':
        row['original_onnx_logits'][0] += 1e-5
    elif bad == 'feature':
        row['feature_attribution'][0]['max_feature_absolute_error'] += 1.
    else:
        row['instrumented_onnx_logits'][0] += 1.
    try:
        path.write_text(json.dumps(details))
        if bad != 'detail-checksum':
            changed['diagnostic_details_sha256'] = sha256(path)
        with pytest.raises(ValueError, match='runtime profiles'):
            audit_profile_report(repo, output, changed, prepared, run, experiments, source, prior, backbone_factory=toy_backbone)
    finally:
        path.write_text(original)


@pytest.mark.parametrize('bad', ['fit', 'details', 'graph', 'empty-experiments'])
def test_prior_failures_are_rejected_before_training_inputs(profile_evidence, monkeypatch, bad):
    from numbra_ml import export_runtime_profiles
    repo, prepared, run, experiments, source, prior, output, _, _ = profile_evidence
    target = output.parent / ('PLACEHOLDER-refused-' + bad)
    def unexpected_input(*_):
        raise AssertionError('must reject stale prior evidence before opening an input')
    monkeypatch.setattr(export_runtime_profiles, 'component_input', unexpected_input)
    path = prior / 'PLACEHOLDER-promoted-bn-report.json'
    original = path.read_text()
    changed = json.loads(original)
    if bad == 'fit':
        changed['protocol']['temperature'] += 0.1
    elif bad == 'details':
        changed['diagnostic_details_sha256'] = 'bad'
    elif bad == 'graph':
        changed['artifacts']['complete_promoted_bn']['graph']['sha256'] = 'bad'
    else:
        experiments = []
    try:
        path.write_text(json.dumps(changed))
        with pytest.raises(ValueError):
            profiles_run(repo, prepared, run, experiments, source, prior, target, backbone_factory=toy_backbone)
        assert not target.exists()
    finally:
        path.write_text(original)
