"""ADR-024 guarded retained PLACEHOLDER training inputs; diagnostic only.

The complete ADR-023 audit finishes before the first row is exposed. Reading
rechecks every accessed row and tensor, without decoding images or inference.
No arithmetic experiment, deployment selection or historical authentication.
"""

from .export_provenance import checked_file
from .export_remaining_evidence import (INDEX, NOTICE as EVIDENCE_NOTICE, check_prior,
    decode, prior_logits, read_json)
from .export_remaining_replay import reconstruct_row
from .export_remaining_run import (OBSERVATIONS, REPORT, audit_training,
                                   training_context)
from .pretrained import ignored_path, sha256
from .verify import backbone_architecture

NOTICE = 'PLACEHOLDER retained training reader diagnostic only; never bundle'


def training_rows(repo, retained, prepared, run, experiments, source, prior, profiles, *,
                  source_commit=None, profile_source_commit=None,
                  backbone_factory=backbone_architecture):
    """Yield all ordered rows only after complete provenance/observation audit.

    The caller must exhaust this iterator for a complete replay. No optional
    node/component subset is offered. Old graphs, controls and observations
    remain read-only. A partial consumer has no complete-experiment evidence.
    """
    retained = ignored_path(repo, retained)
    report = read_json(checked_file(retained, REPORT))
    audit_training(repo, retained, report, prepared, run, experiments, source, prior,
        profiles, source_commit=source_commit, profile_source_commit=profile_source_commit,
        backbone_factory=backbone_factory)
    # Reconstruct the exact graph/native plan and prior scope; no forward call.
    context, _, graphs, training, previous = training_context(repo, prepared, run,
        experiments, source, prior, profiles, profile_source_commit=profile_source_commit,
        backbone_factory=backbone_factory)
    root = retained / OBSERVATIONS
    index_path = checked_file(root, INDEX)
    if sha256(index_path) != report['observations']['evidence_index_sha256']:
        raise ValueError('retained training index changed after complete audit')
    index = read_json(index_path)
    ids = [component.id for component in training]
    previous = prior_logits(previous, ids)
    used = set()
    for position, (identifier, record) in enumerate(zip(ids, index['rows'])):
        relative = f'rows/PLACEHOLDER-component-{position:04d}.json'
        path = checked_file(root, relative)
        if (set(record) != {'position', 'path', 'sha256'} or record['position'] != position
                or record['path'] != relative or sha256(path) != record['sha256']):
            raise ValueError('retained training ordered row changed after complete audit')
        row = read_json(path)
        if (set(row) != {'notice', 'position', 'component_id', 'evidence', 'metrics'}
                or row['notice'] != EVIDENCE_NOTICE or row['position'] != position
                or row['component_id'] != identifier):
            raise ValueError('retained training ordered row identity mismatch')
        evidence = decode(root, row['evidence'], index['arrays'], used, {})
        if reconstruct_row(graphs[0], context['native_plan'], evidence) != row['metrics']:
            raise ValueError('retained training reconstructed row metric mismatch')
        check_prior(evidence, previous, position)
        yield identifier, evidence
        del evidence, row
    if len(index['rows']) != len(ids) or used != set(index['arrays']):
        raise ValueError('retained training complete row/array scope mismatch')
