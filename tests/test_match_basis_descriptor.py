import pytest
from app.services.match_basis_descriptor import describe, short_label


def test_describe_manual():
    entry = {"user_override": True, "confidence": "manual",
             "vdt": {"code": "EP"}, "odot": {"code": "EDGE"}}
    assert "Manual" in describe(entry)


def test_describe_exact():
    entry = {"confidence": "exact", "score": 1.0,
             "match_basis": ["description", "type"],
             "vdt": {"code": "EP"}, "odot": {"code": "EP"}}
    assert "Exact" in describe(entry)


def test_describe_best_guess():
    entry = {"confidence": "best-guess", "score": 0.85,
             "match_basis": ["description", "type"],
             "vdt": {"code": "DR"}, "odot": {"code": "DRIVE"}}
    desc = describe(entry)
    assert "Best guess" in desc
    assert "85" in desc


def test_describe_unmatched():
    entry = {"confidence": "unmatched", "vdt": {"code": "X"}, "odot": None}
    assert "No match" in describe(entry)


def test_describe_empty():
    assert describe(None) == ""


def test_short_label_exact():
    assert short_label({"confidence": "exact"}) == "Exact"


def test_short_label_best_guess():
    label = short_label({"confidence": "best-guess", "score": 0.85})
    assert "Best-guess" in label
    assert "85" in label


def test_short_label_manual():
    assert "Manual" in short_label({"user_override": True, "confidence": "manual"})
