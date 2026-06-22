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
