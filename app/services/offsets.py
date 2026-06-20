"""Survey data offset utilities (v0.3.9.5.2.0.2).

Provides pure functions for applying numeric offsets to rows.
N and E values are NEVER modified by any function in this module.
"""
from __future__ import annotations
from collections import Counter
from typing import List, Dict, Tuple


def apply_point_offset(rows, offset):
    """Add `offset` to the P value of every row.

    Returns (new_rows, applied_count). The original list is NOT mutated.
    """
    new_rows = []
    applied = 0
    for r in rows:
        new_r = dict(r)
        try:
            p_val = int(float(r.get("P", 0)))
            new_r["P"] = p_val + offset
            applied += 1
        except (TypeError, ValueError):
            # P unparseable - leave it alone
            pass
        new_rows.append(new_r)
    return new_rows, applied


def detect_point_collisions(rows, offset):
    """Detect both kinds of P collisions if `offset` were applied:

    1. Duplicate-in-new: two rows would end up with the same new P value.
    2. Old-new overlap: a new P value would equal an OLD P value of a
       DIFFERENT row (the shift would clobber an existing point).

    (v0.3.9.5.2.0.2: Interpretation C - returns the UNION of both kinds.)

    Returns the sorted list of unique conflicting P values (the new P
    values where the conflict occurs).
    """
    new_ps = []
    old_p_to_index = {}
    for i, r in enumerate(rows):
        try:
            old_p = int(float(r.get("P", 0)))
        except (TypeError, ValueError):
            new_ps.append(None)
            continue
        new_ps.append(old_p + offset)
        # Note: if duplicate old P values exist, only the LAST index wins.
        # That is fine: any other row with the same old P will still be
        # detected via the duplicate-in-new path below.
        old_p_to_index[old_p] = i

    new_counts = Counter(p for p in new_ps if p is not None)
    conflicts = set()

    for i, new_p in enumerate(new_ps):
        if new_p is None:
            continue
        # Kind 1: duplicate among the new values
        if new_counts[new_p] > 1:
            conflicts.add(new_p)
            continue
        # Kind 2: overlap with an existing OLD P from a DIFFERENT row
        if new_p in old_p_to_index and old_p_to_index[new_p] != i:
            conflicts.add(new_p)

    return sorted(conflicts)


def apply_elevation_offset(rows, offset, skip_zero=True):
    """Add `offset` to the Z value of every row.

    N and E are NEVER modified. If skip_zero is True (default), rows where
    Z == 0.0 are left untouched (these are usually missing-data flags).

    Returns (new_rows, applied_count). The original list is NOT mutated.
    """
    new_rows = []
    applied = 0
    for r in rows:
        new_r = dict(r)
        try:
            z_val = float(r.get("Z", 0) or 0)
        except (TypeError, ValueError):
            z_val = 0.0
        if skip_zero and z_val == 0.0:
            new_rows.append(new_r)
            continue
        new_r["Z"] = round(z_val + offset, 4)
        applied += 1
        new_rows.append(new_r)
    return new_rows, applied

