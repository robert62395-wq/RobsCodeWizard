"""Translation map loader, validator, and accessor."""
import json
from pathlib import Path
from typing import Optional

SCHEMA_VERSION = "1.0"
MAP_PATH = Path(__file__).parent.parent / "data" / "translation_map.json"

REQUIRED_TOP_KEYS = {"schema_version", "map_version", "generated", "entries"}
REQUIRED_ENTRY_KEYS = {"id", "vdt", "odot", "confidence", "match_basis",
                       "score", "user_override", "notes"}
VALID_CONFIDENCE = {"exact", "best-guess", "unmatched", "manual"}


def load(path: Path = MAP_PATH) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    validate(data)
    return data


def save(data: dict, path: Path = MAP_PATH) -> None:
    validate(data)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def validate(data: dict) -> None:
    missing = REQUIRED_TOP_KEYS - data.keys()
    if missing:
        raise ValueError(f"Translation map missing keys: {missing}")
    if data["schema_version"] != SCHEMA_VERSION:
        raise ValueError(f"Unsupported schema_version: {data['schema_version']}")
    for i, entry in enumerate(data["entries"]):
        missing = REQUIRED_ENTRY_KEYS - entry.keys()
        if missing:
            raise ValueError(f"Entry {i} missing keys: {missing}")
        if entry["confidence"] not in VALID_CONFIDENCE:
            raise ValueError(f"Entry {i} invalid confidence: {entry['confidence']}")
        if entry["vdt"] is None and entry["odot"] is None:
            raise ValueError(f"Entry {i} has both vdt and odot null")


def find_by_vdt(code: str, data: Optional[dict] = None) -> Optional[dict]:
    data = data if data is not None else load()
    for e in data["entries"]:
        if e["vdt"] and e["vdt"]["code"] == code:
            return e
    return None


def find_by_odot(code: str, data: Optional[dict] = None) -> Optional[dict]:
    data = data if data is not None else load()
    for e in data["entries"]:
        if e["odot"] and e["odot"]["code"] == code:
            return e
    return None
