"""Status bar formatting helpers (v0.5.2)."""
from __future__ import annotations
from pathlib import Path


def format_permanent_status(codeset, source_path, rows, results):
    """Build the persistent left-aligned status bar text."""
    parts = []
    if codeset is not None:
        name = str(getattr(codeset, "name", "?")).upper()
        n_codes = len(getattr(codeset, "codes", []) or [])
        parts.append(f"Code set: {name} ({n_codes} codes)")
    if source_path:
        parts.append(f"File: {Path(source_path).name}")
    if rows:
        parts.append(f"Points: {len(rows):,}")
    if results:
        issues = sum(1 for r in results if not r.get("valid", True))
        parts.append(f"Issues: {issues}")
    if not parts:
        return "No file loaded - use File menu or Open CSV/TXT button to begin."
    return "  |  ".join(parts)