"""M4 contract probes on invented logits only; no export or patient data."""

import json
import math

import numpy as np
import pytest

from numbra_ml.parity import FLOAT_BUDGET, QUANTISED_BUDGET, ParityBudget, parity_report
from numbra_ml.verify import calibrated_scores


def compare(reference, candidate, *, budget=QUANTISED_BUDGET, threshold=0.5, temperature=19.15):
    return parity_report(reference, candidate, identifiers=[f'synthetic-{i}' for i in range(len(reference))],
                         budget=budget, temperature=temperature, threshold=threshold)


def test_exact_parity_and_stable_extreme_sigmoid():
    values = [-1e6, -20, 0, 20, 1e6]
    report = compare(values, values)
    assert report['status'] == 'PASS' and report['n'] == 5
    assert report['max_raw_logit_absolute_error'] == 0
    assert report['max_calibrated_probability_absolute_error'] == 0
    assert report['frozen_threshold_flip_count'] == 0 and report['failure_cases'] == []
    assert calibrated_scores(values, 19.15).tolist()[::4] == [0, 1]
    assert 'PLACEHOLDER' in report['notice']
    json.dumps(report, allow_nan=False)


def test_tiny_probability_error_must_fail_when_frozen_threshold_decision_flips():
    # At high temperature both errors pass; the action still flips. A margin can
    # recover the referral but cannot make the original parity result pass.
    report = compare([0.001, -0.001], [-0.001, 0.001])
    assert report['status'] == 'FAIL'
    assert report['raw_budget_exceeded_count'] == 0
    assert report['probability_budget_exceeded_count'] == 0
    assert report['frozen_threshold_flip_count'] == 2
    assert report['positive_to_below_threshold_count'] == 1
    assert report['below_threshold_to_positive_count'] == 1
    assert report['conservative_margin_lost_reference_referrals'] == 0
    assert report['conservative_margin_added_referrals'] == 1
    assert len(report['failure_cases']) == 2


def test_raw_error_fails_even_when_sigmoid_saturation_hides_it():
    report = compare([1000], [1001])
    assert report['status'] == 'FAIL'
    assert report['raw_budget_exceeded_count'] == 1
    assert report['probability_budget_exceeded_count'] == 0
    assert report['frozen_threshold_flip_count'] == 0


def test_probability_budget_independent_of_raw_budget():
    report = compare([1], [1.09], temperature=0.05, threshold=0.99,
                     budget=ParityBudget(0.1, 1e-10, 0))
    assert report['raw_budget_exceeded_count'] == 0
    assert report['probability_budget_exceeded_count'] == 1 and report['status'] == 'FAIL'


def test_inclusive_comparison_and_separate_conservative_added_referral():
    # The frozen equality is inclusive, also in the float contract.
    assert compare([0], [0], budget=FLOAT_BUDGET)['status'] == 'PASS'
    report = compare([-0.05, -3], [-0.05, -3])
    assert report['status'] == 'PASS' and report['frozen_threshold_flip_count'] == 0
    assert report['conservative_margin_added_referrals'] == 1
    assert report['conservative_margin_lost_reference_referrals'] == 0


def test_missing_refer_all_and_above_one_sentinel_stay_explicit():
    assert compare([-100, 0, 100], [-100, 0, 100], threshold=0)['status'] == 'PASS'
    sentinel = math.nextafter(1., math.inf)
    report = compare([1000], [1000], threshold=sentinel)
    assert report['frozen_threshold_flip_count'] == 0 and report['status'] == 'PASS'
    assert report['conservative_margin_added_referrals'] == 1


def test_within_numerical_budgets_without_flips_passes():
    report = compare([-5, 5], [-5.01, 5.01])
    assert report['status'] == 'PASS'
    assert report['max_raw_logit_absolute_error'] == pytest.approx(0.01)
    assert report['mean_raw_logit_absolute_error'] == pytest.approx(0.01)


@pytest.mark.parametrize('reference,candidate,ids', [([], [], []), ([0], [0, 1], ['a']),
                                                  ([math.nan], [0], ['a']), ([0], [math.inf], ['a']),
                                                  ([[0]], [[0]], ['a']), ([0, 1], [0, 1], ['a', 'a']),
                                                  ([0], [0], ['']), ([0], [0], [1]),
                                                  ([1e300], [0], ['a']), ([0], [-1e300], ['a'])])
def test_invalid_inputs_are_rejected(reference, candidate, ids):
    with pytest.raises(ValueError, match='matched logits'):
        parity_report(reference, candidate, identifiers=ids, temperature=1, threshold=0.5, budget=FLOAT_BUDGET)


@pytest.mark.parametrize('temperature', [0, 0.01, 21, math.inf, math.nan, True])
def test_invalid_temperature(temperature):
    with pytest.raises(ValueError, match='temperature'):
        compare([0], [0], temperature=temperature)


@pytest.mark.parametrize('threshold', [-1, math.inf, math.nan, True])
def test_invalid_threshold(threshold):
    with pytest.raises(ValueError, match='threshold'):
        compare([0], [0], threshold=threshold)


@pytest.mark.parametrize('args', [(-1, 0, 0), (1, 2, 0), (1, 0, 2), (math.nan, 0, 0), (True, 0, 0)])
def test_invalid_budget(args):
    with pytest.raises(ValueError, match='budget'):
        ParityBudget(*args)
