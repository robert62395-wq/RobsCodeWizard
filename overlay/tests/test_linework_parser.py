import pytest
from app.services.linework_parser import tokenize, classify_token, parse


def test_tokenize_simple():
    assert tokenize("EP 1") == ["EP", "1"]


def test_parse_ep_1():
    result = parse("EP 1", "odot")
    assert result == [{"code": "EP", "line_connects": ["1"], "size": None, "raw_index": 0}]


def test_parse_vtd_with_size():
    result = parse("VTD 12", "vdt")
    assert result[0]["code"] == "VTD"
    assert result[0]["size"] == "12"


def test_parse_pi1_with_size():
    result = parse("PI1 6", "vdt")
    assert result[0]["size"] == "6"


def test_parse_grbr_with_size():
    result = parse("GRBR 24", "vdt")
    assert result[0]["size"] == "24"


def test_parse_size_then_vdt_linework():
    result = parse("VTD 12 B", "vdt")
    assert result[0]["size"] == "12"
    assert result[0]["line_connects"] == ["B"]


def test_parse_size_bearing_no_size_follows():
    result = parse("VTD", "vdt")
    assert result[0]["size"] is None


def test_parse_ep_size_not_absorbed():
    result = parse("EP 1", "odot")
    assert result[0]["line_connects"] == ["1"]
    assert result[0]["size"] is None


def test_parse_dr_2_ep1():
    result = parse("DR 2 EP1", "odot")
    assert len(result) == 2
    assert result[0]["code"] == "DR"
    assert result[0]["line_connects"] == ["2"]
    assert result[1]["code"] == "EP1"
