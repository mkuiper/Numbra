"""Versioned M0 taxonomy. Disease evidence and referral actions are separate."""

from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType


TAXONOMY_VERSION = "1.0.0"


class LabelFamily(StrEnum):
    LEPROSY = "leprosy"
    DIFFERENTIAL = "leprosy_differential"
    OTHER = "other"
    UNRESOLVED = "unresolved"


class Classification(StrEnum):
    PB = "PB"
    MB = "MB"
    UNKNOWN = "unknown"


class ReactionStatus(StrEnum):
    TYPE_1 = "type_1"
    TYPE_2 = "type_2"
    NONE = "none"
    UNKNOWN = "unknown"


class LabelStatus(StrEnum):
    PROVISIONAL = "provisional"
    CONFIRMED = "confirmed"
    SYNTHETIC = "synthetic"
    UNRESOLVED = "unresolved"
    QUARANTINED = "quarantined"
    WITHDRAWN = "withdrawn"


@dataclass(frozen=True)
class Label:
    original_label: str
    diagnosis: str | None
    family: LabelFamily
    status: LabelStatus
    leprosy_classification: Classification = Classification.UNKNOWN
    reaction_status: ReactionStatus = ReactionStatus.UNKNOWN

    def __post_init__(self) -> None:
        # Direct construction has the same enums/invariants as manifest parsing.
        for name, enum in (
            ("family", LabelFamily), ("status", LabelStatus),
            ("leprosy_classification", Classification), ("reaction_status", ReactionStatus),
        ):
            object.__setattr__(self, name, enum(getattr(self, name)))
        if not isinstance(self.original_label, str) or not self.original_label.strip():
            raise ValueError("original_label must preserve a nonempty source label")
        if self.family != LabelFamily.UNRESOLVED:
            if not isinstance(self.diagnosis, str) or not self.diagnosis.strip():
                raise ValueError("resolved families require a named diagnosis")
        elif self.diagnosis is not None:
            raise ValueError("unresolved mapping must not invent a diagnosis")
        if self.family != LabelFamily.LEPROSY and (
            self.leprosy_classification != Classification.UNKNOWN
            or self.reaction_status != ReactionStatus.UNKNOWN
        ):
            raise ValueError("PB/MB and reaction annotations only belong to leprosy labels")

    @property
    def binary_target(self) -> int | None:
        """Explicit evidence target; zero never means no referral or disease absence."""
        if self.status not in {LabelStatus.CONFIRMED, LabelStatus.SYNTHETIC}:
            return None
        if self.family == LabelFamily.UNRESOLVED:
            return None
        return int(self.family == LabelFamily.LEPROSY)


def unresolved_label(original_label: str) -> Label:
    """Unknown source names stay unresolved; no fuzzy or substring remapping."""
    return Label(original_label, None, LabelFamily.UNRESOLVED, LabelStatus.UNRESOLVED)


# Exact-name proposed vocabulary from M0. This is not a source import approval.
# Eczema/dermatitis remains a proposed local challenge, pending clinical ranking.
EXACT_DIAGNOSES = MappingProxyType({
    "leprosy": (LabelFamily.LEPROSY, "leprosy"),
    "tinea corporis": (LabelFamily.DIFFERENTIAL, "tinea_corporis"),
    "tinea versicolor": (LabelFamily.DIFFERENTIAL, "pityriasis_versicolor"),
    "pityriasis versicolor": (LabelFamily.DIFFERENTIAL, "pityriasis_versicolor"),
    "vitiligo": (LabelFamily.DIFFERENTIAL, "vitiligo"),
    "psoriasis": (LabelFamily.DIFFERENTIAL, "psoriasis"),
    "pityriasis alba": (LabelFamily.DIFFERENTIAL, "pityriasis_alba"),
    "pityriasis rotunda": (LabelFamily.DIFFERENTIAL, "pityriasis_rotunda"),
    "post-inflammatory hypopigmentation": (LabelFamily.DIFFERENTIAL, "post_inflammatory_hypopigmentation"),
    "morphea": (LabelFamily.DIFFERENTIAL, "morphea"),
    "lupus vulgaris": (LabelFamily.DIFFERENTIAL, "lupus_vulgaris"),
    "discoid lupus erythematosus": (LabelFamily.DIFFERENTIAL, "discoid_lupus_erythematosus"),
    "post-kala-azar dermal leishmaniasis": (LabelFamily.DIFFERENTIAL, "pkdl"),
    "cutaneous leishmaniasis": (LabelFamily.DIFFERENTIAL, "cutaneous_leishmaniasis"),
    "Kaposi sarcoma": (LabelFamily.DIFFERENTIAL, "kaposi_sarcoma"),
    "neurofibromatosis": (LabelFamily.DIFFERENTIAL, "neurofibromatosis"),
    "macular PKDL": (LabelFamily.DIFFERENTIAL, "macular_pkdl"),
    "nodular PKDL": (LabelFamily.DIFFERENTIAL, "nodular_pkdl"),
    "eczema": (LabelFamily.DIFFERENTIAL, "eczema"),
    "dermatitis": (LabelFamily.DIFFERENTIAL, "dermatitis"),
})


def map_exact_diagnosis(original_label: str) -> Label:
    """Map proposed exact vocabulary, always provisional until independently confirmed."""
    mapping = EXACT_DIAGNOSES.get(original_label)
    if mapping is None:
        return unresolved_label(original_label)
    family, diagnosis = mapping
    return Label(original_label, diagnosis, family, LabelStatus.PROVISIONAL)
