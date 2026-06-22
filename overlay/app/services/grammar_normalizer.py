"""Line-connect grammar normalizer (v0.4.7).

Maps any line-connect token to one of three target grammars:
    VDT grammar:         B, E, BC, EC, CC, RC, CLS  (letters only, NO asterisk)
    ODOT alphabetic:     BL*, EL*, BC*, EC*, OC*, CL*
    ODOT numeric:        1, 2, 3, 4
"""
from __future__ import annotations

_VDT_TO_ODOT_ALPHA = {
    "B": "BL*", "E": "EL*", "BC": "BC*", "EC": "EC*",
    "CC": "OC*", "RC": "OC*", "CLS": "CL*",
}

_ODOT_TO_VDT = {
    "BL": "B", "BL*": "B", "1": "B",
    "EL": "E", "EL*": "E", "2": "E",
    "BC": "BC", "BC*": "BC",
    "EC": "EC", "EC*": "EC",
    "OC": "BC", "OC*": "BC", "3": "BC",
    "CL": "CLS", "CL*": "CLS", "4": "CLS",
}

_ODOT_NUMERIC_TO_ALPHA = {"1": "BL*", "2": "EL*", "3": "OC*", "4": "CL*"}

_ODOT_ALPHA_TO_NUMERIC = {
    "BL": "1", "BL*": "1",
    "EL": "2", "EL*": "2",
    "OC": "3", "OC*": "3",
    "CL": "4", "CL*": "4",
}


def to_vdt(token):
    """Convert any line-connect token to VDT grammar (letters only, no asterisk)."""
    if not token:
        return token
    if token in _VDT_TO_ODOT_ALPHA:
        return token
    if token in _ODOT_TO_VDT:
        return _ODOT_TO_VDT[token]
    bare = token.rstrip("*")
    if bare in _ODOT_TO_VDT:
        return _ODOT_TO_VDT[bare]
    return token


def to_odot_alpha(token):
    """Convert any line-connect token to ODOT alphabetic grammar (BL*/EL*/OC*/CL*)."""
    if not token:
        return token
    if token in _ODOT_NUMERIC_TO_ALPHA:
        return _ODOT_NUMERIC_TO_ALPHA[token]
    if token in _VDT_TO_ODOT_ALPHA:
        return _VDT_TO_ODOT_ALPHA[token]
    if token in ("BL", "EL", "OC", "CL", "BC", "EC"):
        return token + "*"
    return token


def to_odot_numeric(token):
    """Convert any line-connect token to ODOT numeric grammar (1/2/3/4).

    BC*/EC* have no numeric equivalent and pass through.
    """
    if not token:
        return token
    if token in _ODOT_ALPHA_TO_NUMERIC:
        return _ODOT_ALPHA_TO_NUMERIC[token]
    if token in _VDT_TO_ODOT_ALPHA:
        odot_alpha = _VDT_TO_ODOT_ALPHA[token]
        if odot_alpha in _ODOT_ALPHA_TO_NUMERIC:
            return _ODOT_ALPHA_TO_NUMERIC[odot_alpha]
        return odot_alpha
    return token
