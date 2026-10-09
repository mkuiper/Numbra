"""Strict local JSONL manifests with explicit provenance and leakage checks."""

from dataclasses import asdict, dataclass
from datetime import date
import json
from pathlib import Path, PurePosixPath
from typing import Iterable

from jsonschema import Draft202012Validator, FormatChecker

from .schema import SCHEMA_VERSION, manifest_schema
from .taxonomy import Label, LabelFamily, LabelStatus, TAXONOMY_VERSION


class ManifestError(ValueError):
    """A manifest failed structural or semantic validation."""


@dataclass(frozen=True)
class Source:
    id: str
    version: str
    url: str


@dataclass(frozen=True)
class Licence:
    id: str
    url: str
    attribution: str


@dataclass(frozen=True)
class Confirmation:
    method: str
    reference: str
    date: str


@dataclass(frozen=True)
class SkinTone:
    scheme: str
    value: str


@dataclass(frozen=True)
class Observations:
    # None distinguishes an omitted field from an explicitly recorded unknown.
    sensation: str | None = None
    sensation_method: str | None = None
    sensation_assessor: str | None = None
    patch_count: int | None = None
    duration_days: int | None = None
    widespread: str | None = None
    nerve_symptoms: str | None = None
    new_weakness: str | None = None
    eye_symptoms: str | None = None
    skin_or_earlobe_changes: str | None = None
    eyebrow_loss: str | None = None
    painless_wounds_or_burns: str | None = None
    volunteer_concern: str | None = None
    contact_history: str | None = None

    def to_dict(self) -> dict:
        # These nullable fields can be explicitly null; categorical None is omitted.
        nullable = {"sensation_method", "sensation_assessor", "patch_count", "duration_days"}
        return {k: v for k, v in asdict(self).items() if v is not None or k in nullable}


_VALIDATOR = Draft202012Validator(manifest_schema(), format_checker=FormatChecker())


@dataclass(frozen=True)
class ManifestRow:
    record_id: str
    image_path: str
    sha256: str
    source: Source
    licence: Licence
    label: Label
    confirmed_by: Confirmation | None
    patient_id: str | None
    group_id: str | None
    split: str
    synthetic: bool
    placeholder: bool
    skin_tone: SkinTone | None
    observations: Observations
    schema_version: str = SCHEMA_VERSION
    taxonomy_version: str = TAXONOMY_VERSION

    @classmethod
    def from_dict(cls, data: dict) -> "ManifestRow":
        errors = sorted(_VALIDATOR.iter_errors(data), key=lambda e: str(list(e.path)))
        if errors:
            error = errors[0]
            raise ManifestError(f"{'.'.join(map(str, error.path)) or 'row'}: {error.message}")
        try:
            row = cls(
                **{k: v for k, v in data.items() if k not in {
                    "source", "licence", "label", "confirmed_by", "skin_tone", "observations",
                }},
                source=Source(**data["source"]), licence=Licence(**data["licence"]),
                label=Label(**data["label"]),
                confirmed_by=Confirmation(**data["confirmed_by"]) if data["confirmed_by"] else None,
                skin_tone=SkinTone(**data["skin_tone"]) if data["skin_tone"] else None,
                observations=Observations(**data["observations"]),
            )
            row._validate_semantics()
            return row
        except (ValueError, TypeError) as exc:
            raise ManifestError(str(exc)) from exc

    def _validate_semantics(self) -> None:
        path = PurePosixPath(self.image_path)
        if path.is_absolute() or ".." in path.parts or "\\" in self.image_path:
            raise ManifestError("image_path must stay relative to the data root")
        if path.as_posix() != self.image_path or self.image_path in {".", ""}:
            raise ManifestError("image_path must be a normalised file path")
        if self.synthetic:
            if not self.placeholder:
                raise ManifestError("synthetic rows must be PLACEHOLDER")
            if self.label.status not in {LabelStatus.SYNTHETIC, LabelStatus.PROVISIONAL,
                                         LabelStatus.UNRESOLVED, LabelStatus.QUARANTINED,
                                         LabelStatus.WITHDRAWN}:
                raise ManifestError("synthetic labels cannot claim clinical confirmation")
            if self.confirmed_by is not None:
                raise ManifestError("synthetic fixtures cannot invent clinical confirmation")
            if not self.label.original_label.startswith("SYNTHETIC:"):
                raise ManifestError("synthetic source label must start with SYNTHETIC:")
            if self.skin_tone is not None and self.skin_tone.scheme != "synthetic_colour":
                raise ManifestError("synthetic colour strata cannot claim clinical skin-tone annotations")
        elif self.label.status == LabelStatus.SYNTHETIC:
            raise ManifestError("real rows cannot use synthetic ground truth")
        if self.label.status == LabelStatus.CONFIRMED and (
            self.confirmed_by is None or self.label.family == LabelFamily.UNRESOLVED
        ):
            raise ManifestError("confirmed label needs confirmation and a resolved diagnosis")
        if self.confirmed_by is not None:
            date.fromisoformat(self.confirmed_by.date)
            if self.confirmed_by.method.lower() in {"model", "model_prediction", "prediction"}:
                raise ManifestError("model predictions cannot confirm labels")

    @property
    def group_key(self) -> tuple[str, str] | None:
        return (self.source.id, self.group_id) if self.group_id is not None else None

    def to_dict(self) -> dict:
        value = asdict(self)
        value["observations"] = self.observations.to_dict()
        return value


def validate_manifest(rows: Iterable[ManifestRow]) -> tuple[ManifestRow, ...]:
    """Fail on split leakage; M2 will merge duplicate-connected groups before splits."""
    rows = tuple(rows)
    seen: set[str] = set()
    assignments: dict[tuple, str] = {}
    source_versions: dict[str, tuple[str, str, str, str, str]] = {}
    for row in rows:
        # Revalidate direct dataclass construction, too.
        ManifestRow.from_dict(row.to_dict())
        if row.record_id in seen:
            raise ManifestError(f"duplicate record_id: {row.record_id}")
        seen.add(row.record_id)
        provenance = (row.source.version, row.source.url, row.licence.id,
                      row.licence.url, row.licence.attribution)
        previous = source_versions.setdefault(row.source.id, provenance)
        if previous != provenance:
            raise ManifestError(f"inconsistent source version/licence: {row.source.id}")
        keys = [("hash", row.sha256)]
        if row.group_id is not None:
            keys.append(("group", row.source.id, row.group_id))
        if row.patient_id is not None:
            keys.append(("patient", row.source.id, row.patient_id))
        for key in keys:
            previous_split = assignments.setdefault(key, row.split)
            if previous_split != row.split:
                raise ManifestError(f"split leakage for {key[0]}: {previous_split} vs {row.split}")
    return rows


def _unique_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ManifestError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def read_manifest(path: Path) -> tuple[ManifestRow, ...]:
    rows = []
    with Path(path).open(encoding="utf-8") as stream:
        for number, line in enumerate(stream, 1):
            try:
                if not line.strip():
                    raise ManifestError("blank JSONL row")
                data = json.loads(line, object_pairs_hook=_unique_object)
                rows.append(ManifestRow.from_dict(data))
            except (ValueError, TypeError) as exc:
                raise ManifestError(f"{path}:{number}: {exc}") from exc
    return validate_manifest(rows)


def write_manifest(path: Path, rows: Iterable[ManifestRow]) -> None:
    rows = validate_manifest(rows)
    content = "".join(json.dumps(row.to_dict(), sort_keys=True, ensure_ascii=False,
                                 allow_nan=False) + "\n" for row in rows)
    Path(path).write_text(content, encoding="utf-8")
