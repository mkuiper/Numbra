from dataclasses import replace
import json

from jsonschema import Draft202012Validator
import pytest

from numbra_ml.manifest import (
    Confirmation, ManifestError, ManifestRow, Observations, SkinTone, read_manifest,
    validate_manifest, write_manifest,
)
from numbra_ml.schema import manifest_schema, OBSERVATION_ANSWERS


def test_json_schema_is_valid():
    Draft202012Validator.check_schema(manifest_schema())


def test_manifest_round_trip_preserves_taxonomy_and_provenance(tmp_path, tiny_fixture):
    path = tmp_path / "fixture.jsonl"
    write_manifest(path, tiny_fixture)
    assert read_manifest(path) == tiny_fixture
    assert all(row.licence.id == "Apache-2.0" for row in read_manifest(path))
    assert {row.source.id for row in tiny_fixture} == {"synthetic-shapes", "synthetic-colours"}


@pytest.mark.parametrize("field,value", [
    ("schema_version", "2.0.0"), ("taxonomy_version", "2.0.0"),
    ("split", "validation"), ("sha256", "not-a-checksum"), ("synthetic", "yes"),
    ("placeholder", False), ("image_path", "../other.png"),
    ("image_path", "/outside.png"), ("image_path", "a/../other.png"),
    ("image_path", "C:\\outside.png"), ("image_path", "a//b.png"), ("image_path", "."),
    ("record_id", ""), ("record_id", " "),
    ("confirmed_by", {"method": "clinical", "reference": "invented", "date": "2026-10-09"}),
])
def test_invalid_manifest_rows_are_rejected(row_factory, field, value):
    data = row_factory().to_dict() | {field: value}
    with pytest.raises(ManifestError):
        ManifestRow.from_dict(data)


@pytest.mark.parametrize("field", ["source", "licence", "label", "confirmed_by", "patient_id", "group_id", "split"])
def test_required_provenance_fields_cannot_be_omitted(row_factory, field):
    data = row_factory().to_dict()
    del data[field]
    with pytest.raises(ManifestError):
        ManifestRow.from_dict(data)


def test_extra_fields_and_invalid_label_family_fail(row_factory):
    data = row_factory().to_dict()
    with pytest.raises(ManifestError, match="Additional properties"):
        ManifestRow.from_dict(data | {"patient_name": "not permitted"})
    data["label"]["family"] = "refer_for_review"
    with pytest.raises(ManifestError):
        ManifestRow.from_dict(data)


def test_missing_confirmation_never_promoted_to_ground_truth(row_factory):
    row = row_factory()
    data = row.to_dict()
    data["synthetic"] = False
    data["label"]["status"] = "confirmed"
    with pytest.raises(ManifestError, match="needs confirmation"):
        ManifestRow.from_dict(data)
    data["confirmed_by"] = {"method": "model_prediction", "reference": "v1", "date": "2026-10-09"}
    with pytest.raises(ManifestError, match="cannot confirm"):
        ManifestRow.from_dict(data)
    data["confirmed_by"] = {"method": "clinical_examination", "reference": "opaque", "date": "invalid"}
    with pytest.raises(ManifestError):
        ManifestRow.from_dict(data)


def test_future_confirmed_record_keeps_explicit_assertion_separate(row_factory):
    # Schema can describe a future record; dataset policy still blocks real loading.
    data = row_factory().to_dict()
    data["synthetic"] = False
    data["label"].update(status="confirmed", original_label="leprosy", diagnosis="leprosy")
    data["confirmed_by"] = {"method": "clinical_examination", "reference": "opaque", "date": "2026-10-09"}
    row = ManifestRow.from_dict(data)
    assert row.confirmed_by == Confirmation("clinical_examination", "opaque", "2026-10-09")
    assert row.label.binary_target == 1


def test_unknown_group_and_all_new_observation_answers_round_trip(row_factory, tmp_path):
    row = row_factory()
    answers = {field: "uncertain" for field in OBSERVATION_ANSWERS}
    answers.update(contact_history="declined", sensation="not_tested", patch_count=None,
                   sensation_method="untrained_fixture", sensation_assessor="invented",
                   duration_days=None)
    row = replace(row, patient_id=None, group_id=None, observations=Observations(**answers))
    path = tmp_path / "missing.jsonl"
    write_manifest(path, [row])
    restored = read_manifest(path)[0]
    assert restored.group_key is None and restored.patient_id is None
    assert restored.observations.contact_history == "declined"
    assert restored.observations.volunteer_concern == "uncertain"
    assert restored.observations == row.observations


def test_missing_answer_remains_distinct_from_recorded_unknown(row_factory):
    omitted = row_factory()
    data = omitted.to_dict()
    data["observations"]["volunteer_concern"] = "unknown"
    explicit = ManifestRow.from_dict(data)
    assert omitted.observations.volunteer_concern is None
    assert explicit.observations.volunteer_concern == "unknown"


def test_synthetic_tone_is_only_an_invented_colour_stratum(row_factory):
    row = replace(row_factory(), skin_tone=SkinTone("synthetic_colour", "dark-background"))
    assert ManifestRow.from_dict(row.to_dict()).skin_tone == row.skin_tone
    with pytest.raises(ManifestError, match="clinical skin-tone"):
        ManifestRow.from_dict(replace(row, skin_tone=SkinTone("Fitzpatrick", "VI")).to_dict())


@pytest.mark.parametrize("answers", [
    {"patch_count": -1}, {"patch_count": True}, {"duration_days": -2},
    {"volunteer_concern": False}, {"contact_history": "none"}, {"sensation": "normal"},
])
def test_invalid_observations_do_not_coerce_missingness(row_factory, answers):
    data = row_factory().to_dict() | {"observations": answers}
    with pytest.raises(ManifestError):
        ManifestRow.from_dict(data)


@pytest.mark.parametrize("kind", ["group", "patient", "hash"])
def test_group_patient_and_duplicate_hash_leakage_rejected(row_factory, kind):
    first, second = row_factory(1), row_factory(2, split="test")
    field = {"group": "group_id", "patient": "patient_id", "hash": "sha256"}[kind]
    second = replace(second, **{field: getattr(first, field)})
    with pytest.raises(ManifestError, match="split leakage"):
        validate_manifest([first, second])


def test_patient_with_multiple_groups_stays_in_one_split(row_factory):
    rows = [row_factory(1), row_factory(2)]
    rows[1] = replace(rows[1], patient_id=rows[0].patient_id)
    assert validate_manifest(rows) == tuple(rows)


def test_source_namespacing_and_global_duplicate_check(row_factory):
    first = row_factory(1)
    second = replace(row_factory(2, source="synthetic-colours", split="test"),
                     group_id=first.group_id, patient_id=first.patient_id)
    assert validate_manifest([first, second]) == (first, second)
    with pytest.raises(ManifestError, match="hash"):
        validate_manifest([first, replace(second, sha256=first.sha256)])


def test_repeated_record_id_and_source_provenance_mismatch_rejected(row_factory):
    first, second = row_factory(1), row_factory(2)
    with pytest.raises(ManifestError, match="record_id"):
        validate_manifest([first, replace(second, record_id=first.record_id)])
    with pytest.raises(ManifestError, match="source version/licence"):
        validate_manifest([first, replace(second, source=replace(second.source, version="v2"))])


@pytest.mark.parametrize("text", ["\n", "{broken}\n", "[]\n", '{"a":1,"a":2}\n'])
def test_malformed_jsonl_reports_line_number(tmp_path, text):
    path = tmp_path / "bad.jsonl"
    path.write_text(text)
    with pytest.raises(ManifestError, match=r"bad.jsonl:1:"):
        read_manifest(path)


def test_reader_validates_entire_manifest_before_split_filtering(tmp_path, row_factory):
    first, second = row_factory(1), row_factory(2, split="test")
    second = replace(second, group_id=first.group_id)
    path = tmp_path / "leak.jsonl"
    # Deliberately bypass writer so that reader validation is exercised.
    path.write_text("\n".join(json.dumps(row.to_dict()) for row in [first, second]) + "\n")
    with pytest.raises(ManifestError, match="split leakage"):
        read_manifest(path)


@pytest.mark.parametrize("field,value", [
    ("record_id", "id\n"), ("group_id", "g1\n"), ("patient_id", "p1\n"),
    ("sha256", "a" * 64 + "\n"),
])
def test_identifier_and_hash_control_characters_rejected(row_factory, field, value):
    with pytest.raises(ManifestError):
        ManifestRow.from_dict(row_factory().to_dict() | {field: value})


def real_row_data(row_factory):
    data = row_factory().to_dict()
    data["synthetic"] = False
    data["label"].update(status="confirmed", original_label="leprosy", diagnosis="leprosy")
    data["confirmed_by"] = {"method": "clinical_examination", "reference": "opaque", "date": "2026-10-09"}
    return data


@pytest.mark.parametrize("method", ["ai", "classifier", "volunteer_impression", "self_report", "model"])
def test_confirmation_allowlist_rejects_unapproved_methods(row_factory, method):
    data = real_row_data(row_factory)
    data["confirmed_by"]["method"] = method
    with pytest.raises(ManifestError):
        ManifestRow.from_dict(data)


@pytest.mark.parametrize("value", ["20261009", "2026-W41-5", "9999-01-01", "2026-10-09\n"])
def test_confirmation_dates_are_calendar_dates_and_not_future(row_factory, value):
    data = real_row_data(row_factory)
    data["confirmed_by"]["date"] = value
    with pytest.raises(ManifestError):
        ManifestRow.from_dict(data)


def test_photo_and_source_confirmation_remain_explicitly_weaker():
    assert Confirmation("dermatologist_photo_assessment", "opaque", "2026-10-09").evidence_category == "photo_only_weaker"
    assert Confirmation("source_dataset_assertion", "opaque", "2026-10-09").evidence_category == "source_assertion_unverified"


@pytest.mark.parametrize("diagnosis,family", [
    ("vitiligo", "leprosy"), ("leprosy", "other"), ("typo", "leprosy_differential"),
])
def test_real_diagnosis_family_must_match_vocabulary(row_factory, diagnosis, family):
    data = real_row_data(row_factory)
    data["label"].update(diagnosis=diagnosis, family=family)
    with pytest.raises(ManifestError):
        ManifestRow.from_dict(data)


def test_named_unknown_real_diagnosis_can_be_preserved_as_other(row_factory):
    data = real_row_data(row_factory)
    data["label"].update(diagnosis="unlisted_condition", family="other")
    assert ManifestRow.from_dict(data).label.diagnosis == "unlisted_condition"


@pytest.mark.parametrize("tone", [
    {"scheme": "Fitzpatrick", "value": "VII", "assigned_by": "clinician"},
    {"scheme": "Monk", "value": "11", "assigned_by": "self_report"},
    {"scheme": "Monk", "value": "1", "assigned_by": "generator"},
    {"scheme": "arbitrary", "value": "1", "assigned_by": "algorithm"},
])
def test_invalid_real_tone_annotation_rejected(row_factory, tone):
    with pytest.raises(ManifestError):
        ManifestRow.from_dict(real_row_data(row_factory) | {"skin_tone": tone})


def test_capture_and_controlled_tone_provenance_roundtrip(row_factory):
    data = real_row_data(row_factory) | {
        "skin_tone": {"scheme": "Monk", "value": "10", "assigned_by": "photo_annotator"},
        "capture": {"site_id": "opaque-site", "device_class": "phone", "body_site": "arm"},
    }
    assert ManifestRow.from_dict(ManifestRow.from_dict(data).to_dict()).to_dict() == data


def test_quarantine_is_per_connected_group_not_per_row(row_factory):
    first, second = row_factory(1, split="quarantine"), row_factory(2)
    second = replace(second, patient_id=first.patient_id)
    with pytest.raises(ManifestError, match="split leakage"):
        validate_manifest([first, second])
    assert len(validate_manifest([first, replace(second, split="quarantine")])) == 2
