"""PLACEHOLDER M4 numerical/decision parity contract; no export/runtime claim."""

from dataclasses import asdict, dataclass
import math

import numpy as np

from . import PLACEHOLDER_NOTICE
from .verify import calibrated_scores


@dataclass(frozen=True)
class ParityBudget:
    raw_absolute: float
    probability_absolute: float
    conservative_margin: float

    def __post_init__(self):
        if (any(type(x) not in (int, float) or not math.isfinite(x) or x < 0
                for x in (self.raw_absolute, self.probability_absolute, self.conservative_margin))
                or self.probability_absolute > 1 or self.conservative_margin > 1):
            raise ValueError('invalid parity budget')


# ADR-011 fixes these before any export/quantisation experiment. Zero frozen-
# threshold flips is independently required, even for errors inside each budget.
FLOAT_BUDGET = ParityBudget(1e-4, 1e-6, 0.0)
QUANTISED_BUDGET = ParityBudget(0.1, 0.001, 0.001)


def parity_report(reference_logits, candidate_logits, *, identifiers, temperature: float,
                  threshold: float, budget: ParityBudget) -> dict:
    """Compare the same ordered preprocessed inputs and frozen scoring layer.

    Returns PASS/FAIL with all mismatches so a failing export remains diagnosable.
    Failure details are per-component observations: persist only under ignored
    data/, with aggregates alone eligible for tracked reports.
    """
    reference, candidate = [np.asarray(values, dtype=np.float64)
                            for values in (reference_logits, candidate_logits)]
    ids = tuple(identifiers)
    if (reference.ndim != 1 or not len(reference) or candidate.shape != reference.shape
            or len(ids) != len(reference) or any(not isinstance(i, str) or not i for i in ids)
            or len(set(ids)) != len(ids) or not np.isfinite(reference).all()
            or not np.isfinite(candidate).all()
            or (np.abs(reference) > np.finfo(np.float32).max).any()
            or (np.abs(candidate) > np.finfo(np.float32).max).any()):
        raise ValueError('parity requires nonempty finite matched logits and unique identifiers')
    if (type(threshold) not in (int, float) or not math.isfinite(threshold)
            or not 0 <= threshold <= math.nextafter(1.0, math.inf)
            or not isinstance(budget, ParityBudget)):
        raise ValueError('invalid parity threshold or budget')
    if type(temperature) not in (int, float) or not math.isfinite(temperature) or not 0.05 <= temperature <= 20:
        raise ValueError('invalid parity temperature')
    reference_probability, candidate_probability = [calibrated_scores(values, temperature)
                                                   for values in (reference, candidate)]
    raw_errors = np.abs(candidate - reference)
    probability_errors = np.abs(candidate_probability - reference_probability)
    reference_decisions = reference_probability >= threshold
    candidate_decisions = candidate_probability >= threshold
    flips = reference_decisions != candidate_decisions
    # Add a separate conservative near-threshold referral; never use this to
    # erase parity failures at the original frozen operating point.
    conservative_decisions = candidate_probability >= max(0.0, threshold - budget.conservative_margin)
    lost_referrals = reference_decisions & ~conservative_decisions
    added_referrals = ~reference_decisions & conservative_decisions
    raw_failures = raw_errors > budget.raw_absolute
    probability_failures = probability_errors > budget.probability_absolute
    failures = raw_failures | probability_failures | flips
    cases = [{'component_id': ids[i], 'reference_raw_logit': float(reference[i]),
              'candidate_raw_logit': float(candidate[i]), 'raw_absolute_error': float(raw_errors[i]),
              'reference_probability': float(reference_probability[i]),
              'candidate_probability': float(candidate_probability[i]),
              'probability_absolute_error': float(probability_errors[i]),
              'raw_budget_exceeded': bool(raw_failures[i]),
              'probability_budget_exceeded': bool(probability_failures[i]),
              'frozen_threshold_flip': bool(flips[i])}
             for i in np.flatnonzero(failures)]
    return {'notice': PLACEHOLDER_NOTICE, 'version': '1.0.0',
            'status': 'FAIL' if failures.any() or lost_referrals.any() else 'PASS',
            'n': len(reference), 'budget': asdict(budget), 'temperature': temperature,
            'threshold': threshold, 'comparison': 'calibrated score >= frozen threshold',
            'max_raw_logit_absolute_error': float(raw_errors.max()),
            'mean_raw_logit_absolute_error': float(raw_errors.mean()),
            'max_calibrated_probability_absolute_error': float(probability_errors.max()),
            'mean_calibrated_probability_absolute_error': float(probability_errors.mean()),
            'raw_budget_exceeded_count': int(raw_failures.sum()),
            'probability_budget_exceeded_count': int(probability_failures.sum()),
            'frozen_threshold_flip_count': int(flips.sum()),
            'positive_to_below_threshold_count': int((reference_decisions & ~candidate_decisions).sum()),
            'below_threshold_to_positive_count': int((~reference_decisions & candidate_decisions).sum()),
            'conservative_margin_added_referrals': int(added_referrals.sum()),
            'conservative_margin_lost_reference_referrals': int(lost_referrals.sum()),
            'failure_cases': cases, 'failure_cases_storage': 'ignored data/ only; never tracked observations',
            'scope': 'numerical parity of same tensors; not clinical validation or device performance'}
