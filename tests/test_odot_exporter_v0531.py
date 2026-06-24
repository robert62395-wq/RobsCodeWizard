"""Tests for v0.5.3.1 ODOT exporter row-level error recovery."""
import pytest
from pathlib import Path
from app.services.odot_exporter import (
    export_vdt_to_civil3d,
    export_odot_to_civil3d,
    export_odot_to_openroads,
)


def test_civil3d_vdt_returns_three_tuple(tmp_path):
    out = tmp_path / "out.csv"
    rows = [{"P": "1", "N": "1000", "E": "2000", "Z": "800", "D": "EP"}]
    result = export_vdt_to_civil3d(rows, out)
    assert len(result) == 3
    written, conversions, errors = result
    assert written == 1
    assert errors == []


def test_civil3d_odot_returns_three_tuple(tmp_path):
    out = tmp_path / "out.csv"
    rows = [{"P": "1", "N": "1000", "E": "2000", "Z": "800", "D": "EP BL*"}]
    result = export_odot_to_civil3d(rows, out)
    assert len(result) == 3
    written, conversions, errors = result
    assert written == 1


def test_openroads_returns_three_tuple(tmp_path):
    out = tmp_path / "out.csv"
    rows = [{"P": "1", "N": "1000", "E": "2000", "Z": "800", "D": "EP 1"}]
    result = export_odot_to_openroads(rows, out, use_numeric=True)
    assert len(result) == 3


def test_legacy_export_civil3d_alias_still_two_tuple(tmp_path):
    """The export_civil3d alias keeps the old 2-tuple return shape."""
    from app.services.odot_exporter import export_civil3d
    out = tmp_path / "out.csv"
    rows = [{"P": "1", "N": "1000", "E": "2000", "Z": "800", "D": "EP"}]
    result = export_civil3d(rows, out)
    assert len(result) == 2  # backward compatible