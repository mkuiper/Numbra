import pytest

from numbra_ml.taxonomy import (
    Classification, Label, LabelFamily, LabelStatus, ReactionStatus,
    map_exact_diagnosis, unresolved_label,
)


@pytest.mark.parametrize("family,target", [
    ("leprosy", 1), ("leprosy_differential", 0), ("other", 0), ("unresolved", None),
])
def test_synthetic_binary_evidence_target(family, target):
    label = Label("SYNTHETIC:shape", None if family == "unresolved" else "synthetic_shape",
                  family, "synthetic")
    assert label.binary_target == target


@pytest.mark.parametrize("status", ["provisional", "unresolved", "quarantined", "withdrawn"])
def test_uncertain_labels_never_become_primary_ground_truth(status):
    assert Label("leprosy", "leprosy", "leprosy", status).binary_target is None


def test_exact_mapping_preserves_source_and_alias():
    label = map_exact_diagnosis("tinea versicolor")
    assert label.original_label == "tinea versicolor"
    assert label.diagnosis == "pityriasis_versicolor"
    assert label.family == LabelFamily.DIFFERENTIAL
    assert label.status == LabelStatus.PROVISIONAL
    assert label.binary_target is None
    assert map_exact_diagnosis("pityriasis versicolor").diagnosis == label.diagnosis


@pytest.mark.parametrize("name", ["suspected leprosy", "Leprosy", "leprosy-like", "safe", "refer_for_review"])
def test_unrecognised_names_are_not_fuzzy_mapped(name):
    label = map_exact_diagnosis(name)
    assert label == unresolved_label(name)
    assert label.diagnosis is None and label.binary_target is None


def test_reaction_and_classification_are_independent_explicit_annotations():
    label = Label("leprosy", "leprosy", "leprosy", "confirmed", "MB", "type_1")
    assert label.leprosy_classification == Classification.MB
    assert label.reaction_status == ReactionStatus.TYPE_1
    assert label.binary_target == 1
    assert map_exact_diagnosis("leprosy").leprosy_classification == Classification.UNKNOWN


@pytest.mark.parametrize("kwargs", [
    {"family": "refer_for_review"}, {"status": "model_confirmed"},
    {"leprosy_classification": "PB"}, {"reaction_status": "none"}, {"diagnosis": None},
])
def test_taxonomy_rejects_invalid_or_inferred_labels(kwargs):
    values = dict(original_label="vitiligo", diagnosis="vitiligo", family="leprosy_differential",
                  status="provisional")
    with pytest.raises(ValueError):
        Label(**(values | kwargs))
