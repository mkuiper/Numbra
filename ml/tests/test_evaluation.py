"""Evaluation tests use invented logits and generated pixels only."""

from dataclasses import replace
import json
import math

import pytest

from numbra_ml.evaluation import (
    Prediction, component_predictions, evaluation_report, exact_interval,
    fit_temperature, index_components, metrics, read_component_index, select_threshold,
)
from numbra_ml.manifest import ManifestError, read_manifest
from numbra_ml.prepare import prepare_run


def cohort(split, per_class=100, *, prefix=None):
    prefix = prefix or split
    source = "synthetic-source-c" if split == "held_out" else "synthetic-source-a"
    return tuple(Prediction(f"{prefix}-{target}-{i}", split, target,
                            (1 if target else -1) * (0.2 + i / max(1, per_class)),
                            (source,), "background-stratum-1")
                 for target in (0, 1) for i in range(per_class))


def calibrated():
    return fit_temperature(cohort("calibration", 20))


@pytest.fixture
def prepared(tmp_path):
    output = tmp_path / "prepared"
    prepare_run(output, groups_per_source=16)
    return output


def test_index_is_deterministic_and_one_image_per_component(prepared):
    rows = read_manifest(prepared / "manifest.jsonl")
    report = json.loads((prepared / "preparation-report.json").read_text())
    forward = index_components(rows, report)
    backward = index_components(reversed(rows), report)
    assert forward == backward
    assert len(forward.components) == 48
    assert sum(len(item["records"]) for item in report["components"].values()) == 96
    for item in forward.components:
        assert item.row.record_id == min(report["components"][item.id]["records"])
        assert item.sources == tuple(report["components"][item.id]["sources"])
        assert item.target == report["components"][item.id]["target"]
    assert read_component_index(prepared / "manifest.jsonl", prepared / "preparation-report.json") == forward


@pytest.mark.parametrize("mutation", ["membership", "source", "split", "target", "mapping", "holdout"])
def test_index_rejects_corrupt_partition(prepared, mutation):
    rows = read_manifest(prepared / "manifest.jsonl")
    report = json.loads((prepared / "preparation-report.json").read_text())
    info = next(value for value in report["components"].values() if value["split"] == "train")
    if mutation == "membership":
        info["records"].append(info["records"][0])
    elif mutation == "source":
        info["sources"] = ["synthetic-source-c"]
    elif mutation == "split":
        info["split"] = "held_out"
    elif mutation == "target":
        info["target"] = 1 - info["target"]
    elif mutation == "mapping":
        report["record_components"].pop(info["records"][0])
    else:
        report["config"]["held_out_source"] = "synthetic-source-a"
    with pytest.raises(ManifestError):
        index_components(rows, report)


def test_index_checksum_is_checked_before_consumption(prepared):
    path = prepared / "manifest.jsonl"
    path.write_text(path.read_text() + "\n")
    with pytest.raises(ManifestError, match="checksum"):
        read_component_index(path, prepared / "preparation-report.json")


def test_index_reports_quarantine_and_conflicting_colour(prepared):
    rows = read_manifest(prepared / "manifest.jsonl")
    report = json.loads((prepared / "preparation-report.json").read_text())
    key, info = next((key, value) for key, value in report["components"].items() if value["split"] == "train")
    ids = set(info["records"])
    info.update(split="quarantine", target=None, quarantine_reasons=["manual_fixture_exclusion"])
    rows = tuple(replace(row, split="quarantine", label=replace(row.label, status="quarantined"))
                 if row.record_id in ids else row for row in rows)
    other_key, other = next((k, v) for k, v in report["components"].items() if v["split"] == "test")
    rows = tuple(replace(row, skin_tone=None) if row.record_id == other["records"][0] else row for row in rows)
    result = index_components(rows, report)
    assert result.excluded == {key: ("manual_fixture_exclusion",)}
    assert next(item for item in result.components if item.id == other_key).colour_stratum == "conflicting_or_partial"
    assert key not in {item.id for item in result.components}


def test_predictions_require_exact_component_coverage_and_finite_scores(prepared):
    index = read_component_index(prepared / "manifest.jsonl", prepared / "preparation-report.json")
    logits = {item.id: 0.0 for item in index.components}
    assert len(component_predictions(index, logits)) == len(index.components)
    with pytest.raises(ValueError, match="cover"):
        component_predictions(index, {**logits, "extra": 1.0})
    logits.pop(next(iter(logits)))
    with pytest.raises(ValueError, match="cover"):
        component_predictions(index, logits)
    logits = {item.id: float("nan") for item in index.components}
    with pytest.raises(ValueError, match="invalid"):
        component_predictions(index, logits)


@pytest.mark.parametrize("split", ["train", "threshold_validation", "test", "held_out"])
def test_temperature_rejects_wrong_fit_split(split):
    with pytest.raises(ValueError, match="calibration"):
        fit_temperature(cohort(split, 20))


@pytest.mark.parametrize("split", ["train", "calibration", "test", "held_out"])
def test_threshold_rejects_wrong_fit_split(split):
    with pytest.raises(ValueError, match="threshold_validation"):
        select_threshold(cohort(split), calibrated())


@pytest.mark.parametrize("per_class,expected", [(0, "unavailable_insufficient_groups"),
                                              (19, "unavailable_insufficient_groups"), (20, "fitted")])
def test_calibration_count_guard(per_class, expected):
    result = fit_temperature(cohort("calibration", per_class))
    assert result["status"] == expected
    if expected != "fitted":
        assert result["temperature"] == 1


def test_single_class_calibration_unavailable():
    values = tuple(item for item in cohort("calibration", 50) if item.target == 1)
    assert fit_temperature(values)["status"] == "unavailable_insufficient_groups"


def test_temperature_minimises_nll_and_exposes_boundaries():
    values = cohort("calibration", 100)
    # Deliberate high-confidence errors make a genuine interior optimum.
    noisy = tuple(replace(item, logit=-item.logit * 4 if i % 5 == 0 else item.logit * 4)
                  for i, item in enumerate(values))
    fit = fit_temperature(noisy)
    temp = fit["temperature"]
    optimum = metrics(noisy, temp, 0.5)["log_loss"]
    assert fit["boundary"] is None
    assert optimum < metrics(noisy, 1, 0.5)["log_loss"]
    assert optimum <= metrics(noisy, temp * 0.99, 0.5)["log_loss"]
    assert optimum <= metrics(noisy, temp * 1.01, 0.5)["log_loss"]
    assert fit_temperature(values)["boundary"] == "minimum_temperature"
    inverted = tuple(replace(item, logit=-item.logit) for item in values)
    assert fit_temperature(inverted)["boundary"] == "maximum_temperature"


@pytest.mark.parametrize("per_class,expected", [(0, "unavailable_insufficient_groups"),
                                              (99, "unavailable_insufficient_groups"), (100, "selected")])
def test_threshold_count_guard(per_class, expected):
    result = select_threshold(cohort("threshold_validation", per_class), calibrated())
    assert result["status"] == expected
    if expected != "selected":
        assert result["threshold"] == 0
        assert result["fallback"] == "unselected refer-all"


def test_threshold_requires_separate_sufficient_calibration():
    result = select_threshold(cohort("threshold_validation"), fit_temperature(cohort("calibration", 19)))
    assert result["status"] == "unavailable_insufficient_groups"
    assert result["threshold"] == 0


def test_high_sensitivity_selects_highest_qualifying_threshold_and_ties():
    calibration = calibrated()
    calibration["temperature"] = 1.0
    values = cohort("threshold_validation")
    result = select_threshold(values, calibration)
    scores = {item.logit: 1 / (1 + math.exp(-item.logit)) for item in values}
    # Five of 100 positive groups fall below the sixth smallest positive score.
    expected = scores[0.25]
    assert result["threshold"] == pytest.approx(expected)
    assert result["target_evidence"] == "empirical_target_only"
    measured = metrics(values, 1, result["threshold"])
    assert measured["tp"] == 95 and measured["fn"] == 5
    assert measured["sensitivity"] == 0.95
    all_tied = tuple(replace(item, logit=0) for item in values)
    tied = select_threshold(all_tied, calibration)
    assert tied["threshold"] == 0.5
    assert tied["degenerate"] == "refer_all"
    assert metrics(all_tied, 1, 0.5)["tp"] == 100
    assert metrics(all_tied, 1, math.nextafter(0.5, math.inf))["tp"] == 0


def test_secondary_specificity_and_above_one_sentinel():
    calibration = calibrated()
    calibration["temperature"] = 1
    values = cohort("threshold_validation")
    result = select_threshold(values, calibration, endpoint="specificity")
    measured = metrics(values, 1, result["threshold"])
    assert measured["specificity"] == 0.8
    tied = tuple(replace(item, logit=1000) for item in values)
    fallback = select_threshold(tied, calibration, endpoint="specificity")
    assert fallback["threshold"] == math.nextafter(1.0, math.inf)
    assert fallback["degenerate"] == "all_negative"
    assert metrics(tied, 1, fallback["threshold"])["specificity"] == 1
    assert metrics(tied, 1, fallback["threshold"])["sensitivity"] == 0


@pytest.mark.parametrize("successes,total", [(0, 10), (10, 10), (1, 2), (95, 100), (100, 100)])
def test_exact_intervals_against_closed_forms_and_plan(successes, total):
    lower, upper = exact_interval(successes, total)
    if successes == 0:
        assert lower == 0
        assert upper == pytest.approx(1 - 0.025 ** (1 / total), abs=1e-12)
    elif successes == total:
        assert upper == 1
        assert lower == pytest.approx(0.025 ** (1 / total), abs=1e-12)
    elif total == 2:
        assert lower == pytest.approx(1 - math.sqrt(0.975), abs=1e-12)
        assert upper == pytest.approx(math.sqrt(0.975), abs=1e-12)
    else:
        assert lower == pytest.approx(0.887, abs=0.001)  # ADR-001 methods plan example.
        assert upper == pytest.approx(0.984, abs=0.001)
    symmetric = exact_interval(total - successes, total)
    assert lower == pytest.approx(1 - symmetric[1], abs=1e-12)
    assert upper == pytest.approx(1 - symmetric[0], abs=1e-12)


def test_empty_and_invalid_binomial_counts():
    assert exact_interval(0, 0) is None
    for counts in [(-1, 10), (11, 10), (1.5, 2), (0, -1)]:
        with pytest.raises(ValueError):
            exact_interval(*counts)


def test_metrics_auc_ties_reliability_extremes_and_stable_loss():
    tied = tuple(replace(item, logit=0) for item in cohort("test", 2))
    report = metrics(tied, 1, 0.5)
    assert report["auc"] == 0.5
    assert report["brier"] == 0.25
    assert report["log_loss"] == pytest.approx(math.log(2))
    assert report["ece"] == 0
    assert sum(item["count"] for item in report["reliability_bins"]) == 4
    assert report["reliability_bins"][5]["count"] == 4
    assert metrics(cohort("test", 2), 1, 0.5)["auc"] == 1
    inverted = tuple(replace(item, logit=-item.logit) for item in cohort("test", 2))
    assert metrics(inverted, 1, 0.5)["auc"] == 0
    extremes = tuple(replace(item, logit=1000 if item.target else -1000) for item in cohort("test", 2))
    report = metrics(extremes, 1, 0.5)
    assert report["reliability_bins"][0]["count"] == 2
    assert report["reliability_bins"][-1]["count"] == 2
    assert report["log_loss"] == 0 and report["brier"] == 0
    assert metrics(tuple(replace(item, logit=-item.logit) for item in extremes), 1, 0.5)["log_loss"] == 1000


def test_auc_with_partial_ties_is_pairwise_probability():
    values = (Prediction("a", "test", 1, 0), Prediction("b", "test", 1, 2),
              Prediction("c", "test", 0, 0), Prediction("d", "test", 0, 1))
    assert metrics(values, 1, 0.5)["auc"] == 0.625


def test_missing_single_class_empty_metrics_are_explicit():
    values = tuple(item for item in cohort("test", 2) if item.target == 1)
    report = metrics(values, 1, 0)
    assert report["sensitivity"] == 1
    assert report["specificity"] is None and report["auc"] is None
    assert report["specificity_interval_95"] is None
    empty = metrics((), 1, 0)
    for key in ("sensitivity", "specificity", "auc", "brier", "log_loss", "ece"):
        assert empty[key] is None
    assert empty["n"] == 0


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -float("inf")])
def test_nonfinite_logit_rejected(value):
    with pytest.raises(ValueError, match="invalid"):
        metrics((Prediction("a", "test", 1, value),), 1, 0)


def test_duplicate_component_across_splits_rejected():
    values = cohort("calibration", 20)
    with pytest.raises(ValueError, match="leakage"):
        evaluation_report(values + (replace(values[0], split="test"),), held_out_source="synthetic-source-c")


def test_frozen_protocol_does_not_depend_on_test_or_heldout_scores():
    values = sum((cohort(split, 100 if split == "threshold_validation" else 20)
                  for split in ("calibration", "threshold_validation", "test", "held_out")), ())
    before = evaluation_report(values, held_out_source="synthetic-source-c")
    changed = tuple(replace(item, logit=-item.logit, target=1 - item.target)
                    if item.split in {"test", "held_out"} else item for item in values)
    after = evaluation_report(changed, held_out_source="synthetic-source-c")
    for key in ("calibration", "primary_operating_point", "secondary_operating_point"):
        assert before[key] == after[key]
    assert before["splits"]["test"]["primary"] != after["splits"]["test"]["primary"]
    assert before["splits"]["held_out"]["score_sha256"] != after["splits"]["held_out"]["score_sha256"]
    assert before["target_names"] == {"1": "synthetic circle", "0": "synthetic square"}
    assert "single held-out source" in before["source_fold"]["description"]
    assert "PLACEHOLDER" in before["notice"]
    json.dumps(before, allow_nan=False)


def test_report_missing_colour_and_multi_source_membership():
    values = sum((cohort(split, 2) for split in ("calibration", "threshold_validation", "test", "held_out")), ())
    changed = tuple(replace(item, sources=("synthetic-source-a", "synthetic-source-b"),
                            colour_stratum="missing") if item.split == "test" else item for item in values)
    report = evaluation_report(changed, held_out_source="synthetic-source-c")
    test = report["splits"]["test"]
    assert test["primary"]["n"] == 4
    assert test["by_source"]["synthetic-source-a"]["n"] == 4
    assert test["by_source"]["synthetic-source-b"]["n"] == 4
    assert test["missing_or_conflicting_colour_fraction"] == 1
    assert report["primary_operating_point"]["fallback"] == "unselected refer-all"
    assert test["primary"]["sensitivity"] == 1
    assert test["primary"]["specificity"] == 0


def test_report_rejects_any_source_leakage():
    values = cohort("test", 2)
    with pytest.raises(ValueError, match="boundary"):
        evaluation_report(tuple(replace(item, sources=("synthetic-source-c",)) for item in values),
                          held_out_source="synthetic-source-c")


def test_known_links_cannot_be_counted_as_separate_components(prepared):
    rows = read_manifest(prepared / "manifest.jsonl")
    report = json.loads((prepared / "preparation-report.json").read_text())
    key, info = next((key, value) for key, value in report["components"].items() if value["split"] == "train")
    record = info["records"].pop()
    other = {**info, "records": [record]}
    report["components"]["fabricated-independent-unit"] = other
    report["record_components"][record] = "fabricated-independent-unit"
    with pytest.raises(ManifestError, match="known linked"):
        index_components(rows, report)


def test_both_class_count_guards_apply_independently():
    calibration_values = tuple(item for item in cohort("calibration", 100)
                               if item.target == 1 or int(item.component_id.rsplit("-", 1)[1]) < 19)
    assert fit_temperature(calibration_values)["status"] == "unavailable_insufficient_groups"
    threshold_values = tuple(item for item in cohort("threshold_validation", 100)
                             if item.target == 0 or int(item.component_id.rsplit("-", 1)[1]) < 99)
    assert select_threshold(threshold_values, calibrated())["status"] == "unavailable_insufficient_groups"


def test_exact_count_guard_fallback_is_not_a_selected_target():
    result = select_threshold(cohort("threshold_validation", 20), calibrated())
    assert result["target_evidence"] == "unavailable"
    counts = metrics(cohort("test", 3), 1, result["threshold"])
    assert counts["tp"] == 3 and counts["tn"] == 0
    assert counts["sensitivity_interval_95"][0] < 0.95


@pytest.mark.parametrize("temperature", [0, 0.049, 20.01, float("nan"), float("inf")])
def test_invalid_temperatures_fail(temperature):
    with pytest.raises(ValueError, match="temperature"):
        metrics(cohort("test", 2), temperature, 0.5)


@pytest.mark.parametrize("threshold", [-0.1, 1.01, float("nan"), float("inf")])
def test_invalid_thresholds_fail(threshold):
    with pytest.raises(ValueError, match="threshold"):
        metrics(cohort("test", 2), 1, threshold)


def test_all_zero_logits_calibration_has_explicit_boundary():
    fit = fit_temperature(tuple(replace(item, logit=0) for item in cohort("calibration", 20)))
    assert fit["temperature"] == 20
    assert fit["boundary"] == "maximum_temperature"
