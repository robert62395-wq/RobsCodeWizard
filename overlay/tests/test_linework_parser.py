"""Phase 2 tests for the linework token parser."""
from pathlib import Path

import pytest

from app.services.linework_parser import (
    tokenize, classify_token, parse,
)


# ---------- tokenize ----------

def test_tokenize_simple():
    assert tokenize("EP 1") == ["EP", "1"]


def test_tokenize_multi_space():
    assert tokenize("EP   1") == ["EP", "1"]


def test_tokenize_leading_trailing_space():
    assert tokenize("  EP 1  ") == ["EP", "1"]


def test_tokenize_empty():
    assert tokenize("") == []
    assert tokenize("   ") == []


# ---------- classify_token ----------

def test_classify_numeric():
    assert classify_token("1", "odot") == "numeric_lc"
    assert classify_token("2", "odot") == "numeric_lc"
    assert classify_token("3", "odot") == "numeric_lc"
    assert classify_token("4", "odot") == "numeric_lc"


def test_classify_numeric_suffix_is_code():
    assert classify_token("EP1", "odot") == "point_code"
    assert classify_token("DR1", "odot") == "point_code"
    assert classify_token("WALK1", "odot") == "point_code"


def test_classify_lettered():
    assert classify_token("BL", "odot") == "lettered_lc"
    assert classify_token("BL*", "odot") == "lettered_lc"
    assert classify_token("EL*", "odot") == "lettered_lc"


def test_classify_vdt_only_in_vdt_dialect():
    assert classify_token("B", "vdt") == "vdt_lc"
    assert classify_token("B", "odot") == "point_code"  # B is a ground-break code in ODOT


# ---------- parse ----------

def test_parse_ep_1():
    result = parse("EP 1", "odot")
    assert result == [{"code": "EP", "line_connects": ["1"], "raw_index": 0}]


def test_parse_ep_2_end_line():
    result = parse("EP 2", "odot")
    assert result == [{"code": "EP", "line_connects": ["2"], "raw_index": 0}]


def test_parse_dr_2_ep1():
    result = parse("DR 2 EP1", "odot")
    assert len(result) == 2
    assert result[0]["code"] == "DR"
    assert result[0]["line_connects"] == ["2"]
    assert result[1]["code"] == "EP1"
    assert result[1]["line_connects"] == []


def test_parse_dr1_3_dr1_2_ep1():
    result = parse("DR1 3 DR1 2 EP1", "odot")
    assert len(result) == 3
    assert result[0]["code"] == "DR1"
    assert result[0]["line_connects"] == ["3"]
    assert result[1]["code"] == "DR1"
    assert result[1]["line_connects"] == ["2"]
    assert result[2]["code"] == "EP1"
    assert result[2]["line_connects"] == []


def test_parse_line_2d_1_ep_1():
    result = parse("LINE_2D 1 EP 1", "odot")
    assert len(result) == 2
    assert result[0]["code"] == "LINE_2D"
    assert result[0]["line_connects"] == ["1"]
    assert result[1]["code"] == "EP"
    assert result[1]["line_connects"] == ["1"]


def test_parse_just_code():
    result = parse("EP", "odot")
    assert result == [{"code": "EP", "line_connects": [], "raw_index": 0}]


def test_parse_empty():
    assert parse("", "odot") == []


# ---------- fixture file ----------

FIXTURE = Path(__file__).parent / "fixtures" / "241867_Topo_Only_PK.csv"


def _load_descriptions(point_numbers):
    """Pull the D column for the requested point numbers out of the fixture CSV."""
    wanted = {str(p) for p in point_numbers}
    out = {}
    if not FIXTURE.exists():
        return out
    for line in FIXTURE.read_text(encoding="utf-8").splitlines():
        parts = [p.strip() for p in line.split(",")]
        if not parts or parts[0] not in wanted:
            continue
        if len(parts) >= 5:
            out[parts[0]] = parts[4]
    return out


def test_parse_fixture_examples():
    descs = _load_descriptions([1000, 1072, 1228, 1230, 1257, 1268])
    if not descs:
        pytest.skip("Fixture file not present")

    # Spot-check parse() against real-world rows
    if "1000" in descs:
        # 1000,...,EP 1 -> EP begin line
        entries = parse(descs["1000"], "odot")
        assert entries[0]["code"] == "EP"
        assert "1" in entries[0]["line_connects"]

    if "1072" in descs:
        # 1072,...,DR 2 EP1 -> DR end line, then EP1
        entries = parse(descs["1072"], "odot")
        assert entries[0]["code"] == "DR"
        assert "2" in entries[0]["line_connects"]
        assert entries[1]["code"] == "EP1"

    if "1228" in descs:
        # 1228,...,LINE_2D 1 EP 1 -> both codes begin
        entries = parse(descs["1228"], "odot")
        codes = [e["code"] for e in entries]
        assert "LINE_2D" in codes
        assert "EP" in codes
