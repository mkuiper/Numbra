"""ADR-024 lossless ordered PLACEHOLDER arithmetic evidence; never bundle.

Persists every original control and both engines of every fixed arithmetic
recipe. This supplied-row API does not establish training/source provenance:
a guarded runner must first verify the entire original retained experiment,
audit every new setup graph before inputs, exhaust the ordered reader and
independently reconstruct this evidence before publishing a complete report.
No image decoding, sessions or inference occurs here.
"""

from .export_arithmetic_replay import reconstruct_arithmetic, targets
from .export_remaining_arithmetic import RECIPES
from .export_remaining_evidence import (OrderedEvidence, _audit_ordered, aggregate,
                                       digest_json, scope)
from .export_remaining_replay import KINDS, ORIGINS

NOTICE = 'PLACEHOLDER persisted complete arithmetic diagnostic only; never bundle'


def arithmetic_scope(source, plan, identifiers, temperature, threshold):
    protocol = scope(source, plan, identifiers, temperature, threshold)
    protocol.update({'notice': NOTICE, 'decision': 'ADR-024',
        'ordered_targets_sha256': digest_json(targets(plan)),
        'fixed_recipes': [[operator, list(variants)] for operator, variants in RECIPES.items()],
        'graph_contexts': list(KINDS), 'input_origins': list(ORIGINS),
        'engines': ['eager', 'runtime']})
    return protocol


def arithmetic_aggregate(*args):
    report = aggregate(*args)
    report.update({'notice': NOTICE, 'whole_model_parity': 'UNVERIFIED',
                   'deployment_selection': False})
    return report


class OrderedArithmeticEvidence(OrderedEvidence):
    """Complete ordered rows; validation/prior checks precede every row write.

    Shared storage preserves explicit dictionary order, float32/int64 bits,
    signed zeros and all original arrays. Only bit-identical arrays deduplicate.
    Partial runs have no completed index, and finish is not a provenance audit.
    """

    notice = NOTICE
    make_protocol = staticmethod(arithmetic_scope)
    reconstruct = staticmethod(reconstruct_arithmetic)
    aggregate = staticmethod(arithmetic_aggregate)

    @staticmethod
    def retained(evidence):
        return evidence['retained']


def audit_arithmetic_ordered(repo, output, source, plan, identifiers, prior, report, *,
                             temperature, threshold):
    """Stream complete rows with a per-row array cache, without inference.

    Rebuild every signed comparison/accounting term, original control/lineage,
    metric aggregate, unchanged ADR-011 original-graph parity and prior bits.
    Recorded observations do not authenticate historical inference or prove
    that recipe outputs equal independently rerun arithmetic.
    """
    return _audit_ordered(repo, output, source, plan, identifiers, prior, report,
        temperature=temperature, threshold=threshold, persistence=OrderedArithmeticEvidence)
