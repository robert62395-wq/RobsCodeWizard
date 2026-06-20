"""Phase 2 tests for numeric<->alphabetic line-connect translator."""
import pytest

from app.services.line_connect_translator import (
    convert_numeric_to_alpha,
    convert_alpha_to_numeric,
    preview_changes,
    NUMERIC_TO_ALPHA,
)


def test_simple_begin_line():
    assert convert_numeric_to_alpha("EP 1") == ("EP BL*", 1)


def test_end_line():
    assert convert_numeric_to_alpha("EP 2") == ("EP EL*", 1)


def test_open_curve():
    assert convert_numeric_to_alpha("EP 3") == ("EP OC*", 1)


def test_close_shape():
    assert convert_numeric_to_alpha("EP 4") == ("EP CL*", 1)


def test_compound_dr_2_ep1():
    # DR end line, then EP1 (a separate point code)
    assert convert_numeric_to_alpha("DR 2 EP1") == ("DR EL* EP1", 1)


def test_compound_multi_code():
    assert convert_numeric_to_alpha("DR1 3 DR1 2 EP1") == ("DR1 OC* DR1 EL* EP1", 2)


def test_line_2d_with_ep():
    assert convert_numeric_to_alpha("LINE_2D 1 EP 1") == ("LINE_2D BL* EP BL*", 2)


def test_no_change_when_code_only():
    assert convert_numeric_to_alpha("EP") == ("EP", 0)


def test_already_alpha():
    assert convert_numeric_to_alpha("EP BL*") == ("EP BL*", 0)


def test_numeric_suffix_point_code_preserved():
    # EP1 is a point code, the trailing 1 is the line connect
    assert convert_numeric_to_alpha("EP1 1") == ("EP1 BL*", 1)


def test_empty():
    assert convert_numeric_to_alpha("") == ("", 0)


def test_reverse_not_implemented():
    with pytest.raises(NotImplementedError, match="v0.4.5"):
        convert_alpha_to_numeric("EP BL*")


def test_preview_changes_basic():
    rows = [
        {"point": 1000, "description": "EP 1"},
        {"point": 1001, "description": "X"},
        {"point": 1072, "description": "DR 2 EP1"},
    ]
    preview = preview_changes(rows)
    assert len(preview) == 2
    points = {p["point"] for p in preview}
    assert 1000 in points
    assert 1072 in points
    # row 1001 ("X") has no change, should be excluded
    assert 1001 not in points


def test_preview_respects_limit():
    rows = [{"point": i, "description": "EP 1"} for i in range(50)]
    preview = preview_changes(rows, limit=10)
    assert len(preview) == 10


def test_numeric_to_alpha_mapping_locked():
    # Sanity check the canonical mapping doesn't drift
    assert NUMERIC_TO_ALPHA == {"1": "BL*", "2": "EL*", "3": "OC*", "4": "CL*"}
