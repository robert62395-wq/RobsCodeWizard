"""Phase 3 tests for end-to-end description translator."""
import pytest
from app.services.description_translator import translate_description, translate_rows


def _make_map():
    return {
        "schema_version": "1.0",
        "map_version": "test",
        "generated": None,
        "entries": [
            {
                "id": "vdt-EP->odot-EP",
                "vdt": {"code": "EP", "type": "Point", "description": "Edge of Pavement"},
                "odot": {"code": "EP", "type": "Point", "description": "Edge of Pavement"},
                "confidence": "exact", "match_basis": ["description", "type"],
                "score": 1.0, "user_override": False, "notes": "",
            },
            {
                "id": "vdt-DR->odot-DR",
                "vdt": {"code": "DR", "type": "Linework", "description": "Driveway"},
                "odot": {"code": "DR", "type": "Linework", "description": "Driveway"},
                "confidence": "exact", "match_basis": ["description", "type"],
                "score": 1.0, "user_override": False, "notes": "",
            },
        ],
    }


def test_vdt_to_odot_basic():
    out, info = translate_description("EP B", "vdt_to_odot", map_data=_make_map())
    assert out == "EP BL*"
    assert info["linework_changes"] == 1
    assert info["code_changes"] == 0


def test_odot_to_vdt_basic():
    out, info = translate_description("EP BL*", "odot_to_vdt", map_data=_make_map())
    assert out == "EP B"
    assert info["linework_changes"] == 1


def test_odot_numeric_to_vdt():
    out, info = translate_description("EP 1", "odot_to_vdt", map_data=_make_map())
    assert out == "EP B"
    assert info["linework_changes"] == 1


def test_ambiguous_flagged_vdt_to_odot():
    out, info = translate_description("EP CC", "vdt_to_odot", map_data=_make_map())
    assert out == "EP OC*"
    assert "CC" in info["ambiguous_tokens"]


def test_ambiguous_flagged_odot_to_vdt_numeric():
    out, info = translate_description("EP 3", "odot_to_vdt", map_data=_make_map())
    assert out == "EP BC"
    assert "3" in info["ambiguous_tokens"]


def test_unmatched_code_flagged():
    out, info = translate_description("UNKNOWN B", "vdt_to_odot", map_data=_make_map())
    assert "BL*" in out
    assert info["linework_changes"] == 1


def test_empty_description():
    out, info = translate_description("", "vdt_to_odot", map_data=_make_map())
    assert out == ""
    assert info["code_changes"] == 0


def test_translate_rows_summary():
    rows = [
        {"P": 1, "D": "EP B"},
        {"P": 2, "D": "DR BC"},
        {"P": 3, "D": "EP"},
    ]
    out_rows, summary = translate_rows(rows, "vdt_to_odot", map_data=_make_map())
    assert summary["rows_changed"] == 2
    assert summary["linework_changes"] == 2
    assert out_rows[0]["D"] == "EP BL*"
    assert out_rows[1]["D"] == "DR BC*"
    assert out_rows[2]["D"] == "EP"


def test_translate_rows_with_ambiguous():
    rows = [{"P": 100, "D": "EP CC"}]
    _, summary = translate_rows(rows, "vdt_to_odot", map_data=_make_map())
    assert len(summary["ambiguous_rows"]) == 1
    assert summary["ambiguous_rows"][0]["point"] == 100
