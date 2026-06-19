import tempfile, pathlib
from app.services.parser import parse_pnezd

def test_parse_basic():
    p = pathlib.Path(tempfile.mkstemp(suffix=".csv")[1])
    p.write_text("1,5000,5000,100,EPA\n2,5001,5002,0,WAFH\n")
    rows = parse_pnezd(str(p))
    assert len(rows) == 2 and rows[0]["D"] == "EPA"
