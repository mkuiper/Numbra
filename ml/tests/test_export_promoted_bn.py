"""Generated PLACEHOLDER whole-graph arithmetic, audits and training isolation."""

import json
from pathlib import Path
import tempfile

import numpy as np
import onnx
import pytest
import torch
from torch import nn

from numbra_ml.evaluation import read_component_index
from numbra_ml.export import export_run, runtime, runtime_logit
from numbra_ml.export_batchnorm import batchnorm_run, export_preserving_batchnorm
from numbra_ml.export_precision import python_promoted_affine
from numbra_ml.export_promoted_bn import PREFIX, audit_promoted_graph, promoted_bn_run, substitute_batchnorm
from numbra_ml.prepare import prepare_run, repository_root
from numbra_ml.pretrained import sha256
from numbra_ml.train import train_run
from numbra_ml.training import TrainingConfig, tensor_hash
from test_export_replay import toy_backbone, toy_model


def test_complete_substitution_preserves_connections_parameters_and_activation(tmp_path):
    model = toy_model()
    # Integer centre-pixel convolutions avoid Conv accumulation drift, leaving
    # an independent Python sequence to check both BN and timm activations.
    with torch.no_grad():
        for module in model.modules():
            if isinstance(module, nn.Conv2d):
                module.weight.fill_(1)
                module.bias.zero_()
    before = tensor_hash(model.state_dict())
    source, target, optimized = [tmp_path / f'PLACEHOLDER-{tag}.onnx'
                                 for tag in ('source', 'promoted', 'runtime')]
    export_preserving_batchnorm(model, source)
    source_hash = sha256(source)
    records = substitute_batchnorm(model, source, target)
    assert [record['module'] for record in records] == ['backbone.1', 'backbone.3']
    session = runtime(target, optimisation='disabled', optimized_path=optimized)
    for path in (target, optimized):
        audit = audit_promoted_graph(path, source, records, serialized=(path == target))
        assert audit['promoted_expression_nodes'] == 12
        assert audit['replaced_batchnorm_nodes'] == 2
        assert audit['status'] == 'PASS'
        assert {item.key: item.value for item in onnx.load(path).metadata_props}['diagnostic_notice'].endswith('never bundle')
    for value in (-7., -2., 1., 9.):
        image = np.full((1, 3, 224, 224), value, np.float32)
        with torch.inference_mode():
            expected = model.backbone[0](torch.from_numpy(image)).numpy()
            for norm_index, conv_index in ((1, 2), (3, None)):
                expected = python_promoted_affine(model.backbone[norm_index], expected, 'affine_rsqrt')
                expected = model.backbone[norm_index].act(torch.from_numpy(expected)).numpy()
                if conv_index is not None:
                    expected = model.backbone[conv_index](torch.from_numpy(expected)).numpy()
            expected = float(model.head(torch.from_numpy(expected.reshape(1, 4)))[0])
        assert runtime_logit(session, image) == expected
    assert tensor_hash(model.state_dict()) == before
    assert sha256(source) == source_hash
    assert not any(module._forward_hooks or module._forward_pre_hooks for module in model.modules())


@pytest.mark.parametrize('corruption', ['coefficient', 'cast', 'missing-expression', 'conv'])
def test_actual_runtime_audit_rejects_corrupted_expressions_and_scope(tmp_path, corruption):
    model = toy_model()
    source, target = [tmp_path / f'PLACEHOLDER-{tag}.onnx' for tag in ('source', 'promoted')]
    export_preserving_batchnorm(model, source)
    records = substitute_batchnorm(model, source, target)
    graph = onnx.load(target)
    if corruption == 'coefficient':
        item = next(item for item in graph.graph.initializer if item.name == PREFIX + '0-alpha')
        array = onnx.numpy_helper.to_array(item).copy()
        array.flat[0] += 1
        item.CopyFrom(onnx.numpy_helper.from_array(array, item.name))
        message = 'coefficient audit'
    elif corruption == 'cast':
        node = next(node for node in graph.graph.node if node.name == PREFIX + '0-5')
        node.attribute[0].i = onnx.TensorProto.DOUBLE
        message = 'arithmetic/cast audit'
    elif corruption == 'missing-expression':
        node = next(node for node in graph.graph.node if node.name == PREFIX + '0-3')
        graph.graph.node.remove(node)
        message = 'arithmetic/cast audit'
    else:
        graph.graph.node.remove(next(node for node in graph.graph.node if node.op_type == 'Conv'))
        message = 'Conv/head operator count'
    onnx.save(graph, target)
    with pytest.raises(ValueError, match=message):
        audit_promoted_graph(target, source, records)


@pytest.mark.parametrize('corruption', ['epsilon', 'parameter', 'extra-bn', 'training', 'collision', 'nonfinite'])
def test_substitution_rejects_wrong_saved_state_and_unsupported_graph(tmp_path, corruption):
    model = toy_model()
    source, target = [tmp_path / f'PLACEHOLDER-{tag}.onnx' for tag in ('source', 'promoted')]
    export_preserving_batchnorm(model, source)
    graph = onnx.load(source)
    norm = next(node for node in graph.graph.node if node.op_type == 'BatchNormalization')
    if corruption == 'epsilon':
        next(attr for attr in norm.attribute if attr.name == 'epsilon').f = 0.1
        message = 'epsilon or parameter'
    elif corruption == 'parameter':
        item = next(item for item in graph.graph.initializer if item.name == norm.input[1])
        array = onnx.numpy_helper.to_array(item).copy()
        array.flat[0] += 1
        item.CopyFrom(onnx.numpy_helper.from_array(array, item.name))
        message = 'parameter mismatch'
    elif corruption == 'extra-bn':
        graph.graph.node.append(onnx.helper.make_node('BatchNormalization', list(norm.input), ['extra-output']))
        message = 'node count mismatch'
    elif corruption == 'training':
        model.backbone[1].train()
        message = 'every module in eval'
    elif corruption == 'collision':
        graph.graph.node[0].name = PREFIX + 'reserved'
        message = 'namespace collision'
    else:
        # Keep source/model parameter bits equal, but make coefficients undefined.
        with torch.no_grad():
            model.backbone[1].running_var.fill_(-1)
        item = next(item for item in graph.graph.initializer if item.name == norm.input[4])
        item.CopyFrom(onnx.numpy_helper.from_array(model.backbone[1].running_var.numpy(), item.name))
        message = 'non-finite'
    onnx.save(graph, source)
    with pytest.raises(ValueError, match=message):
        substitute_batchnorm(model, source, target)
    assert not target.exists()


@pytest.mark.parametrize('rounding_recipe', [None, 'e32-r32-a32-b64-o64'])
def test_complete_training_only_pipeline_and_rejection_before_inputs(rounding_recipe):
    repo = repository_root()
    parent = repo / 'data/test-runs'
    parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=parent) as temporary:
        root = Path(temporary)
        prepared, run = root / 'prepared', root / 'model'
        prepare_run(prepared, groups_per_source=16)
        name = f'PLACEHOLDER-promoted-bn-test-{root.name}'
        reports = [repo / 'ml/reports' / f'{name}{suffix}' for suffix in ('.json', '-MODEL-CARD.md')]
        try:
            train_run(repo, prepared, root / 'checkpoint', run, name=name,
                config=TrainingConfig(epochs=3), bootstrap_replicates=100,
                backbone_loader=lambda _: (toy_backbone(), {'notice': 'PLACEHOLDER toy; no pretraining'}))
            experiment, preserved = root / 'PLACEHOLDER-export', root / 'PLACEHOLDER-preserved'
            export_run(repo, prepared, run, experiment, backbone_factory=toy_backbone)
            batchnorm_run(repo, prepared, run, [experiment], preserved, backbone_factory=toy_backbone)
            inputs = list(run.iterdir()) + list(experiment.iterdir()) + list(preserved.rglob('*'))
            hashes = {path: sha256(path) for path in inputs if path.is_file()}
            index = read_component_index(prepared / 'manifest.jsonl', prepared / 'preparation-report.json')
            for component in index.components:
                if component.split != 'train':
                    (prepared / component.row.image_path).write_bytes(b'bad nontraining pixels')
            output = root / 'PLACEHOLDER-promoted-bn'
            result = promoted_bn_run(repo, prepared, run, [experiment], preserved, output,
                                     backbone_factory=toy_backbone, rounding_recipe=rounding_recipe)
            train_ids = [item.id for item in index.components if item.split == 'train']
            assert result['status'] == 'DIAGNOSTIC ONLY'
            assert result['protocol']['components'] == len(train_ids)
            assert result['protocol']['expected_batchnorm_substitutions'] == 2
            assert not any(result['protocol'][key] for key in
                           ('frozen_evaluation_inputs_used', 'quantisation_fit', 'deployment_selection'))
            assert result['model_state_before_sha256'] == result['model_state_after_sha256']
            detail_path = output / 'PLACEHOLDER-promoted-bn-details.json'
            details = json.loads(detail_path.read_text())
            assert sha256(detail_path) == result['diagnostic_details_sha256']
            for artifact, evidence in result['artifacts'].items():
                assert evidence['diagnostics']['original_graph_training_parity']['n'] == len(train_ids)
                assert details['artifacts'][artifact]['component_ids'] == train_ids
                assert evidence['diagnostics']['original_graph_training_parity']['status'] in ('PASS', 'FAIL')
                assert all(audit['status'] == 'PASS' for audit in evidence['runtime_audits'].values())
            for private in ('component_ids"', 'python_logits"', 'rows"', 'failure_cases"'):
                assert private not in json.dumps(result)
            assert {path: sha256(path) for path in hashes} == hashes
            assert json.loads((output / 'PLACEHOLDER-promoted-bn-report.json').read_text()) == result
            if rounding_recipe is not None:
                from copy import deepcopy
                from numbra_ml.export_rounded_bn import audit_rounded_report
                from numbra_ml.verify import load_reference
                model, saved = load_reference(run, backbone_factory=toy_backbone)
                source = preserved / 'PLACEHOLDER-preserved.onnx'
                assert result['coefficient_audit']['status'] == result['evidence_audit']['status'] == 'PASS'
                assert result['protocol']['decision'] == 'ADR-021'
                assert audit_rounded_report(output, result, model, source, index, saved) == result['evidence_audit']
                for corruption in ('budget', 'recipe', 'coefficient', 'scope', 'graph'):
                    bad = deepcopy(result)
                    if corruption == 'budget':
                        bad['artifacts']['complete_promoted_bn']['diagnostics']['original_graph_training_parity']['budget']['raw_absolute'] = 1.
                    elif corruption == 'recipe':
                        bad['protocol']['rounding_recipe'] = 'adaptive'
                    elif corruption == 'coefficient':
                        bad['substitutions'][0]['rounding']['epsilon_bits']['float64'] = 'bad'
                    elif corruption == 'scope':
                        del bad['artifacts']['preserved_control']
                    else:
                        bad['artifacts']['complete_promoted_bn']['graph']['sha256'] = 'bad'
                    with pytest.raises(ValueError):
                        audit_rounded_report(output, bad, model, source, index, saved)
                # A rehashed private row corruption still fails exact ordered scope.
                original_details = detail_path.read_text()
                details['artifacts']['complete_promoted_bn']['component_ids'].reverse()
                detail_path.write_text(json.dumps(details))
                bad = deepcopy(result)
                bad['diagnostic_details_sha256'] = sha256(detail_path)
                with pytest.raises(ValueError, match='ordered training'):
                    audit_rounded_report(output, bad, model, source, index, saved)
                detail_path.write_text(original_details)
            with pytest.raises(ValueError, match='new and named'):
                promoted_bn_run(repo, prepared, run, [experiment], preserved, output, backbone_factory=toy_backbone)
            with pytest.raises(ValueError, match='ignored data'):
                promoted_bn_run(repo, prepared, run, [experiment], preserved, repo / 'docs/unsafe', backbone_factory=toy_backbone)
            with pytest.raises(ValueError, match='retained export'):
                promoted_bn_run(repo, prepared, run, [], preserved, root / 'PLACEHOLDER-empty', backbone_factory=toy_backbone)
            report_path = preserved / 'PLACEHOLDER-batchnorm-report.json'
            text = report_path.read_text()
            stale = json.loads(text)
            stale['protocol']['temperature'] += 0.1
            report_path.write_text(json.dumps(stale))
            with pytest.raises(ValueError, match='provenance mismatch'):
                promoted_bn_run(repo, prepared, run, [experiment], preserved, root / 'PLACEHOLDER-stale', backbone_factory=toy_backbone)
            assert not (root / 'PLACEHOLDER-stale').exists()
            report_path.write_text(text)
            (preserved / 'PLACEHOLDER-batchnorm-details.json').write_text('{}')
            with pytest.raises(ValueError, match='checksum/report mismatch'):
                promoted_bn_run(repo, prepared, run, [experiment], preserved, root / 'PLACEHOLDER-bad-detail', backbone_factory=toy_backbone)
            assert not (root / 'PLACEHOLDER-bad-detail').exists()
        finally:
            for path in reports:
                path.unlink(missing_ok=True)
