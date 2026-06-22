import pytest
from app.services.validator import validate_rows


def test_validator_ep_valid():
    rows = [{"P": 1, "D": "EP", "Z": 850.0}]
    results = validate_rows(rows, {"EP"})
    assert results[0]["valid"] is True


def test_validator_vtd_12_not_flagged():
    rows = [{"P": 1, "D": "VTD 12", "Z": 850.0}]
    results = validate_rows(rows, {"VTD"})
    assert results[0]["valid"] is True
    assert not any("12" in iss for iss in results[0]["issues"])


def test_validator_pi1_6_not_flagged():
    rows = [{"P": 1, "D": "PI1 6", "Z": 850.0}]
    results = validate_rows(rows, {"PI1"})
    assert results[0]["valid"] is True


def test_validator_unknown_token_flagged():
    rows = [{"P": 1, "D": "EP foobar", "Z": 850.0}]
    results = validate_rows(rows, {"EP"})
    assert results[0]["valid"] is False
    assert any("FOOBAR" in iss for iss in results[0]["issues"])


def test_validator_ignores_comment_after_slash():
    rows = [{"P": 1, "D": "EP / this is just a note", "Z": 850.0}]
    results = validate_rows(rows, {"EP"})
    assert results[0]["valid"] is True


def test_validator_zero_elev_flagged():
    rows = [{"P": 1, "D": "EP", "Z": 0.0}]
    results = validate_rows(rows, {"EP"})
    assert any("Zero" in iss for iss in results[0]["issues"])


def test_validator_grbr_24():
    rows = [{"P": 1, "D": "GRBR 24", "Z": 850.0}]
    results = validate_rows(rows, {"GRBR"})
    assert results[0]["valid"] is True
