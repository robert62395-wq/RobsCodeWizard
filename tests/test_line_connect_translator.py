"""Phase 2 + Phase 5 tests for line connect translator."""
import pytest
from app.services.line_connect_translator import (
    convert_numeric_to_alpha, convert_alpha_to_numeric, preview_changes,
    NUMERIC_TO_ALPHA, ALPHA_TO_NUMERIC,
)


# Phase 2: forward direction (numeric -> alpha)
def test_simple_begin_line():
    assert convert_numeric_to_alpha("EP 1") == ("EP BL*", 1)

def test_end_line():
    assert convert_numeric_to_alpha("EP 2") == ("EP EL*", 1)

def test_open_curve():
    assert convert_numeric_to_alpha("EP 3") == ("EP OC*", 1)

def test_close_shape():
    assert convert_numeric_to_alpha("EP 4") == ("EP CL*", 1)

def test_compound_dr_2_ep1():
    assert convert_numeric_to_alpha("DR 2 EP1") == ("DR EL* EP1", 1)

def test_compound_multi_code():
    assert convert_numeric_to_alpha("DR1 3 DR1 2 EP1") == ("DR1 OC* DR1 EL* EP1", 2)

def test_line_2d_with_ep():
    assert convert_numeric_to_alpha("LINE_2D 1 EP 1") == ("LINE_2D BL* EP BL*", 2)

def test_no_change_when_code_only():
    assert convert_numeric_to_alpha("EP") == ("EP", 0)

def test_already_alpha():
    assert convert_numeric_to_alpha("EP BL*") == ("EP BL*", 0)

def test_numeric_suffix_point_code_preserved():
    assert convert_numeric_to_alpha("EP1 1") == ("EP1 BL*", 1)

def test_empty():
    assert convert_numeric_to_alpha("") == ("", 0)


# Phase 5: reverse direction (alpha -> numeric)
def test_reverse_bl_star_to_1():
    assert convert_alpha_to_numeric("EP BL*") == ("EP 1", 1)

def test_reverse_el_star_to_2():
    assert convert_alpha_to_numeric("EP EL*") == ("EP 2", 1)

def test_reverse_oc_star_to_3():
    assert convert_alpha_to_numeric("EP OC*") == ("EP 3", 1)

def test_reverse_cl_star_to_4():
    assert convert_alpha_to_numeric("EP CL*") == ("EP 4", 1)

def test_reverse_bare_lettered_bl():
    assert convert_alpha_to_numeric("EP BL") == ("EP 1", 1)

def test_reverse_bare_lettered_el():
    assert convert_alpha_to_numeric("EP EL") == ("EP 2", 1)

def test_reverse_compound():
    assert convert_alpha_to_numeric("DR EL* EP1") == ("DR 2 EP1", 1)

def test_reverse_no_change_when_no_alpha():
    assert convert_alpha_to_numeric("EP") == ("EP", 0)

def test_reverse_already_numeric():
    assert convert_alpha_to_numeric("EP 1") == ("EP 1", 0)

def test_reverse_bc_ec_preserved():
    # BC and EC don't have numeric equivalents, pass through
    assert convert_alpha_to_numeric("EP BC*") == ("EP BC*", 0)
    assert convert_alpha_to_numeric("EP EC*") == ("EP EC*", 0)

def test_reverse_multi_token():
    assert convert_alpha_to_numeric("DR1 OC* DR1 EL* EP1") == ("DR1 3 DR1 2 EP1", 2)

def test_preview_changes_basic():
    rows = [
        {"point": 1000, "description": "EP 1"},
        {"point": 1001, "description": "X"},
        {"point": 1072, "description": "DR 2 EP1"},
    ]
    preview = preview_changes(rows, direction="numeric_to_alpha")
    assert len(preview) == 2
    points = {p["point"] for p in preview}
    assert 1000 in points
    assert 1072 in points

def test_preview_reverse_direction():
    rows = [
        {"point": 1, "description": "EP BL*"},
        {"point": 2, "description": "DR EL*"},
    ]
    preview = preview_changes(rows, direction="alpha_to_numeric")
    assert len(preview) == 2
    assert preview[0]["after"] == "EP 1"
    assert preview[1]["after"] == "DR 2"

def test_mapping_constants_locked():
    assert NUMERIC_TO_ALPHA == {"1": "BL*", "2": "EL*", "3": "OC*", "4": "CL*"}
    assert ALPHA_TO_NUMERIC == {"BL*": "1", "EL*": "2", "OC*": "3", "CL*": "4"}
