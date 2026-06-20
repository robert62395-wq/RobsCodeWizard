"""ODOT survey data exporter for Civil3D and OpenRoads (v0.4.5)."""
from __future__ import annotations

import csv
from pathlib import Path
from typing import List, Dict, Tuple

from app.services.line_connect_translator import (
    convert_numeric_to_alpha,
    convert_alpha_to_numeric,
)


def _row_to_pnezd(row, description):
    out = [row.get("P", ""), row.get("N", ""), row.get("E", ""), row.get("Z", ""), description]
    attrs = row.get("attributes") or []
    for k, v in attrs:
        out.extend([k, v])
    return out


def export_civil3d(rows, out_path):
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    conversions = 0
    rows_written = 0
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        for row in rows:
            desc = row.get("D", "")
            new_desc, count = convert_numeric_to_alpha(desc)
            conversions += count
            writer.writerow(_row_to_pnezd(row, new_desc))
            rows_written += 1
    return rows_written, conversions


def export_openroads(rows, out_path, use_numeric=True):
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    conversions = 0
    rows_written = 0
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        for row in rows:
            desc = row.get("D", "")
            if use_numeric:
                new_desc, count = convert_alpha_to_numeric(desc)
                conversions += count
            else:
                new_desc = desc
            writer.writerow(_row_to_pnezd(row, new_desc))
            rows_written += 1
    return rows_written, conversions
