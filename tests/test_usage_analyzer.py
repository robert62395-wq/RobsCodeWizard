import pytest
from app.services.usage_analyzer import analyze_used_codes, build_usage_summary


def test_empty_rows():
    assert analyze_used_codes([]) == {}


def test_single_row():
    assert analyze_used_codes([{"D": "EP"}]) == {"EP": 1}


def test_count_increments():
    rows = [{"D": "EP"}, {"D": "EP"}, {"D": "EP"}]
    assert analyze_used_codes(rows) == {"EP": 3}


def test_multiple_codes():
    rows = [{"D": "EP"}, {"D": "DR"}, {"D": "EP"}]
    assert analyze_used_codes(rows) == {"EP": 2, "DR": 1}


def test_line_connects_not_counted():
    rows = [{"D": "EP 1"}, {"D": "EP BL*"}]
    assert analyze_used_codes(rows) == {"EP": 2}


def test_slash_tail_ignored():
    assert analyze_used_codes([{"D": "EP / foo bar comment"}]) == {"EP": 1}


def test_case_normalized():
    rows = [{"D": "ep"}, {"D": "EP"}, {"D": "Ep"}]
    assert analyze_used_codes(rows) == {"EP": 3}


def test_summary_all_exact():
    used_counts = {"EP": 3, "DR": 2}
    map_data = {"entries": [
        {"id": "1", "vdt": {"code": "EP"}, "odot": {"code": "EP"}, "confidence": "exact", "user_override": False},
        {"id": "2", "vdt": {"code": "DR"}, "odot": {"code": "DR"}, "confidence": "exact", "user_override": False},
    ]}
    summary = build_usage_summary(used_counts, map_data)
    assert summary["exact"] == 2


def test_summary_not_in_map():
    used_counts = {"WEIRD": 1}
    summary = build_usage_summary(used_counts, {"entries": []})
    assert "WEIRD" in summary["not_in_map"]
    assert summary["unmatched"] == 1


def test_summary_manual_override():
    used_counts = {"EP": 1}
    map_data = {"entries": [
        {"id": "1", "vdt": {"code": "EP"}, "odot": {"code": "EDGE"},
         "confidence": "manual", "user_override": True},
    ]}
    summary = build_usage_summary(used_counts, map_data)
    assert summary["manual"] == 1
