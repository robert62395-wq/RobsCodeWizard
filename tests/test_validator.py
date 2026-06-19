from app.services.validator import validate_rows
from app.services.catalog_loader import load_catalog


def test_validate_flags_unknown_and_zero():
    rows = [{"P":"1","N":"1","E":"1","Z":"100","D":"EPA"},
            {"P":"2","N":"1","E":"1","Z":"0","D":"ZZZ"}]
    r = validate_rows(rows, ["EPA","WAFH"])
    assert r[0]["valid"] is True
    assert r[1]["valid"] is False


def test_validate_with_codeset_recognizes_linework_commands():
    vdt = load_catalog("vdt")
    rows = [
        {"P":"1","N":"1","E":"1","Z":"100","D":"EPA B"},
        {"P":"2","N":"1","E":"1","Z":"100","D":"EPA E"},
        {"P":"3","N":"1","E":"1","Z":"100","D":"EPA BC EC"},
    ]
    r = validate_rows(rows, vdt)
    assert all(x["valid"] for x in r)


def test_validate_odot_recognizes_linework():
    odot = load_catalog("odot")
    rows = [
        {"P":"1","N":"1","E":"1","Z":"100","D":"EP BL*"},
        {"P":"2","N":"1","E":"1","Z":"100","D":"EP EL*"},
        {"P":"3","N":"1","E":"1","Z":"100","D":"EP OC*"},
    ]
    r = validate_rows(rows, odot)
    assert all(x["valid"] for x in r)


def test_validate_multi_codes():
    vdt = load_catalog("vdt")
    rows = [{"P":"1","N":"1","E":"1","Z":"100","D":"EPA E EPC B"}]
    r = validate_rows(rows, vdt)
    assert r[0]["valid"] is True
