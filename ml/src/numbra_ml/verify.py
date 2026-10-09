"""Offline PLACEHOLDER saved-model verification and M4 Python reference path."""

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import sys

import numpy as np
from safetensors.torch import load_file
import timm
import torch

from . import PLACEHOLDER_NOTICE
from .evaluation import component_predictions, read_component_index
from .prepare import repository_root
from .preprocessing import SPEC
from .pretrained import MODEL_NAME, ignored_path, sha256
from .training import Baseline, FeatureHead, TrainingConfig, extract_features, initialise, predict, tensor_hash


def backbone_architecture():
    """Construct architecture only; bundled state supplies every frozen weight."""
    model = timm.create_model(MODEL_NAME, pretrained=False)
    model.reset_classifier(0)
    return model.requires_grad_(False).cpu().eval()


def load_reference(run: Path, *, backbone_factory=backbone_architecture):
    """Verify bundled bytes and strictly load the full backbone/scaling/head.

    This reference does not require the original pretrained checkpoint or network.
    A factory is injectable only through Python for generated toy-model tests.
    """
    paths = {name: run / f'PLACEHOLDER-{name}' for name in
             ('run.json', 'model.safetensors', 'predictions.json')}
    if any(not p.is_file() or p.is_symlink() for p in paths.values()):
        raise ValueError('missing or symlinked PLACEHOLDER run artifact')
    report = json.loads(paths['run.json'].read_text())
    if report.get('notice') != PLACEHOLDER_NOTICE or report.get('preprocessing') != SPEC:
        raise ValueError('PLACEHOLDER notice or preprocessing contract mismatch')
    provenance = report['provenance']
    for name, key in (('model.safetensors', 'model_sha256'), ('predictions.json', 'predictions_sha256')):
        if sha256(paths[name]) != provenance[key]:
            raise ValueError(f'saved artifact checksum mismatch: {name}')
    if paths['model.safetensors'].stat().st_size != provenance['model_bytes']:
        raise ValueError('saved model size mismatch')
    state = load_file(str(paths['model.safetensors']), device='cpu')
    mean, scale = state['head.mean'], state['head.scale']
    if (mean.ndim != 1 or mean.numel() == 0 or scale.shape != mean.shape
            or not all(torch.isfinite(value).all() for value in state.values())
            or not (scale > 0).all()):
        raise ValueError('invalid saved model state')
    config = TrainingConfig(**report['training']['config'])
    initialise(config)
    model = Baseline(backbone_factory(), FeatureHead(mean, scale)).cpu().eval()
    model.load_state_dict(state, strict=True)
    model.requires_grad_(False)
    if (tensor_hash(model.backbone.state_dict()) != provenance['frozen_backbone_sha256']
            or tensor_hash(model.head.state_dict()) != report['training']['head_sha256']):
        raise ValueError('saved backbone/head state hash mismatch')
    return model, report


def calibrated_scores(logits, temperature):
    values = np.asarray(logits, dtype=np.float64)
    if not np.isfinite(temperature) or temperature <= 0 or not np.isfinite(values).all():
        raise ValueError('invalid logits or temperature')
    scaled = values / temperature
    return np.exp(-np.logaddexp(0, -scaled))


def verify_run(repo: Path, prepared: Path, run: Path, *, backbone_factory=backbone_architecture,
               raw_tolerance: float = 1e-5) -> dict:
    if not np.isfinite(raw_tolerance) or raw_tolerance < 0:
        raise ValueError('invalid raw-logit tolerance')
    prepared, run = [ignored_path(repo, path) for path in (prepared, run)]
    model, report = load_reference(run, backbone_factory=backbone_factory)
    index = read_component_index(prepared / 'manifest.jsonl', prepared / 'preparation-report.json')
    if (index.manifest_sha256 != report['provenance']['manifest_sha256']
            or sha256(prepared / 'preparation-report.json') != report['provenance']['preparation_report_sha256']):
        raise ValueError('saved-run preparation checksum mismatch')
    stored = json.loads((run / 'PLACEHOLDER-predictions.json').read_text())
    if stored.get('notice') != PLACEHOLDER_NOTICE:
        raise ValueError('stored prediction PLACEHOLDER notice mismatch')
    items = stored['predictions']
    if len({item['component_id'] for item in items}) != len(items):
        raise ValueError('duplicate stored prediction')
    expected = component_predictions(index, {item['component_id']: item['logit'] for item in items})
    # JSON turns source tuples into lists; compare the canonical JSON form.
    if json.loads(json.dumps([asdict(item) for item in expected])) != items:
        raise ValueError('stored prediction component metadata mismatch')
    features = extract_features(index, prepared, model.backbone,
                                batch_size=report['training']['config']['batch_size'])
    actual = predict(index, features, model.head)
    before, after = [np.array([item.logit for item in values], dtype=np.float64) for values in (expected, actual)]
    error = float(np.max(np.abs(after - before)))
    temperature = report['calibration']['temperature']
    threshold = report['primary_operating_point']['threshold']
    reference_scores, restored_scores = [calibrated_scores(logits, temperature) for logits in (before, after)]
    flips = int(np.count_nonzero((reference_scores >= threshold) != (restored_scores >= threshold)))
    if error > raw_tolerance or flips:
        raise ValueError(f'saved-model parity failed: max raw-logit error {error}, decision flips {flips}')
    return {'notice': PLACEHOLDER_NOTICE, 'status': 'PASS', 'components': len(actual),
            'model_sha256': report['provenance']['model_sha256'],
            'predictions_sha256': report['provenance']['predictions_sha256'],
            'manifest_sha256': index.manifest_sha256, 'raw_logit_absolute_tolerance': raw_tolerance,
            'max_raw_logit_absolute_error': error,
            'max_calibrated_probability_absolute_error': float(np.max(np.abs(reference_scores - restored_scores))),
            'decision_flips_at_frozen_threshold': flips, 'threshold': threshold,
            'scope': 'saved Python model only; not exported/quantised/mobile or clinical validation'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=f'{PLACEHOLDER_NOTICE}; verify saved Python model')
    parser.add_argument('--prepared', type=Path, default=Path('data/prepared/synthetic-v2-selection'))
    parser.add_argument('--run', type=Path, default=Path('data/models/PLACEHOLDER-m3-baseline'))
    args = parser.parse_args(argv)
    try:
        result = verify_run(repository_root(), args.prepared, args.run)
    except (ValueError, OSError, RuntimeError, KeyError, TypeError) as exc:
        print(f'PLACEHOLDER verification failed: {exc}', file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
