import pytest
from app.services.catalog_loader import load_catalog


def test_load_vdt():
    cs = load_catalog("vdt")
    assert cs.name == "vdt"
    assert len(cs.codes) == 381
    assert cs.parser_kind == "pnezd"
    assert cs.linework_grammar.begin_line == "B"
    assert cs.is_known_code("EPA")


def test_load_odot():
    cs = load_catalog("odot")
    assert cs.name == "odot"
    assert len(cs.codes) == 314
    assert cs.parser_kind == "odot"
    assert cs.linework_grammar.begin_line == "BL*"
    assert cs.is_known_code("PP")


def test_unknown_raises():
    with pytest.raises(ValueError):
        load_catalog("xyz")


def test_case_insensitive():
    assert load_catalog("VDT").name == "vdt"
    assert load_catalog("ODOT").name == "odot"
