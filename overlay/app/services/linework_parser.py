"""Linework token parser (v0.4.6: size-bearing code support)."""
from __future__ import annotations
import re

from app.services.size_bearing import is_size_bearing

NUMERIC_LINE_CONNECTS = {"1", "2", "3", "4"}
LETTERED_LINE_CONNECTS = {
    "BL", "EL", "OC", "CL", "BC", "EC",
    "BL*", "EL*", "OC*", "CL*", "BC*", "EC*",
}
VDT_LINE_CONNECTS = {"B", "E", "BC", "EC", "CC", "RC", "CLS"}

_WHITESPACE_RE = re.compile(r"\s+")


def tokenize(description):
    if not description:
        return []
    return [t for t in _WHITESPACE_RE.split(description.strip()) if t]


def classify_token(token, dialect="odot"):
    if token in NUMERIC_LINE_CONNECTS:
        return "numeric_lc"
    if token in LETTERED_LINE_CONNECTS:
        return "lettered_lc"
    if dialect == "vdt" and token in VDT_LINE_CONNECTS:
        return "vdt_lc"
    return "point_code"


def parse(description, dialect="odot"):
    """Parse a description into entries.

    Entry dict: {code, line_connects, size, raw_index}
    """
    tokens = tokenize(description)
    entries = []
    current = None
    expect_size_next = False

    for i, tok in enumerate(tokens):
        kind = classify_token(tok, dialect=dialect)
        is_lc = kind in ("numeric_lc", "lettered_lc", "vdt_lc")

        if expect_size_next and not is_lc and current is not None:
            current["size"] = tok
            expect_size_next = False
            continue
        expect_size_next = False

        if is_lc and current is not None:
            current["line_connects"].append(tok)
        else:
            current = {"code": tok, "line_connects": [], "size": None, "raw_index": i}
            entries.append(current)
            if is_size_bearing(tok):
                expect_size_next = True

    return entries
