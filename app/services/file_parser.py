"""File parser dispatcher (v0.5.3.3: adds parse_file_with_errors)."""
from __future__ import annotations


def parse_file(path, codeset=None):
    """Legacy API: returns just the rows list."""
    result = parse_file_with_errors(path, codeset)
    return result.rows


def parse_file_with_errors(path, codeset=None):
    """v0.5.3.3: returns ParseResult so callers can show per-row errors.
    
    For ODOT files, the ParseResult will have no errors collected
    (the ODOT parser does not yet emit ParseError; that's v0.5.3.4+).
    For PNEZD files, errors are collected via parse_pnezd_with_errors.
    """
    from app.services.parse_errors import ParseResult
    
    parser_kind = getattr(codeset, "parser_kind", "pnezd") if codeset is not None else "pnezd"
    if parser_kind == "odot":
        from app.services.odot_parser import parse_odot
        rows = parse_odot(path, codeset)
        return ParseResult(rows=rows, total_lines=len(rows))
    from app.services.parser import parse_pnezd_with_errors
    return parse_pnezd_with_errors(path)