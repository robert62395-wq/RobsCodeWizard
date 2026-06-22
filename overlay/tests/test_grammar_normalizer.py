import pytest
from app.services.grammar_normalizer import to_vdt, to_odot_alpha, to_odot_numeric


# to_vdt
def test_to_vdt_pass_through():
    assert to_vdt("B") == "B"
    assert to_vdt("CLS") == "CLS"
    assert to_vdt("BC") == "BC"

def test_to_vdt_strip_asterisk():
    assert to_vdt("BL*") == "B"
    assert to_vdt("EL*") == "E"
    assert to_vdt("CL*") == "CLS"
    assert to_vdt("OC*") == "BC"

def test_to_vdt_from_numeric():
    assert to_vdt("1") == "B"
    assert to_vdt("2") == "E"
    assert to_vdt("3") == "BC"
    assert to_vdt("4") == "CLS"

def test_to_vdt_unknown_passes_through():
    assert to_vdt("XYZ") == "XYZ"

def test_to_vdt_empty():
    assert to_vdt("") == ""


# to_odot_alpha
def test_to_odot_alpha_numeric():
    assert to_odot_alpha("1") == "BL*"
    assert to_odot_alpha("2") == "EL*"
    assert to_odot_alpha("3") == "OC*"
    assert to_odot_alpha("4") == "CL*"

def test_to_odot_alpha_vdt():
    assert to_odot_alpha("B") == "BL*"
    assert to_odot_alpha("E") == "EL*"
    assert to_odot_alpha("CLS") == "CL*"

def test_to_odot_alpha_already_starred():
    assert to_odot_alpha("BL*") == "BL*"

def test_to_odot_alpha_bare_gets_star():
    assert to_odot_alpha("BL") == "BL*"
    assert to_odot_alpha("OC") == "OC*"


# to_odot_numeric
def test_to_odot_numeric_alpha():
    assert to_odot_numeric("BL*") == "1"
    assert to_odot_numeric("EL*") == "2"
    assert to_odot_numeric("OC*") == "3"
    assert to_odot_numeric("CL*") == "4"

def test_to_odot_numeric_already_numeric():
    assert to_odot_numeric("1") == "1"

def test_to_odot_numeric_bc_ec_preserved():
    assert to_odot_numeric("BC*") == "BC*"
    assert to_odot_numeric("EC*") == "EC*"

def test_to_odot_numeric_vdt():
    assert to_odot_numeric("B") == "1"
    assert to_odot_numeric("E") == "2"
    assert to_odot_numeric("CLS") == "4"
