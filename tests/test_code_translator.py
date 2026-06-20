"""Phase 3 tests for point code translator."""
import pytest
from app.services.code_translator import translate_code, clear_cache


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
                "id": "vdt-DR->odot-DRIVE",
                "vdt": {"code": "DR", "type": "Linework", "description": "Driveway"},
                "odot": {"code": "DRIVE", "type": "Linework", "description": "Driveway"},
                "confidence": "best-guess", "match_basis": ["description", "type"],
                "score": 0.85, "user_override": False, "notes": "",
            },
        ],
    }


def test_vdt_to_odot_exact():
    assert translate_code("EP", "vdt_to_odot", data=_make_map()) == ("EP", "exact")


def test_vdt_to_odot_best_guess():
    assert translate_code("DR", "vdt_to_odot", data=_make_map()) == ("DRIVE", "best-guess")


def test_vdt_to_odot_passthrough_when_missing():
    assert translate_code("UNKNOWN", "vdt_to_odot", data=_make_map()) == ("UNKNOWN", "passthrough")


def test_odot_to_vdt_exact():
    assert translate_code("EP", "odot_to_vdt", data=_make_map()) == ("EP", "exact")


def test_odot_to_vdt_reverse_lookup():
    assert translate_code("DRIVE", "odot_to_vdt", data=_make_map()) == ("DR", "best-guess")


def test_odot_to_vdt_passthrough():
    assert translate_code("NOPE", "odot_to_vdt", data=_make_map()) == ("NOPE", "passthrough")


def test_invalid_direction_raises():
    with pytest.raises(ValueError, match="direction"):
        translate_code("EP", "sideways", data=_make_map())


def test_clear_cache_callable():
    clear_cache()
