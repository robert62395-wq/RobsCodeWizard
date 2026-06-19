"""PNEZD CSV/TXT exporter."""
import csv

# v0.3.9.5.0.9: PNEZD-only because AutoCAD Civil 3D point import accepts only
# this column set. FUTURE: extend to ODOT/OpenRoads column sets (additional
# attribute fields per Phase 4 codeset) when needed.


def write_pnezd(rows, out_path):
    """Write rows in P,N,E,Z,D order, comma-delimited, NO header row.

    Each row is a dict with keys P, N, E, Z, D. D may contain commas
    (used for ODOT-style comments) - csv.QUOTE_MINIMAL handles quoting
    so the file stays valid CSV but D is preserved verbatim.
    N/E/Z are written as-parsed (no rounding).
    """
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        for row in rows:
            writer.writerow([
                _fmt(row.get("P", "")),
                _fmt(row.get("N", "")),
                _fmt(row.get("E", "")),
                _fmt(row.get("Z", "")),
                str(row.get("D", "")),
            ])
    return out_path


def _fmt(v):
    if v is None:
        return ""
    return str(v)
