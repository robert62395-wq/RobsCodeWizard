"""Analyze loaded rows to identify codes in use and their frequency (v0.5.1)."""
from __future__ import annotations
from collections import Counter

from app.services.linework_parser import parse


def analyze_used_codes(rows, dialect="odot"):
    """Scan parent.rows and return {code: count} for every distinct point_code."""
    counter = Counter()
    if not rows:
        return dict(counter)
    for row in rows:
        desc = str(row.get("D", "")).strip()
        if not desc:
            continue
        main = desc.partition("/")[0].strip() if "/" in desc else desc
        entries = parse(main, dialect=dialect)
        for entry in entries:
            code = entry["code"].upper()
            if code:
                counter[code] += 1
    return dict(counter)


def build_usage_summary(used_counts, map_data):
    """Return summary of how loaded file codes map to the translation map."""
    entries = map_data.get("entries", []) if map_data else []
    by_vdt = {}
    by_odot = {}
    for e in entries:
        v = e.get("vdt") or {}
        o = e.get("odot") or {}
        if v.get("code"):
            by_vdt[str(v["code"]).upper()] = e
        if o.get("code"):
            by_odot[str(o["code"]).upper()] = e
    summary = {
        "unique_codes": len(used_counts),
        "exact": 0, "best_guess": 0, "unmatched": 0, "manual": 0,
        "not_in_map": [],
    }
    for code in used_counts:
        entry = by_vdt.get(code) or by_odot.get(code)
        if entry is None:
            summary["not_in_map"].append(code)
            summary["unmatched"] += 1
            continue
        conf = str(entry.get("confidence", "unmatched"))
        if entry.get("user_override"):
            summary["manual"] += 1
        elif conf == "exact":
            summary["exact"] += 1
        elif conf == "best-guess":
            summary["best_guess"] += 1
        else:
            summary["unmatched"] += 1
    return summary
