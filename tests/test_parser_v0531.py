"""Tests for v0.5.3.1 PNEZD parser error recovery."""
import pytest
from pathlib import Path
from app.services.parser import parse_pnezd, parse_pnezd_with_errors


def test_legacy_api_returns_list(tmp_path):
    p = tmp_path / "good.csv"
    p.write_text("1,1000,2000,800,EP\n2,1001,2001,801,DR\n", encoding="utf-8")
    rows = parse_pnezd(p)
    assert isinstance(rows, list)
    assert len(rows) == 2


def test_with_errors_returns_result(tmp_path):
    p = tmp_path / "good.csv"
    p.write_text("1,1000,2000,800,EP\n", encoding="utf-8")
    result = parse_pnezd_with_errors(p)
    assert hasattr(result, "rows")
    assert hasattr(result, "errors")
    assert len(result.rows) == 1


def test_empty_point_number_flagged(tmp_path):
    p = tmp_path / "bad.csv"
    p.write_text("1,1000,2000,800,EP\n,1001,2001,801,DR\n", encoding="utf-8")
    result = parse_pnezd_with_errors(p)
    assert len(result.rows) == 1
    assert len(result.errors) == 1
    assert "P field" in result.errors[0].reason or "Empty Point" in result.errors[0].reason


def test_non_numeric_n_is_warning_not_fatal(tmp_path):
    p = tmp_path / "warn.csv"
    p.write_text("1,not_a_number,2000,800,EP\n", encoding="utf-8")
    result = parse_pnezd_with_errors(p)
    # Row is still loaded with N replaced by "0" - that's a soft warning.
    assert len(result.rows) == 1
    assert len(result.errors) == 1
    assert "Non-numeric N" in result.errors[0].reason


def test_blank_lines_skipped(tmp_path):
    p = tmp_path / "blanks.csv"
    p.write_text("1,1000,2000,800,EP\n\n\n2,1001,2001,801,DR\n", encoding="utf-8")
    result = parse_pnezd_with_errors(p)
    assert len(result.rows) == 2
    assert len(result.errors) == 0