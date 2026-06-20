import pytest
from app.services import translation_map as tm


def make_valid():
    return {
        "schema_version": "1.0",
        "map_version": "0.4.1",
        "generated": "2026-06-20T00:00:00Z",
        "entries": [{
            "id": "vdt-EP->odot-EP",
            "vdt": {"code": "EP", "type": "Point", "description": "Edge of Pavement"},
            "odot": {"code": "EP", "type": "Point", "description": "Edge of Pavement"},
            "confidence": "exact", "match_basis": ["description", "type"],
            "score": 1.0, "user_override": False, "notes": "",
        }],
    }


def test_roundtrip(tmp_path):
    p = tmp_path / "m.json"
    data = make_valid()
    tm.save(data, p)
    assert tm.load(p) == data


def test_validate_missing_top_key():
    bad = make_valid(); del bad["entries"]
    with pytest.raises(ValueError, match="missing keys"):
        tm.validate(bad)


def test_validate_bad_confidence():
    bad = make_valid(); bad["entries"][0]["confidence"] = "maybe"
    with pytest.raises(ValueError, match="invalid confidence"):
        tm.validate(bad)


def test_validate_both_null():
    bad = make_valid()
    bad["entries"][0]["vdt"] = None
    bad["entries"][0]["odot"] = None
    with pytest.raises(ValueError, match="both vdt and odot null"):
        tm.validate(bad)


def test_find_helpers():
    data = make_valid()
    assert tm.find_by_vdt("EP", data)["odot"]["code"] == "EP"
    assert tm.find_by_odot("EP", data)["vdt"]["code"] == "EP"
    assert tm.find_by_vdt("NOPE", data) is None
