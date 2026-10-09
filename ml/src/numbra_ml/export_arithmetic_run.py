"""ADR-024 guarded retained training PLACEHOLDER arithmetic; never bundle."""

import argparse
from datetime import datetime, timezone
from pathlib import Path
import sys

import onnx

from .export_arithmetic_evidence import OrderedArithmeticEvidence, audit_arithmetic_ordered
from .export_arithmetic_replay import ArithmeticReplay, audit_arithmetic_setup
from .export_provenance import audit_environment, checked_file
from .export_remaining_evidence import read_json
from .export_remaining_retained import training_rows
from .export_remaining_run import REPORT as RETAINED_REPORT, audit_training, training_context
from .prepare import repository_root
from .pretrained import ignored_path, sha256
from .train import json_text
from .training import tensor_hash
from .verify import backbone_architecture

NOTICE = 'PLACEHOLDER complete retained training arithmetic diagnostic only; never bundle'
REPORT = 'PLACEHOLDER-arithmetic-training-report.json'
SETUP = 'PLACEHOLDER-arithmetic-setup-records.json'
KERNELS = 'PLACEHOLDER-arithmetic-kernels'
OBSERVATIONS = 'PLACEHOLDER-arithmetic-observations'


def arithmetic_context(repo, retained, prepared, run, experiments, source, prior, profiles, *,
                       backbone_factory=backbone_architecture, retained_source_commit=None,
                       profile_source_commit=None):
    """Reconstruct the entire original experiment before sessions or inputs."""
    retained = ignored_path(repo, retained)
    path = checked_file(retained, RETAINED_REPORT)
    retained_hash = sha256(path)
    retained_audit = audit_training(repo, retained, read_json(path), prepared, run, experiments,
        source, prior, profiles, backbone_factory=backbone_factory,
        source_commit=retained_source_commit, profile_source_commit=profile_source_commit)
    context, model, graphs, components, previous = training_context(repo, prepared, run,
        experiments, source, prior, profiles, backbone_factory=backbone_factory,
        profile_source_commit=profile_source_commit)
    if sha256(checked_file(retained, RETAINED_REPORT)) != retained_hash:
        raise ValueError('arithmetic retained report changed during context audit')
    context['notice'] = NOTICE
    context['protocol'].update(decision='ADR-024', stage='complete retained training arithmetic',
        new_native_model_inference=False, image_decoding=False, original_control_replay=False,
        whole_model_recipe_parity='UNVERIFIED')
    context.update(retained_report_sha256=retained_hash, retained_report_audit=retained_audit)
    return context, model, graphs, components, previous


def audit_arithmetic_training(repo, output, report, retained, prepared, run, experiments,
                              source, prior, profiles, *, backbone_factory=backbone_architecture,
                              retained_source_commit=None, profile_source_commit=None,
                              source_commit=None):
    """Complete read-only reconstruction without decode, sessions or recipes.

    Historical source snapshots are supplied explicitly by the auditor, never
    inferred from a report. All live dependencies, hardware, original evidence,
    ordered scope, unchanged fits/budgets and new arithmetic evidence are checked.
    Recorded observations cannot authenticate past inference or numerical truth.
    """
    output = ignored_path(repo, output)
    expected, model, graphs, components, previous = arithmetic_context(repo, retained,
        prepared, run, experiments, source, prior, profiles, backbone_factory=backbone_factory,
        retained_source_commit=retained_source_commit, profile_source_commit=profile_source_commit)
    environment = report['context']['preflight']['environment']
    environment_audit = audit_environment(repo, environment,
        expected['preflight']['environment'], source_commit=source_commit)
    historical = ('git_commit', 'git_dirty')
    if source_commit is not None:
        historical += ('source_files_sha256', 'source_tree_sha256')
    for key in historical:
        expected['preflight']['environment'][key] = environment[key]
    if (set(report) != {'notice', 'status', 'created_utc', 'context', 'setup_records_sha256',
            'setup_audit', 'observations', 'model_state_after_sha256'}
            or report['notice'] != NOTICE or report['status'] != 'DIAGNOSTIC ONLY'
            or report['context'] != expected
            or report['model_state_after_sha256'] != expected['model_state_sha256']):
        raise ValueError('arithmetic training report/context reconstruction mismatch')
    if datetime.fromisoformat(report['created_utc']).tzinfo != timezone.utc:
        raise ValueError('arithmetic training report requires UTC creation time')
    if set(p.name for p in output.iterdir()) not in (
            {SETUP, KERNELS, OBSERVATIONS}, {SETUP, KERNELS, OBSERVATIONS, REPORT}):
        raise ValueError('arithmetic training output file scope mismatch')
    if (output / REPORT).exists() and read_json(checked_file(output, REPORT)) != report:
        raise ValueError('arithmetic training saved report mismatch')
    setup_path = checked_file(output, SETUP)
    if sha256(setup_path) != report['setup_records_sha256']:
        raise ValueError('arithmetic training setup checksum mismatch')
    setup = audit_arithmetic_setup(model, *graphs, output / KERNELS, read_json(setup_path))
    if setup != report['setup_audit']:
        raise ValueError('arithmetic training setup audit reconstruction mismatch')
    protocol = expected['protocol']
    observations = audit_arithmetic_ordered(repo, output / OBSERVATIONS, graphs[0],
        expected['native_plan'], [c.id for c in components], previous, report['observations'],
        temperature=protocol['temperature'], threshold=protocol['threshold'])
    return {'notice': NOTICE, 'status': 'PASS', 'components': len(components),
        'complete_original_and_arithmetic_evidence': True,
        'source_environment_audit': environment_audit, 'retained': expected['retained_report_audit'],
        'setup': setup, 'ordered_observations': observations, 'baseline_inference': False,
        'historical_inference_authentication': False, 'whole_model_recipe_parity': 'UNVERIFIED',
        'deployment_selection': False}


def arithmetic_run(repo, retained, prepared, run, experiments, source, prior, profiles, output, *,
                   backbone_factory=backbone_architecture, retained_source_commit=None,
                   profile_source_commit=None):
    output = ignored_path(repo, output)
    if output.exists() or not output.name.startswith('PLACEHOLDER-'):
        raise ValueError('arithmetic training output must be fresh and named PLACEHOLDER-*')
    context, model, graphs, components, previous = arithmetic_context(repo, retained, prepared,
        run, experiments, source, prior, profiles, backbone_factory=backbone_factory,
        retained_source_commit=retained_source_commit, profile_source_commit=profile_source_commit)
    output.mkdir(parents=True, exist_ok=False)
    kernels = output / KERNELS
    kernels.mkdir()
    engine = ArithmeticReplay(model, *graphs, kernels)
    if engine.plan != context['native_plan']:
        raise ValueError('arithmetic training setup changed native scope')
    setup = audit_arithmetic_setup(model, *graphs, kernels, engine.records)
    setup_path = output / SETUP
    with setup_path.open('x') as stream:
        stream.write(json_text(engine.records))
    protocol = context['protocol']
    writer = OrderedArithmeticEvidence(repo, output / OBSERVATIONS, graphs[0], engine.plan,
        [c.id for c in components], previous, temperature=protocol['temperature'],
        threshold=protocol['threshold'])
    # Every original artifact and new setup graph is audited before reader access.
    # Exhaustion (including the reader's final scope check) precedes finish/report.
    for identifier, retained_row in training_rows(repo, retained, prepared, run, experiments,
            source, prior, profiles, backbone_factory=backbone_factory,
            source_commit=retained_source_commit, profile_source_commit=profile_source_commit):
        _, evidence = engine.run(retained_row)
        writer.append(identifier, evidence)
        del evidence, retained_row
    report = {'notice': NOTICE, 'status': 'DIAGNOSTIC ONLY',
        'created_utc': datetime.now(timezone.utc).isoformat(), 'context': context,
        'setup_records_sha256': sha256(setup_path), 'setup_audit': setup,
        'observations': writer.finish(), 'model_state_after_sha256': tensor_hash(model.state_dict())}
    audit_arithmetic_training(repo, output, report, retained, prepared, run, experiments,
        source, prior, profiles, backbone_factory=backbone_factory,
        retained_source_commit=retained_source_commit, profile_source_commit=profile_source_commit)
    with (output / REPORT).open('x') as stream:
        stream.write(json_text(report))
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=NOTICE + '; all ordered training components only')
    parser.add_argument('--retained', type=Path,
        default=Path('data/exports/PLACEHOLDER-m4-remaining-training3'))
    parser.add_argument('--prepared', type=Path, default=Path('data/prepared/synthetic-v2-selection'))
    parser.add_argument('--run', type=Path, default=Path('data/models/PLACEHOLDER-m3-baseline'))
    parser.add_argument('--experiments', nargs='+', type=Path, default=[
        Path('data/exports/PLACEHOLDER-m4-attempt1'), Path('data/exports/PLACEHOLDER-m4-attempt2')])
    parser.add_argument('--source', type=Path, default=Path('data/exports/PLACEHOLDER-m4-batchnorm2'))
    parser.add_argument('--prior', type=Path, default=Path('data/exports/PLACEHOLDER-m4-rounded-bn2'))
    parser.add_argument('--profiles', type=Path, default=Path('data/exports/PLACEHOLDER-m4-runtime-profiles1'))
    parser.add_argument('--retained-source-commit', help='Full exact local ADR-023 source snapshot')
    parser.add_argument('--profile-source-commit', help='Full exact local ADR-022 source snapshot')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    repo = repository_root()
    try:
        output = ignored_path(repo, args.output)
        target = repo / 'ml/reports' / f'{output.name}.json'
        if (target.exists() or target.is_symlink() or target.parent.resolve() != target.parent
                or not output.name.startswith('PLACEHOLDER-')):
            raise ValueError('arithmetic training aggregate target must be fresh, local and PLACEHOLDER-*')
        report = arithmetic_run(repo, args.retained, args.prepared, args.run, args.experiments,
            args.source, args.prior, args.profiles, output,
            retained_source_commit=args.retained_source_commit,
            profile_source_commit=args.profile_source_commit)
        with target.open('x') as stream:
            stream.write(json_text(report))
    except (ValueError, OSError, RuntimeError, KeyError, TypeError, onnx.checker.ValidationError) as exc:
        print(f'PLACEHOLDER retained training arithmetic failed: {exc}', file=sys.stderr)
        return 1
    print(f'PLACEHOLDER DIAGNOSTIC ONLY: {target.relative_to(repo)}; M4 remains incomplete')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
