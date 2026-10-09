"""Bootstrap versus pairwise arithmetic on invented logits."""
from dataclasses import replace
import numpy as np
import pytest
from numbra_ml.evaluation import Prediction, bootstrap_intervals
from numbra_ml.evaluation import evaluation_report
from numbra_ml.train import add_bootstrap

def values():
    return tuple(Prediction(str(i), "test", target, logit) for i, (target, logit) in
                 enumerate([(0, -1), (0, 0), (1, 0), (1, 1)]))

def test_bootstrap_reproducible_and_tied_auc_matches_pairwise_reference():
    cohort = values()
    result = bootstrap_intervals(cohort, 1, 0.5, seed=42, replicates=100)
    assert result == bootstrap_intervals(cohort, 1, 0.5, seed=42, replicates=100)
    samples = []
    rng = np.random.default_rng(42)
    for _ in range(100):
        draw = [cohort[i] for i in rng.integers(0, 4, size=4)]
        positives = [p.logit for p in draw if p.target]
        negatives = [p.logit for p in draw if not p.target]
        if positives and negatives:
            samples.append(np.mean([float(p > n) + 0.5 * float(p == n) for p in positives for n in negatives]))
    assert result["metrics"]["auc"]["valid_replicates"] == len(samples)
    assert result["metrics"]["auc"]["interval_95"] == np.quantile(samples, [0.025, 0.975]).tolist()
    assert result["metrics"]["brier"]["valid_replicates"] == 100
    assert "PLACEHOLDER" in result["notice"]

def test_perfect_scores_and_one_class_unavailability():
    cohort = tuple(replace(p, logit=10 if p.target else -10) for p in values())
    result = bootstrap_intervals(cohort, 1, 0.5, seed=10, replicates=100)
    for metric in ("sensitivity", "specificity", "auc"):
        assert result["metrics"][metric]["interval_95"] == [1, 1]
    one = bootstrap_intervals([cohort[0]], 1, 0.5, seed=10, replicates=100)
    assert one["metrics"]["auc"]["interval_95"] is None
    assert one["metrics"]["sensitivity"]["valid_replicates"] == 0
    assert one["metrics"]["specificity"]["interval_95"] == [1, 1]
    empty = bootstrap_intervals([], 1, 0.5, seed=10, replicates=100)
    assert all(m["interval_95"] is None and m["valid_replicates"] == 0 for m in empty["metrics"].values())

@pytest.mark.parametrize("split", ["train", "calibration", "threshold_validation"])
def test_bootstrap_rejects_fitting_splits(split):
    with pytest.raises(ValueError, match="frozen"):
        bootstrap_intervals([replace(p, split=split) for p in values()], 1, 0.5, seed=1)

def test_bootstrap_rejects_pooled_splits_and_duplicate_components():
    cohort = values()
    with pytest.raises(ValueError, match="pool"):
        bootstrap_intervals([*cohort[:-1], replace(cohort[-1], split="held_out")], 1, 0.5, seed=1)
    with pytest.raises(ValueError, match="duplicate"):
        bootstrap_intervals([*cohort, cohort[0]], 1, 0.5, seed=1)

@pytest.mark.parametrize("kwargs", [{"seed": -1}, {"seed": True}, {"seed": 1, "replicates": 99},
                                   {"seed": 1, "replicates": 10001}, {"seed": 1, "replicates": True}])
def test_bootstrap_rejects_invalid_config(kwargs):
    with pytest.raises(ValueError, match="bootstrap"):
        bootstrap_intervals(values(), 1, 0.5, **kwargs)


def test_report_bootstrap_reuses_identical_cohorts_and_suppresses_tiny_subgroups():
    predictions = tuple(Prediction(f'{split}-{i}', split, i % 2, float(i % 3),
                                   ('synthetic-source-c',) if split == 'held_out' else ('synthetic-source-a',),
                                   'tiny' if i < 4 else 'large')
                        for split in ('calibration', 'threshold_validation', 'test', 'held_out') for i in range(40))
    report = evaluation_report(predictions, held_out_source='synthetic-source-c')
    add_bootstrap(report, predictions, seed=20, replicates=100)
    for split, source in (('test', 'synthetic-source-a'), ('held_out', 'synthetic-source-c')):
        boot = report['splits'][split]['bootstrap']
        assert boot['overall'] == boot[f'source:{source}']
        assert boot['colour:tiny']['status'] == 'suppressed_small_cell'
        assert boot['colour:tiny']['metrics'] is None
        assert boot['colour:large']['status'] == 'suppressed_small_cell'
