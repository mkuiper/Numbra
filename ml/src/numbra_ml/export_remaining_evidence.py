"""ADR-023 ignored, lossless PLACEHOLDER replay evidence; never bundle.

This module neither opens images nor executes inference. A caller must verify
saved/preparation/source/prior provenance before supplying ordered training
scope, fixed fits and prior disabled-profile observations. Checksums bind local
files; they do not authenticate historical inference or establish M4 acceptance.
"""

import hashlib
import json
import math
import re

import numpy as np

from .export import aggregate_parity
from .export_remaining_native import same_bits
from .export_remaining_replay import KINDS, reconstruct_row
from .parity import FLOAT_BUDGET, parity_report
from .pretrained import ignored_path, sha256
from .train import json_text

NOTICE = 'PLACEHOLDER persisted complete replay diagnostic only; never bundle'
INDEX = 'PLACEHOLDER-evidence-index.json'
ARTIFACTS = dict(zip(KINDS, ('preserved_control', 'complete_promoted_bn')))
HEX = re.compile(r'[0-9a-f]{64}')


def digest_json(value):
    return hashlib.sha256(json_text(value).encode()).hexdigest()


def read_json(path):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('persisted replay duplicate JSON key')
            result[key] = value
        return result
    def nonfinite(_):
        raise ValueError('persisted replay nonfinite JSON value')
    return json.loads(path.read_text(), object_pairs_hook=pairs, parse_constant=nonfinite)


def array_id(value):
    if (not isinstance(value, np.ndarray) or value.dtype not in (np.dtype('float32'), np.dtype('int64'))
            or not value.size or not np.isfinite(value).all()):
        raise ValueError('persisted replay requires finite nonempty float32/int64 arrays')
    header = json_text({'dtype': str(value.dtype), 'shape': list(value.shape)}).encode()
    return hashlib.sha256(header + value.tobytes(order='C')).hexdigest()


def local_file(root, relative):
    """Only internally assigned direct paths; reject symlinks on reading too."""
    path = root / relative
    if (path.is_symlink() or path.parent.is_symlink() or root.is_symlink()
            or path.resolve() != path.absolute() or not path.is_file()):
        raise ValueError('persisted replay missing/unsafe evidence file')
    return path


class ArrayStore:
    """Content-addressed lossless NPZ arrays, deduplicated without dropping bits.

    Store without compression to bound complete-run CPU cost. Reading also
    supports earlier compressed evidence; decoded bits and file hashes stay
    separately verified for both formats.
    """

    def __init__(self, root):
        self.root = root
        self.records = {}

    def encode(self, value):
        if isinstance(value, np.ndarray):
            key = array_id(value)
            if key not in self.records:
                path = self.root / 'tensors' / f'PLACEHOLDER-{key}.npz'
                with path.open('xb') as stream:
                    np.savez(stream, value=value)
                self.records[key] = {'array_sha256': key, 'file_sha256': sha256(path),
                    'dtype': str(value.dtype), 'shape': list(value.shape),
                    'uncompressed_bytes': value.nbytes, 'file_bytes': path.stat().st_size}
            return ['array', key]
        if isinstance(value, dict) and all(isinstance(k, str) for k in value):
            # JSON objects may be sorted by serializers: order is explicit here.
            return ['dict', [[k, self.encode(v)] for k, v in value.items()]]
        if isinstance(value, list):
            return ['list', [self.encode(v) for v in value]]
        if isinstance(value, str):
            return ['string', value]
        raise ValueError('persisted replay unsupported evidence tree value')


def decode(root, tree, records, used, cache):
    if not isinstance(tree, list) or len(tree) != 2:
        raise ValueError('persisted replay malformed evidence tree')
    tag, value = tree
    if tag == 'string' and isinstance(value, str):
        return value
    if tag == 'list' and isinstance(value, list):
        return [decode(root, item, records, used, cache) for item in value]
    if tag == 'dict' and isinstance(value, list):
        result = {}
        for item in value:
            if (not isinstance(item, list) or len(item) != 2 or not isinstance(item[0], str)
                    or item[0] in result):
                raise ValueError('persisted replay duplicate/malformed ordered dictionary')
            result[item[0]] = decode(root, item[1], records, used, cache)
        return result
    if tag != 'array' or not isinstance(value, str) or not HEX.fullmatch(value) or value not in records:
        raise ValueError('persisted replay invalid array reference')
    used.add(value)
    if value not in cache:
        record = records[value]
        if (not isinstance(record, dict) or set(record) != {'array_sha256', 'file_sha256', 'dtype',
                'shape', 'uncompressed_bytes', 'file_bytes'} or record['array_sha256'] != value):
            raise ValueError('persisted replay array record scope mismatch')
        path = local_file(root, f'tensors/PLACEHOLDER-{value}.npz')
        if path.stat().st_size != record['file_bytes'] or sha256(path) != record['file_sha256']:
            raise ValueError('persisted replay archive checksum mismatch')
        with np.load(path, allow_pickle=False) as archive:
            if archive.files != ['value']:
                raise ValueError('persisted replay archive array scope mismatch')
            array = archive['value']
        if ({'dtype': str(array.dtype), 'shape': list(array.shape), 'uncompressed_bytes': array.nbytes}
                != {k: record[k] for k in ('dtype', 'shape', 'uncompressed_bytes')}
                or array_id(array) != value):
            raise ValueError('persisted replay array bits/specification mismatch')
        array.flags.writeable = False
        cache[value] = array
    return cache[value]


def prior_logits(details, identifiers):
    """Validate complete ordered ADR-022 disabled observations, without inference.

    This is deliberately not a substitute for audit_profile_report. A guarded
    runner must reconstruct that report/provenance before calling this module.
    """
    result = {}
    for kind, artifact in ARTIFACTS.items():
        row = details['artifacts'][artifact]['disabled']
        if row['component_ids'] != list(identifiers):
            raise ValueError('persisted replay prior ordered component scope mismatch')
        logits = {}
        for key in ('python_logits', 'original_onnx_logits'):
            values = row[key]
            if (not isinstance(values, list) or len(values) != len(identifiers)
                    or any(type(v) not in (int, float) or not math.isfinite(v)
                           or abs(v) > np.finfo(np.float32).max for v in values)):
                raise ValueError('persisted replay invalid prior logits')
            arrays = [np.array([v], dtype=np.float32) for v in values]
            if any(float(a[0]) != v for a, v in zip(arrays, values)):
                raise ValueError('persisted replay prior logits are not exact float32 values')
            logits[key] = arrays
        result[kind] = logits
    if any(not same_bits(a, b) for a, b in zip(result['preserved']['python_logits'], result['rounded']['python_logits'])):
        raise ValueError('persisted replay inconsistent prior Python references')
    return result


def check_prior(evidence, previous, position):
    for kind in KINDS:
        if (not same_bits(evidence['native_original_logit'], previous[kind]['python_logits'][position])
                or not same_bits(evidence['graphs'][kind]['original_logit'],
                                 previous[kind]['original_onnx_logits'][position])):
            raise ValueError('persisted replay prior disabled logit bits mismatch')


class Metrics:
    """Aggregate every numeric/boolean metric leaf, across all ordered rows."""

    def __init__(self):
        self.count = 0
        self.values = {}

    def add(self, metrics):
        def leaves(value, path=()):
            if isinstance(value, dict):
                for key, item in value.items():
                    yield from leaves(item, (*path, key))
            elif type(value) in (int, float, bool):
                if not math.isfinite(value):
                    raise ValueError('persisted replay nonfinite metric')
                yield path, value
            elif not isinstance(value, str):
                raise ValueError('persisted replay unsupported metric type')
        incoming = dict(leaves(metrics))
        if self.count and incoming.keys() != self.values.keys():
            raise ValueError('persisted replay metric scope changed')
        for path, value in incoming.items():
            entry = self.values.get(path)
            if entry is None:
                entry = self.values[path] = {'boolean': type(value) is bool, 'min': value, 'max': value, 'sum': 0.0}
            if entry['boolean'] != (type(value) is bool):
                raise ValueError('persisted replay metric type changed')
            entry['min'], entry['max'] = min(entry['min'], value), max(entry['max'], value)
            entry['sum'] += value
        self.count += 1

    def summary(self):
        result = {}
        for path, entry in self.values.items():
            cursor = result
            for key in path[:-1]:
                cursor = cursor.setdefault(key, {})
            cursor[path[-1]] = ({'all': bool(entry['min']), 'true_count': int(entry['sum'])}
                if entry['boolean'] else {'min': entry['min'], 'max': entry['max'], 'mean': entry['sum'] / self.count})
        return result


def scope(source, plan, identifiers, temperature, threshold):
    identifiers = tuple(identifiers)
    if (not identifiers or any(not isinstance(i, str) or not i for i in identifiers)
            or len(identifiers) != len(set(identifiers))):
        raise ValueError('persisted replay requires complete unique ordered component scope')
    # Validate fixed scoring fits using the unchanged ADR-011 contract.
    parity_report([0.], [0.], identifiers=['scope-check'], temperature=temperature,
                  threshold=threshold, budget=FLOAT_BUDGET)
    return {'notice': NOTICE, 'decision': 'ADR-023', 'components': len(identifiers),
        'component_ids_sha256': digest_json(list(identifiers)), 'plan_sha256': digest_json(plan),
        'source_sha256': hashlib.sha256(source.SerializeToString()).hexdigest(),
        'temperature': temperature, 'threshold': threshold, 'budget': {
            'raw_absolute': FLOAT_BUDGET.raw_absolute, 'probability_absolute': FLOAT_BUDGET.probability_absolute,
            'conservative_margin': FLOAT_BUDGET.conservative_margin}}


class OrderedEvidence:
    """Write one component at a time; partial runs have no completed index."""

    def __init__(self, repo, output, source, plan, identifiers, prior, *, temperature, threshold):
        self.output = ignored_path(repo, output)
        if self.output.exists() or not self.output.name.startswith('PLACEHOLDER-'):
            raise ValueError('persisted replay output must be fresh and named PLACEHOLDER-*')
        self.source, self.plan, self.ids = source, plan, tuple(identifiers)
        self.protocol = scope(source, plan, self.ids, temperature, threshold)
        self.prior = prior_logits(prior, self.ids)
        self.output.mkdir(parents=True, exist_ok=False)
        (self.output / 'tensors').mkdir()
        (self.output / 'rows').mkdir()
        self.arrays, self.rows, self.metrics = ArrayStore(self.output), [], Metrics()
        self.reference, self.candidates = [], {kind: [] for kind in KINDS}
        self.finished = False

    def append(self, identifier, evidence):
        position = len(self.rows)
        if self.finished or position >= len(self.ids) or identifier != self.ids[position]:
            raise ValueError('persisted replay append ordered component scope mismatch')
        metrics = reconstruct_row(self.source, self.plan, evidence)
        check_prior(evidence, self.prior, position)
        tree = self.arrays.encode(evidence)
        row = {'notice': NOTICE, 'position': position, 'component_id': identifier,
               'evidence': tree, 'metrics': metrics}
        relative = f'rows/PLACEHOLDER-component-{position:04d}.json'
        with (self.output / relative).open('x') as stream:
            stream.write(json_text(row))
        self.rows.append({'position': position, 'path': relative, 'sha256': sha256(self.output / relative)})
        self.metrics.add(metrics)
        self.reference.append(float(evidence['native_original_logit'][0]))
        for kind in KINDS:
            self.candidates[kind].append(float(evidence['graphs'][kind]['original_logit'][0]))

    def finish(self):
        if self.finished or len(self.rows) != len(self.ids):
            raise ValueError('persisted replay cannot complete partial/repeated evidence')
        index = {'notice': NOTICE, 'protocol': self.protocol, 'rows': self.rows, 'arrays': self.arrays.records}
        with (self.output / INDEX).open('x') as stream:
            stream.write(json_text(index))
        self.finished = True
        return aggregate(self.protocol, self.metrics, self.ids, self.reference, self.candidates,
                         sha256(self.output / INDEX))


def aggregate(protocol, metrics, ids, reference, candidates, index_hash):
    return {'notice': NOTICE, 'status': 'DIAGNOSTIC ONLY', 'protocol': protocol,
        'evidence_index_sha256': index_hash, 'complete_metric_aggregates': metrics.summary(),
        'original_graph_training_parity': {kind: aggregate_parity(parity_report(reference, values,
            identifiers=ids, temperature=protocol['temperature'], threshold=protocol['threshold'],
            budget=FLOAT_BUDGET)) for kind, values in candidates.items()},
        'prior_disabled_original_logits_exact_bits': True,
        'limits': 'Recorded observations reconstructed; no independent inference, historical authentication or mobile acceptance.'}


def audit_ordered(repo, output, source, plan, identifiers, prior, report, *, temperature, threshold):
    """Stream complete arrays/rows, reconstruct all metrics and original parity."""
    output = ignored_path(repo, output)
    ids = tuple(identifiers)
    expected = scope(source, plan, ids, temperature, threshold)
    previous = prior_logits(prior, ids)
    path = local_file(output, INDEX)
    index = read_json(path)
    if (set(index) != {'notice', 'protocol', 'rows', 'arrays'} or index['notice'] != NOTICE
            or index['protocol'] != expected or not isinstance(index['rows'], list)
            or len(index['rows']) != len(ids) or not isinstance(index['arrays'], dict)):
        raise ValueError('persisted replay index scope/protocol mismatch')
    if (set(p.name for p in output.iterdir()) != {INDEX, 'rows', 'tensors'}
            or (output / 'rows').is_symlink() or (output / 'tensors').is_symlink()
            or set(p.name for p in (output / 'rows').iterdir()) != {
                f'PLACEHOLDER-component-{i:04d}.json' for i in range(len(ids))}
            or any(not HEX.fullmatch(key) for key in index['arrays'])
            or set(p.name for p in (output / 'tensors').iterdir()) != {
                f'PLACEHOLDER-{key}.npz' for key in index['arrays']}):
        raise ValueError('persisted replay extra/missing evidence files')
    used, metrics, reference, candidates = set(), Metrics(), [], {kind: [] for kind in KINDS}
    for position, (identifier, record) in enumerate(zip(ids, index['rows'])):
        relative = f'rows/PLACEHOLDER-component-{position:04d}.json'
        row_path = local_file(output, relative)
        if (set(record) != {'position', 'path', 'sha256'} or record['position'] != position
                or record['path'] != relative or record['sha256'] != sha256(row_path)):
            raise ValueError('persisted replay ordered row checksum/scope mismatch')
        row = read_json(row_path)
        if (set(row) != {'notice', 'position', 'component_id', 'evidence', 'metrics'}
                or row['notice'] != NOTICE or row['position'] != position or row['component_id'] != identifier):
            raise ValueError('persisted replay ordered row identity mismatch')
        evidence = decode(output, row['evidence'], index['arrays'], used, {})
        reconstructed = reconstruct_row(source, plan, evidence)
        if row['metrics'] != reconstructed:
            raise ValueError('persisted replay reconstructed row metric mismatch')
        check_prior(evidence, previous, position)
        metrics.add(reconstructed)
        reference.append(float(evidence['native_original_logit'][0]))
        for kind in KINDS:
            candidates[kind].append(float(evidence['graphs'][kind]['original_logit'][0]))
        del evidence, row  # Per-row array cache is released before the next component.
    if used != set(index['arrays']):
        raise ValueError('persisted replay unreferenced array records')
    if report != aggregate(expected, metrics, ids, reference, candidates, sha256(path)):
        raise ValueError('persisted replay complete aggregate reconstruction mismatch')
    return {'notice': NOTICE, 'status': 'PASS', 'components': len(ids),
            'complete_ordered_rows_arrays_metrics_and_parity': True,
            'prior_disabled_original_logits_exact_bits': True,
            'baseline_inference': False, 'historical_inference_authentication': False}
