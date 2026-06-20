"""Tests for app.services.offsets (v0.3.9.5.2.0.2 — Interpretation C)."""
from app.services.offsets import (
    apply_point_offset,
    detect_point_collisions,
    apply_elevation_offset,
)


def _rows(*p_values):
    return [{"P": p, "N": 100.0 + i, "E": 200.0 + i, "Z": 10.0 + i, "D": "EP"}
            for i, p in enumerate(p_values)]


def test_apply_point_offset_positive():
    rows = _rows(1, 2, 3)
    new_rows, applied = apply_point_offset(rows, 1000)
    assert applied == 3
    assert [r["P"] for r in new_rows] == [1001, 1002, 1003]
    assert [r["P"] for r in rows] == [1, 2, 3]


def test_apply_point_offset_negative():
    rows = _rows(1001, 1002, 1003)
    new_rows, applied = apply_point_offset(rows, -1000)
    assert applied == 3
    assert [r["P"] for r in new_rows] == [1, 2, 3]


def test_apply_point_offset_preserves_nez():
    rows = _rows(1, 2, 3)
    new_rows, _ = apply_point_offset(rows, 100)
    for orig, new in zip(rows, new_rows):
        assert orig["N"] == new["N"]
        assert orig["E"] == new["E"]
        assert orig["Z"] == new["Z"]


def test_detect_point_collisions_none():
    rows = _rows(1, 2, 3)
    dups = detect_point_collisions(rows, 1000)
    assert dups == []


def test_detect_point_collisions_old_new_overlap():
    """Interpretation C: new P shouldn't equal an OLD P of a different row."""
    # rows at 1, 2, 1001, 1002.  Offset +1000:
    #   new values = [1001, 1002, 2001, 2002]
    #   old values = [1, 2, 1001, 1002]
    #   1001 (new row 0) collides with 1001 (old row 2) -- conflict
    #   1002 (new row 1) collides with 1002 (old row 3) -- conflict
    rows = _rows(1, 2, 1001, 1002)
    dups = detect_point_collisions(rows, 1000)
    assert 1001 in dups
    assert 1002 in dups


def test_detect_point_collisions_duplicate_in_new():
    """Two rows shifting to the same new P value should also flag."""
    # Construct duplicate-input rows (invalid but worth catching):
    rows = [
        {"P": 100, "N": 1, "E": 2, "Z": 3, "D": "EP"},
        {"P": 100, "N": 4, "E": 5, "Z": 6, "D": "EP"},
    ]
    dups = detect_point_collisions(rows, 50)
    assert 150 in dups


def test_detect_point_collisions_self_doesnt_count():
    """Offset of 0 means new P == old P for every row, but that is not a collision."""
    rows = _rows(1, 2, 3)
    dups = detect_point_collisions(rows, 0)
    assert dups == []


def test_apply_elevation_offset_default():
    rows = _rows(1, 2, 3)
    new_rows, applied = apply_elevation_offset(rows, -0.5)
    assert applied == 3
    assert new_rows[0]["Z"] == 9.5
    assert new_rows[1]["Z"] == 10.5
    assert new_rows[2]["Z"] == 11.5


def test_apply_elevation_offset_skips_zero_by_default():
    rows = [
        {"P": 1, "N": 100, "E": 200, "Z": 10.0, "D": "EP"},
        {"P": 2, "N": 101, "E": 201, "Z": 0.0, "D": "EP"},
        {"P": 3, "N": 102, "E": 202, "Z": 11.0, "D": "EP"},
    ]
    new_rows, applied = apply_elevation_offset(rows, -0.5)
    assert applied == 2
    assert new_rows[0]["Z"] == 9.5
    assert new_rows[1]["Z"] == 0.0
    assert new_rows[2]["Z"] == 10.5


def test_apply_elevation_offset_preserves_n_e():
    rows = _rows(1, 2, 3)
    new_rows, _ = apply_elevation_offset(rows, 1.0)
    for orig, new in zip(rows, new_rows):
        assert orig["N"] == new["N"]
        assert orig["E"] == new["E"]
        assert orig["P"] == new["P"]


def test_apply_elevation_offset_handles_nonnumeric_z():
    rows = [{"P": 1, "N": 100, "E": 200, "Z": "bad", "D": "EP"}]
    new_rows, applied = apply_elevation_offset(rows, -0.5)
    assert applied == 0

