"""ODOT variable-attribute CSV parser (Phase 3 of v0.4.0).

ODOT survey files follow this row layout::

    P, N, E, Z, "Desc with codes and linework commands", attr_name, attr_value, ...

The description column may contain multiple codes interleaved with linework
commands (BL*/EL*/CL*/OC*).  Each non-command code consumes a number of
key/value attribute pairs equal to its catalog ``AttributesSchema`` entry; if
the actual number of pairs does not match the total expected, this parser
falls back to a greedy left-to-right walk so we degrade gracefully.

Quoted CSV values with embedded commas and doubled quotes are handled by the
stdlib ``csv`` module.
"""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, List, Optional, Tuple


PNEZD_KEYS = ("P", "N", "E", "Z", "D")


def _split_suffix(token: str) -> Tuple[str, str]:
    """Strip trailing digits.  ``"EP1"`` -> ``("EP", "1")``."""
    i = len(token)
    while i > 0 and token[i - 1].isdigit():
        i -= 1
    base = token[:i] or token
    suffix = token[i:]
    return base, suffix


def _schemas_from_codeset(codeset) -> Dict[str, List[str]]:
    """Return a {CODE_UPPER: [attr_name, ...]} map from the catalog."""
    out: Dict[str, List[str]] = {}
    if codeset is None:
        return out
    for entry in getattr(codeset, "codes", []):
        code = (entry.get("code") or "").strip().upper()
        if not code:
            continue
        schema_raw = (entry.get("attributes_schema") or "").strip()
        if not schema_raw:
            out[code] = []
            continue
        names = [n.strip() for n in schema_raw.split(";") if n.strip()]
        out[code] = names
    return out


def _expected_attr_count(code_token: str, schemas: Dict[str, List[str]]) -> int:
    """Look up the expected attribute count for ``code_token``.

    Falls back to ``schemas[base]`` when the code has a numeric suffix
    (``EP1`` -> ``EP``).  Unknown codes get ``1`` so they consume one pair
    in the greedy fallback.
    """
    if not code_token:
        return 0
    upper = code_token.upper()
    if upper in schemas:
        return len(schemas[upper])
    base, _ = _split_suffix(upper)
    if base in schemas:
        return len(schemas[base])
    return 1


def assign_attributes(
    codes_with_index: List[Tuple[int, str]],
    pairs: List[Tuple[str, str]],
    schemas: Dict[str, List[str]],
) -> Tuple[List[dict], Dict[str, str]]:
    """Distribute ``pairs`` across ``codes_with_index`` per the catalog schemas.

    Parameters
    ----------
    codes_with_index : list of (index_in_description, code_token)
        Only the non-command code tokens, in left-to-right description order.
    pairs : list of (name, value)
        Attribute key/value pairs from the trailing CSV cells.
    schemas : dict
        Output of :func:`_schemas_from_codeset`.

    Returns
    -------
    assignments : list of dict
        One per code, with keys ``code``, ``code_index``, ``attrs`` (dict),
        ``expected`` (schema length) and ``consumed`` (actual count).
    trailing : dict
        Any pairs that didn't fit into a known schema (with duplicate names
        suffixed ``_2``, ``_3`` ... to avoid clobbering).
    """
    assignments: List[dict] = []
    trailing: Dict[str, str] = {}

    if not codes_with_index:
        for name, value in pairs:
            _put_unique(trailing, name, value)
        return assignments, trailing

    expected_per_code = [_expected_attr_count(tok, schemas) for _, tok in codes_with_index]
    total_expected = sum(expected_per_code)

    if pairs and total_expected == len(pairs):
        # Perfect match - use the schema names.
        cursor = 0
        for (desc_idx, tok), expected in zip(codes_with_index, expected_per_code):
            attrs: Dict[str, str] = {}
            upper = tok.upper()
            base, _ = _split_suffix(upper)
            names = schemas.get(upper) or schemas.get(base) or []
            for k in range(expected):
                value_pair = pairs[cursor + k]
                # Prefer catalog name if available, otherwise the file-supplied name.
                if k < len(names) and names[k]:
                    key = names[k]
                else:
                    key = value_pair[0] or f"attr{k+1}"
                _put_unique(attrs, key, value_pair[1])
            assignments.append({
                "code": tok,
                "code_index": desc_idx,
                "attrs": attrs,
                "expected": expected,
                "consumed": expected,
            })
            cursor += expected
        return assignments, trailing

    # Fallback: greedy left-to-right.  Each code may grab fewer pairs than its
    # schema if there are not enough remaining; later codes get at least zero.
    cursor = 0
    remaining_codes = len(codes_with_index)
    for (desc_idx, tok), expected in zip(codes_with_index, expected_per_code):
        remaining_codes -= 1
        pairs_left = len(pairs) - cursor
        # Reserve at least 0 for following codes; never go below zero.
        reserve = max(0, remaining_codes)
        # Cap consumption so we don\'t starve the rest.
        available = max(0, pairs_left - reserve)
        consumed = min(expected, available)
        attrs: Dict[str, str] = {}
        upper = tok.upper()
        base, _ = _split_suffix(upper)
        names = schemas.get(upper) or schemas.get(base) or []
        for k in range(consumed):
            name, value = pairs[cursor + k]
            if k < len(names) and names[k]:
                key = names[k]
            else:
                key = name or f"attr{k+1}"
            _put_unique(attrs, key, value)
        assignments.append({
            "code": tok,
            "code_index": desc_idx,
            "attrs": attrs,
            "expected": expected,
            "consumed": consumed,
        })
        cursor += consumed

    # Anything left over goes into trailing.
    for name, value in pairs[cursor:]:
        _put_unique(trailing, name or "attr", value)

    return assignments, trailing


def _put_unique(d: Dict[str, str], key: str, value: str) -> None:
    """Insert ``key -> value`` into ``d``; on collision, suffix _2, _3 ..."""
    if not key:
        key = "attr"
    if key not in d:
        d[key] = value
        return
    i = 2
    while f"{key}_{i}" in d:
        i += 1
    d[f"{key}_{i}"] = value


def parse_odot(path, codeset=None) -> List[dict]:
    """Parse an ODOT variable-attribute CSV file.

    Returns a list of row dicts shaped like::

        {
            "P": "...",
            "N": "...",
            "E": "...",
            "Z": "...",
            "D": "EPA BL* DR ...",
            "attributes": [
                {"code": "EPA", "code_index": 0, "attrs": {"Material": "Asphalt"},
                 "expected": 1, "consumed": 1},
                ...
            ],
            "trailing_attrs": {...},
        }
    """
    p = Path(path)
    schemas = _schemas_from_codeset(codeset)
    grammar = getattr(codeset, "linework_grammar", None) if codeset is not None else None
    grammar_set = frozenset(c.upper() for c in grammar.all_commands) if grammar else frozenset()

    rows: List[dict] = []
    with p.open("r", newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        for raw in reader:
            # Strip trailing empty cells (the sample file has trailing commas).
            while raw and (raw[-1] is None or str(raw[-1]).strip() == ""):
                raw = raw[:-1]
            if not raw:
                continue
            if all(not str(c).strip() for c in raw):
                continue
            cells = [str(c).strip() for c in raw]
            if len(cells) < 5:
                continue

            point, north, east, elev, desc = cells[0], cells[1], cells[2], cells[3], cells[4]

            # Parse the attribute pairs from cells[5:].
            tail = cells[5:]
            pairs: List[Tuple[str, str]] = []
            i = 0
            while i < len(tail):
                name = tail[i]
                value = tail[i + 1] if i + 1 < len(tail) else ""
                if name or value:
                    pairs.append((name, value))
                i += 2

            # Tokenize the description: keep code tokens with their position,
            # drop linework commands from the schema-walk (but keep them in D).
            tokens = desc.split()
            codes_with_index: List[Tuple[int, str]] = []
            for idx, tok in enumerate(tokens):
                if tok.upper() in grammar_set:
                    continue
                codes_with_index.append((idx, tok))

            assignments, trailing = assign_attributes(codes_with_index, pairs, schemas)

            rows.append({
                "P": point,
                "N": north,
                "E": east,
                "Z": elev,
                "D": desc,
                "attributes": assignments,
                "trailing_attrs": trailing,
            })
    return rows
