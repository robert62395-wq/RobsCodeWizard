"""Smoke tests for csv_exporter.write_pnezd."""
import csv
from app.services.csv_exporter import write_pnezd


def test_write_pnezd_basic(tmp_path):
    out = tmp_path / "out.csv"
    rows = [
        {"P": 1, "N": 100.0, "E": 200.0, "Z": 10.0, "D": "EP"},
        {"P": 2, "N": 101.0, "E": 201.0, "Z": 10.5, "D": "BL"},
        {"P": 3, "N": 102.0, "E": 202.0, "Z": 11.0, "D": "EL"},
    ]
    write_pnezd(rows, str(out))
    with open(out, newline="", encoding="utf-8") as f:
        data = list(csv.reader(f))
    assert len(data) == 3
    assert data[0] == ["1", "100.0", "200.0", "10.0", "EP"]
    assert data[2][4] == "EL"


def test_write_pnezd_comma_in_description(tmp_path):
    out = tmp_path / "with_comma.csv"
    rows = [
        {"P": 10, "N": 500, "E": 600, "Z": 0, "D": "STA 1+00, OFFSET 5"},
    ]
    write_pnezd(rows, str(out))
    with open(out, newline="", encoding="utf-8") as f:
        data = list(csv.reader(f))
    assert len(data) == 1
    # csv module round-trips comma-containing fields correctly
    assert data[0][4] == "STA 1+00, OFFSET 5"
    # raw file contains quotes around that field
    raw = out.read_text(encoding="utf-8")
    assert '"STA 1+00, OFFSET 5"' in raw


def test_write_pnezd_no_header_row(tmp_path):
    out = tmp_path / "no_header.csv"
    rows = [{"P": 99, "N": 1, "E": 2, "Z": 3, "D": "X"}]
    write_pnezd(rows, str(out))
    first_line = out.read_text(encoding="utf-8").splitlines()[0]
    # First line should be data, not "P,N,E,Z,D"
    assert first_line.startswith("99,")
    assert "P,N,E,Z,D" not in out.read_text(encoding="utf-8")
