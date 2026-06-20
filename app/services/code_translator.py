"""Point code translator backed by app/data/translation_map.json."""
from __future__ import annotations

from app.services import translation_map as tm

_CACHE = {"data": None}


def _load_cached():
    if _CACHE["data"] is None:
        _CACHE["data"] = tm.load()
    return _CACHE["data"]


def clear_cache():
    _CACHE["data"] = None


def translate_code(code, direction, data=None):
    """Translate a point code via the translation map.

    Returns (translated_code, confidence).
    """
    data = data if data is not None else _load_cached()
    if direction == "vdt_to_odot":
        entry = tm.find_by_vdt(code, data)
        if entry and entry.get("odot"):
            return entry["odot"]["code"], entry.get("confidence", "best-guess")
        return code, "passthrough"
    if direction == "odot_to_vdt":
        entry = tm.find_by_odot(code, data)
        if entry and entry.get("vdt"):
            return entry["vdt"]["code"], entry.get("confidence", "best-guess")
        return code, "passthrough"
    raise ValueError("direction must be 'vdt_to_odot' or 'odot_to_vdt'")
