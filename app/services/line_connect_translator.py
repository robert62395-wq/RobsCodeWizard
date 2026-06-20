"""Numeric <-> Alphabetic line-connect code translator.

Phase 2: forward direction only (Numeric -> Alphabetic) for Civil3D export.
Phase 5 (v0.4.5): adds reverse direction (Alphabetic -> Numeric) for OpenRoads export.
"""
from __future__ import annotations

from typing import List, Dict, Tuple

from app.services.linework_parser import (
    parse,
    NUMERIC_LINE_CONNECTS,
)

NUMERIC_TO_ALPHA = {
    "1": "BL*",
    "2": "EL*",
    "3": "OC*",
    "4": "CL*",
}

# Reserved for Phase 5 (v0.4.5)
ALPHA_TO_NUMERIC = {v: k for k, v in NUMERIC_TO_ALPHA.items()}


def convert_numeric_to_alpha(description: str) -> Tuple[str, int]:
    """Convert numeric line-connect tokens to alphabetic equivalents.

    Returns (new_description, count_of_conversions).
    Preserves order and spacing (single-space delimited output).
    Point codes (including numeric-suffixed ones like EP1) are untouched.
    """
    entries = parse(description, dialect="odot")
    count = 0
    out_tokens: List[str] = []

    for entry in entries:
        out_tokens.append(entry["code"])
        for lc in entry["line_connects"]:
            if lc in NUMERIC_LINE_CONNECTS:
                out_tokens.append(NUMERIC_TO_ALPHA[lc])
                count += 1
            else:
                out_tokens.append(lc)

    return " ".join(out_tokens), count


def convert_alpha_to_numeric(description: str) -> Tuple[str, int]:
    """Reserved for Phase 5 (v0.4.5) - OpenRoads export."""
    raise NotImplementedError(
        "Reverse conversion (Alphabetic -> Numeric) lands in v0.4.5 "
        "alongside OpenRoads export."
    )


def preview_changes(
    rows: List[Dict],
    scope: str = "all",
    limit: int = 20,
) -> List[Dict]:
    """Generate a before/after preview for the dialog UI.

    rows: list of {"point": int|str, "description": str, ...}
    scope: "all" or "selection" (caller is responsible for pre-filtering on selection)
    limit: max number of CHANGED rows to return

    Returns list of {"point", "before", "after", "changed", "count"}.
    """
    out: List[Dict] = []
    for row in rows:
        before = row.get("description", "")
        after, count = convert_numeric_to_alpha(before)
        changed = before != after
        if changed:
            out.append({
                "point": row.get("point", ""),
                "before": before,
                "after": after,
                "changed": True,
                "count": count,
            })
            if len(out) >= limit:
                break
    return out
