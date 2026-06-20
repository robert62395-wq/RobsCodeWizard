"""Phase 3 tests for VDT<->ODOT linework grammar translator."""
import pytest
from app.services.grammar_translator import (
    translate_linework_token, normalize_odot_numeric_to_alpha,
)


def test_vdt_b_to_odot_bl_star():
    assert translate_linework_token("B", "vdt_to_odot") == ("BL*", False)


def test_vdt_e_to_odot_el_star():
    assert translate_linework_token("E", "vdt_to_odot") == ("EL*", False)


def test_vdt_bc_to_odot_bc_star():
    assert translate_linework_token("BC", "vdt_to_odot") == ("BC*", False)


def test_vdt_ec_to_odot_ec_star():
    assert translate_linework_token("EC", "vdt_to_odot") == ("EC*", False)


def test_vdt_cc_to_odot_oc_star_ambiguous():
    assert translate_linework_token("CC", "vdt_to_odot") == ("OC*", True)


def test_vdt_rc_to_odot_oc_star_ambiguous():
    assert translate_linework_token("RC", "vdt_to_odot") == ("OC*", True)


def test_vdt_cls_to_odot_cl_star():
    assert translate_linework_token("CLS", "vdt_to_odot") == ("CL*", False)


def test_odot_bl_star_to_vdt_b():
    assert translate_linework_token("BL*", "odot_to_vdt") == ("B", False)


def test_odot_el_to_vdt_e():
    assert translate_linework_token("EL", "odot_to_vdt") == ("E", False)


def test_odot_numeric_1_to_vdt_b():
    assert translate_linework_token("1", "odot_to_vdt") == ("B", False)


def test_odot_numeric_2_to_vdt_e():
    assert translate_linework_token("2", "odot_to_vdt") == ("E", False)


def test_odot_oc_star_to_vdt_bc_ambiguous():
    assert translate_linework_token("OC*", "odot_to_vdt") == ("BC", True)


def test_odot_numeric_3_to_vdt_bc_ambiguous():
    assert translate_linework_token("3", "odot_to_vdt") == ("BC", True)


def test_odot_cl_star_to_vdt_cls():
    assert translate_linework_token("CL*", "odot_to_vdt") == ("CLS", False)


def test_unknown_token_passes_through_vdt_to_odot():
    assert translate_linework_token("XYZ", "vdt_to_odot") == ("XYZ", False)


def test_unknown_token_passes_through_odot_to_vdt():
    assert translate_linework_token("XYZ", "odot_to_vdt") == ("XYZ", False)


def test_invalid_direction_raises():
    with pytest.raises(ValueError, match="direction"):
        translate_linework_token("B", "sideways")


def test_normalize_numeric_to_alpha():
    assert normalize_odot_numeric_to_alpha("1") == "BL*"
    assert normalize_odot_numeric_to_alpha("2") == "EL*"
    assert normalize_odot_numeric_to_alpha("3") == "OC*"
    assert normalize_odot_numeric_to_alpha("4") == "CL*"
    assert normalize_odot_numeric_to_alpha("BL*") == "BL*"
