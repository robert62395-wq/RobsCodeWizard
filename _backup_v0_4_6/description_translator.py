"""End-to-end description translator: parser + code map + grammar map."""
from __future__ import annotations

from app.services.linework_parser import parse
from app.services.code_translator import translate_code
from app.services.grammar_translator import translate_linework_token


def translate_description(description, direction, map_data=None):
    if not description:
        return description, {
            "code_changes": 0, "linework_changes": 0,
            "ambiguous_tokens": [], "unmatched_codes": [],
        }

    source_dialect = "vdt" if direction == "vdt_to_odot" else "odot"
    entries = parse(description, dialect=source_dialect)

    out_tokens = []
    info = {
        "code_changes": 0,
        "linework_changes": 0,
        "ambiguous_tokens": [],
        "unmatched_codes": [],
    }

    for entry in entries:
        code = entry["code"]
        new_code, confidence = translate_code(code, direction, data=map_data)
        if new_code != code:
            info["code_changes"] += 1
        if confidence == "unmatched":
            info["unmatched_codes"].append(code)
        out_tokens.append(new_code)

        for lc in entry["line_connects"]:
            new_lc, ambiguous = translate_linework_token(lc, direction=direction)
            if new_lc != lc:
                info["linework_changes"] += 1
            if ambiguous:
                info["ambiguous_tokens"].append(lc)
            out_tokens.append(new_lc)

    return " ".join(out_tokens), info


def translate_rows(rows, direction, map_data=None):
    summary = {
        "rows_changed": 0,
        "code_changes": 0,
        "linework_changes": 0,
        "ambiguous_rows": [],
        "unmatched_codes": set(),
    }
    for row in rows:
        desc_key = "D" if "D" in row else "description"
        before = row.get(desc_key, "")
        after, info = translate_description(before, direction, map_data=map_data)
        if after != before:
            summary["rows_changed"] += 1
            row[desc_key] = after
        summary["code_changes"] += info["code_changes"]
        summary["linework_changes"] += info["linework_changes"]
        if info["ambiguous_tokens"]:
            summary["ambiguous_rows"].append({
                "point": row.get("P", row.get("point", "")),
                "tokens": info["ambiguous_tokens"],
            })
        summary["unmatched_codes"].update(info["unmatched_codes"])
    summary["unmatched_codes"] = sorted(summary["unmatched_codes"])
    return rows, summary
