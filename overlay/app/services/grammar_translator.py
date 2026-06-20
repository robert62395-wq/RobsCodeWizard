"""VDT <-> ODOT linework grammar translator.

VDT linework commands (letters only, NO asterisk):
    B   = Begin line
    E   = End line
    BC  = Begin curve
    EC  = End curve
    CC  = Compound curve
    RC  = Reverse curve
    CLS = Close shape

ODOT linework commands (letters with OPTIONAL asterisk):
    BL  = Begin Line       (alphabetic)  also 1 (numeric)
    EL  = End Line         (alphabetic)  also 2 (numeric)
    BC  = Begin Curve      (alphabetic)
    EC  = End Curve        (alphabetic)
    OC  = Open Curve       (alphabetic)  also 3 (numeric)
    CL  = Close Shape      (alphabetic)  also 4 (numeric)

Conflict: VDT 'B' (Begin line) collides with ODOT point code 'B' (Ground Break
Line). Disambiguation is done by the parser using the `dialect` parameter.
"""
from __future__ import annotations

VDT_TO_ODOT = {
    "B":   "BL*",
    "E":   "EL*",
    "BC":  "BC*",
    "EC":  "EC*",
    "CC":  "OC*",
    "RC":  "OC*",
    "CLS": "CL*",
}

ODOT_TO_VDT_LETTERED = {
    "BL":  "B",
    "EL":  "E",
    "BC":  "BC",
    "EC":  "EC",
    "OC":  "BC",
    "CL":  "CLS",
}

ODOT_NUMERIC_TO_VDT = {"1": "B", "2": "E", "3": "BC", "4": "CLS"}
ODOT_NUMERIC_TO_ALPHA = {"1": "BL*", "2": "EL*", "3": "OC*", "4": "CL*"}
AMBIGUOUS_VDT = {"CC", "RC"}
AMBIGUOUS_ODOT = {"OC", "OC*", "3"}


def translate_linework_token(token, direction):
    """Translate a single linework command between VDT and ODOT grammars."""
    if direction == "vdt_to_odot":
        if token in VDT_TO_ODOT:
            return VDT_TO_ODOT[token], token in AMBIGUOUS_VDT
        return token, False
    if direction == "odot_to_vdt":
        if token in ODOT_NUMERIC_TO_VDT:
            return ODOT_NUMERIC_TO_VDT[token], token in AMBIGUOUS_ODOT
        bare = token.rstrip("*")
        if bare in ODOT_TO_VDT_LETTERED:
            return ODOT_TO_VDT_LETTERED[bare], (token in AMBIGUOUS_ODOT or bare in AMBIGUOUS_ODOT)
        return token, False
    raise ValueError("direction must be 'vdt_to_odot' or 'odot_to_vdt'")


def normalize_odot_numeric_to_alpha(token):
    """Convert ODOT numeric line-connect (1/2/3/4) to alphabetic (BL*/EL*/OC*/CL*)."""
    return ODOT_NUMERIC_TO_ALPHA.get(token, token)
