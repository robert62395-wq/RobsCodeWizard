"""Numeric <-> Alphabetic line-connect code translator (v0.4.5: forward + reverse)."""
from __future__ import annotations
from typing import List, Dict, Tuple

from app.services.linework_parser import parse, NUMERIC_LINE_CONNECTS

NUMERIC_TO_ALPHA = {"1": "BL*", "2": "EL*", "3": "OC*", "4": "CL*"}
ALPHA_TO_NUMERIC = {"BL*": "1", "EL*": "2", "OC*": "3", "CL*": "4"}
ALPHA_TO_NUMERIC_NO_STAR = {"BL": "1", "EL": "2", "OC": "3", "CL": "4"}


def convert_numeric_to_alpha(description):
    entries = parse(description, dialect="odot")
    count = 0
    out_tokens = []
    for entry in entries:
        out_tokens.append(entry["code"])
        for lc in entry["line_connects"]:
            if lc in NUMERIC_LINE_CONNECTS:
                out_tokens.append(NUMERIC_TO_ALPHA[lc])
                count += 1
            else:
                out_tokens.append(lc)
    return " ".join(out_tokens), count


def convert_alpha_to_numeric(description):
    entries = parse(description, dialect="odot")
    count = 0
    out_tokens = []
    for entry in entries:
        out_tokens.append(entry["code"])
        for lc in entry["line_connects"]:
            if lc in ALPHA_TO_NUMERIC:
                out_tokens.append(ALPHA_TO_NUMERIC[lc])
                count += 1
            elif lc in ALPHA_TO_NUMERIC_NO_STAR:
                out_tokens.append(ALPHA_TO_NUMERIC_NO_STAR[lc])
                count += 1
            else:
                out_tokens.append(lc)
    return " ".join(out_tokens), count


def preview_changes(rows, scope="all", limit=20, direction="numeric_to_alpha"):
    convert = convert_numeric_to_alpha if direction == "numeric_to_alpha" else convert_alpha_to_numeric
    out = []
    for row in rows:
        before = row.get("description", "")
        after, count = convert(before)
        if before != after:
            out.append({"point": row.get("point", ""), "before": before, "after": after, "changed": True, "count": count})
            if len(out) >= limit:
                break
    return out
