"""ADR-023 guarded training-only PLACEHOLDER complete replay; never bundle."""

import argparse
from datetime import datetime, timezone
from pathlib import Path
import sys

import onnx
import torch

from .export import INPUT_SHAPE, component_input
from .export_provenance import audit_environment, checked_file, checkout_context
from .export_remaining import preflight_evidence
from .export_remaining_evidence import OrderedEvidence, audit_ordered, digest_json, prior_logits, read_json
from .export_remaining_native import native_plan
from .export_remaining_replay import CompleteReplay, audit_replay_setup
from .export_runtime_profiles import (DETAILS as PROFILE_DETAILS, REPORT as PROFILE_REPORT,
                                      audit_profile_report, verified_prior)
from .evaluation import read_component_index
from .prepare import repository_root
from .pretrained import ignored_path, sha256
from .train import json_text
from .training import tensor_hash
from .verify import backbone_architecture, load_reference

NOTICE = 'PLACEHOLDER complete training replay diagnostic only; never bundle'
REPORT = 'PLACEHOLDER-complete-training-report.json'
SETUP = 'PLACEHOLDER-setup-records.json'
KERNELS = 'PLACEHOLDER-kernels'
OBSERVATIONS = 'PLACEHOLDER-observations'


def training_context(repo, prepared, run, experiments, source, prior, profiles, *,
                     backbone_factory=backbone_architecture, profile_source_commit=None):
    """Complete static/provenance checks precede session setup and image loading."""
    prepared, run, source, prior, profiles = [ignored_path(repo, path) for path in
                                             (prepared, run, source, prior, profiles)]
    experiments = tuple(ignored_path(repo, path) for path in experiments)
    preflight = preflight_evidence(repo, prepared, run, experiments, source, prior,
                                  backbone_factory=backbone_factory)
    model, saved = load_reference(run, backbone_factory=backbone_factory)
    if saved['training']['config']['threads'] != 2 or torch.get_num_threads() != 2:
        raise ValueError('complete training replay requires unchanged two-thread reference')
    index = read_component_index(prepared / 'manifest.jsonl', prepared / 'preparation-report.json')
    if (saved['provenance']['manifest_sha256'] != index.manifest_sha256
            or saved['provenance']['preparation_report_sha256'] != sha256(prepared / 'preparation-report.json')):
        raise ValueError('complete training saved preparation mismatch')
    preserved, rounded, _, _ = verified_prior(repo, prepared, run, experiments, source, prior, model, saved, index)
    graphs = [onnx.load(path, load_external_data=False) for path in (preserved, rounded)]
    plan = native_plan(model, *graphs)
    training = tuple(c for c in index.components if c.split == 'train')
    ids = [c.id for c in training]
    profile_report_path = checked_file(profiles, PROFILE_REPORT)
    profile_report = read_json(profile_report_path)
    profile_audit = audit_profile_report(repo, profiles, profile_report, prepared, run, experiments,
        source, prior, backbone_factory=backbone_factory, source_commit=profile_source_commit)
    environment = preflight['environment']
    profile_environment_audit = audit_environment(repo, profile_report['environment'], environment,
                                                 source_commit=profile_source_commit)
    detail_path = checked_file(profiles, PROFILE_DETAILS)
    previous = read_json(detail_path)
    prior_logits(previous, ids)  # Exact float32 bits and complete ordered scope.
    context = {'notice': NOTICE, 'preflight': preflight,
        'protocol': {'decision': 'ADR-023', 'stage': 'complete training replay', 'split': 'train',
            'components': len(ids), 'component_ids_sha256': digest_json(ids), 'shape': list(INPUT_SHAPE),
            'execution': 'sequential', 'optimisation': 'disabled', 'intra_op_threads': 2, 'inter_op_threads': 1,
            'temperature': saved['calibration']['temperature'],
            'threshold': saved['primary_operating_point']['threshold'],
            'preprocessing': saved['preprocessing'], 'frozen_evaluation_inputs_used': False,
            'quantisation_fit': False, 'deployment_selection': False},
        'native_plan': plan, 'profile_report_sha256': sha256(profile_report_path),
        'profile_details_sha256': sha256(detail_path), 'profile_report_audit': profile_audit,
        'profile_environment_audit': profile_environment_audit,
        'model_state_sha256': tensor_hash(model.state_dict())}
    return context, model, graphs, training, previous


def audit_training(repo, output, report, prepared, run, experiments, source, prior, profiles, *,
                   backbone_factory=backbone_architecture, profile_source_commit=None):
    """Read-only reconstruction; no decode, eager replay, forward or ORT session."""
    output = ignored_path(repo, output)
    expected, model, graphs, training, previous = training_context(repo, prepared, run, experiments,
        source, prior, profiles, backbone_factory=backbone_factory, profile_source_commit=profile_source_commit)
    context = report['context']
    environment = context['preflight']['environment']
    checkout_context(repo, environment)
    # Preserve historical checkout flags; all current source/dependency/hardware
    # fields and complete context are still reconstructed exactly.
    for key in ('git_commit', 'git_dirty'):
        expected['preflight']['environment'][key] = environment[key]
    if (set(report) != {'notice', 'status', 'created_utc', 'context', 'setup_records_sha256',
            'setup_audit', 'observations', 'model_state_after_sha256'}
            or report['notice'] != NOTICE or report['status'] != 'DIAGNOSTIC ONLY'
            or context != expected or report['model_state_after_sha256'] != expected['model_state_sha256']):
        raise ValueError('complete training report/context reconstruction mismatch')
    created = datetime.fromisoformat(report['created_utc'])
    if created.tzinfo != timezone.utc:
        raise ValueError('complete training report requires UTC creation time')
    if set(p.name for p in output.iterdir()) not in (
            {SETUP, KERNELS, OBSERVATIONS}, {SETUP, KERNELS, OBSERVATIONS, REPORT}):
        raise ValueError('complete training output file scope mismatch')
    if (output / REPORT).exists() and read_json(checked_file(output, REPORT)) != report:
        raise ValueError('complete training saved report mismatch')
    setup_path = checked_file(output, SETUP)
    if sha256(setup_path) != report['setup_records_sha256']:
        raise ValueError('complete training setup checksum mismatch')
    setup = audit_replay_setup(model, *graphs, output / KERNELS, read_json(setup_path))
    if setup != report['setup_audit']:
        raise ValueError('complete training setup audit reconstruction mismatch')
    observation_audit = audit_ordered(repo, output / OBSERVATIONS, graphs[0], expected['native_plan'],
        [c.id for c in training], previous, report['observations'],
        temperature=context['protocol']['temperature'], threshold=context['protocol']['threshold'])
    return {'notice': NOTICE, 'status': 'PASS', 'components': len(training),
        'complete_saved_preparation_retained_source_dependencies_and_prior': True,
        'setup': setup, 'ordered_observations': observation_audit,
        'baseline_inference': False, 'historical_inference_authentication': False}


def training_run(repo, prepared, run, experiments, source, prior, profiles, output, *,
                 backbone_factory=backbone_architecture, profile_source_commit=None):
    output = ignored_path(repo, output)
    if output.exists() or not output.name.startswith('PLACEHOLDER-'):
        raise ValueError('complete training output must be fresh and named PLACEHOLDER-*')
    context, model, graphs, training, previous = training_context(repo, prepared, run, experiments,
        source, prior, profiles, backbone_factory=backbone_factory, profile_source_commit=profile_source_commit)
    prepared = ignored_path(repo, prepared)
    output.mkdir(parents=True, exist_ok=False)
    kernels = output / KERNELS
    kernels.mkdir()
    engine = CompleteReplay(model, *graphs, kernels)
    if engine.plan != context['native_plan']:
        raise ValueError('complete training setup changed native scope')
    setup = audit_replay_setup(model, *graphs, kernels, engine.records)
    setup_path = output / SETUP
    with setup_path.open('x') as stream:
        stream.write(json_text(engine.records))
    writer = OrderedEvidence(repo, output / OBSERVATIONS, graphs[0], engine.plan, [c.id for c in training],
        previous, temperature=context['protocol']['temperature'], threshold=context['protocol']['threshold'])
    # No images are opened before complete context and actual runtime setup audit.
    for component in training:
        _, evidence = engine.run(component_input(prepared, component))
        writer.append(component.id, evidence)
        del evidence
    report = {'notice': NOTICE, 'status': 'DIAGNOSTIC ONLY',
        'created_utc': datetime.now(timezone.utc).isoformat(), 'context': context,
        'setup_records_sha256': sha256(setup_path), 'setup_audit': setup,
        'observations': writer.finish(), 'model_state_after_sha256': tensor_hash(model.state_dict())}
    audit_training(repo, output, report, prepared, run, experiments, source, prior, profiles,
                   backbone_factory=backbone_factory, profile_source_commit=profile_source_commit)
    with (output / REPORT).open('x') as stream:
        stream.write(json_text(report))
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=NOTICE + '; all ordered training components only')
    parser.add_argument('--prepared', type=Path, default=Path('data/prepared/synthetic-v2-selection'))
    parser.add_argument('--run', type=Path, default=Path('data/models/PLACEHOLDER-m3-baseline'))
    parser.add_argument('--experiments', nargs='+', type=Path, default=[
        Path('data/exports/PLACEHOLDER-m4-attempt1'), Path('data/exports/PLACEHOLDER-m4-attempt2')])
    parser.add_argument('--source', type=Path, default=Path('data/exports/PLACEHOLDER-m4-batchnorm2'))
    parser.add_argument('--prior', type=Path, default=Path('data/exports/PLACEHOLDER-m4-rounded-bn2'))
    parser.add_argument('--profiles', type=Path, default=Path('data/exports/PLACEHOLDER-m4-runtime-profiles1'))
    parser.add_argument('--profile-source-commit', help='Full local commit whose exact source tree matches ADR-022')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    repo = repository_root()
    try:
        output = ignored_path(repo, args.output)
        target = repo / 'ml/reports' / f'{output.name}.json'
        if (target.exists() or target.is_symlink() or target.parent.resolve() != target.parent
                or not output.name.startswith('PLACEHOLDER-')):
            raise ValueError('complete training aggregate target must be fresh, local and PLACEHOLDER-*')
        report = training_run(repo, args.prepared, args.run, args.experiments, args.source, args.prior,
            args.profiles, output, profile_source_commit=args.profile_source_commit)
        with target.open('x') as stream:
            stream.write(json_text(report))
    except (ValueError, OSError, RuntimeError, KeyError, TypeError, onnx.checker.ValidationError) as exc:
        print(f'PLACEHOLDER complete training replay failed: {exc}', file=sys.stderr)
        return 1
    print(f'PLACEHOLDER DIAGNOSTIC ONLY: {target.relative_to(repo)}; M4 remains incomplete')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
