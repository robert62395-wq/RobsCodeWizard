## v0.4.7 - 2026-06-22 - Phase 7: Dialect-aware export dispatch

### Added
- `app/services/grammar_normalizer.py` - to_vdt(), to_odot_alpha(),
  to_odot_numeric() normalizers. Maps any line-connect token to the
  target grammar.
- `tests/test_grammar_normalizer.py` (17 tests)
- `tests/test_odot_exporter.py` (10 tests covering all 3 dispatch paths)

### Changed
- `app/services/odot_exporter.py` - REPLACED. New explicit functions:
  export_vdt_to_civil3d, export_odot_to_civil3d, export_odot_to_openroads.
  Each is dialect-aware. Size tokens and '/' comment tails preserved.
  Backward-compat aliases export_civil3d / export_openroads kept.
- `app/ui/export_tab.py` - REPLACED. Detects parent.codeset.name and
  reconfigures UI: VDT mode disables OpenRoads with tooltip; ODOT mode
  enables both with grammar-specific button labels.

### Fixes
- Bug 4 (pre-v1.0): Dialect-aware export grammar dispatch.
  - VDT -> Civil3D: VDT grammar (letters only)
  - ODOT -> Civil3D: ODOT alphabetic
  - ODOT -> OpenRoads: ODOT numeric (default) or alphabetic
  - VDT -> OpenRoads: blocked at UI with explanatory tooltip

### v0.4.x track complete
All four pre-v1.0 bugs from the bug list are now fixed:
  - v0.4.4.1: PL added to ODOT catalog
  - v0.4.6:   size-bearing codes + suggestion column cleanup
  - v0.4.7:   dialect-aware export dispatch
Next stop: v1.0 final polish.
