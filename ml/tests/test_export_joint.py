"""Generated PLACEHOLDER joint propagation, graph corruption and input isolation."""

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
from numbra_ml.export_joint import PREFIX, audit_stem_graph, substitute_stem
from numbra_ml.export_precision import python_promoted_affine, python_promoted_conv
from numbra_ml.export_promoted_bn import audit_promoted_graph, promoted_bn_run, substitute_batchnorm
from numbra_ml.prepare import prepare_run, repository_root
from numbra_ml.pretrained import sha256
from numbra_ml.train import train_run
from numbra_ml.training import TrainingConfig, tensor_hash
from test_export_replay import toy_backbone, toy_model


def test_embedded_joint_arithmetic_and_unchanged_boundaries(tmp_path):
    model = toy_model()
    # More than a centre pixel: check the embedded patch expression, border
    # padding and channel order through both in-place activations and the head.
    torch.manual_seed(117)
    model.backbone[0] = nn.Conv2d(3, 4, (3, 2), stride=224, padding=(1, 0)).eval()
    paths = {tag: tmp_path / f'PLACEHOLDER-{tag}.onnx'
             for tag in ('source', 'stem', 'bn', 'joint', 'runtime')}
    before = tensor_hash(model.state_dict())
    export_preserving_batchnorm(model, paths['source'])
    original_hash = sha256(paths['source'])
    stem_record = substitute_stem(model, paths['source'], paths['stem'])
    records = substitute_batchnorm(model, paths['source'], paths['bn'])
    assert substitute_batchnorm(model, paths['stem'], paths['joint']) == records
    audit_stem_graph(paths['joint'], paths['bn'], stem_record, serialized=True)
    session = runtime(paths['joint'], optimisation='disabled', optimized_path=paths['runtime'])
    for tag in ('joint', 'runtime'):
        assert audit_stem_graph(paths[tag], paths['source'], stem_record)['status'] == 'PASS'
        assert audit_promoted_graph(paths[tag], paths['stem'], records)['status'] == 'PASS'
    generator = np.random.default_rng(822)
    for _ in range(5):
        image = generator.normal(size=(1, 3, 224, 224)).astype(np.float32)
        with torch.inference_mode():
            value = python_promoted_conv(model.backbone[0], image)
            for bn_index, conv_index in ((1, 2), (3, None)):
                value = python_promoted_affine(model.backbone[bn_index], value, 'affine_rsqrt')
                value = model.backbone[bn_index].act(torch.from_numpy(value)).numpy()
                if conv_index is not None:
                    value = model.backbone[conv_index](torch.from_numpy(value)).numpy()
            expected = float(model.head(torch.from_numpy(value.reshape(1, 4)))[0])
        assert runtime_logit(session, image) == expected
    assert sha256(paths['source']) == original_hash
    assert tensor_hash(model.state_dict()) == before


@pytest.mark.parametrize('corruption', ['geometry', 'weights', 'connection', 'namespace', 'training'])
def test_stem_rejects_changed_saved_operator(tmp_path, corruption):
    model = toy_model()
    source, target = [tmp_path / f'PLACEHOLDER-{tag}.onnx' for tag in ('source', 'stem')]
    export_preserving_batchnorm(model, source)
    graph = onnx.load(source)
    stem = next(node for node in graph.graph.node if node.op_type == 'Conv')
    if corruption == 'geometry':
        next(attr for attr in stem.attribute if attr.name == 'strides').ints[0] = 1
        message = 'geometry mismatch'
    elif corruption == 'weights':
        item = next(item for item in graph.graph.initializer if item.name == stem.input[1])
        value = onnx.numpy_helper.to_array(item).copy()
        value.flat[0] += 1
        item.CopyFrom(onnx.numpy_helper.from_array(value, item.name))
        message = 'parameter mismatch'
    elif corruption == 'connection':
        stem.input[0] = 'some-other-input'
        message = 'connect directly'
    elif corruption == 'namespace':
        graph.graph.node[0].name = PREFIX + 'reserved'
        message = 'namespace collision'
    else:
        model.train()
        message = 'every module in eval'
    onnx.save(graph, source)
    with pytest.raises(ValueError, match=message):
        substitute_stem(model, source, target)
    assert not target.exists()


@pytest.mark.parametrize('corruption', ['cast', 'reshape-default', 'weights', 'patch-geometry', 'extra-conv', 'other-node'])
def test_actual_stem_audit_detects_expression_and_scope_corruption(tmp_path, corruption):
    model = toy_model()
    source, target = [tmp_path / f'PLACEHOLDER-{tag}.onnx' for tag in ('source', 'stem')]
    export_preserving_batchnorm(model, source)
    record = substitute_stem(model, source, target)
    graph = onnx.load(target)
    serialized = False
    if corruption in ('weights', 'patch-geometry'):
        key = 'weights' if corruption == 'weights' else 'patch-0-0-steps'
        item = next(item for item in graph.graph.initializer if item.name == PREFIX + key)
        value = onnx.numpy_helper.to_array(item).copy()
        value.flat[0] += 1
        item.CopyFrom(onnx.numpy_helper.from_array(value, item.name))
        message = 'constant audit'
    elif corruption == 'cast':
        node = next(node for node in graph.graph.node if node.name.startswith(PREFIX) and node.op_type == 'Cast')
        node.attribute[0].i = onnx.TensorProto.FLOAT
        message = 'arithmetic/cast audit'
    elif corruption == 'reshape-default':
        node = next(node for node in graph.graph.node if node.name.startswith(PREFIX) and node.op_type == 'Reshape')
        node.attribute[0].i = 1
        message = 'arithmetic/cast audit'
    elif corruption == 'extra-conv':
        node = next(node for node in graph.graph.node if node.op_type == 'Conv')
        graph.graph.node.append(node)
        message = 'operator count'
    else:
        node = next(node for node in graph.graph.node if node.op_type == 'Gemm')
        node.input[0] = 'wrong-head-connection'
        message = 'retained nodes'
        serialized = True
    onnx.save(graph, target)
    with pytest.raises(ValueError, match=message):
        audit_stem_graph(target, source, record, serialized=serialized)


def test_joint_pipeline_uses_only_training_pixels_and_retains_provenance():
    repo = repository_root()
    parent = repo / 'data/test-runs'
    parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=parent) as temporary:
        root = Path(temporary)
        prepared, run = root / 'prepared', root / 'model'
        prepare_run(prepared, groups_per_source=16)
        name = f'PLACEHOLDER-joint-test-{root.name}'
        reports = [repo / 'ml/reports' / f'{name}{suffix}' for suffix in ('.json', '-MODEL-CARD.md')]
        try:
            train_run(repo, prepared, root / 'checkpoint', run, name=name,
                config=TrainingConfig(epochs=3), bootstrap_replicates=100,
                backbone_loader=lambda _: (toy_backbone(), {'notice': 'PLACEHOLDER toy; no pretraining'}))
            experiment, preserved = root / 'PLACEHOLDER-export', root / 'PLACEHOLDER-preserved'
            export_run(repo, prepared, run, experiment, backbone_factory=toy_backbone)
            batchnorm_run(repo, prepared, run, [experiment], preserved, backbone_factory=toy_backbone)
            hashes = {path: sha256(path) for directory in (run, experiment, preserved)
                      for path in directory.rglob('*') if path.is_file()}
            index = read_component_index(prepared / 'manifest.jsonl', prepared / 'preparation-report.json')
            for component in index.components:
                if component.split != 'train':
                    (prepared / component.row.image_path).write_bytes(b'bad nontraining pixels')
            output = root / 'PLACEHOLDER-joint'
            result = promoted_bn_run(repo, prepared, run, [experiment], preserved, output,
                                     backbone_factory=toy_backbone, joint_stem=True)
            ids = [item.id for item in index.components if item.split == 'train']
            assert result['status'] == 'DIAGNOSTIC ONLY'
            assert result['protocol']['decision'] == 'ADR-018'
            assert result['protocol']['promoted_stem_convolutions'] == 1
            assert not any(result['protocol'][key] for key in
                           ('frozen_evaluation_inputs_used', 'quantisation_fit', 'deployment_selection'))
            assert result['model_state_before_sha256'] == result['model_state_after_sha256']
            detail_path = output / 'PLACEHOLDER-promoted-bn-details.json'
            assert sha256(detail_path) == result['diagnostic_details_sha256']
            details = json.loads(detail_path.read_text())
            assert set(result['artifacts']) == {'preserved_control', 'complete_promoted_bn', 'joint_promoted_stem_bn'}
            for key, artifact in result['artifacts'].items():
                assert artifact['diagnostics']['original_graph_training_parity']['n'] == len(ids)
                assert details['artifacts'][key]['component_ids'] == ids
                assert all(audit['status'] == 'PASS' for audit in artifact['runtime_audits'].values())
            for private in ('component_ids"', 'python_logits"', 'rows"', 'failure_cases"'):
                assert private not in json.dumps(result)
            assert hashes == {path: sha256(path) for path in hashes}
            stale_path = preserved / 'PLACEHOLDER-batchnorm-report.json'
            stale = json.loads(stale_path.read_text())
            stale['protocol']['threshold'] += 0.01
            stale_path.write_text(json.dumps(stale))
            with pytest.raises(ValueError, match='provenance mismatch'):
                promoted_bn_run(repo, prepared, run, [experiment], preserved,
                    root / 'PLACEHOLDER-stale', backbone_factory=toy_backbone, joint_stem=True)
            assert not (root / 'PLACEHOLDER-stale').exists()
        finally:
            for path in reports:
                path.unlink(missing_ok=True)
