"""Tests for v0.5.3.3 parse_file_with_errors dispatcher."""
import pytest
from app.services.file_parser import parse_file, parse_file_with_errors
from app.services.parse_errors import ParseResult


def test_parse_file_returns_list(tmp_path):
    p = tmp_path / "good.csv"
    p.write_text("1,1000,2000,800,EP\n", encoding="utf-8")
    rows = parse_file(p, codeset=None)
    assert isinstance(rows, list)
    assert len(rows) == 1


def test_parse_file_with_errors_returns_parseresult(tmp_path):
    p = tmp_path / "good.csv"
    p.write_text("1,1000,2000,800,EP\n", encoding="utf-8")
    result = parse_file_with_errors(p, codeset=None)
    assert isinstance(result, ParseResult)
    assert len(result.rows) == 1
    assert len(result.errors) == 0


def test_parse_file_with_errors_pnezd_collects_errors(tmp_path):
    p = tmp_path / "bad.csv"
    p.write_text("1,1000,2000,800,EP\n,1001,2001,801,DR\n", encoding="utf-8")
    result = parse_file_with_errors(p, codeset=None)
    assert len(result.rows) == 1
    assert len(result.errors) == 1
    assert "P field" in result.errors[0].reason or "Point" in result.errors[0].reason


def test_parse_file_with_errors_odot_path_no_errors(tmp_path, monkeypatch):
    """ODOT path returns a ParseResult with no errors (v0.5.3.4+ wires those)."""
    class FakeCodeset:
        parser_kind = "odot"
    
    # Monkeypatch the odot_parser import to avoid needing a real odot file
    def fake_parse_odot(path, codeset):
        return [{"P": "1", "N": "1000", "E": "2000", "Z": "800", "D": "EPA"}]
    
    import app.services.odot_parser
    monkeypatch.setattr(app.services.odot_parser, "parse_odot", fake_parse_odot)
    
    result = parse_file_with_errors(tmp_path / "any.csv", codeset=FakeCodeset())
    assert isinstance(result, ParseResult)
    assert len(result.rows) == 1
    assert len(result.errors) == 0