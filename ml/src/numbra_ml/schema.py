"""JSON Schema for one JSONL row; extra fields fail rather than disappearing."""

import json

from .taxonomy import (
    Classification, LabelFamily, LabelStatus, ReactionStatus, TAXONOMY_VERSION,
)


SCHEMA_VERSION = "1.1.0"
CONFIRMATION_METHODS = (
    "clinical_examination", "slit_skin_smear", "histopathology",
    "dermatologist_photo_assessment", "source_dataset_assertion",
)
SPLITS = (
    "unassigned", "train", "calibration", "threshold_validation", "test",
    "held_out", "quarantine",
)
ANSWERS = ("yes", "no", "uncertain", "unknown", "declined")
SENSATION = ("present", "reduced", "absent", "uncertain", "unknown", "declined", "not_tested")
OBSERVATION_ANSWERS = (
    "widespread", "nerve_symptoms", "new_weakness", "eye_symptoms",
    "skin_or_earlobe_changes", "eyebrow_loss", "painless_wounds_or_burns",
    "volunteer_concern", "contact_history",
)


def _object(properties: dict, *, required: list[str] | None = None) -> dict:
    return {
        "type": "object", "additionalProperties": False, "properties": properties,
        "required": list(properties) if required is None else required,
    }


def manifest_schema() -> dict:
    """Structural schema; manifest.py adds provenance/group/path semantics."""
    text = {"type": "string", "minLength": 1, "pattern": r"\S"}
    nullable_text = {"anyOf": [text, {"type": "null"}]}
    identifier = {"type": "string", "pattern": r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}(?![\s\S])"}
    source = _object({"id": identifier, "version": text, "url": text})
    licence = _object({"id": text, "url": text, "attribution": text})
    label = _object({
        "original_label": text, "diagnosis": nullable_text,
        "family": {"enum": list(LabelFamily)}, "status": {"enum": list(LabelStatus)},
        "leprosy_classification": {"enum": list(Classification)},
        "reaction_status": {"enum": list(ReactionStatus)},
    })
    confirmation = _object({
        "method": {"enum": list(CONFIRMATION_METHODS)}, "reference": text,
        "date": {"type": "string", "format": "date", "pattern": r"^[0-9]{4}-[0-9]{2}-[0-9]{2}(?![\s\S])"},
    })
    observations = {
        "sensation": {"enum": list(SENSATION)},
        "sensation_method": nullable_text, "sensation_assessor": nullable_text,
        "patch_count": {"type": ["integer", "null"], "minimum": 0},
        "duration_days": {"type": ["integer", "null"], "minimum": 0},
        **{name: {"enum": list(ANSWERS)} for name in OBSERVATION_ANSWERS},
    }
    tone = _object({
        "scheme": {"enum": ["synthetic_colour", "Fitzpatrick", "Monk"]}, "value": text,
        "assigned_by": {"enum": ["generator", "self_report", "clinician", "photo_annotator", "algorithm"]},
    })
    capture = _object({"site_id": nullable_text, "device_class": nullable_text,
                       "body_site": nullable_text})
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "Numbra PLACEHOLDER manifest row v1 (M1–M4 synthetic-only policy)",
        **_object({
            "schema_version": {"const": SCHEMA_VERSION},
            "taxonomy_version": {"const": TAXONOMY_VERSION},
            "record_id": identifier,
            "image_path": text,
            "sha256": {"type": "string", "pattern": r"^[a-f0-9]{64}(?![\s\S])"},
            "source": source, "licence": licence, "label": label,
            "confirmed_by": {"anyOf": [confirmation, {"type": "null"}]},
            "patient_id": {"anyOf": [identifier, {"type": "null"}]},
            "group_id": {"anyOf": [identifier, {"type": "null"}]},
            "split": {"enum": list(SPLITS)},
            "synthetic": {"type": "boolean"}, "placeholder": {"type": "boolean"},
            "skin_tone": {"anyOf": [tone, {"type": "null"}]},
            "observations": _object(observations, required=[]),
            "capture": capture,
        }, required=["schema_version", "taxonomy_version", "record_id", "image_path", "sha256",
                     "source", "licence", "label", "confirmed_by", "patient_id", "group_id",
                     "split", "synthetic", "placeholder", "skin_tone", "observations"]),
    }


if __name__ == "__main__":
    print(json.dumps(manifest_schema(), indent=2, ensure_ascii=False))
