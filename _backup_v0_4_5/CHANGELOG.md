## v0.4.4 - 2026-06-20 - Phase 4: Hardened Offsets + IGLD85 Helpers

### Changed
- app/services/offsets.py - hardened, signatures preserved, NaN/inf rejected,
  input never mutated, N/E never touched.

### Added
- NAVD88_TO_IGLD85_OFFSET_OHIO = -0.55
- get_navd88_to_igld85_offset(region) helper
- apply_navd88_to_igld85(rows, region, skip_zero) shortcut
- tests/test_offsets.py (21 tests)
