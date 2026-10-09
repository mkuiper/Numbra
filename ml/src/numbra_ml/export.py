"""Offline PLACEHOLDER ONNX experiments; failed parity is retained, never waived."""

import argparse
from collections import Counter
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import sys
import tempfile

import numpy as np
import onnx
import onnxruntime as ort
from onnxruntime.quantization import CalibrationDataReader, CalibrationMethod, QuantFormat, QuantType, quantize_static
from onnxruntime.quantization.shape_inference import quant_pre_process
import torch

from . import PLACEHOLDER_NOTICE
from .dataset import load_rgb
from .evaluation import component_predictions, metrics, read_component_index, subgroup_metrics
from .parity import FLOAT_BUDGET, QUANTISED_BUDGET, parity_report
from .prepare import repository_root
from .preprocessing import SPEC, preprocess
from .pretrained import ignored_path, sha256
from .train import environment, json_text
from .verify import backbone_architecture, calibrated_scores, load_reference, verify_run

INPUT_NAME = 'rgb'
OUTPUT_NAME = 'raw_logit'
INPUT_SHAPE = (1, 3, 224, 224)
MAX_MODEL_BYTES = 20_000_000
ATTEMPTS = ('minmax-per-tensor', 'minmax-per-channel')


@contextmanager
def local_temporaries(directory):
    """Keep library-managed temporary artifacts beside the ignored output."""
    previous = tempfile.tempdir
    try:
        tempfile.tempdir = str(directory.resolve())
        yield
    finally:
        tempfile.tempdir = previous


def export_environment(repo):
    evidence = environment(repo)  # Preserve M3 environment; check additions too.
    lock = repo / 'ml/requirements-export.lock'
    for line in lock.read_text().splitlines():
        if ' --hash=' not in line:
            continue
        name, pinned = line.split()[0].split('==')
        if version(name) != pinned:
            raise ValueError(f'export dependency drift: {name}')
        evidence['dependencies'][name] = pinned
    evidence['export_dependency_lock_sha256'] = sha256(lock)
    return evidence


def tensor_input(value):
    if (not isinstance(value, np.ndarray) or value.dtype != np.float32
            or value.shape != INPUT_SHAPE or not value.flags.c_contiguous
            or not np.isfinite(value).all()):
        raise ValueError('export input must be finite contiguous float32 1x3x224x224')
    return value


def component_input(prepared, component):
    return tensor_input(preprocess(load_rgb(prepared, component.row))[None])


class TrainingCalibration(CalibrationDataReader):
    """One predetermined index image for every train component; no other split."""
    def __init__(self, index, prepared):
        self.components = tuple(item for item in index.components if item.split == 'train')
        if not self.components:
            raise ValueError('quantisation requires training components')
        self.prepared = prepared
        self.rewind()

    def rewind(self):
        self.iterator = iter(self.components)

    def get_next(self):
        item = next(self.iterator, None)
        return None if item is None else {INPUT_NAME: component_input(self.prepared, item)}


def stress_inputs():
    """Fixed independent RGB stress suite; never used for quantisation fitting."""
    values = []
    for colour in (0, 128, 255):
        values.append((f'stress-uniform-{colour}', np.full((224, 224, 3), colour, np.uint8)))
    for channel in range(3):
        rgb = np.zeros((224, 224, 3), np.uint8)
        rgb[:, :, channel] = 255
        values.append((f'stress-channel-{channel}', rgb))
    rng = np.random.default_rng(741902)
    for height, width in ((1, 1), (1, 4096), (4096, 1), (7, 113), (113, 7), (225, 319)):
        values.append((f'stress-noise-{height}x{width}', rng.integers(0, 256, (height, width, 3), dtype=np.uint8)))
    yy, xx = np.indices((301, 179))
    checker = np.repeat((((xx + yy) % 2) * 255).astype(np.uint8)[:, :, None], 3, axis=2)
    gradient = np.stack([xx * 255 // 178, yy * 255 // 300, (xx + yy) * 255 // 478], axis=-1).astype(np.uint8)
    values.extend((('stress-checker', checker), ('stress-gradient', gradient)))
    return tuple((name, tensor_input(preprocess(rgb)[None])) for name, rgb in values)


def export_float(model, path):
    # PyTorch 2.8 supports the legacy exporter. Fixed shape avoids dynamic/mobile
    # graph ambiguity; external_data=False guarantees a single inspectable file.
    with local_temporaries(path.parent), torch.inference_mode():
        torch.onnx.export(model.cpu().eval(), torch.zeros(INPUT_SHAPE), str(path),
                          input_names=[INPUT_NAME], output_names=[OUTPUT_NAME],
                          opset_version=17, dynamo=False, external_data=False)
    graph = onnx.load(path, load_external_data=False)
    onnx.helper.set_model_props(graph, {'notice': PLACEHOLDER_NOTICE,
                                      'preprocessing_version': SPEC['version']})
    onnx.checker.check_model(graph, full_check=True)
    onnx.save(graph, path)


def graph_report(path):
    graph = onnx.load(path, load_external_data=False)
    onnx.checker.check_model(graph, full_check=True)
    if any(value.data_location == onnx.TensorProto.EXTERNAL for value in graph.graph.initializer):
        raise ValueError('external weight files are not permitted')
    ops = Counter(node.op_type for node in graph.graph.node)
    initializers = {item.name: item for item in graph.graph.initializer}
    producers = {name: node for node in graph.graph.node for name in node.output}
    # Count weight-bearing Conv/Gemm/MatMul whose weight comes through INT8 DQ.
    quantised, remaining = Counter(), Counter()
    for node in graph.graph.node:
        if node.op_type not in ('Conv', 'Gemm', 'MatMul'):
            continue
        producer = producers.get(node.input[1])
        weight = initializers.get(producer.input[0]) if producer is not None and producer.op_type == 'DequantizeLinear' else None
        target = quantised if weight is not None and weight.data_type in (onnx.TensorProto.INT8, onnx.TensorProto.UINT8) else remaining
        target[node.op_type] += 1
    return {'notice': PLACEHOLDER_NOTICE, 'bytes': path.stat().st_size,
            'sha256': sha256(path), 'size_pass': path.stat().st_size <= MAX_MODEL_BYTES,
            'opsets': {item.domain or 'ai.onnx': item.version for item in graph.opset_import},
            'ir_version': graph.ir_version, 'operators': dict(sorted(ops.items())),
            'int8_weight_qdq_operators': dict(sorted(quantised.items())),
            'remaining_float_weight_operators': dict(sorted(remaining.items())),
            'other_float_or_structural_operators': {name: count for name, count in sorted(ops.items())
                 if name not in ('Conv', 'Gemm', 'MatMul', 'QuantizeLinear', 'DequantizeLinear')},
            'warning': 'QDQ graph inspection; not proof of all-integer execution or Android support'}


def runtime(path):
    options = ort.SessionOptions()
    options.intra_op_num_threads = 2
    options.inter_op_num_threads = 1
    options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
    session = ort.InferenceSession(str(path), sess_options=options, providers=['CPUExecutionProvider'])
    inputs, outputs = session.get_inputs(), session.get_outputs()
    if (len(inputs) != 1 or inputs[0].name != INPUT_NAME or inputs[0].type != 'tensor(float)'
            or inputs[0].shape != list(INPUT_SHAPE) or len(outputs) != 1
            or outputs[0].name != OUTPUT_NAME or outputs[0].shape != [1]
            or outputs[0].type != 'tensor(float)'):
        raise ValueError('ONNX runtime interface mismatch')
    return session


def runtime_logit(session, inputs):
    value = session.run([OUTPUT_NAME], {INPUT_NAME: tensor_input(inputs)})[0]
    if value.shape != (1,) or value.dtype != np.float32 or not np.isfinite(value).all():
        raise ValueError('invalid ONNX raw-logit output')
    return float(value[0])


def aggregate_parity(report):
    return {key: value for key, value in report.items() if key not in ('failure_cases', 'failure_cases_storage')}


def compare(model, session, inputs, *, temperature, threshold, budget):
    ids, reference, candidate = [], [], []
    with torch.inference_mode():
        for name, tensor in inputs:
            ids.append(name)
            reference.append(float(model(torch.from_numpy(tensor_input(tensor)))[0]))
            candidate.append(runtime_logit(session, tensor))
    report = parity_report(reference, candidate, identifiers=ids, temperature=temperature,
                           threshold=threshold, budget=budget)
    return report, reference, candidate


def frozen_evaluation(index, logits, temperature, threshold):
    # Deliberately never call evaluation_report: that would refit calibration and
    # threshold on the exported scores and conceal drift from the frozen M3 fit.
    values = component_predictions(index, logits)
    result = {}
    for split in ('test', 'held_out'):
        subset = tuple(item for item in values if item.split == split)
        result[split] = {'primary': metrics(subset, temperature, threshold),
                         'by_source': {source: subgroup_metrics(tuple(item for item in subset if source in item.sources), temperature, threshold)
                                       for source in sorted({source for item in subset for source in item.sources})},
                         'by_synthetic_colour': {colour: subgroup_metrics(tuple(item for item in subset if item.colour_stratum == colour), temperature, threshold)
                                       for colour in sorted({item.colour_stratum for item in subset})}}
    return {'notice': PLACEHOLDER_NOTICE, 'temperature': temperature, 'threshold': threshold,
            'fits': 'frozen M3 values; no refitting', 'held_out_source': index.held_out_source,
            'scope': 'one synthetic leave-one-source-out fold; no skin-tone/clinical claim', 'splits': result}


def export_run(repo, prepared, run, output, *, attempt='minmax-per-tensor',
               backbone_factory=backbone_architecture):
    if attempt not in ATTEMPTS:
        raise ValueError('unknown predeclared quantisation attempt')
    prepared, run, output = [ignored_path(repo, p) for p in (prepared, run, output)]
    if output.exists() or not output.name.startswith('PLACEHOLDER-'):
        raise ValueError('output must be new and named PLACEHOLDER-*')
    evidence = export_environment(repo)
    verification = verify_run(repo, prepared, run, backbone_factory=backbone_factory)
    model, saved = load_reference(run, backbone_factory=backbone_factory)
    index = read_component_index(prepared / 'manifest.jsonl', prepared / 'preparation-report.json')
    temperature, threshold = saved['calibration']['temperature'], saved['primary_operating_point']['threshold']
    output.mkdir(parents=True, exist_ok=False)
    float_path, quant_path = output / 'PLACEHOLDER-float.onnx', output / 'PLACEHOLDER-int8.onnx'
    export_float(model, float_path)
    reader = TrainingCalibration(index, prepared)
    preprocessed = output / 'PLACEHOLDER-inferred.onnx'
    with local_temporaries(output):
        quant_pre_process(str(float_path), str(preprocessed), skip_optimization=True, skip_symbolic_shape=True)
        quantize_static(str(preprocessed), str(quant_path), reader, quant_format=QuantFormat.QDQ,
                        activation_type=QuantType.QInt8, weight_type=QuantType.QInt8,
                        op_types_to_quantize=['Conv', 'Gemm', 'MatMul'],
                        per_channel=attempt == 'minmax-per-channel', calibrate_method=CalibrationMethod.MinMax)
    report = {'notice': PLACEHOLDER_NOTICE, 'version': '1.0.0',
              'created_utc': datetime.now(timezone.utc).isoformat(),
              'attempt': attempt, 'python_saved_verification': verification, 'environment': evidence,
              'saved_model_sha256': saved['provenance']['model_sha256'],
              'saved_run_sha256': sha256(run / 'PLACEHOLDER-run.json'), 'preprocessing': SPEC,
              'interface': {'input': INPUT_NAME, 'shape': list(INPUT_SHAPE), 'dtype': 'float32',
                            'output': OUTPUT_NAME, 'output_shape': [1], 'temperature': temperature,
                            'threshold': threshold, 'conservative_margin': QUANTISED_BUDGET.conservative_margin},
              'calibration': {'split': 'train', 'components': len(reader.components),
                              'component_ids_sha256': hashlib.sha256(json_text([c.id for c in reader.components]).encode()).hexdigest(),
                              'method': 'MinMax', 'format': 'QDQ', 'activation_type': 'QInt8',
                              'weight_type': 'QInt8', 'per_channel': attempt == 'minmax-per-channel',
                              'operators': ['Conv', 'Gemm', 'MatMul'], 'graph_optimization_before_quantisation': False},
              'stress_suite': {'version': '1.0.0', 'seed': 741902, 'n': len(stress_inputs()),
                               'calibration_use': False}, 'artifacts': {},
              'scope': 'PLACEHOLDER desktop CPU export experiment; no Android or clinical validity'}
    details = {'notice': PLACEHOLDER_NOTICE, 'artifacts': {}}
    for name, path, budget in (('float', float_path, FLOAT_BUDGET), ('int8', quant_path, QUANTISED_BUDGET)):
        session = runtime(path)
        paired, before, after = compare(model, session,
              ((item.id, component_input(prepared, item)) for item in index.components),
              temperature=temperature, threshold=threshold, budget=budget)
        stress, _, _ = compare(model, session, stress_inputs(), temperature=temperature, threshold=threshold, budget=budget)
        frozen_parity, _, _ = compare(model, session,
              ((item.id, component_input(prepared, item)) for item in index.components if item.split in ('test', 'held_out')),
              temperature=temperature, threshold=threshold, budget=budget)
        graph = graph_report(path)
        report['artifacts'][name] = {'graph': graph, 'all_components_parity': aggregate_parity(paired),
                                    'test_held_out_parity': aggregate_parity(frozen_parity),
                                    'stress_parity': aggregate_parity(stress),
                                    'frozen_evaluation': frozen_evaluation(index, dict(zip((c.id for c in index.components), after)), temperature, threshold)}
        details['artifacts'][name] = {'all_components_parity': paired, 'stress_parity': stress,
                                     'test_held_out_parity': frozen_parity,
                                     'same_tensor_python_logits': before, 'onnx_logits': after,
                                     'component_ids': [c.id for c in index.components]}
    report['status'] = 'PASS' if all(a['graph']['size_pass'] and all(a[key]['status'] == 'PASS' for key in
                       ('all_components_parity', 'test_held_out_parity', 'stress_parity')) for a in report['artifacts'].values()) else 'FAIL'
    # Reject a graph with no actual quantised weights, even if numerical parity passes.
    if not report['artifacts']['int8']['graph']['int8_weight_qdq_operators']:
        report['status'] = 'FAIL'
    (output / 'PLACEHOLDER-export-report.json').write_text(json_text(report))
    (output / 'PLACEHOLDER-parity-details.json').write_text(json_text(details))
    return report


def summarise_run(repo, prepared, output, *, run=Path('data/models/PLACEHOLDER-m3-baseline')):
    """Verify local experiment bytes and rebuild tracked-safe aggregate evidence.

    This also corrects prototype subgroup reporting without changing saved
    logits, quantisation, fits or the recorded experimental source provenance.
    """
    prepared, output, run = [ignored_path(repo, path) for path in (prepared, output, run)]
    report_path = output / 'PLACEHOLDER-export-report.json'
    details_path = output / 'PLACEHOLDER-parity-details.json'
    report, details = [json.loads(path.read_text()) for path in (report_path, details_path)]
    if any(value.get('notice') != PLACEHOLDER_NOTICE for value in (report, details)):
        raise ValueError('experiment PLACEHOLDER notice mismatch')
    index = read_component_index(prepared / 'manifest.jsonl', prepared / 'preparation-report.json')
    if index.manifest_sha256 != report['python_saved_verification']['manifest_sha256']:
        raise ValueError('experiment preparation checksum mismatch')
    saved_path = run / 'PLACEHOLDER-run.json'
    saved_predictions = run / 'PLACEHOLDER-predictions.json'
    saved = json.loads(saved_path.read_text())
    if (sha256(saved_path) != report['saved_run_sha256']
            or sha256(saved_predictions) != saved['provenance']['predictions_sha256']):
        raise ValueError('original saved-run checksum mismatch')
    predictions = json.loads(saved_predictions.read_text())['predictions']
    original = {p['component_id']: p['logit'] for p in predictions}
    ids = [item.id for item in index.components]
    if set(original) != set(ids) or len(original) != len(predictions):
        raise ValueError('original saved predictions do not match experiment')
    original = np.array([original[i] for i in ids])
    temperature, threshold = report['interface']['temperature'], report['interface']['threshold']
    for name, budget in (('float', FLOAT_BUDGET), ('int8', QUANTISED_BUDGET)):
        artifact = report['artifacts'][name]
        local = details['artifacts'][name]
        graph = graph_report(output / f'PLACEHOLDER-{name}.onnx')
        if graph != artifact['graph'] or local['component_ids'] != ids:
            raise ValueError('experiment graph or component identity mismatch')
        parity = parity_report(local['same_tensor_python_logits'], local['onnx_logits'],
                     identifiers=ids, temperature=report['interface']['temperature'],
                     threshold=report['interface']['threshold'], budget=budget)
        if aggregate_parity(parity) != artifact['all_components_parity']:
            raise ValueError('experiment parity summary mismatch')
        artifact['frozen_evaluation'] = frozen_evaluation(index, dict(zip(ids, local['onnx_logits'])),
                     report['interface']['temperature'], report['interface']['threshold'])
        python_single, candidate = [np.array(local[key]) for key in ('same_tensor_python_logits', 'onnx_logits')]
        original_decisions = calibrated_scores(original, temperature) >= threshold
        artifact['saved_batch_reference_diagnostic'] = {
            'python_single_vs_saved_batch_max_raw_error': float(np.max(np.abs(python_single-original))),
            'python_single_vs_saved_batch_decision_flips': int(np.count_nonzero(
                (calibrated_scores(python_single, temperature) >= threshold) != original_decisions)),
            'candidate_vs_saved_batch_decision_flips': int(np.count_nonzero(
                (calibrated_scores(candidate, temperature) >= threshold) != original_decisions)),
            'scope': 'saved training batch-size logits vs single-image execution; export budgets use same-shaped single-image tensors'}
    report['reporting_revision'] = {'version': '1.0.1', 'source_report_sha256': sha256(report_path),
        'parity_details_sha256': sha256(details_path), 'reporter_source_sha256': sha256(Path(__file__)),
        'change': 'verified graph/ordered logits; rebuilt frozen source/colour aggregates; no new inference or fit'}
    reports = repo / 'ml/reports'
    target = reports / f'{output.name}.json'
    if (not output.name.startswith('PLACEHOLDER-') or reports.is_symlink()
            or reports.resolve() != reports or target.exists() or target.is_symlink()):
        raise ValueError('summary target must be new, local and PLACEHOLDER-labelled')
    target.write_text(json_text(report))
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=f'{PLACEHOLDER_NOTICE}; export and retain failed parity')
    parser.add_argument('--prepared', type=Path, default=Path('data/prepared/synthetic-v2-selection'))
    parser.add_argument('--run', type=Path, default=Path('data/models/PLACEHOLDER-m3-baseline'))
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--attempt', choices=ATTEMPTS, default=ATTEMPTS[0])
    parser.add_argument('--summarise', action='store_true', help='verify existing experiment and write aggregate ml/reports evidence')
    args = parser.parse_args(argv)
    try:
        report = (summarise_run(repository_root(), args.prepared, args.output, run=args.run) if args.summarise else
                  export_run(repository_root(), args.prepared, args.run, args.output, attempt=args.attempt))
    except (ValueError, OSError, RuntimeError, KeyError, TypeError) as exc:
        print(f'PLACEHOLDER export failed: {exc}', file=sys.stderr)
        return 1
    print(json_text({'notice': PLACEHOLDER_NOTICE, 'status': report['status'], 'output': str(args.output)}))
    return 0 if report['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
