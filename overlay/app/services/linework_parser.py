"""Linework token parser for ODOT, VDT, and OpenRoads numeric grammars.

A point code's description field may contain a sequence of tokens separated by
whitespace. Tokens are one of:
    - point_code   : an alphanumeric code from the catalog (EP, EP1, DR, LINE_2D, ...)
    - numeric_lc   : an OpenRoads numeric line-connect command ("1", "2", "3", "4")
    - lettered_lc  : an ODOT/Civil3D lettered line-connect command (BL, EL, OC, CL, with optional *)
    - vdt_lc       : a VDT linework command (B, E, BC, EC, CC, RC, CLS)

Numeric line connects are POSITIONAL: a bare "1" is only a line connect if it
follows a point code with whitespace separation. Numeric-suffixed point codes
like "EP1" or "DR1" are point codes, not line connects.
"""
from __future__ import annotations

import re
from typing import List, Dict

NUMERIC_LINE_CONNECTS = {"1", "2", "3", "4"}

LETTERED_LINE_CONNECTS = {
    "BL", "EL", "OC", "CL", "BC", "EC",
    "BL*", "EL*", "OC*", "CL*", "BC*", "EC*",
}

VDT_LINE_CONNECTS = {"B", "E", "BC", "EC", "CC", "RC", "CLS"}

_WHITESPACE_RE = re.compile(r"\s+")


def tokenize(description: str) -> List[str]:
    """Split a description string by whitespace, collapsing multiple spaces."""
    if not description:
        return []
    return [t for t in _WHITESPACE_RE.split(description.strip()) if t]


def classify_token(token: str, dialect: str = "odot") -> str:
    """Classify a single token in isolation (no positional context).

    For positional resolution (whether a bare numeric "1" is a line connect or
    just a stray number), use parse() instead.
    """
    if token in NUMERIC_LINE_CONNECTS:
        return "numeric_lc"
    if token in LETTERED_LINE_CONNECTS:
        return "lettered_lc"
    if dialect == "vdt" and token in VDT_LINE_CONNECTS:
        return "vdt_lc"
    return "point_code"


def parse(description: str, dialect: str = "odot") -> List[Dict]:
    """Parse a description into [{code, line_connects, raw_index}, ...] entries.

    Each point code becomes one entry. Line-connect tokens that follow are
    attached to the most recent point code. Lookup order:
        token in NUMERIC_LINE_CONNECTS -> attach as line connect
        token in LETTERED_LINE_CONNECTS -> attach as line connect
        dialect == "vdt" and token in VDT_LINE_CONNECTS -> attach as line connect
        otherwise -> new point code entry

    Note: tokens are classified positionally. A leading numeric token (no
    preceding code) is treated as a stray point_code entry to preserve the data.
    """
    tokens = tokenize(description)
    entries: List[Dict] = []
    current: Dict | None = None

    for i, tok in enumerate(tokens):
        kind = classify_token(tok, dialect=dialect)
        is_lc = kind in ("numeric_lc", "lettered_lc", "vdt_lc")

        if is_lc and current is not None:
            current["line_connects"].append(tok)
        else:
            # New point code (or leading orphan token)
            current = {"code": tok, "line_connects": [], "raw_index": i}
            entries.append(current)

    return entries
