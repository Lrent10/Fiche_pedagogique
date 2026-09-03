from __future__ import annotations

import re
import unicodedata


CURRICULUM_LEVEL = "4e"
CLASS_LEVEL_ERROR = "Cette fiche utilise le programme de 4e. La classe doit appartenir au niveau 4e."


def _without_accents(value: str) -> str:
    return "".join(
        character
        for character in unicodedata.normalize("NFKD", value)
        if not unicodedata.combining(character)
    )


def class_label_level(class_label: object) -> str | None:
    """Extract the level from the deliberately small set of supported class labels."""
    if not isinstance(class_label, str):
        return None
    normalized = _without_accents(class_label).strip().lower()
    match = re.fullmatch(r"(\d+)\s*(?:e|eme)(?:\s+.+)?", normalized)
    return f"{match.group(1)}e" if match else None


def class_label_matches_level(class_label: object, curriculum_level: str) -> bool:
    return class_label_level(class_label) == curriculum_level.strip().lower()
