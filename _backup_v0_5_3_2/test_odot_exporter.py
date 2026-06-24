import csv
import pytest
from pathlib import Path
from app.services.odot_exporter import (
    export_vdt_to_civil3d, export_odot_to_civil3d, export_odot_to_openroads,
)


def _read_csv(path):
    with open(path, "r", encoding="utf-8", newline="") as f:
        return list(csv.reader(f))


# VDT -> Civil3D
def test_vdt_civil3d_letters_only(tmp_path):
    out = tmp_path / "v.csv"
    rows = [{"P": 1, "N": 1.0, "E": 2.0, "Z": 3.0, "D": "EP B"}]
    export_vdt_to_civil3d(rows, out)
    assert _read_csv(out)[0][4] == "EP B"


def test_vdt_civil3d_strips_asterisk(tmp_path):
    out = tmp_path / "v.csv"
    rows = [{"P": 1, "N": 1.0, "E": 2.0, "Z": 3.0, "D": "EP BL*"}]
    written, conversions = export_vdt_to_civil3d(rows, out)
    assert _read_csv(out)[0][4] == "EP B"
    assert conversions == 1


def test_vdt_civil3d_preserves_size(tmp_path):
    out = tmp_path / "v.csv"
    rows = [{"P": 1, "N": 1.0, "E": 2.0, "Z": 3.0, "D": "VTD 12"}]
    export_vdt_to_civil3d(rows, out)
    assert _read_csv(out)[0][4] == "VTD 12"


def test_vdt_civil3d_no_header(tmp_path):
    out = tmp_path / "v.csv"
    rows = [{"P": 1, "N": 1.0, "E": 2.0, "Z": 3.0, "D": "EP"}]
    export_vdt_to_civil3d(rows, out)
    assert _read_csv(out)[0][0] == "1"


# ODOT -> Civil3D
def test_odot_civil3d_numeric_to_alpha(tmp_path):
    out = tmp_path / "o.csv"
    rows = [{"P": 1, "N": 1.0, "E": 2.0, "Z": 3.0, "D": "EP 1"}]
    written, conversions = export_odot_to_civil3d(rows, out)
    assert _read_csv(out)[0][4] == "EP BL*"
    assert conversions == 1


def test_odot_civil3d_alpha_preserved(tmp_path):
    out = tmp_path / "o.csv"
    rows = [{"P": 1, "N": 1.0, "E": 2.0, "Z": 3.0, "D": "EP BL*"}]
    export_odot_to_civil3d(rows, out)
    assert _read_csv(out)[0][4] == "EP BL*"


# ODOT -> OpenRoads
def test_odot_openroads_alpha_to_numeric(tmp_path):
    out = tmp_path / "or.csv"
    rows = [{"P": 1, "N": 1.0, "E": 2.0, "Z": 3.0, "D": "EP BL*"}]
    written, conversions = export_odot_to_openroads(rows, out, use_numeric=True)
    assert _read_csv(out)[0][4] == "EP 1"
    assert conversions == 1


def test_odot_openroads_alpha_preserved_when_disabled(tmp_path):
    out = tmp_path / "or.csv"
    rows = [{"P": 1, "N": 1.0, "E": 2.0, "Z": 3.0, "D": "EP BL*"}]
    export_odot_to_openroads(rows, out, use_numeric=False)
    assert _read_csv(out)[0][4] == "EP BL*"


def test_slash_tail_preserved(tmp_path):
    out = tmp_path / "v.csv"
    rows = [{"P": 1, "N": 1.0, "E": 2.0, "Z": 3.0, "D": "EP B / my note"}]
    export_vdt_to_civil3d(rows, out)
    assert "/ my note" in _read_csv(out)[0][4]


def test_pnez_never_modified(tmp_path):
    out = tmp_path / "v.csv"
    rows = [{"P": 100, "N": 12345.678, "E": 98765.432, "Z": 850.5, "D": "EP B"}]
    export_vdt_to_civil3d(rows, out)
    r = _read_csv(out)
    assert r[0][0] == "100"
    assert r[0][1] == "12345.678"
    assert r[0][2] == "98765.432"
    assert r[0][3] == "850.5"
