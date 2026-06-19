"""File parser dispatcher (Phase 3 of v0.4.0).

Picks the right parser based on the active code set's ``parser_kind`` attribute:
``"odot"`` for the variable-attribute CSV, anything else (or ``None``) for the
classic PNEZD parser.
"""
from __future__ import annotations


def parse_file(path, codeset=None):
    """Parse ``path`` using the parser appropriate for ``codeset``."""
    parser_kind = getattr(codeset, "parser_kind", "pnezd") if codeset is not None else "pnezd"
    if parser_kind == "odot":
        from app.services.odot_parser import parse_odot
        return parse_odot(path, codeset)
    from app.services.parser import parse_pnezd
    return parse_pnezd(path)
