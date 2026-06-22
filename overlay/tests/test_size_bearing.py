import pytest
from app.services.size_bearing import is_size_bearing, SIZE_BEARING_CODES


def test_grbr(): assert is_size_bearing("GRBR") is True
def test_vtd(): assert is_size_bearing("VTD") is True
def test_vte(): assert is_size_bearing("VTE") is True
def test_vts(): assert is_size_bearing("VTS") is True
def test_vbu(): assert is_size_bearing("VBU") is True
def test_pi(): assert is_size_bearing("PI") is True
def test_pi1(): assert is_size_bearing("PI1") is True
def test_pi20(): assert is_size_bearing("PI20") is True
def test_pipipe(): assert is_size_bearing("PIPIPE") is True
def test_ep_not(): assert is_size_bearing("EP") is False
def test_dr_not(): assert is_size_bearing("DR") is False
def test_empty(): assert is_size_bearing("") is False
def test_none(): assert is_size_bearing(None) is False
def test_case_vtd(): assert is_size_bearing("vtd") is True
def test_case_pi(): assert is_size_bearing("pi1") is True
def test_set_membership():
    assert "VTD" in SIZE_BEARING_CODES
    assert "EP" not in SIZE_BEARING_CODES
