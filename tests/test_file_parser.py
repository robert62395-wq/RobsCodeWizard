import tempfile, pathlib
from app.services.file_parser import parse_file
from app.services.catalog_loader import load_catalog


def _write(text, suffix=".csv"):
    p = pathlib.Path(tempfile.mkstemp(suffix=suffix)[1])
    p.write_text(text, encoding="utf-8")
    return p


def test_vdt_uses_pnezd_parser():
    vdt = load_catalog("vdt")
    p = _write("1,5000,5000,100,EPA\n")
    rows = parse_file(p, vdt)
    assert len(rows) == 1
    assert rows[0]["D"] == "EPA"
    # PNEZD parser doesn't add attributes key
    assert "attributes" not in rows[0]


def test_odot_uses_odot_parser():
    odot = load_catalog("odot")
    p = _write("1,5000,5000,100,EP BL*,Material,Asphalt\n")
    rows = parse_file(p, odot)
    assert len(rows) == 1
    # ODOT parser adds attributes key
    assert "attributes" in rows[0]
    assert rows[0]["attributes"][0]["code"] == "EP"


def test_none_codeset_falls_back_to_pnezd():
    p = _write("1,5000,5000,100,EPA\n")
    rows = parse_file(p, None)
    assert "attributes" not in rows[0]
