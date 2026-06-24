"""ODOT/VDT survey data exporter (v0.4.7: dialect-aware dispatch).

Dispatch rules (locked in v1.0 spec):
    VDT  -> Civil3D    : VDT grammar (B, E, BC, EC, CLS)
    ODOT -> Civil3D    : ODOT alphabetic grammar (BL*, EL*, OC*, CL*)
    ODOT -> OpenRoads  : ODOT numeric (default) or alphabetic
    VDT  -> OpenRoads  : Not supported - translate to ODOT first

Output is PNEZD CSV, no header row. P, N, E, Z are never modified.
"""
from __future__ import annotations

import csv
from pathlib import Path

from app.services.linework_parser import parse
from app.services.grammar_normalizer import to_vdt, to_odot_alpha, to_odot_numeric


def _row_to_pnezd(row, description):
    out = [
        row.get("P", ""),
        row.get("N", ""),
        row.get("E", ""),
        row.get("Z", ""),
        description,
    ]
    attrs = row.get("attributes") or []
    for k, v in attrs:
        out.extend([k, v])
    return out


def _convert_description(description, source_dialect, target_fn):
    """Re-emit a description with line-connects normalized via target_fn.

    Preserves '/' comment tail untouched and preserves size tokens.
    """
    if not description:
        return description, 0
    if "/" in description:
        main, _, tail = description.partition("/")
        main = main.strip()
        tail = tail.strip()
        tail_suffix = f" / {tail}" if tail else ""
    else:
        main = description.strip()
        tail_suffix = ""

    entries = parse(main, dialect=source_dialect)
    out_tokens = []
    count = 0
    for entry in entries:
        out_tokens.append(entry["code"])
        if entry.get("size"):
            out_tokens.append(entry["size"])
        for lc in entry["line_connects"]:
            new_lc = target_fn(lc)
            if new_lc != lc:
                count += 1
            out_tokens.append(new_lc)
    return " ".join(out_tokens) + tail_suffix, count


def export_vdt_to_civil3d(rows, out_path):
    """VDT rows -> Civil3D PNEZD CSV. Line connects use VDT grammar."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    conversions = 0
    written = 0
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        for row in rows:
            new_desc, c = _convert_description(row.get("D", ""), "vdt", to_vdt)
            conversions += c
            writer.writerow(_row_to_pnezd(row, new_desc))
            written += 1
    return written, conversions


def export_odot_to_civil3d(rows, out_path):
    """ODOT rows -> Civil3D PNEZD CSV. Line connects use ODOT alphabetic grammar."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    conversions = 0
    written = 0
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        for row in rows:
            new_desc, c = _convert_description(row.get("D", ""), "odot", to_odot_alpha)
            conversions += c
            writer.writerow(_row_to_pnezd(row, new_desc))
            written += 1
    return written, conversions


def export_odot_to_openroads(rows, out_path, use_numeric=True):
    """ODOT rows -> OpenRoads PNEZD CSV. Line connects numeric by default."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    conversions = 0
    written = 0
    target_fn = to_odot_numeric if use_numeric else to_odot_alpha
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        for row in rows:
            new_desc, c = _convert_description(row.get("D", ""), "odot", target_fn)
            conversions += c
            writer.writerow(_row_to_pnezd(row, new_desc))
            written += 1
    return written, conversions


# Backward-compat aliases for v0.4.5 callers (assume ODOT source)
def export_civil3d(rows, out_path):
    return export_odot_to_civil3d(rows, out_path)


def export_openroads(rows, out_path, use_numeric=True):
    return export_odot_to_openroads(rows, out_path, use_numeric=use_numeric)
