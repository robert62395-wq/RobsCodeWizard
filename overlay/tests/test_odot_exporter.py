"""Phase 5 tests for ODOT exporter."""
import csv
import pytest
from pathlib import Path

from app.services.odot_exporter import export_civil3d, export_openroads


def _sample_rows():
    return [
        {"P": 100, "N": 1000.0, "E": 2000.0, "Z": 850.0, "D": "EP 1"},
        {"P": 101, "N": 1001.0, "E": 2001.0, "Z": 851.0, "D": "EP"},
        {"P": 102, "N": 1002.0, "E": 2002.0, "Z": 852.0, "D": "DR 2 EP1"},
    ]


def _read_csv(path):
    with open(path, "r", encoding="utf-8", newline="") as f:
        return list(csv.reader(f))


def test_civil3d_no_header(tmp_path):
    out = tmp_path / "out.csv"
    export_civil3d(_sample_rows(), out)
    rows = _read_csv(out)
    assert rows[0][0].lower() not in ("p", "point", "point number", "pt")


def test_civil3d_numeric_to_alpha(tmp_path):
    out = tmp_path / "out.csv"
    written, conversions = export_civil3d(_sample_rows(), out)
    assert written == 3
    assert conversions == 2
    rows = _read_csv(out)
    assert rows[0][4] == "EP BL*"
    assert rows[2][4] == "DR EL* EP1"


def test_civil3d_passthrough_when_no_numeric(tmp_path):
    out = tmp_path / "out.csv"
    rows_in = [{"P": 1, "N": 1.0, "E": 2.0, "Z": 3.0, "D": "EP BL*"}]
    written, conversions = export_civil3d(rows_in, out)
    assert conversions == 0
    rows = _read_csv(out)
    assert rows[0][4] == "EP BL*"


def test_openroads_alpha_to_numeric(tmp_path):
    out = tmp_path / "out.csv"
    rows_in = [
        {"P": 1, "N": 1.0, "E": 2.0, "Z": 3.0, "D": "EP BL*"},
        {"P": 2, "N": 1.0, "E": 2.0, "Z": 3.0, "D": "EP EL*"},
        {"P": 3, "N": 1.0, "E": 2.0, "Z": 3.0, "D": "DR OC*"},
    ]
    written, conversions = export_openroads(rows_in, out, use_numeric=True)
    assert conversions == 3
    rows = _read_csv(out)
    assert rows[0][4] == "EP 1"
    assert rows[1][4] == "EP 2"
    assert rows[2][4] == "DR 3"


def test_openroads_preserve_alpha(tmp_path):
    out = tmp_path / "out.csv"
    rows_in = [{"P": 1, "N": 1.0, "E": 2.0, "Z": 3.0, "D": "EP BL*"}]
    written, conversions = export_openroads(rows_in, out, use_numeric=False)
    assert conversions == 0
    rows = _read_csv(out)
    assert rows[0][4] == "EP BL*"


def test_preserves_NEZ(tmp_path):
    out = tmp_path / "out.csv"
    rows_in = [{"P": 100, "N": 12345.678, "E": 98765.432, "Z": 850.0, "D": "EP"}]
    export_civil3d(rows_in, out)
    rows = _read_csv(out)
    assert rows[0][1] == "12345.678"
    assert rows[0][2] == "98765.432"
    assert rows[0][3] == "850.0"


def test_attribute_pairs(tmp_path):
    out = tmp_path / "out.csv"
    rows_in = [{"P": 100, "N": 1.0, "E": 2.0, "Z": 3.0, "D": "EP", "attributes": [("Material", "Asphalt")]}]
    export_civil3d(rows_in, out)
    rows = _read_csv(out)
    assert rows[0][5] == "Material"
    assert rows[0][6] == "Asphalt"


def test_dual_stringing_preserved_civil3d(tmp_path):
    out = tmp_path / "out.csv"
    rows_in = [{"P": 100, "N": 1.0, "E": 2.0, "Z": 3.0, "D": "EP1 1"}]
    export_civil3d(rows_in, out)
    rows = _read_csv(out)
    assert rows[0][4] == "EP1 BL*"


def test_dual_stringing_preserved_openroads(tmp_path):
    out = tmp_path / "out.csv"
    rows_in = [{"P": 100, "N": 1.0, "E": 2.0, "Z": 3.0, "D": "EP1 BL*"}]
    export_openroads(rows_in, out, use_numeric=True)
    rows = _read_csv(out)
    assert rows[0][4] == "EP1 1"


def test_compound_codes_civil3d(tmp_path):
    out = tmp_path / "out.csv"
    rows_in = [{"P": 100, "N": 1.0, "E": 2.0, "Z": 3.0, "D": "DR1 3 DR1 2 EP1"}]
    written, conversions = export_civil3d(rows_in, out)
    assert conversions == 2
    rows = _read_csv(out)
    assert rows[0][4] == "DR1 OC* DR1 EL* EP1"


def test_empty_rows_list(tmp_path):
    out = tmp_path / "out.csv"
    written, conversions = export_civil3d([], out)
    assert written == 0
    assert conversions == 0


def test_creates_parent_dir(tmp_path):
    out = tmp_path / "subdir" / "out.csv"
    export_civil3d(_sample_rows(), out)
    assert out.exists()
