"""Tests for v0.5.3.1 parse error collection."""
import pytest
from app.services.parse_errors import ParseError, ParseResult


def test_parse_error_str():
    err = ParseError(line_number=42, snippet="bad,row,data", reason="invalid format")
    s = str(err)
    assert "42" in s
    assert "invalid format" in s
    assert "bad,row,data" in s


def test_parse_result_summary_no_errors():
    result = ParseResult(rows=[{"P": 1}], total_lines=1)
    summary = result.summary()
    assert "1 rows" in summary
    assert "skipped" not in summary


def test_parse_result_summary_with_errors():
    result = ParseResult(
        rows=[{"P": 1}, {"P": 2}],
        total_lines=5,
        errors=[
            ParseError(line_number=3, snippet="bad", reason="missing P"),
            ParseError(line_number=4, snippet="worse", reason="bad N"),
            ParseError(line_number=5, snippet="awful", reason="bad Z"),
        ],
    )
    summary = result.summary()
    assert "2 of 5" in summary
    assert "3 rows skipped" in summary


def test_parse_result_has_errors_true():
    result = ParseResult(errors=[ParseError(1, "x", "y")])
    assert result.has_errors is True
    assert result.error_count == 1


def test_parse_result_has_errors_false():
    result = ParseResult(rows=[{"P": 1}])
    assert result.has_errors is False
    assert result.error_count == 0


def test_parse_error_snippet_truncation_in_str():
    err = ParseError(line_number=1, snippet="x" * 200, reason="too long")
    assert len(str(err)) < 200