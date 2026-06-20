"""Phase 4 tests for Point + Elevation offset utilities."""
import pytest

from app.services.offsets import (
    apply_point_offset, detect_point_collisions, apply_elevation_offset,
    apply_navd88_to_igld85, get_navd88_to_igld85_offset,
    NAVD88_TO_IGLD85_OFFSET_OHIO,
)


def _sample_rows():
    return [
        {"P": 100, "N": 1000.0, "E": 2000.0, "Z": 850.0, "D": "EP"},
        {"P": 101, "N": 1001.0, "E": 2001.0, "Z": 851.0, "D": "EP"},
        {"P": 102, "N": 1002.0, "E": 2002.0, "Z": 0.0,   "D": "X"},
    ]


def test_apply_point_offset_positive():
    new_rows, applied = apply_point_offset(_sample_rows(), 1000)
    assert applied == 3
    assert [r["P"] for r in new_rows] == [1100, 1101, 1102]


def test_apply_point_offset_negative():
    new_rows, applied = apply_point_offset(_sample_rows(), -50)
    assert [r["P"] for r in new_rows] == [50, 51, 52]


def test_apply_point_offset_zero_keeps_values():
    new_rows, _ = apply_point_offset(_sample_rows(), 0)
    assert [r["P"] for r in new_rows] == [100, 101, 102]


def test_apply_point_offset_preserves_NEZ_and_D():
    rows = _sample_rows()
    new_rows, _ = apply_point_offset(rows, 500)
    for original, updated in zip(rows, new_rows):
        assert updated["N"] == original["N"]
        assert updated["E"] == original["E"]
        assert updated["Z"] == original["Z"]
        assert updated["D"] == original["D"]


def test_apply_point_offset_does_not_mutate_input():
    rows = _sample_rows()
    original_p = [r["P"] for r in rows]
    apply_point_offset(rows, 1000)
    assert [r["P"] for r in rows] == original_p


def test_apply_point_offset_rejects_nan():
    with pytest.raises(ValueError, match="must not be NaN"):
        apply_point_offset(_sample_rows(), float("nan"))


def test_apply_point_offset_rejects_inf():
    with pytest.raises(ValueError, match="infinity"):
        apply_point_offset(_sample_rows(), float("inf"))


def test_detect_point_collisions_finds_dups():
    rows = [{"P": 100}, {"P": 101}, {"P": 102}]
    assert detect_point_collisions(rows, 1) == [101, 102]


def test_detect_point_collisions_none():
    rows = [{"P": 100}, {"P": 101}, {"P": 102}]
    assert detect_point_collisions(rows, 1000) == []


def test_detect_point_collisions_with_negative_offset():
    rows = [{"P": 100}, {"P": 101}, {"P": 102}]
    assert detect_point_collisions(rows, -1) == [100, 101]


def test_detect_point_collisions_zero_offset_empty():
    assert detect_point_collisions([{"P": 100}, {"P": 101}], 0) == []


def test_apply_elevation_offset_basic():
    new_rows, applied = apply_elevation_offset(_sample_rows(), 1.5, skip_zero=True)
    assert applied == 2
    assert new_rows[0]["Z"] == pytest.approx(851.5)
    assert new_rows[1]["Z"] == pytest.approx(852.5)
    assert new_rows[2]["Z"] == 0.0


def test_apply_elevation_offset_includes_zero_when_disabled():
    new_rows, applied = apply_elevation_offset(_sample_rows(), 1.5, skip_zero=False)
    assert applied == 3
    assert new_rows[2]["Z"] == pytest.approx(1.5)


def test_apply_elevation_offset_negative():
    new_rows, applied = apply_elevation_offset(_sample_rows(), -0.55, skip_zero=True)
    assert applied == 2
    assert new_rows[0]["Z"] == pytest.approx(849.45)


def test_apply_elevation_offset_preserves_PNED():
    rows = _sample_rows()
    new_rows, _ = apply_elevation_offset(rows, 1.5)
    for original, updated in zip(rows, new_rows):
        assert updated["P"] == original["P"]
        assert updated["N"] == original["N"]
        assert updated["E"] == original["E"]
        assert updated["D"] == original["D"]


def test_apply_elevation_offset_does_not_mutate_input():
    rows = _sample_rows()
    original_z = [r["Z"] for r in rows]
    apply_elevation_offset(rows, 1.5)
    assert [r["Z"] for r in rows] == original_z


def test_apply_elevation_offset_rejects_nan():
    with pytest.raises(ValueError, match="must not be NaN"):
        apply_elevation_offset(_sample_rows(), float("nan"))


def test_apply_elevation_offset_rejects_inf():
    with pytest.raises(ValueError, match="infinity"):
        apply_elevation_offset(_sample_rows(), float("-inf"))


def test_navd88_to_igld85_offset_ohio():
    assert get_navd88_to_igld85_offset("ohio") == NAVD88_TO_IGLD85_OFFSET_OHIO
    assert get_navd88_to_igld85_offset("OHIO") == NAVD88_TO_IGLD85_OFFSET_OHIO


def test_navd88_to_igld85_unknown_region_raises():
    with pytest.raises(ValueError, match="Unknown region"):
        get_navd88_to_igld85_offset("antarctica")


def test_apply_navd88_to_igld85_basic():
    rows = _sample_rows()
    new_rows, applied = apply_navd88_to_igld85(rows, region="ohio")
    assert applied == 2
    assert new_rows[0]["Z"] == pytest.approx(850.0 + NAVD88_TO_IGLD85_OFFSET_OHIO)
    assert new_rows[2]["Z"] == 0.0
