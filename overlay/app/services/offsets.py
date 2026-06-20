"""Point Number Offset + Elevation (IGLD85) Offset utilities.

v0.4.4 hardening (Phase 4):
    - Signatures preserved from v0.3.9.5.2 so main_window.py keeps working.
    - Added input validation: rejects NaN/+/-inf.
    - Returns NEW lists with deep-copied rows (input is never mutated).
    - Northings (N) and Eastings (E) are NEVER touched (verified by tests).
    - Added IGLD85 region offsets + apply_navd88_to_igld85 convenience helper.
"""
from __future__ import annotations

import copy
import math
from typing import List, Dict, Tuple, Sequence


NAVD88_TO_IGLD85_OFFSET_OHIO = -0.55
IGLD85_TO_NAVD88_OFFSET_OHIO = +0.55

_REGION_OFFSETS = {
    "ohio": NAVD88_TO_IGLD85_OFFSET_OHIO,
    "ohio_lake_erie": NAVD88_TO_IGLD85_OFFSET_OHIO,
}


def get_navd88_to_igld85_offset(region: str = "ohio") -> float:
    key = region.lower().strip()
    if key not in _REGION_OFFSETS:
        raise ValueError(
            f"Unknown region '{region}'. Known regions: "
            f"{sorted(_REGION_OFFSETS.keys())}. "
            "Look up the exact offset via NOAA VERTCON for your site."
        )
    return _REGION_OFFSETS[key]


def _reject_bad_number(value, name: str) -> None:
    try:
        f = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{name} must be a real number, got {value!r}")
    if math.isnan(f):
        raise ValueError(f"{name} must not be NaN.")
    if math.isinf(f):
        raise ValueError(f"{name} must not be +/-infinity.")


def _coerce_point(value) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return 0


def _coerce_elev(value) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def apply_point_offset(rows: Sequence[Dict], offset: int) -> Tuple[List[Dict], int]:
    _reject_bad_number(offset, "Point offset")
    offset_int = int(offset)
    new_rows: List[Dict] = []
    applied = 0
    for row in rows:
        new_row = copy.deepcopy(row)
        if "P" in new_row:
            old_p = _coerce_point(new_row.get("P", 0))
            new_row["P"] = old_p + offset_int
            applied += 1
        new_rows.append(new_row)
    return new_rows, applied


def detect_point_collisions(rows: Sequence[Dict], offset: int) -> List[int]:
    _reject_bad_number(offset, "Point offset")
    offset_int = int(offset)
    if offset_int == 0:
        return []
    originals = {_coerce_point(r.get("P", 0)) for r in rows}
    shifted = {_coerce_point(r.get("P", 0)) + offset_int for r in rows}
    return sorted(shifted & originals)


def apply_elevation_offset(rows: Sequence[Dict], offset: float, skip_zero: bool = True) -> Tuple[List[Dict], int]:
    _reject_bad_number(offset, "Elevation offset")
    offset_f = float(offset)
    new_rows: List[Dict] = []
    applied = 0
    for row in rows:
        new_row = copy.deepcopy(row)
        if "Z" in new_row:
            old_z = _coerce_elev(new_row.get("Z", 0.0))
            if skip_zero and old_z == 0.0:
                new_rows.append(new_row)
                continue
            new_row["Z"] = old_z + offset_f
            applied += 1
        new_rows.append(new_row)
    return new_rows, applied


def apply_navd88_to_igld85(rows: Sequence[Dict], region: str = "ohio", skip_zero: bool = True) -> Tuple[List[Dict], int]:
    offset = get_navd88_to_igld85_offset(region)
    return apply_elevation_offset(rows, offset, skip_zero=skip_zero)
