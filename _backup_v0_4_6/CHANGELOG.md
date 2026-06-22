## v0.4.5 - 2026-06-20 - Phase 5: ODOT Export + Reverse Line-Connect

### Added
- `app/services/odot_exporter.py` - Civil3D and OpenRoads exporters
- `app/ui/export_tab.py` - new Export tab in main tab bar
- `tests/test_odot_exporter.py` (12 tests)

### Changed
- `app/services/line_connect_translator.py` - reverse direction
  (alphabetic -> numeric) implemented. BL/BL* -> 1, EL/EL* -> 2,
  OC/OC* -> 3, CL/CL* -> 4. BC/EC preserved.
- `app/ui/convert_line_connect_dialog.py` - reverse radio button enabled.
- `app/ui/main_window.py` - auto-patched to insert Export tab after
  Modified Data tab.
- `tests/test_line_connect_translator.py` - added 13 reverse-direction tests.

### Notes
- main_window.py is patched in-place by overlay/patch_main_window.py.
  The patcher is idempotent (safe to run multiple times).
- N, E, Z, and Point numbers are NEVER touched on export.
- Output CSVs have NO header row (AutoCAD/Civil3D requirement).
