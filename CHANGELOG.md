## v0.5.5 - 2026-06-25 - First-launch and Translation tab UX polish

### Added
- Raw Data first-launch empty-state guidance panel.
- Translation tab autoload/refresh behavior after opening a point file.
- Translation tab visual cleanup so the banner and confidence colors match the dark Raw Data theme.
- Translation tab model/view migration using `QTableView` + `TranslationTableModel`.

### Changed
- Translation tab no longer uses fragile QTableWidget row-building for its main table.
- Translation confidence colors now match Raw Data visual intensity:
  - Unmatched: red
  - Best-guess: yellow
  - Exact: green
  - Manual: blue
- Under-construction banner now uses dark-theme-safe styling.
- Removed forced white table styling from Translation tab.
- Removed broken `self.banner` styling reference.

### Fixed
- Translation tab unreadable text caused by pale row colors on dark theme.
- Startup crash caused by missing `QTableView` import after the model/view conversion.
- Runtime error caused by `QTableWidget.setModel()` being private.

### Notes
- Translation matching algorithm quality is still deferred for a later version.
- v0.5.5 focused on usability, readability, and architectural cleanup.
## v0.5.4 - 2026-06-24 - Performance rewrite (Raw Data tab)

### 🚀 Major Performance Improvement
- Replaced QTableWidget with QTableView + QAbstractTableModel (RawDataTableModel).
- Eliminated per-cell item creation and per-row coloring loops.
- `_populate_table` now completes in milliseconds instead of ~41 seconds on large files.
- Measured: ~525 rows now load essentially instantly (~0.05s or less).

### Technical Changes
- New file: `app/ui/raw_data_model.py` (QAbstractTableModel implementation).
- `_build_raw_data_tab` now uses QTableView bound to RawDataTableModel.
- `_populate_table`, `_apply_row_color`, `_jump_to_row`, `_on_context_menu`,
  `_apply_suggestion` fully rewritten to use model/view architecture.
- Row coloring moved into `model.data()` via `Qt.BackgroundRole`.
- Status update and recovery timer hooks preserved.

### Changed Logging
- Replaced noisy `[diag]` timing logs with a single summary:
  - `populate: X.XXXs (N rows)`

### Result
- Code-set switch and initial load are now instantaneous.
- UI no longer freezes during table population.
- Scales cleanly to thousands of rows.

### Notes
- This is the largest UI architecture change in v0.5.x.
- QTableWidget fully removed from Raw Data tab (now dead code elsewhere).
## v0.5.3.3 - 2026-06-23 - v0.5.3.1 wire-up + latent export crash hotfix

### Fixed
- 🚨 `app/ui/export_tab.py` — was unpacking 2-tuple returns from
  `export_vdt_to_civil3d`, `export_odot_to_civil3d`, and `export_odot_to_openroads`.
  v0.5.3.1 changed those to 3-tuples; this was a latent runtime crash
  that would fire the moment any user clicked an export button.
  Now correctly unpacks `(written, conversions, errors)` and displays a
  warning popup listing the first 10 row-level errors (if any).

### Added
- `app/services/file_parser.parse_file_with_errors()` — dispatcher that
  returns a `ParseResult` so callers can collect row-level errors.
  Legacy `parse_file()` preserved.
- `app/ui/main_window.py`:
  - `RecoveryTimer` created in `__init__`, started if
    `auto_save_recovery` setting is True (default), stopped cleanly in
    `closeEvent`.
  - `on_open_file` now uses `parse_file_with_errors` and shows the
    `ParseErrorDialog` after parse if any rows were skipped.
  - `mark_dirty()` called after every `_update_status_bar()` so the
    auto-save timer knows when to save.
  - `closeEvent` calls `force_save_now()` + `stop()` on the timer.
- `tests/test_file_parser_v0533.py` (4 tests)

### Notes
- Patchers idempotent via sentinel strings (`"v0.5.3.3 export errors"`,
  `"v0.5.3.3 wireup"`). Backups in `_backup_v0_5_3_3/`.
- v0.5.3.1 infrastructure (parse_errors, recovery_timer, parse_error_dialog)
  now actively serves users.
- ODOT parser still does not emit row-level errors; that's a v0.5.3.4
  candidate.
## v0.5.3.2 - 2026-06-23 - Hotfix: legacy test_odot_exporter.py 3-tuple unpack

### Fixed
- `tests/test_odot_exporter.py` — three legacy tests (`test_vdt_civil3d_strips_asterisk`,
  `test_odot_civil3d_numeric_to_alpha`, `test_odot_openroads_alpha_to_numeric`) were
  still unpacking 2-tuple returns after v0.5.3.1 changed the export functions to
  return `(written, conversions, errors)`. CI build failed with
  `ValueError: too many values to unpack (expected 2)`.
- Tests now unpack as `(written, conversions, _errors)` so the legacy assertions
  still pass while the new error-list contract is honored.

### Notes
- Patcher idempotent via sentinel `"v0.5.3.2 three-tuple unpack"`.
- Backups in `_backup_v0_5_3_2/`.
- No runtime behavior changes; only test expectations updated.
## v0.5.3.1 - 2026-06-23 - Error handling Phase 2

### Added
- `app/services/parse_errors.py` — `ParseError` and `ParseResult` dataclasses
  for collecting row-level errors during file parsing.
- `app/ui/parse_error_dialog.py` — `ParseErrorDialog` summary shown after
  parse if errors were collected. Lists skipped rows with line number,
  reason, and raw content. "Save error log..." button writes a text report.
- `app/services/recovery_timer.py` — `RecoveryTimer` Qt timer that
  auto-saves the current session every 5 minutes during edit sessions.
  Disables itself after 3 consecutive save failures.
- `tests/test_parse_errors.py` (6 tests)
- `tests/test_recovery_timer.py` (5 tests)
- `tests/test_parser_v0531.py` (5 tests)
- `tests/test_odot_exporter_v0531.py` (4 tests)

### Changed
- `app/services/parser.py` — added `parse_pnezd_with_errors()` returning
  `ParseResult`. Legacy `parse_pnezd()` kept as alias. Soft warnings for
  non-numeric N/E/Z values; hard errors for empty Point numbers.
- `app/services/recovery.py` — atomic write via temp file + `os.replace()`
  so a crash mid-save leaves the previous recovery intact.
- `app/services/odot_exporter.py` — all three export functions now return
  a 3-tuple `(written, conversions, errors)`. Errors list contains
  per-row failures with row index, point number, and exception message.
  Legacy `export_civil3d`/`export_openroads` aliases keep the 2-tuple
  return shape for backward compatibility.

### Notes
- Patchers idempotent via sentinel strings ("v0.5.3.1 row error recovery",
  "v0.5.3.1 atomic recovery write", "v0.5.3.1 export error tracking").
  Safe to re-run. Backups in `_backup_v0_5_3_1/`.
- Q1 picks (in order):
  - **Q1 = B**: parse errors shown via summary dialog after parse completes.
  - **Q2 = A**: recovery timer fires every 5 minutes.
  - **Q3 = A**: exporter skips bad rows, summarizes errors at the end.
## v0.5.3 - 2026-06-23 - Error handling & resilience (Phase 1)

### Added
- `app/services/safe_event_handler.py` — `@safe_handler` decorator for Qt
  event handlers. Routes exceptions to status bar (minor) or modal dialog
  (severe), preventing app crashes from uncaught slot exceptions.
- `app/services/recovery_dialog.py` — `CorruptionRecoveryDialog` shown when
  `translation_map.json` fails to load. Offers "Restore from backup" /
  "Reseed from catalog" / "Cancel" actions.
- `app/services/translation_map.py`:
  - `safe_load(path)` returns `(data, error_msg)` instead of raising,
    enabling graceful corruption recovery.
  - `restore_from_backup()` and `has_backup()` helpers.
  - Automatic backup-on-save: each successful `save()` first copies the
    existing map to `translation_map.backup.json` (replace) and to
    `data/translation_map_backups/translation_map_<timestamp>.json`
    (rolling history, last 10 kept).
- `tests/test_safe_event_handler.py` (5 tests)
- `tests/test_translation_map_safe_load.py` (7 tests)

### Changed
- `app/ui/main_window.py` — `[diag]` logging markers in
  `_revalidate_and_repopulate` downgraded from INFO to DEBUG. Logs are now
  less noisy during normal use; verbose tracing still available when DEBUG
  level is enabled.

### Deferred to v0.5.3.1
- CSV parse error row-level recovery (file_parser.py)
- Auto-save recovery file timer (recovery.py)
- Exporter file-level error reporting (odot_exporter.py)

### Notes
- All v0.5.3 patchers are idempotent (sentinel string check) and safe to
  re-run. Backups in `_backup_v0_5_3/`.
- Translation map backups in `app/data/translation_map_backups/` are
  pruned automatically; only the 10 most recent are kept.
## v0.5.2.1 - 2026-06-22 - Status bar foundation

### Added
- `app/services/status_bar_helper.py` - format_permanent_status() helper that
  builds the persistent left-aligned status bar text from codeset + source path
  + rows + results. Uses "Points:" label (not "Rows:") per locked spec, with
  thousands separators on point counts.
- `app/ui/help_icon.py` - reusable HelpIcon widget (small `?` toolbutton)
  that pops up a HelpDialog with HTML content and a "Don't show again"
  checkbox persisted in settings.
- `app/ui/help_dialogs.py` - HTML help content for 11 contextual topics:
  code_set, linework_fix, translate_source_target, translate_button,
  translate_filter_used, translate_bulk_accept, translate_reseed,
  export_use_numeric, point_offset, elevation_offset, convert_line_connect.

### Changed
- `app/ui/main_window.py` - patched in place (idempotent, sentinel
  "v0.5.2 status bar"):
  - Added imports for HelpIcon and format_permanent_status
  - Added QStatusBar initialization at end of `_build_ui`
  - Added `_update_status_bar` and `_flash_status` helper methods

### Notes
- This is the foundation patch. Wire-up calls to `self._update_status_bar()`
  in on_open_file / _on_revalidation_done / _maybe_restore_session are
  deferred to v0.5.2.2, which will also add tooltips and place the 11 ?
  icons next to advanced controls.
- Patcher is idempotent via the sentinel string. Safe to re-run.
- Original main_window.py backed up to _backup_v0_5_2/main_window.py.
## v0.5.1 - 2026-06-22 - Phase 1 of 7: Translation Tab UX Rebuild

### Removed Friction
- Source dropdown replaced with auto-detected read-only label.
- Target dropdown defaults to opposite of source.
- Apply Translation button simplified to "Translate Loaded Rows".

### Added
- `app/services/usage_analyzer.py` - analyze_used_codes() counts how many
  times each point code appears in parent.rows. build_usage_summary()
  cross-references against the translation map.
- `app/services/match_basis_descriptor.py` - describe() and short_label()
  produce human-readable match-basis explanations.
- Two-section table on Translation tab: USED IN LOADED FILE (sorted by
  frequency) + OTHER CATALOG CODES (alphabetical).
- Dirty indicator (bullet) for entries with unsaved overrides.
- Why column with match-basis explanation per entry.
- Used indicator column + Count column.
- Bulk "Accept all Best-Guess in view" action.
- Empty-state summary in review pane (Option C - used-in-file stats).
- Manual edits to ANY entry are supported (not just ODOT side).
- `tests/test_usage_analyzer.py` (10 tests)
- `tests/test_match_basis_descriptor.py` (8 tests)

### Changed
- `app/ui/translation_tab.py` - full rebuild.
- `app/ui/translation_review_pane.py` - wide bottom-mounted layout
  with side-by-side VDT/ODOT editors and full-width notes.

### Notes
- showEvent triggers refresh of source label, used counts, target default,
  and table repopulation. No live signal connection to Modified Data tab.
- map_modified signal still fires after Save Overrides or Accept-all-best
  for external listeners.
