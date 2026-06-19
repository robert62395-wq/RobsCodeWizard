from app.services.vdt_lookup_loader import load_vdt_codes


def test_catalog_size_and_codes():
    codes = load_vdt_codes()
    assert len(codes) >= 380
    code_set = {c["code"] for c in codes}
    for expected in ("EPA","BDCR","SCCP","WAFH","STCB","VTD","GAHM","ELTWC"):
        assert expected in code_set


def test_catalog_types():
    codes = load_vdt_codes()
    types = {c["type"] for c in codes}
    assert "Linework" in types and "Symbol" in types and "Point" in types
