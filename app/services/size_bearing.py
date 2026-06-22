"""Size-bearing code detection for VDT codes (v0.4.6)."""
from __future__ import annotations

SIZE_BEARING_CODES = {"GRBR", "VTD", "VTE", "VTS", "VBU"}


def is_size_bearing(code):
    """Return True if `code` accepts a size attribute as the next token."""
    if not code:
        return False
    code_upper = str(code).upper()
    if code_upper in SIZE_BEARING_CODES:
        return True
    if code_upper.startswith("PI"):
        return True
    return False
