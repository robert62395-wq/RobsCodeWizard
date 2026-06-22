import pytest
from app.services.suggester import build_suggestions


def _row(d, z=850.0): return {"P": 1, "D": d, "Z": z}
def _valid_result(): return [{"valid": True, "issues": []}]
def _invalid_result(): return [{"valid": False, "issues": ["x"]}]


def test_valid_row_no_suggestion():
    rows = [_row("EP")]
    out = build_suggestions(rows, {"EP"}, _valid_result())
    assert out[0] == ""


def test_orphan_moved_behind_slash():
    rows = [_row("EP foobar")]
    out = build_suggestions(rows, {"EP"}, _invalid_result())
    assert "/" in out[0]
    assert "FOOBAR" in out[0]
    assert out[0].startswith("EP")


def test_existing_slash_tail_preserved():
    rows = [_row("EP foobar / note")]
    out = build_suggestions(rows, {"EP"}, _invalid_result())
    assert "NOTE" in out[0] or "note" in out[0]


def test_size_bearing_code_kept_with_size():
    rows = [_row("VTD 12")]
    out = build_suggestions(rows, {"VTD"}, _invalid_result())
    if out[0]:
        parts = out[0].split("/") if "/" in out[0] else [out[0]]
        assert "12" in parts[0]
